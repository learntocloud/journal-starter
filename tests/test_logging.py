"""Tests for logging configuration in the OpenTelemetry-based application."""

import importlib
import logging

import pytest
from opentelemetry.sdk._logs import LoggingHandler

pytestmark = pytest.mark.no_db


def test_root_logger_is_configured_at_info():
    """api.main imports the application logger from telemetry.py and that setup
    configures the root logger at INFO.
    """
    import api.main  # noqa: F401

    root = logging.getLogger()
    assert root.level == logging.INFO, (
        "Root logger should be configured at INFO by api.telemetry.configure_logging()."
    )


def test_telemetry_configures_opentelemetry_logging_handler():
    """Telemetry must register an OpenTelemetry LoggingHandler on the root logger.

    The current implementation publishes logs through OpenTelemetry. The
    observable contract is that importing api.telemetry wires a LoggingHandler
    into the root logger and that the handler is configured at INFO. We avoid
    calling configure_logging() a second time, because that would attempt to
    replace the global OpenTelemetry LoggerProvider and raise an override error.
    """
    import api.telemetry  # noqa: F401

    root = logging.getLogger()
    otel_handlers = [h for h in root.handlers if isinstance(h, LoggingHandler)]

    assert otel_handlers, (
        "Expected api.telemetry to attach an OpenTelemetry LoggingHandler to the root logger."
    )

    otel_handler = otel_handlers[-1]
    assert otel_handler.level == logging.INFO, (
        "The OTel LoggingHandler should be configured at INFO."
    )


def test_api_main_emits_startup_log(caplog):
    """Importing api.main should emit the INFO-level startup record from the
    shared logger configured in api.telemetry.
    """
    import api.main

    with caplog.at_level(logging.INFO):
        importlib.reload(api.main)

    startup_records = [
        r
        for r in caplog.records
        if r.levelno >= logging.INFO and getattr(r, "name", None) == "journal-api"
    ]

    assert startup_records, (
        "Expected api.main to emit an INFO-level startup record via the "
        "application logger configured in api.telemetry. No INFO records were "
        "captured."
    )


def test_telemetry_uses_environment_service_name(monkeypatch):
    """Telemetry should read OTEL_SERVICE_NAME from the environment."""
    monkeypatch.setenv("OTEL_SERVICE_NAME", "custom-service")
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)

    import api.telemetry as telemetry

    reloaded = importlib.reload(telemetry)

    assert reloaded.resource.attributes["service.name"] == "custom-service"

"""Tests for Task 1: logging configuration in api.main."""

import importlib
import logging

import pytest

pytestmark = pytest.mark.no_db


def test_root_logger_is_configured_at_info():
    """Task 1: root logger level should be INFO (or finer) after importing api.main."""
    import api.main  # noqa: F401

    root = logging.getLogger()
    assert root.level != 0, (
        "Root logger should be configured (level should not be NOTSET). "
        "Did you call logging.basicConfig() in api/main.py?"
    )
    assert root.level <= logging.INFO, (
        "Root logger should be configured at INFO (or finer). "
        "Did you call logging.basicConfig() in api/main.py?"
    )


def test_api_main_installs_stream_handler_with_formatter():
    """Task 1: api/main.py must attach a StreamHandler with a Formatter to root.

    pytest installs its own handlers on the root logger at session start, so a
    naive ``len(root.handlers) >= 1`` check passes trivially even on a fresh
    fork. This test temporarily clears root handlers, reloads ``api.main`` so
    the learner's logging configuration runs from a clean slate, and verifies
    that a ``StreamHandler`` with a ``Formatter`` was actually attached — the
    behavior produced by ``logging.basicConfig(level=..., format=...)``.
    """
    root = logging.getLogger()
    saved_handlers = root.handlers[:]
    saved_level = root.level
    for h in saved_handlers:
        root.removeHandler(h)
    try:
        import api.main

        importlib.reload(api.main)

        handlers_with_formatter = [
            h
            for h in root.handlers
            if isinstance(h, logging.StreamHandler) and h.formatter is not None
        ]
        assert handlers_with_formatter, (
            "Expected api/main.py to configure logging so that a StreamHandler "
            "with a Formatter is attached to the root logger. The standard way "
            "to do this is logging.basicConfig(level=logging.INFO, format=...)."
        )
    finally:
        for h in root.handlers[:]:
            root.removeHandler(h)
        for h in saved_handlers:
            root.addHandler(h)
        root.setLevel(saved_level)


def test_api_main_emits_startup_log(caplog):
    """Task 1: importing api.main should emit at least one INFO-level log record.

    The reference solution logs a "Journal API starting up" message at import
    time. This test forces a fresh module execution via ``importlib.reload``
    under ``caplog.at_level(logging.INFO)`` and verifies a record is captured.
    On a fresh fork, ``api/main.py`` contains no logging calls, so no records
    are emitted and this test fails. Once the learner adds a
    ``logger.info(...)`` call (or ``logging.info(...)``) it passes.
    """
    import api.main

    with caplog.at_level(logging.INFO):
        importlib.reload(api.main)

    info_records = [r for r in caplog.records if r.levelno >= logging.INFO]
    assert info_records, (
        "Expected api/main.py to emit at least one INFO-level log when imported "
        "(e.g. logger.info('Journal API starting up') after configuring logging). "
        "No INFO records were captured."
    )

"""Task 3 configuration, operation logs, lifecycle, and privacy acceptance."""

import logging
import subprocess
import sys
from contextlib import asynccontextmanager, nullcontext
from unittest.mock import AsyncMock

import pytest

from api import main
from api.logging_config import configure_logging
from api.models.entry import EntryCreate
from api.repositories.interface_repository import DatabaseInterface
from api.services.entry_service import EntryService

pytestmark = pytest.mark.no_db


@pytest.fixture(autouse=True)
def restored_root_logger():
    root = logging.getLogger()
    saved_handlers = root.handlers[:]
    saved_level = root.level
    try:
        yield root
    finally:
        for handler in root.handlers[:]:
            root.removeHandler(handler)
            if handler not in saved_handlers:
                handler.close()
        for handler in saved_handlers:
            root.addHandler(handler)
        root.setLevel(saved_level)


@pytest.fixture
def isolated_root_logger(restored_root_logger):
    root = restored_root_logger
    for handler in root.handlers[:]:
        root.removeHandler(handler)
    root.setLevel(logging.WARNING)
    return root


@pytest.mark.exercise
def test_configures_clean_root_at_info_with_formatted_stream(isolated_root_logger):
    root = isolated_root_logger
    configure_logging()
    assert root.level == logging.INFO
    assert any(
        isinstance(handler, logging.StreamHandler) and handler.formatter is not None
        for handler in root.handlers
    )
    record = logging.LogRecord(
        "api.example", logging.INFO, __file__, 1, "example operation", (), None
    )
    assert any(
        all(part in handler.format(record) for part in ("INFO", "api.example", "example operation"))
        for handler in root.handlers
        if isinstance(handler, logging.StreamHandler)
    )


@pytest.mark.exercise
def test_sets_info_level_when_a_handler_already_exists(isolated_root_logger):
    root = isolated_root_logger
    handler = logging.StreamHandler()
    root.addHandler(handler)
    configure_logging()
    assert root.level == logging.INFO
    assert handler in root.handlers


@pytest.mark.exercise
@pytest.mark.parametrize("level", [logging.INFO, logging.DEBUG], ids=["INFO", "DEBUG"])
async def test_entry_operations(level, caplog, restored_root_logger):
    database = AsyncMock(spec=DatabaseInterface)
    database.create_entry.side_effect = lambda entry: entry
    database.delete_entry.return_value = True
    service = EntryService(database)
    entry_data = EntryCreate(
        work="sample-work-do-not-log",
        struggle="sample-struggle-do-not-log",
        intention="sample-intention-do-not-log",
    )
    configure_logging(level)
    assert restored_root_logger.level == level
    entry = await service.create_entry(entry_data)
    assert await service.delete_entry(entry.id) is True

    records = [record for record in caplog.records if record.name == "api.services.entry_service"]
    database.create_entry.assert_awaited_once_with(entry)
    database.delete_entry.assert_awaited_once_with(entry.id)
    assert any(record.levelno == logging.INFO for record in records)
    assert any(entry.id in record.getMessage() for record in records)
    debug_records = [record for record in records if record.levelno == logging.DEBUG]
    if level == logging.DEBUG:
        assert any(entry.id in record.getMessage() for record in debug_records)
        assert any("True" in record.getMessage() for record in debug_records)
    else:
        assert not debug_records
    for text in (entry_data.work, entry_data.struggle, entry_data.intention):
        assert text not in caplog.text


def test_configuration_preserves_existing_handlers(caplog, restored_root_logger):
    root = restored_root_logger
    existing = root.handlers[:]
    configure_logging()
    configure_logging()
    assert all(handler in root.handlers for handler in existing)
    assert caplog.handler in root.handlers
    with caplog.at_level(logging.INFO):
        logging.getLogger("api.main").info("capture-handler-still-active")
    assert "capture-handler-still-active" in caplog.text


def test_import_does_not_configure_logging_or_announce_startup():
    script = """
import logging
root = logging.getLogger()
assert not root.handlers
before = root.level
records = []
original_handle = logging.Logger.handle
def capture(self, record):
    records.append(record)
    return original_handle(self, record)
logging.Logger.handle = capture
logging.getLogger("api").setLevel(logging.DEBUG)
import api.main
assert root.handlers == []
assert root.level == before
assert not records
"""
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-c", script],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    assert result.stderr == ""


@pytest.fixture
def fake_database(monkeypatch):
    events = []
    database = object()

    @asynccontextmanager
    async def open_database(_url):
        events.append("ready")
        try:
            yield database
        finally:
            events.append("closed")

    monkeypatch.setattr(main, "PostgresDB", open_database)
    return database, events


@pytest.mark.exercise
@pytest.mark.parametrize("fail_inside", [False, True])
async def test_lifespan_logs_after_database_ready_and_during_cleanup(
    fake_database,
    caplog,
    fail_inside,
):
    database, events = fake_database
    observed = []

    class LifecycleHandler(logging.Handler):
        def emit(self, record):
            if record.name == "api.main" and record.levelno == logging.INFO:
                observed.append((record, events[:]))

    handler = LifecycleHandler()
    logger = logging.getLogger("api.main")
    logger.addHandler(handler)
    expected_error = (
        pytest.raises(RuntimeError, match="simulated application failure")
        if fail_inside
        else nullcontext()
    )
    try:
        with caplog.at_level(logging.INFO, logger="api"), expected_error:
            async with main.app.router.lifespan_context(main.app):
                assert main.app.state.database is database
                assert any(
                    record.getMessage().strip() and state == ["ready"] for record, state in observed
                )
                events.append("serving")
                if fail_inside:
                    raise RuntimeError("simulated application failure")
        assert events == ["ready", "serving", "closed"]
        assert any(
            record.getMessage().strip() and state == ["ready", "serving"]
            for record, state in observed
        )
        assert not hasattr(main.app.state, "database")
    finally:
        logger.removeHandler(handler)


async def test_lifespan_invokes_logging_configuration(fake_database, monkeypatch):
    calls = []
    monkeypatch.setattr(main, "configure_logging", lambda: calls.append("configured"))
    async with main.app.router.lifespan_context(main.app):
        assert calls == ["configured"]


@pytest.mark.parametrize("failure", ["settings", "pool"])
async def test_failed_startup_never_logs_readiness(failure, monkeypatch, caplog):
    def fail_settings():
        raise ValueError("invalid startup configuration")

    @asynccontextmanager
    async def fail_pool(_url):
        raise ValueError("pool unavailable")
        yield  # pragma: no cover

    if failure == "settings":
        monkeypatch.setattr(main, "get_settings", fail_settings)
    else:
        monkeypatch.setattr(main, "PostgresDB", fail_pool)
    with (
        caplog.at_level(logging.INFO, logger="api"),
        pytest.raises(
            ValueError,
            match=r"invalid startup configuration|pool unavailable",
        ),
    ):
        async with main.app.router.lifespan_context(main.app):
            pytest.fail("Invalid startup must not yield")
    assert not any(
        record.name == "api.main" and record.levelno == logging.INFO for record in caplog.records
    )
    assert not hasattr(main.app.state, "database")

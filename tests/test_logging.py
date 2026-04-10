"""Tests for Task 1: logging configuration in api.main."""
import logging

import pytest

pytestmark = pytest.mark.no_db


def test_root_logger_is_configured_at_info():
    import api.main  # noqa: F401

    root = logging.getLogger()
    assert root.level != 0 and root.level <= logging.INFO, (
        "Root logger should be configured at INFO (or finer). "
        "Did you call logging.basicConfig() in api/main.py?"
    )


def test_root_logger_has_handler():
    import api.main  # noqa: F401

    root = logging.getLogger()
    assert len(root.handlers) >= 1, (
        "Root logger should have at least one handler."
    )


def test_journal_logger_propagates():
    import api.main  # noqa: F401

    journal_logger = logging.getLogger("journal")
    assert journal_logger.propagate is True

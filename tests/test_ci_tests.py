"""Safeguards for PR label selection and cumulative exercise acceptance."""

import json
import subprocess
import sys

import pytest

from scripts import ci_tests

pytestmark = pytest.mark.no_db

EXPECTED_SELECTORS = {
    "get-entry": ("tests/test_api.py::TestGetSingleEntry",),
    "delete-entry": (
        "tests/test_api.py::TestGetSingleEntry",
        "tests/test_api.py::TestDeleteEntry",
    ),
    "validation": (
        "tests/test_api.py::TestGetSingleEntry",
        "tests/test_api.py::TestDeleteEntry",
        "tests/test_models.py::TestEntryCreateValidation",
        "tests/test_models.py::TestEntryUpdateModel",
        "tests/test_api.py::TestCreateEntry",
        "tests/test_api.py::TestUpdateEntry",
    ),
    "logging": (
        "tests/test_api.py::TestGetSingleEntry",
        "tests/test_api.py::TestDeleteEntry",
        "tests/test_models.py::TestEntryCreateValidation",
        "tests/test_models.py::TestEntryUpdateModel",
        "tests/test_api.py::TestCreateEntry",
        "tests/test_api.py::TestUpdateEntry",
        "tests/test_logging.py",
    ),
}


@pytest.mark.parametrize("task", ["setup", *EXPECTED_SELECTORS, "analysis"])
def test_selects_exact_task_label(task):
    event = {"pull_request": {"labels": [{"name": "help wanted"}, {"name": f"task:{task}"}]}}
    assert ci_tests.task_from_event(event) == task


@pytest.mark.parametrize(
    "labels",
    [
        [],
        [{"name": "documentation"}],
        [{"name": "task:logging"}, {"name": "task:validation"}],
        [{"name": "task:setup"}, {"name": "task:analysis"}],
        [{"name": "task:unknown"}],
        [{"name": "task:logging"}, {"name": "task:unknown"}],
        [{"name": "task:logging; echo unexpected"}],
        [{"name": "task:logging"}, {"name": "task:logging"}],
    ],
)
def test_requires_one_recognized_task_label(labels):
    with pytest.raises(ValueError, match="exactly one task label"):
        ci_tests.task_from_event({"pull_request": {"labels": labels}})


@pytest.mark.parametrize(
    "event",
    [
        None,
        [],
        {},
        {"pull_request": None},
        {"pull_request": {}},
        {"pull_request": {"labels": None}},
        {"pull_request": {"labels": ["task:logging"]}},
        {"pull_request": {"labels": [{"name": None}]}},
    ],
)
def test_rejects_invalid_event_data(event):
    with pytest.raises(ValueError, match="task label"):
        ci_tests.task_from_event(event)


@pytest.mark.parametrize(("task", "selectors"), EXPECTED_SELECTORS.items())
def test_acceptance_selects_exact_current_and_preceding_exercises(task, selectors):
    assert ci_tests.pytest_arguments(task) == ["-v", *selectors]


def test_analysis_runs_entire_suite_without_filters():
    assert ci_tests.pytest_arguments("analysis") == ["-v"]


def test_setup_runs_only_starter_safeguards():
    assert ci_tests.pytest_arguments("setup") == ["-v", "-m", "not exercise"]


def test_unknown_task_cannot_silently_select_a_subset():
    with pytest.raises(ValueError, match="Unknown task"):
        ci_tests.pytest_arguments("unknown")


@pytest.mark.parametrize("status", [0, 1, 5])
def test_cli_preserves_pytest_exit_status(monkeypatch, status):
    calls = []

    def run(command, *, check):
        assert check is False
        calls.append(command)
        return subprocess.CompletedProcess(command, status)

    monkeypatch.setattr(ci_tests.subprocess, "run", run)
    assert ci_tests.main(["--task", "logging"]) == status
    assert calls == [[sys.executable, "-m", "pytest", "-v", *EXPECTED_SELECTORS["logging"]]]


def test_cli_reads_labels_from_event_file(monkeypatch, tmp_path):
    event_path = tmp_path / "event.json"
    event_path.write_text(
        json.dumps({"pull_request": {"labels": [{"name": "task:delete-entry"}]}}),
        encoding="utf-8",
    )
    calls = []

    def run(command, *, check):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(ci_tests.subprocess, "run", run)
    assert ci_tests.main(["--event", str(event_path), "--collect-only"]) == 0
    assert calls == [
        [
            sys.executable,
            "-m",
            "pytest",
            "-v",
            *EXPECTED_SELECTORS["delete-entry"],
            "--collect-only",
        ]
    ]


@pytest.mark.parametrize("contents", ["not json", "{}", '{"pull_request": {"labels": []}}'])
def test_invalid_event_fails_without_running_pytest(monkeypatch, tmp_path, capsys, contents):
    event_path = tmp_path / "event.json"
    event_path.write_text(contents, encoding="utf-8")

    def unexpected_run(*args, **kwargs):
        pytest.fail("Invalid labels must not invoke pytest")

    monkeypatch.setattr(ci_tests.subprocess, "run", unexpected_run)
    with pytest.raises(SystemExit) as error:
        ci_tests.main(["--event", str(event_path)])
    assert error.value.code == 2
    assert "error:" in capsys.readouterr().err


def test_missing_event_file_fails_with_a_diagnostic(tmp_path, capsys):
    with pytest.raises(SystemExit) as error:
        ci_tests.main(["--event", str(tmp_path / "missing.json")])
    assert error.value.code == 2
    assert "error:" in capsys.readouterr().err

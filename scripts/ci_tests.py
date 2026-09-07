"""Run the acceptance checks selected by a task name or GitHub PR event."""

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path

TASK_TESTS: dict[str, tuple[str, ...]] = {
    "get-entry": ("tests/test_api.py::TestGetSingleEntry",),
    "delete-entry": ("tests/test_api.py::TestDeleteEntry",),
    "validation": (
        "tests/test_models.py::TestEntryCreateValidation",
        "tests/test_models.py::TestEntryUpdateModel",
        "tests/test_api.py::TestCreateEntry",
        "tests/test_api.py::TestUpdateEntry",
    ),
    "logging": ("tests/test_logging.py",),
    "analysis": (),
}
TASKS = ("setup", *TASK_TESTS)
LABEL_HELP = (
    "Add exactly one task label to the PR: "
    + ", ".join(f"task:{task}" for task in TASKS)
    + ". Use task:setup for non-exercise work; "
    "use the matching exercise label for Python tasks. "
    "See docs/04-development-workflow.md#task-labels."
)


def task_from_event(event: object) -> str:
    if not isinstance(event, dict) or not isinstance(event.get("pull_request"), dict):
        raise ValueError("Expected a pull_request event. " + LABEL_HELP)
    labels = event["pull_request"].get("labels")
    if not isinstance(labels, list):
        raise ValueError("Expected a PR labels list. " + LABEL_HELP)
    task_labels: list[str] = []
    for label in labels:
        if not isinstance(label, dict) or not isinstance(label.get("name"), str):
            raise ValueError("Invalid PR label data. " + LABEL_HELP)
        name = label["name"]
        if name.startswith("task:"):
            task_labels.append(name)
    if len(task_labels) != 1:
        raise ValueError(LABEL_HELP)
    task = task_labels[0].removeprefix("task:")
    if task not in TASKS:
        raise ValueError("Unrecognized task label. " + LABEL_HELP)
    return task


def pytest_arguments(task: str) -> list[str]:
    if task not in TASKS:
        raise ValueError(f"Unknown task: {task!r}")
    if task == "setup":
        return ["-v", "-m", "not exercise"]
    if task == "analysis":
        return ["-v"]
    selectors: list[str] = []
    for name, tests in TASK_TESTS.items():
        selectors.extend(tests)
        if name == task:
            break
    return ["-v", *selectors]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--task", choices=TASKS, help="Task to reproduce locally")
    source.add_argument("--event", type=Path, help="GitHub pull_request event JSON file")
    parser.add_argument(
        "--collect-only", action="store_true", help="List the selected tests without running them"
    )
    args = parser.parse_args(argv)
    try:
        task = (
            task_from_event(json.loads(args.event.read_text(encoding="utf-8")))
            if args.event is not None
            else args.task
        )
        arguments = pytest_arguments(task)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if args.collect_only:
        arguments.append("--collect-only")
    command = [sys.executable, "-m", "pytest", *arguments]
    print(f"Task acceptance: task:{task}", flush=True)
    print(shlex.join(command), flush=True)
    return subprocess.run(command, check=False).returncode  # noqa: S603


if __name__ == "__main__":
    raise SystemExit(main())

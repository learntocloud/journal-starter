# Chapter 8: Use Logs to Understand the API

[Home](../README.md) · **Chapter 8 of 11**

Configure logging, trace entry operations, and compare normal operational
events with diagnostic detail.

## Before You Begin

- Branch: `feature/logging-setup`
- PR label: `task:logging`
- Edit: `api/logging_config.py` and `api/main.py`

```bash
git checkout main &&
git pull --ff-only origin main &&
git checkout -b feature/logging-setup
```

## Configure Logging

Complete `configure_logging(level: int = logging.INFO)`:

- Use the requested level and default to INFO.
- Set the root logger's level.
- Add a formatted `StreamHandler` only when no handlers exist.
- Include the level, logger name, and message.
- Preserve handlers installed by a server or test runner.
- Do not use `force=True`.

Use module loggers such as `logging.getLogger(__name__)` and leave propagation
enabled.

## Log the Application Lifecycle

In the application lifespan:

- Log an INFO readiness message after the database is ready.
- Log an INFO shutdown message while the application closes.

Keep logging configuration in the lifespan. Importing a module is not the same
as starting the application.

## Observe the Logs

Start the API, then use its docs to create and delete a made-up entry. Stop the
API and identify the readiness, operation, and shutdown messages.

Compare INFO and DEBUG:

```bash
uv run pytest 'tests/test_logging.py::test_entry_operations[INFO]' --log-cli-level=INFO
uv run pytest 'tests/test_logging.py::test_entry_operations[DEBUG]' --log-cli-level=DEBUG
```

In your pull request description, include a short log sample and explain:

- What appears at INFO versus DEBUG
- How the entry ID connects operations
- Which messages describe an attempt versus a confirmed result
- Why readiness is logged after the database opens
- Which data must stay out of logs

Never log journal text, provider messages, settings objects, or credentials.

## Run the Checks

```bash
uv run pytest tests/test_logging.py
uv run ruff check .
uv run ruff format .
uv run pyright
```

## Finish the Chapter

```bash
git add .
git commit -m "Configure application logging"
git push -u origin feature/logging-setup
```

Then:

1. Open a pull request to your fork's `main`.
2. Add the `task:logging` label and include your observations.
3. Wait for CI, review the diff, and merge the pull request.

---

[← Previous: Input validation](07-input-validation.md) ·
[Next: Set up an AI provider →](09-ai-setup.md)

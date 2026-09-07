# Chapter 7: Use Logs to Understand the API

[Home](../README.md) · **Chapter 7 of 10**

In this chapter, you will configure logging and observe messages from entry
operations. You'll use INFO to follow write outcomes and DEBUG to investigate
attempts and routine reads. An attempt is not proof that an operation succeeded.

## 1. Prepare Your Branch

1. Make sure your validation pull request is merged, then check your working tree:

   ```bash
   git status
   ```

   It should be clean before you continue.

2. Switch to `main`:

   ```bash
   git checkout main
   ```

3. Pull the latest changes:

   ```bash
   git pull origin main
   ```

4. Create the branch for this task:

   ```bash
   git checkout -b feature/logging-setup
   ```

## 2. Configure Logging

1. Open `api/logging_config.py` and find `configure_logging`.

   Logs record events while an application runs. A logger creates a log message,
   and a handler sends it somewhere, such as the terminal. The root logger is
   the shared logger that module loggers can pass their messages to.

2. Complete `configure_logging(level: int = logging.INFO)` so it uses the
   requested level and defaults to INFO.

   INFO includes messages about normal operation. DEBUG includes more detail
   for investigating behavior. Setting a level determines which messages are
   allowed through.

3. Configure a `StreamHandler` only when the root logger has no handlers.
   Format messages to include the level, logger name, and message text.

   A `StreamHandler` writes to a stream such as the terminal. You can use
   `logging.basicConfig()` to set it up. Preserve handlers that a server or
   test runner has already installed, and do not use `force=True`.

4. Set the root logger's level explicitly, even when handlers already exist.

   `logging.basicConfig()` does nothing if the root logger already has handlers.
   Setting the root level separately lets module loggers that inherit it use
   the requested level. Existing handlers keep their own formats, levels, and
   filters, so they may still exclude some messages. Do not overwrite those
   settings to make every output look the same.

5. Open `api/services/entry_service.py` and inspect the existing calls to
   `logger.info()` and `logger.debug()`.

   Use module loggers such as `logging.getLogger(__name__)` for application
   messages. `__name__` identifies the module the message came from. Leave
   propagation enabled so messages reach the shared handlers. The entry-operation
   messages are already supplied; you do not need to add them again.

   In this service, INFO records write outcomes after the database call returns.
   DEBUG adds write attempts and routine read results. A missing entry is reported
   as missing, not as a successful update or deletion. If the database raises an
   exception, the service does not emit a success message.

## 3. Log Startup and Shutdown

1. Open `api/main.py` and find the `lifespan` function.

   The application lifespan runs setup when the API starts and cleanup when it
   stops. Code before `yield` prepares the application to receive requests;
   cleanup after `yield` runs when the application closes.

2. Add an INFO readiness message after the database is ready and before `yield`.
   A readiness message should mean the application is actually ready, not just
   that startup has begun.

3. Add an INFO shutdown message in the cleanup block.

4. Keep the call to `configure_logging()` inside the lifespan. Importing a module
   is not the same as starting the application. Save your changes.

   Never log journal text, provider messages, settings objects, or credentials.
   Keep log samples in your pull request free of that data too.

## 4. Observe the Logs

1. If the API is still running, stop it with `Ctrl+C` in its terminal.

2. Start the API:

   ```bash
   uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Find your readiness message in the terminal.

3. Open <http://localhost:8000/docs>. Use **POST `/entries`** to create a made-up
   entry, then copy its `id` from the HTTP 201 response. Find `Entry <id> created`
   in the server terminal. This INFO message is emitted after the database
   returns the stored entry.

4. Use **DELETE `/entries/{entry_id}`** with the ID you copied. Find
   `Entry <id> deleted` in the server terminal and check the HTTP 200 response.
   The shared ID connects creation and deletion without needing DEBUG.

   Repeat the DELETE with the same ID. Expect HTTP 404 and
   `Entry <id> not found; nothing deleted` at INFO, not another success message.

5. Stop the API with `Ctrl+C`. Find your shutdown message.

6. Run the entry-operation test at INFO:

   ```bash
   uv run pytest 'tests/test_logging.py::test_entry_operations[INFO]' --log-cli-level=INFO
   ```

   Observe which operation messages appear. Pytest's live-log handler uses its
   own format, which may differ from the terminal format you configured with
   `basicConfig()`. That is expected when existing handlers are preserved.

7. Run the same test at DEBUG:

   ```bash
   uv run pytest 'tests/test_logging.py::test_entry_operations[DEBUG]' --log-cli-level=DEBUG
   ```

   This test creates and deletes an entry; it does not fetch one. The same INFO
   outcome messages still appear. DEBUG adds `Creating entry <id>` and
   `Deleting entry <id>` before the database calls. Compare each attempt with
   its completion message: an attempt alone does not confirm success.

   Focus on messages from the `api.services.entry_service` logger. DEBUG may
   also show messages from other loggers, such as an asyncio selector message;
   those are not entry-operation messages.

8. Prepare a short log sample and your observations for the pull request description:

   | Question | What to record |
   |----------|----------------|
   | What changes between INFO and DEBUG? | Examples of messages that appear at each level |
   | How can you follow one entry? | How its ID connects messages from different operations |
   | Did an operation start or finish? | Which messages describe an attempt and which confirm a result |
   | What if the entry is missing? | How the repeated DELETE's message differs from a successful deletion |
   | When is the API ready? | Why the readiness message comes after the database opens |
   | What should stay out of logs? | The kinds of data you must not include |

## 5. Run the Checks

1. Run the logging tests:

   ```bash
   uv run pytest tests/test_logging.py
   ```

   All tests in this file should pass.

2. Run Ruff:

   ```bash
   uv run ruff check .
   ```

3. Format the code:

   ```bash
   uv run ruff format .
   ```

4. Run Pyright:

   ```bash
   uv run pyright
   ```

## 6. Review and Submit Your Work

1. Review your changes:

   ```bash
   git diff
   ```

2. Confirm which files changed:

   ```bash
   git status
   ```

3. Stage the logging configuration and application:

   ```bash
   git add api/logging_config.py api/main.py
   ```

4. Commit your changes:

   ```bash
   git commit -m "Configure application logging"
   ```

5. Push your branch:

   ```bash
   git push -u origin feature/logging-setup
   ```

6. Open a pull request to your fork's `main` branch. Describe your changes and
   include your log sample and observations.

7. Add exactly one task label: `task:logging`. Create it if it does not exist.

8. Wait for CI to pass, review the pull request's changes, and merge it.

## Before You Continue

Your application should log startup, entry operations, and shutdown, and your
pull request should be merged. You should be able to describe what DEBUG adds
to the INFO output.

---

[← Previous: Input validation](06-input-validation.md) ·
[Next: Set up an AI provider →](08-ai-setup.md)

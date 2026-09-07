# Troubleshooting

[Home](../../README.md) · [Capstone](../01-prerequisites.md)

Use the section that matches the problem, then return to the chapter you were
following.

- [Development container will not open](#development-container-will-not-open)
- [API will not start](#api-will-not-start)
- [Missing or invalid settings](#missing-or-invalid-settings)
- [Cannot connect to PostgreSQL](#cannot-connect-to-postgresql)
- [Database-backed tests fail during setup](#database-backed-tests-fail-during-setup)
- [Tests do not appear or breakpoints are not hit](#tests-do-not-appear-or-breakpoints-are-not-hit)
- [Changes are not taking effect](#changes-are-not-taking-effect)

## Development Container Will Not Open

**Likely cause:** Docker Desktop is not running or the container needs rebuilding.

1. Start Docker Desktop.
2. In VS Code, run **Dev Containers: Rebuild and Reopen in Container**.
3. Wait for PostgreSQL to become healthy.

## API Will Not Start

**Likely causes:** Dependencies are missing, PostgreSQL is unavailable, or
configuration is invalid.

1. From the project root inside the devcontainer, run `uv sync`.
2. On your host machine, run `docker ps` and confirm PostgreSQL is running.
3. Read the startup error. If it mentions `ValidationError`, use the next
   section.
4. Restart the API after correcting the problem.

The API opens its database pool during startup, so an unavailable database
prevents the server from starting.

## Missing or Invalid Settings

**Symptom:** Startup reports
`pydantic_core._pydantic_core.ValidationError`.

Compare `.env` with [`.env-sample`](../../.env-sample). Check the field named in
the error:

- `DATABASE_URL` must be a PostgreSQL URL.
- `TEST_DATABASE_URL` must identify a separate database ending in `_test`.
- `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `OPENAI_MODEL` must be nonblank.
- `OPENAI_BASE_URL` must be an HTTP(S) URL.

The placeholder AI values work for Tasks 1-3 but not live AI verification.
Do not print settings or secrets while troubleshooting.

## Cannot Connect to PostgreSQL

1. Confirm `.env` exists and contains the sample local database settings.
2. On your host machine, run `docker ps`.
3. Restart the API after PostgreSQL is available.

Rebuilding the devcontainer preserves the PostgreSQL volume and does not rerun
initialization against an existing volume. Changing `POSTGRES_USER`,
`POSTGRES_PASSWORD`, or `POSTGRES_DB` in `.env` also does not alter an already
initialized database.

Do not delete the volume as a troubleshooting shortcut; it contains your
journal entries.

## Database-Backed Tests Fail During Setup

First check that `TEST_DATABASE_URL`:

- Exists in `.env`
- Names a database ending in `_test`
- Does not name the same database as `DATABASE_URL`
- Places the database name in the URL path

Tests refuse unsafe database settings and never fall back to the application
database.

### Provision a Missing Test Database

Existing PostgreSQL volumes may predate the test-database initialization
script. On your **host machine**, use `docker ps` to find the PostgreSQL
container, then run:

```bash
docker exec YOUR_POSTGRES_CONTAINER psql -U postgres -d career_journal \
  -v ON_ERROR_STOP=1 -f /docker-entrypoint-initdb.d/database_setup_test.sql
```

Replace `YOUR_POSTGRES_CONTAINER` with the actual name. Adjust the username or
database only if you intentionally changed the sample settings.

This creates the test database without deleting application data. Never store
personal entries in the test database because tests erase its rows.

To run only database-free tests:

```bash
uv run pytest -m no_db
```

## Tests Do Not Appear or Breakpoints Are Not Hit

1. Work inside the devcontainer and run `uv sync` from the project root.
2. Run **Python: Select Interpreter** and choose
   `/workspaces/.venv/bin/python`. An interpreter selected previously can
   override the repository's default.
3. Confirm that the **Python** and **Python Debugger** extensions are enabled
   in the devcontainer. Rebuild the container if they have not been installed.
4. In VS Code's **Testing** view, use **Refresh Tests**. If discovery fails,
   read its error output before continuing.
5. Save your Python files, set a breakpoint on an executable line, and choose
   **Debug Test** for the individual case. **Run Test** does not use the
   debugger. Starting the FastAPI launch profile does not run the test.

The guided activity requires the completed `EntryUpdate` model. If
`entry_update` is still a dictionary, finish connecting the model to the PATCH
handler before evaluating its model methods.

A request rejected with 422 may never reach the handler: FastAPI validates
its body first. Use the valid `[work]` case from Chapter 7 for the walkthrough.
Ordinary API tests also bypass application startup and shutdown, so they do
not hit lifespan breakpoints.

Database-backed tests erase rows in the test database. Do not start another
database-backed test while paused in the debugger. Use **Continue** to let the
current test finish and run its cleanup.

## Changes Are Not Taking Effect

| What changed? | What to do |
|---------------|------------|
| Python code | The terminal server with `--reload` reloads automatically; restart an API debugger session after editing |
| `.env` settings | Stop and restart the API or debug session |
| Devcontainer features, extensions, or Compose configuration | Run **Dev Containers: Rebuild Container** |

Process environment variables override `.env`. If restarting does not load an
edited value, check for a conflicting variable exported in the terminal.

For fork updates and merge conflicts, use
[Sync your fork with upstream](upstream-sync.md).

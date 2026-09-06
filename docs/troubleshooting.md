# Troubleshooting

[README](../README.md) > Troubleshooting

Return to [setup](setup.md), the [development workflow](workflow.md), or
[your task](tasks.md) after resolving the problem. Run application and test
commands from the **project root inside the development container**; run
Docker commands on your **host machine**.

## API will not start

- Follow [Run the API](setup.md#5-run-the-api), including installing dependencies.
- Check PostgreSQL is running with `docker ps` on your host.
- If needed, restart its container on your host with
  `docker restart your-postgres-container-name`, using the actual container name.
- The API opens its shared connection pool during startup. If PostgreSQL is
  unavailable, start it first, then restart the API.

## Missing or invalid settings

If startup reports `pydantic_core._pydantic_core.ValidationError`, a required
variable in `.env` may be missing or mistyped. The error names the field, such
as `database_url` or `openai_api_key`.

Compare with [`.env-sample`](../.env-sample), correct the named setting, and
restart the API. The [`Settings` class](../api/config.py) uses
[pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
to validate configuration when settings are first loaded, before the API opens
its database pool.

## Cannot connect to the database

- Verify `.env` exists with the correct `DATABASE_URL`.
- Check the PostgreSQL container is running and restart the API after editing
  its connection settings.
- Rebuilding does not reset an existing database's credentials. See
  [database volumes](#database-volumes-and-initialization) before changing them.

## Restarting versus rebuilding

| What changed? | What to do |
|---------------|------------|
| Python application code | The API's `--reload` mode normally reloads it automatically |
| Application settings in `.env`, such as `OPENAI_*` | Stop the API with `Ctrl+C` and start it again; `.env` is not watched by default and settings are cached |
| Devcontainer image, features, or Compose configuration | Run **Dev Containers: Rebuild Container** from the VS Code Command Palette |

If editing `.env` still has no effect after restarting:

- For an older devcontainer, follow the one-time upgrade below to remove
  container-injected settings.
- Remove conflicting variables explicitly exported in your terminal; process
  environment variables take precedence over `.env`.

### Database volumes and initialization

Rebuilding does not delete the PostgreSQL volume or rerun initialization scripts
against an existing volume. Changing `POSTGRES_USER`, `POSTGRES_PASSWORD`, or
`POSTGRES_DB` in `.env` also does not change an already initialized database.
Keep the sample database settings unless you intentionally update the database
itself. **Do not delete the volume to troubleshoot configuration: it contains
your journal entries.**

## Upgrading an existing devcontainer

If your devcontainer predates the dotenv-loading and test-database isolation
changes:

1. Add `TEST_DATABASE_URL` from [`.env-sample`](../.env-sample) to your `.env`
   if it is missing. It must identify a separate test database, not your
   application database.
2. Run **Dev Containers: Rebuild Container** to load the updated configuration
   and remove previously injected application settings. Restarting the API or
   old container alone does not remove those variables.
3. Provision the test database using the instructions below if it is missing.

After this one-time rebuild, application settings edits only require an API
restart; newly started scripts and test commands load `.env` when run.

### Provision a missing test database

Existing PostgreSQL volumes are preserved, so initialization scripts do not run
again automatically. On your **host machine**, use `docker ps` to find the
PostgreSQL container name, then run:

```bash
docker exec YOUR_POSTGRES_CONTAINER psql -U postgres -d career_journal \
  -v ON_ERROR_STOP=1 -f /docker-entrypoint-initdb.d/database_setup_test.sql
```

Replace `YOUR_POSTGRES_CONTAINER` with its actual name; adjust the username and
application database if you changed the sample defaults. If the script is
missing, rebuild using the current devcontainer configuration first.

This command creates the test database and applies the shared schema without
deleting application data. **Do not delete the existing database volume.**
Never store personal entries in the test database: database-backed tests erase
its entries before and after each test.

## Database-backed tests fail during setup

- Check `TEST_DATABASE_URL` in `.env` points to the dedicated test database,
  not your application database. Follow the
  [test database safety requirements](workflow.md#test-database-safety).
- If `career_journal_test` does not exist,
  [provision the missing test database](#provision-a-missing-test-database).
- Tests marked `no_db` do not need a database connection and can be run with
  `uv run pytest -m no_db`.

Failures in unfinished exercises are different from environment failures.
Use the [task acceptance criteria](tasks.md) and
[test-output guidance](workflow.md#3-run-the-acceptance-and-code-quality-checks)
to distinguish them.

## Development container will not open

- Ensure Docker Desktop is running.
- Try **Dev Containers: Rebuild and Reopen in Container**.

For analysis-provider failures, see the
[AI response and error-handling guide](ai-analysis.md#requesting-structured-output).
For upstream changes or merge conflicts, follow
[safe fork synchronization](upstream-sync.md) rather than deleting your fork.

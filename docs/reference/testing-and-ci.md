# Testing and CI

[Home](../../README.md) · [Capstone](../01-prerequisites.md)

Each exercise includes its targeted tests and code-quality commands. Use this
reference to understand CI's cumulative checks or test database behavior.
Run commands from the **project root inside the devcontainer**.

## Task Labels and Cumulative Checks

Open pull requests against **your fork's `main` branch**, not
`learntocloud/journal-starter`. Add exactly one task label from the table below;
create the label in your fork if it does not exist.

| Chapter | PR label | Local `--task` value |
|---------|----------|----------------------|
| Setup or non-exercise work | `task:setup` | `setup` |
| GET one entry | `task:get-entry` | `get-entry` |
| DELETE one entry | `task:delete-entry` | `delete-entry` |
| Input validation | `task:validation` | `validation` |
| Logging | `task:logging` | `logging` |
| AI analysis | `task:analysis` | `analysis` |

CI runs code quality, starter safeguards, and the labeled task plus all
preceding exercises. A green intermediate task does not mean later tasks are
complete. The setup label runs starter safeguards without requiring any
exercises.

To run the same cumulative exercise selection locally, substitute the
appropriate `--task` value:

```bash
uv run python -m scripts.ci_tests --task logging
```

Run the other CI checks locally with:

```bash
uv run pytest -m 'not exercise'
uv run ruff check .
uv run ruff format --check .
uv run pyright
```

Use `uv run ruff format .` to apply formatting changes. Do not change supplied
tests to make them pass. Wait for CI, review the diff, and merge each exercise's
pull request before starting the next one.

## Test Database Safety

Database-backed tests use only `TEST_DATABASE_URL`. They refuse to run if the
test URL is missing, names the application database, or does not use a database
name ending in `_test`. There is no fallback to the application database.

Database access is opt-in through fixtures: `test_db` (also used by
`test_client`) and the lifespan tests' `application` fixture request
`cleanup_database`. These fixtures erase test entries before and after each
test. Tests without a database fixture do not open or clean a database.
The `no_db` marker selects offline tests and supplies synthetic settings; it
is not what prevents database access.

Run database-backed tests serially. Concurrent runs or workers must use
separate dedicated test databases so cleanup cannot erase another run's data.
Never store personal data in the test database.

If test setup fails, follow
[Database-backed tests fail during setup](troubleshooting.md#database-backed-tests-fail-during-setup).

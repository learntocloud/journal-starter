# Development Workflow

[README](../README.md) > [Setup](setup.md) > Workflow > [Tasks](tasks.md)

Complete [setup](setup.md) first. Then prepare your development tools once and
follow the task workflow for each exercise.

Unless a step explicitly says otherwise, run commands from the **project root**
in the **VS Code terminal inside the development container**. Do not `cd` into
`api/`, `tests/`, or `docs/` to run them.

## First-Time Setup

### Test database safety

**Tests reset the test database; your journal entries are preserved.**
The running API uses `DATABASE_URL` (`career_journal`), while database-backed
tests use only `TEST_DATABASE_URL` (`career_journal_test`). Test requests use
a database dependency override; their HTTP client does not start the production
lifespan. Dedicated lifespan tests explicitly supply the test database to startup.

Never store personal entries in the test database: its entries are deleted
before and after every database-backed test.

A fresh devcontainer provisions both databases automatically. Tests refuse
database operations if `TEST_DATABASE_URL` is missing or invalid, does not
name a database ending in `_test`, or names the same database as `DATABASE_URL`.
Database names must be in the URL path, not a `database` or `dbname` query
parameter. There is no fallback to the application database.

If you already have a devcontainer from before test-database isolation was added,
follow the [existing-devcontainer upgrade instructions](troubleshooting.md#upgrading-an-existing-devcontainer).
Do not delete your database volume to fix test setup.

### Prepare the tools

Dependencies were installed during [Run the API](setup.md#5-run-the-api).
If you skipped that step, or dependencies have changed, run `uv sync` now.
The `dev` group in `pyproject.toml` is included by default by both `uv sync`
and `uv run`, keeping pytest, Ruff, Pyright, and pre-commit available.

Install the pre-commit hooks so Ruff runs automatically on every commit:

```bash
uv run pre-commit install
```

Run the tests to see the starting state:

```bash
uv run pytest
```

Some tests pass for pre-built features and safeguards; failures for unfinished
Tasks 1-4 are expected. For example:

```text
FAILED tests/test_logging.py::test_root_logger_is_configured_at_info
FAILED tests/test_api.py::TestGetSingleEntry::test_get_entry_by_id_success
FAILED tests/test_api.py::TestDeleteEntry::test_delete_entry_success
FAILED tests/test_models.py::TestEntryCreateValidation::test_empty_string_rejected
FAILED tests/test_models.py::TestEntryUpdateModel::test_partial_update
FAILED tests/test_llm_service.py::test_analyze_entry_actually_calls_llm
```

This list is not exhaustive; some tests run once per field or input value.
See [task acceptance criteria and test coverage](tasks.md) for the commands
relevant to each exercise.

Automated tests cover selected behaviors, not every possible bug. They do not
replace the required manual acceptance steps for Tasks 4 and 5.

## For Each Task

### 1. Create a branch

[Branches](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-branches)
let you work on features in isolation. Before starting the next task, review
and merge the previous task's PR into **your fork's `main`** as described in
step 5. Commit any work you intend to keep on its current branch, then check
that your working tree is clean:

```bash
git status
```

Update local `main` and create the new task branch:

```bash
git checkout main &&
git pull --ff-only origin main &&
git checkout -b feature/your-feature-name
```

Replace the feature branch name with the one listed for your task. The `&&`
operators stop the sequence if a command fails. If the fast-forward fails,
reconcile your local and remote commits before continuing; do not reset or
force-push to discard them.

### 2. Implement the feature

Edit the files listed in [your task](tasks.md). Check their TODO comments for
guidance on what to implement.

### 3. Run the acceptance and code-quality checks

First run the acceptance commands listed for your task. You can also run the
full suite to look for regressions; tests for other unfinished tasks are still
expected to fail:

```bash
uv run pytest
```

[pytest](https://docs.pytest.org/) runs automated checks of your code's behavior.
Inspect failures to distinguish an assertion failure from a setup problem, such
as a missing setting or unavailable database. For example, `assert 501 == 200`
means the endpoint is still returning "Not Implemented".

Passing tests mean the covered checks passed, not that every edge case is
correct. Confirm all acceptance criteria, including manual steps.
Use `uv run pytest -v` to see individual results, or
`uv run pytest -v --tb=short` for concise error details.

Run the linter to catch common mistakes:

```bash
uv run ruff check .
```

[Ruff](https://docs.astral.sh/ruff/) analyzes code without running it, checking
for issues such as unused imports, incorrect syntax, and style violations.

Run the formatter to apply consistent formatting:

```bash
uv run ruff format .
```

Both Ruff hooks run automatically on commits after `uv run pre-commit install`.

Run the type checker:

```bash
uv run pyright
```

[Pyright](https://github.com/microsoft/pyright) checks how your code uses
[type hints](https://docs.python.org/3/library/typing.html), helping catch
incorrect argument and return types before runtime.

### 4. Commit and push

Once the automated and applicable manual checks for your task pass,
[commit](https://docs.github.com/en/get-started/using-git/about-commits)
your changes and push to your fork:

```bash
git add . &&
git commit -m "Implement feature X" &&
git push -u origin feature/your-feature-name
```

Use your task's branch name and a commit message describing your change.
Do not commit `.env` or other secrets.

### 5. Create and merge a PR on your fork

Go to `github.com/YOUR_USERNAME/journal-starter` and open a
[pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests)
to merge your feature branch into **your own `main` branch**.

> **Do not target `learntocloud/journal-starter`.** The PR's "base repository"
> must be `YOUR_USERNAME/journal-starter`.

![Core Base Repository Selection](pr_example.png)

Review and merge the PR before starting the next task. Intermediate PRs can
still have CI failures for other unfinished tasks, as explained below; do not
disable tests to get a green check. The current task's acceptance criteria must
be satisfied.

> **Do not modify the supplied test files for the capstone.** Implement each
> task in its listed files. A failure may indicate an implementation issue or
> an environment/setup problem; diagnose it rather than assuming every failure
> is an unfinished feature.

## Continuous Integration

The workflow in [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) runs on
**pushes to `main`** and **pull requests targeting `main`**. Pushing a feature
branch without an open PR does not trigger it.

| Job | What it checks | How to reproduce locally |
|-----|----------------|--------------------------|
| `lint` | Ruff linting, formatting, and Pyright | `uv run ruff check . && uv run ruff format --check . && uv run pyright` |
| `test` | pytest against a dedicated PostgreSQL 15 test database, provisioned by `database_setup_test.sql` using the shared schema | `uv run pytest -v` |

CI and the devcontainer both use PostgreSQL 15. With workflows enabled, your
fork can show two green checks when all Tasks 1-4 are complete and code-quality
checks pass. Intermediate PRs can still have failures for unfinished tasks.

CI receives no learner or provider credentials. It uses a disposable PostgreSQL
service and an injected mock OpenAI client, never a real LLM. Task 4's live
verification runs locally instead.

**Next:** Begin the [development tasks](tasks.md). For setup failures, use
[troubleshooting](troubleshooting.md); for upstream changes, follow
[safe fork synchronization](upstream-sync.md).

# Chapter 4: Learn the Development Workflow

[Home](../README.md) · **Chapter 4 of 11**

Use the same loop for each exercise: create a branch, implement the task, run
its checks, and merge a pull request into your fork.

Run commands from the **project root inside the devcontainer**.

## 1. Create a Branch

Before each task, merge the previous task's pull request and make sure your
working tree is clean:

```bash
git status
git checkout main &&
git pull --ff-only origin main &&
git checkout -b feature/your-feature-name
```

Each task chapter provides a suggested branch name.

## 2. Implement and Check the Task

Each task chapter identifies the files to edit and its acceptance command. Run
that command first, then run the code-quality checks:

```bash
uv run ruff check .
uv run ruff format .
uv run pyright
```

Do not change the supplied tests to make them pass.

To run the same cumulative exercise selection used by CI, substitute a value
from the task-label table:

```bash
uv run python -m scripts.ci_tests --task logging
```

## 3. Commit and Push

```bash
git add .
git commit -m "Describe the completed task"
git push -u origin feature/your-feature-name
```

Do not commit `.env` or other secrets.

## 4. Open and Merge a Pull Request

Open a pull request from your feature branch to **your fork's `main` branch**.
Do not target `learntocloud/journal-starter`.

Add exactly one task label, wait for CI, review the diff, and merge the pull
request before starting the next chapter.

### Task Labels

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
complete.

## 5. Add a Cloud CLI

Use this small configuration change to practice the workflow before the Python
tasks:

1. Create a branch such as `setup/cloud-cli`.
2. Uncomment exactly one cloud CLI feature in
   [`.devcontainer/devcontainer.json`](../.devcontainer/devcontainer.json).
3. Choose **Dev Containers: Rebuild Container** in VS Code.
4. Run `az --version`, `aws --version`, or `gcloud --version` in the rebuilt
   devcontainer.
5. Open a pull request to your fork with the label `task:setup`, then merge it.

No cloud login or deployment is required.

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

If test setup fails, follow
[Database-backed tests fail during setup](reference/troubleshooting.md#database-backed-tests-fail-during-setup).

---

[← Previous: Run the API](03-run-the-api.md) ·
[Next: Build GET for one entry →](05-get-entry.md)

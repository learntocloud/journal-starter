# Chapter 4: Build GET for One Entry

[Home](../README.md) · **Chapter 4 of 10**

Implement **GET `/entries/{entry_id}`** so clients can retrieve one journal
entry.

This is your first implementation exercise. Use the same loop here and in
later exercises: create a branch, implement the task, run its checks, and merge
a pull request into your fork. Each chapter includes the commands and label
you need.

Run commands from the **project root inside the devcontainer**.

## Before You Begin

- Branch: `feature/get-single-entry`
- PR label: `task:get-entry`
- Edit: `api/routers/journal_router.py`

Make sure your setup pull request is merged and `git status` shows a clean
working tree before creating the branch:

```bash
git status
git checkout main &&
git pull --ff-only origin main &&
git checkout -b feature/get-single-entry
```

## Implementation Requirements

Call `entry_service.get_entry(entry_id)`.

- When the service returns an `Entry`, return that model directly.
- When it returns `None`, respond with HTTP 404.
- Do not wrap the entry in another dictionary.

The response model and persistence code are already supplied.

## Run the Checks

Run the task's acceptance tests first, then the code-quality checks:

```bash
uv run pytest tests/test_api.py::TestGetSingleEntry
uv run ruff check .
uv run ruff format .
uv run pyright
```

Do not change the supplied tests to make them pass. Fix the implementation
instead. Ruff formatting may update files; include those changes in your
commit.

CI also runs preceding exercises as you progress. See
[Testing and CI](reference/testing-and-ci.md) for the cumulative local command,
task labels, and test database safety.

## Finish the Chapter

Review `git diff` and `git status` before staging. Do not commit `.env` or other
secrets.

```bash
git add .
git commit -m "Implement GET single entry"
git push -u origin feature/get-single-entry
```

Then:

1. Open a pull request to **your fork's `main` branch**, not
   `learntocloud/journal-starter`.
2. Add exactly one task label: `task:get-entry`. Create the label in your fork
   if it does not exist.
3. Wait for CI, review the diff, and merge the pull request before starting
   the next chapter.

---

[← Previous: Run the API](03-run-the-api.md) ·
[Next: Build DELETE for one entry →](05-delete-entry.md)

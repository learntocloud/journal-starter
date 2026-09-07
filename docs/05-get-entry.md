# Chapter 5: Build GET for One Entry

[Home](../README.md) · **Chapter 5 of 11**

Implement **GET `/entries/{entry_id}`** so clients can retrieve one journal
entry.

## Before You Begin

- Branch: `feature/get-single-entry`
- PR label: `task:get-entry`
- Edit: `api/routers/journal_router.py`

```bash
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

```bash
uv run pytest tests/test_api.py::TestGetSingleEntry
uv run ruff check .
uv run ruff format .
uv run pyright
```

## Finish the Chapter

```bash
git add .
git commit -m "Implement GET single entry"
git push -u origin feature/get-single-entry
```

Then:

1. Open a pull request to your fork's `main`.
2. Add the `task:get-entry` label.
3. Wait for CI, review the diff, and merge the pull request.

---

[← Previous: Development workflow](04-development-workflow.md) ·
[Next: Build DELETE for one entry →](06-delete-entry.md)

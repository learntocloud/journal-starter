# Chapter 6: Build DELETE for One Entry

[Home](../README.md) · **Chapter 6 of 11**

Implement **DELETE `/entries/{entry_id}`** so clients can remove one journal
entry.

## Before You Begin

- Branch: `feature/delete-entry`
- PR label: `task:delete-entry`
- Edit: `api/routers/journal_router.py`

After merging Chapter 5:

```bash
git checkout main &&
git pull --ff-only origin main &&
git checkout -b feature/delete-entry
```

## Implementation Requirements

Call `entry_service.delete_entry(entry_id)` exactly once.

- When it returns `False`, respond with HTTP 404.
- Otherwise, return the existing success detail with HTTP 200.
- Do not fetch the entry before deleting it.

The repository uses an atomic `DELETE ... RETURNING` operation to report
whether the row existed.

## Run the Checks

```bash
uv run pytest tests/test_api.py::TestDeleteEntry
uv run ruff check .
uv run ruff format .
uv run pyright
```

## Finish the Chapter

```bash
git add .
git commit -m "Implement DELETE single entry"
git push -u origin feature/delete-entry
```

Then:

1. Open a pull request to your fork's `main`.
2. Add the `task:delete-entry` label.
3. Wait for CI, review the diff, and merge the pull request.

---

[← Previous: GET one entry](05-get-entry.md) ·
[Next: Add input validation →](07-input-validation.md)

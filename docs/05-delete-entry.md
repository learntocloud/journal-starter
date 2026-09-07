# Chapter 5: Build DELETE for One Entry

[Home](../README.md) · **Chapter 5 of 10**

Implement **DELETE `/entries/{entry_id}`** so clients can remove one journal
entry.

## Before You Begin

- Branch: `feature/delete-entry`
- PR label: `task:delete-entry`
- Edit: `api/routers/journal_router.py`

After merging Chapter 4, confirm your working tree is clean:

```bash
git status
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
2. Add exactly one task label: `task:delete-entry`.
3. Wait for CI, review the diff, and merge the pull request.

---

[← Previous: GET one entry](04-get-entry.md) ·
[Next: Add input validation →](06-input-validation.md)

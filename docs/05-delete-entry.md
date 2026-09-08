# Chapter 5: Build DELETE for One Entry

[Home](../README.md) · **Chapter 5 of 10**

In this chapter, you will implement **DELETE `/entries/{entry_id}`** so a client
can remove one journal entry.

## 1. Prepare Your Branch

1. Make sure your GET pull request is merged, then check your working tree:

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
   git checkout -b feature/delete-entry
   ```

## 2. Implement the Endpoint

1. Open `api/routers/journal_router.py` and find the `delete_entry` function
   below `@router.delete("/entries/{entry_id}")`.

2. Read the TODO instructions. Use `await entry_service.delete_entry(entry_id)`
   exactly once to delete the entry.

   Like the GET service method, this method is asynchronous. Without `await`,
   the call returns a coroutine, not the deletion result. A coroutine is truthy,
   so checking it in an `if` statement would not tell you whether deletion
   succeeded, and the deletion would not run.

   The database deletes the row and reports whether it existed in one operation.
   The service returns `True` when it deleted an entry and `False` when there
   was no matching entry. Do not fetch the entry first: another request could
   delete it between the fetch and your delete call.

3. Replace the placeholder implementation with the required behavior:

   | Service result | What the endpoint should do |
   |----------------|-----------------------------|
   | `True` | Return `DetailResponse` with `"Entry deleted successfully"` and HTTP 200 |
   | `False` | Raise `HTTPException` with HTTP 404 |

4. Save your changes.

## 3. Try It Yourself

1. [Start the API](03-run-the-api.md#3-start-the-api).
2. Open <http://localhost:8000/docs>.
3. Use **POST `/entries`** to create a disposable, made-up entry. Expect **201**
   and copy `entry.id`.
4. Use **DELETE `/entries/{entry_id}`** with that ID. Expect **200** with
   `{"detail": "Entry deleted successfully"}`.
5. Use **GET `/entries/{entry_id}`** with the same ID. Expect **404**.
6. Delete the same ID again. Expect **404**.

Do not use **DELETE `/entries`**: it deletes every entry.

## 4. Run the Checks

1. Run the DELETE endpoint tests:

   ```bash
   uv run pytest tests/test_api.py::TestDeleteEntry
   ```

   All tests in this group should pass.

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

## 5. Review and Submit Your Work

1. Review your changes:

   ```bash
   git diff
   ```

2. Confirm which files changed:

   ```bash
   git status
   ```

3. Stage the router:

   ```bash
   git add api/routers/journal_router.py
   ```

4. Commit your changes:

   ```bash
   git commit -m "Implement DELETE single entry"
   ```

5. Push your branch:

   ```bash
   git push -u origin feature/delete-entry
   ```

6. Open a pull request to your fork's `main` branch with a descriptive title
   and a description of your changes.

   Verify both the **base repository** (`YOUR_USERNAME/journal-starter`) and
   **base branch** (`main`), with `feature/delete-entry` as the compare branch.

7. Add exactly one task label: `task:delete-entry`. Create it if it does not exist.

8. Wait for CI to pass, review the pull request's changes, and merge it.

## Before You Continue

Your DELETE endpoint should remove an existing entry or return HTTP 404, and
your pull request should be merged into your fork.

---

[← Previous: GET one entry](04-get-entry.md) ·
[Next: Add input validation →](06-input-validation.md)

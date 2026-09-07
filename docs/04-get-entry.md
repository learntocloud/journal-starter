# Chapter 4: Build GET for One Entry

[Home](../README.md) · **Chapter 4 of 10**

In this chapter, you will implement **GET `/entries/{entry_id}`** so a client
can retrieve one journal entry by its ID. This is your first Python
implementation exercise.

## 1. Prepare Your Branch

1. Make sure your setup pull request is merged, then check your working tree:

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
   git checkout -b feature/get-single-entry
   ```

## 2. Implement the Endpoint

1. Open `api/routers/journal_router.py` and find the `get_entry` function below
   `@router.get("/entries/{entry_id}")`.

   This function handles requests to that route. The `{entry_id}` part of the
   path becomes the function's `entry_id` argument. The function currently returns
   HTTP 501 because the exercise is not implemented yet.

2. Read the TODO instructions in the function. Use
   `entry_service.get_entry(entry_id)` to retrieve the entry.

   The service handles the operation behind the route, including calling the
   database code. It returns an `Entry` when it finds a match, or `None` when
   there is no matching entry. This is an asynchronous method, so you need to
   `await` its result.

3. Replace the placeholder implementation with the required behavior:

   | Service result | What the endpoint should do |
   |----------------|-----------------------------|
   | An `Entry` | Return that model directly with HTTP 200 |
   | `None` | Raise `HTTPException` with HTTP 404 |

   HTTP 404 means the requested entry was not found. Do not wrap the returned
   entry in another dictionary. The response model and database code are
   already supplied.

4. Save your changes.

## 3. Run the Checks

1. Run the acceptance tests for this endpoint:

   ```bash
   uv run pytest tests/test_api.py::TestGetSingleEntry
   ```

   Acceptance tests describe the behavior your implementation must provide.
   This command selects the `TestGetSingleEntry` group in `tests/test_api.py`.
   All tests in that group should pass. If one fails, read the failure and fix
   your implementation. Do not change the supplied tests to make them pass.

2. Check the code with Ruff:

   ```bash
   uv run ruff check .
   ```

   Resolve any reported issues.

3. Apply Ruff's formatting:

   ```bash
   uv run ruff format .
   ```

   Formatting may update files. Review those changes before committing.

4. Run Pyright:

   ```bash
   uv run pyright
   ```

   Pyright checks that values and function calls match their declared Python
   types. Resolve any errors before continuing.

   CI also runs the starter tests and all exercises up to the task selected by
   your pull request label. Later, unfinished exercises are not included.

## 4. Review and Submit Your Work

1. Review your code changes:

   ```bash
   git diff
   ```

2. Confirm which files changed:

   ```bash
   git status
   ```

   Only stage changes intended for this task.

3. Stage the router:

   ```bash
   git add api/routers/journal_router.py
   ```

4. Commit your changes:

   ```bash
   git commit -m "Implement GET single entry"
   ```

   If the pre-commit hook modifies a file, review and stage the changes, then
   run the commit command again. If it reports an error, fix it before retrying.

5. Push your branch:

   ```bash
   git push -u origin feature/get-single-entry
   ```

6. Open a pull request to your fork's `main` branch. Add a descriptive title
   and explain what you implemented.

7. Add exactly one task label: `task:get-entry`. Create it if it does not exist.

8. Wait for CI to pass, review the pull request's changes, and merge it.

## Before You Continue

Your GET endpoint should return one entry or HTTP 404, and your pull request
should be merged into your fork.

---

[← Previous: Run the API](03-run-the-api.md) ·
[Next: Build DELETE for one entry →](05-delete-entry.md)

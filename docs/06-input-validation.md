# Chapter 6: Add Input Validation

[Home](../README.md) · **Chapter 6 of 10**

In this chapter, you will validate new entries and partial updates before they
reach the service. Then you'll use the debugger to see why updating one field
leaves the other fields unchanged.

## 1. Prepare Your Branch

1. Make sure your DELETE pull request is merged, then check your working tree:

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
   git checkout -b feature/input-validation
   ```

## 2. Validate New Entries

1. Open `api/models/entry.py` and find `EntryCreate`.

   A request model describes the data an endpoint accepts. This project uses
   Pydantic models to check incoming values before the handler calls the service.
   When a request fails validation, FastAPI returns HTTP 422 instead of saving
   the invalid data.

2. Add constraints to the `work`, `struggle`, and `intention` fields so each one
   accepts only strings, removes surrounding whitespace, and contains 1-256
   characters after trimming. Reject empty, whitespace-only, oversized, and
   non-string values.

   `Annotated[str, StringConstraints(...)]` can express these rules.
   `Annotated` lets you attach validation rules to the string type, and
   `StringConstraints` defines rules such as trimming and length limits.

3. Leave the `Entry` read model unchanged. These constraints apply to incoming
   writes, not to the shape of entries returned by the API.

## 3. Validate Partial Updates

1. In `api/models/entry.py`, create an `EntryUpdate` model for the PATCH request
   body.

   PATCH lets a client change selected fields without sending the entire entry.
   For example, sending only `work` should not replace `struggle` or `intention`.
   Your model needs to distinguish a field that was left out from a field
   explicitly set to `null`.

2. Implement the following behavior for all three text fields:

   | PATCH input | Required behavior |
   |-------------|-------------------|
   | Field omitted | Keep the stored value |
   | String supplied | Trim it and require 1-256 characters |
   | `null`, empty, whitespace-only, or non-string supplied | Return HTTP 422 without changing the entry |
   | `{}` supplied | Accept it and keep all three text fields |

   Fields may default to `None` internally to represent omission. A field
   validator must still reject an explicitly supplied `None`. A validator is
   a function Pydantic calls to check a value; use it to handle the explicit
   `null` case without rejecting omitted fields.

3. Open `api/routers/journal_router.py`, import `EntryUpdate`, and use it as the
   type of the `entry_update` argument in the PATCH handler.

4. Update the call to `entry_service.update_entry` so it receives only the fields
   supplied in the request. Use this expression to build the dictionary:

   ```python
   entry_update.model_dump(exclude_unset=True)
   ```

   `model_dump()` converts the model to a dictionary. `exclude_unset=True`
   leaves out fields the client did not send, instead of including their default
   values. Pass that dictionary to the service, not the model itself.

5. Save your changes. Keep the existing API response shape.

## 4. Trace a Partial Update in the Debugger

The debugger pauses running code so you can inspect its values and follow what
happens next. Complete the model and PATCH handler before starting this section.

1. In `api/routers/journal_router.py`, click the gutter (the left margin) beside the PATCH
   handler's call to `entry_service.update_entry` to set a breakpoint.
   A breakpoint marks the line where execution should pause.

2. Open VS Code's **Testing** view and refresh test discovery. Find
   `TestUpdateEntry.test_update_entry_success[work]` in `tests/test_api.py`.
   Select only that case and choose **Debug Test**.

   Use **Debug Test**, not **Run Test** or the FastAPI launch profile. This test
   calls the API directly in the test process, so no running API server is
   needed. It uses made-up entries in the dedicated test database and does not
   call an AI provider. Do not run other database-backed tests while it is paused.

3. When execution pauses, inspect `entry_update` in **Variables**. In the
   **Debug Console**, evaluate:

   ```python
   entry_update.model_fields_set
   ```

   You should see `{'work'}`, the field supplied by the request.

4. Evaluate:

   ```python
   entry_update.model_dump()
   ```

   You should see all three fields, including defaults for the omitted fields.

5. Evaluate:

   ```python
   entry_update.model_dump(exclude_unset=True)
   ```

   You should see `{'work': 'Updated description'}`. Compare this with the
   previous result and decide which dictionary the service should receive.

6. Use **Step Into (F11)** to follow the call into `EntryService.update_entry`.
   Inspect `updated_data`. Use **Step Over (F10)** until `changes` has been
   assigned, then confirm that it contains only `work`.

   Step Into follows a function call into its implementation. Step Over executes
   the next line without following calls into other functions.

7. Use **Continue (F5)** to let the test finish and clean up its test data.
   Confirm that it passes.

8. Write down the values you observed and why updating `work` preserves
   `struggle`, `intention`, the entry ID, and its creation timestamp. Include
   these observations in your pull request description. Use only the made-up
   test values, not settings or credentials.

If tests do not appear or a breakpoint is not reached, use the
[debugger troubleshooting guide](reference/troubleshooting.md#tests-do-not-appear-or-breakpoints-are-not-hit).

## 5. Run the Checks

1. Run the model and endpoint tests for this task:

   ```bash
   uv run pytest \
     tests/test_models.py::TestEntryCreateValidation \
     tests/test_models.py::TestEntryUpdateModel \
     tests/test_api.py::TestCreateEntry \
     tests/test_api.py::TestUpdateEntry
   ```

   This is one command continued across several lines. All selected tests
   should pass.

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

## 6. Review and Submit Your Work

1. Review your changes:

   ```bash
   git diff
   ```

2. Confirm which files changed:

   ```bash
   git status
   ```

3. Stage the model and router:

   ```bash
   git add api/models/entry.py api/routers/journal_router.py
   ```

4. Commit your changes:

   ```bash
   git commit -m "Add entry input validation"
   ```

5. Push your branch:

   ```bash
   git push -u origin feature/input-validation
   ```

6. Open a pull request to your fork's `main` branch. Describe your changes and
   include your debugger observations.

7. Add exactly one task label: `task:validation`. Create it if it does not exist.

8. Wait for CI to pass, review the pull request's changes, and merge it.

## Before You Continue

New entries and partial updates should follow the validation rules, and your
pull request should be merged. You should be able to explain why omitted fields
are preserved during an update.

---

[← Previous: DELETE one entry](05-delete-entry.md) ·
[Next: Use logs to understand the API →](07-logging.md)

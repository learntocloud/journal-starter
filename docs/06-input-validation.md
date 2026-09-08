# Chapter 6: Add Input Validation

[Home](../README.md) · **Chapter 6 of 10**

In this chapter, you will validate new entries and partial updates before they
reach the service. Then you'll use the debugger to see why updating one field
leaves the other fields unchanged.

The starter supplies the partial-update model's omission and null handling,
including its API schema. Your work is to complete the shared string rules
and connect that model to the PATCH handler.

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

1. Open `api/models/entry.py` and find `EntryText` and `EntryCreate`.

   A request model describes the data an endpoint accepts. This project uses
   Pydantic models to check incoming values before the handler calls the service.
   When a request fails validation, FastAPI returns HTTP 422 instead of saving
   the invalid data.

2. Complete the `StringConstraints` in `EntryText` so values have surrounding
   whitespace removed and contain 1-256 characters after trimming. Keep the
   supplied `strict=True` and maximum length. Empty, whitespace-only,
   oversized, and non-string values must be rejected.

   `EntryText` is a shared type used by `work`, `struggle`, and `intention` in
   both request models. `Annotated` attaches validation rules to the string
   type, and `StringConstraints` defines trimming and length limits. Changing
   this one definition applies the same rules to creation and updates.
   `strict=True` prevents conversion from values such as Python bytes.

3. Leave the `Entry` read model unchanged. These constraints apply to incoming
   writes, not to the shape of entries returned by the API.

## 3. Validate Partial Updates

1. In `api/models/entry.py`, read the supplied `EntryUpdate` model for the PATCH
   request body. You do not need to create it or change its default factories
   and validator.

   PATCH lets a client change selected fields without sending the entire entry.
   For example, sending only `work` should not replace `struggle` or `intention`.
   Unlike `EntryCreate`, which requires all three fields, `EntryUpdate` permits
   omission but rejects explicit `null`. Missing and invalid are different:
   invalid input must reject the request, not be silently ignored.

2. With your completed `EntryText` rules, the model must provide this behavior:

   | PATCH input | Required behavior |
   |-------------|-------------------|
   | Field omitted | Keep the stored value |
   | String supplied | Trim it and require 1-256 characters |
   | `null`, empty, whitespace-only, or non-string supplied | Return HTTP 422 without changing the entry |
   | `{}` supplied | Accept it and keep all three text fields |

   The supplied defaults and validator handle omission and explicit null.
   The validator's input-type metadata also keeps the generated API schema
   consistent with the allowed input. You are not expected to implement that
   plumbing; focus on which fields were supplied and whether their text is valid.

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

5. Save your changes. Keep the existing API response shape. Once the handler
   uses `EntryUpdate`, FastAPI validates the request before calling it. Invalid
   input should return HTTP 422 without calling the entry service.

## 4. Trace a Partial Update in the Debugger

The debugger pauses running code so you can inspect its values and follow what
happens next.

1. In `api/routers/journal_router.py`, click the gutter (the left margin) beside the PATCH
   handler's call to `entry_service.update_entry` we just worked with, to set a breakpoint.
   A breakpoint marks the line where execution should pause.

2. Open VS Code's **Testing** view and refresh test discovery. Find
   `TestUpdateEntry.test_update_entry_success[work]` in `tests/test_api.py`.
   Select only that case and click on **Debug Test** icon.

3. When execution pauses, inspect `entry_update` in **Variables**.
4. In the **Debug Console** (You can find this in the terminal area), type in:

   ```python
   entry_update.model_fields_set
   ```

   You should see `{'work'}`, the field supplied by the request.

6. In the same **Debug Console** type in:

   ```python
   entry_update.model_dump()
   ```

   You should see all three fields, including defaults for the omitted fields.

7. Finally:

   ```python
   entry_update.model_dump(exclude_unset=True)
   ```

   You should see `{'work': 'Updated description'}`. Compare this with the previous result: the omitted fields are no longer included. This is why the handler uses exclude_unset=True: it sends only the fields the client supplied, leaving the other stored values unchanged.

8. Use **Step Into (F11)** to follow the call into `EntryService.update_entry`.
9. Once inside the service, inspect `updated_data`. Use **Step Over (F10)** until `changes` has been assigned, then confirm that it contains only `work`.

   Step Into follows a function call into its implementation. Step Over executes
   the next line without following calls into other functions.

10. Use **Continue (F5)** until the test finishes. In the **Testing** you should see all green checkmarks for passing.

11. Write down the values you observed and why updating `work` preserves
   `struggle`, `intention`, the entry ID, and its creation timestamp. Include
   these observations in your pull request description. Use only the made-up
   test values, not settings or credentials.

If tests do not appear or a breakpoint is not reached, use the
[debugger troubleshooting guide](reference/troubleshooting.md#tests-do-not-appear-or-breakpoints-are-not-hit).

## 5. Try It Yourself

1. [Start the API](03-run-the-api.md#3-start-the-api).
2. Open or refresh <http://localhost:8000/docs>.
3. Send **POST `/entries`** with this body:

   ```json
   {
     "work": "   ",
     "struggle": "Understanding partial updates",
     "intention": "Practice input validation"
   }
   ```

   Expect **422** with an error identifying `work`.

4. Change `work` to `"Practiced API requests"` and POST again. Expect **201**
   and copy `entry.id`.
5. Send **PATCH `/entries/{entry_id}`** with that ID and only this body:

   ```json
   {"work": "  Updated description  "}
   ```

   Expect **200** with `work` trimmed to `"Updated description"`.

6. GET the entry. Confirm `struggle`, `intention`, `id`, and `created_at`
   still match the creation response.
7. Try PATCH with `{"work": null}`, then `{"work": "   "}`. Expect **422**
   for each. GET again to confirm nothing changed.
8. Try PATCH with `{}`. Expect **200** with all three text fields unchanged.

## 6. Run the Checks

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

## 7. Review and Submit Your Work

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

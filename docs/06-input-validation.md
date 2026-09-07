# Chapter 6: Add Input Validation

[Home](../README.md) · **Chapter 6 of 10**

Validate new entries and partial updates before they reach the service layer.
Use the debugger to follow a partial update and explain why omitted fields
stay unchanged.

## Before You Begin

- Branch: `feature/input-validation`
- PR label: `task:validation`
- Edit: `api/models/entry.py` and `api/routers/journal_router.py`

Merge the previous exercise's pull request and confirm your working tree is
clean before creating the branch:

```bash
git status
git checkout main &&
git pull --ff-only origin main &&
git checkout -b feature/input-validation
```

## Validate New Entries

Add constraints to the `work`, `struggle`, and `intention` fields in
`EntryCreate` so each one:

- Must be a string
- Has surrounding whitespace removed
- Contains 1-256 characters after trimming
- Rejects empty, whitespace-only, and oversized values

`Annotated[str, StringConstraints(...)]` from Pydantic can express these rules.

## Validate Partial Updates

Create an `EntryUpdate` model and use it as the PATCH request body.

| PATCH input | Required behavior |
|-------------|-------------------|
| Field omitted | Keep the stored value |
| String supplied | Trim it and require 1-256 characters |
| `null`, empty, whitespace-only, or non-string supplied | Return 422 without changing the entry |
| `{}` supplied | Accept it and keep all three text fields |

Fields may default to `None` so omission is represented in the model, but a
validator must reject an explicitly supplied `None`.

Pass only supplied fields to the service:

```python
entry_update.model_dump(exclude_unset=True)
```

Do not apply these write constraints to the `Entry` read model or change the
API response shape.

## Trace a Partial Update in the Debugger

Complete `EntryUpdate` and connect it to the PATCH handler before starting.
Save your changes. VS Code should use the project's `.venv` interpreter, as
configured in [Chapter 3](03-run-the-api.md#1-install-the-project).

1. In `api/routers/journal_router.py`, click the gutter beside the PATCH
   handler's call to `entry_service.update_entry` to set a breakpoint.
2. Open VS Code's **Testing** view and refresh test discovery. Find
   `TestUpdateEntry.test_update_entry_success[work]` in `tests/test_api.py`.
   Select only that case and choose **Debug Test**.
3. When execution pauses in the handler, inspect `entry_update` in **Variables**.
   Evaluate the expressions in the table below in the **Debug Console**.
4. Use **Step Into (F11)** to follow the call into `EntryService.update_entry`.
   Inspect `updated_data`, then use **Step Over (F10)** until `changes` has been
   assigned. Confirm that it contains only `work`.
5. Use **Continue (F5)** to let the test finish and clean up its test data.
   Confirm that it passes.

| Debug Console expression | What to observe |
|--------------------------|-----------------|
| `entry_update.model_fields_set` | `{'work'}`: the field supplied by the request |
| `entry_update.model_dump()` | All three fields, including defaults for omitted fields |
| `entry_update.model_dump(exclude_unset=True)` | `{'work': 'Updated description'}` |

The test sends only `work` and confirms that `struggle`, `intention`, the entry
ID, and its creation timestamp remain unchanged. Compare the two dumps: which
one should the service receive, and why?

Use **Debug Test**, not **Run Test** or the FastAPI launch profile. This test
calls the API in-process, so no running API server is needed. It uses synthetic
entries in the dedicated test database and does not call an AI provider.
Do not run other database-backed tests while this one is paused.

If tests do not appear or a breakpoint is not reached, see
[debugger troubleshooting](reference/troubleshooting.md#tests-do-not-appear-or-breakpoints-are-not-hit).

## Run the Checks

```bash
uv run pytest \
  tests/test_models.py::TestEntryCreateValidation \
  tests/test_models.py::TestEntryUpdateModel \
  tests/test_api.py::TestCreateEntry \
  tests/test_api.py::TestUpdateEntry
uv run ruff check .
uv run ruff format .
uv run pyright
```

## Finish the Chapter

```bash
git add .
git commit -m "Add entry input validation"
git push -u origin feature/input-validation
```

Then:

1. Open a pull request to your fork's `main`.
2. Add exactly one task label: `task:validation`.
3. In the PR description, record the values you inspected in the debugger and
   explain why updating `work` preserves the omitted fields. Use only the
   synthetic test values, not settings or credentials.
4. Wait for CI, review the diff, and merge the pull request.

---

[← Previous: DELETE one entry](05-delete-entry.md) ·
[Next: Use logs to understand the API →](07-logging.md)

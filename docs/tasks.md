# Development Tasks

[README](../README.md) > [Setup](setup.md) > [Workflow](workflow.md) > Tasks

Follow the [per-task workflow](workflow.md#for-each-task) for branches, checks,
and PRs. Run every command from the **project root** in the **VS Code terminal
inside the development container**, not from this `docs/` directory.

Complete every acceptance check listed for a task. Automated tests must pass,
and the manual verification commands for Tasks 4 and 5 must succeed.
Do not change the supplied tests to make them pass.

## Task 1: Logging Setup

- Branch: `feature/logging-setup`
- Edit: `api/main.py`
- Acceptance: `uv run pytest tests/test_logging.py` passes

Configure `logging.basicConfig()` in `api/main.py` so the root logger
ends up at INFO with at least one handler attached. The `journal`
logger used throughout the service layer must continue to propagate.

## Task 2a: GET Single Entry Endpoint

- Branch: `feature/get-single-entry`
- Edit: `api/routers/journal_router.py`
- Acceptance: `uv run pytest tests/test_api.py::TestGetSingleEntry` passes

Implement **GET /entries/{entry_id}** to fetch an entry via
`entry_service.get_entry(entry_id)` and return 404 when not found.

## Task 2b: DELETE Single Entry Endpoint

- Branch: `feature/delete-entry`
- Edit: `api/routers/journal_router.py`
- Acceptance: `uv run pytest tests/test_api.py::TestDeleteEntry` passes

Implement **DELETE /entries/{entry_id}**, returning 404 when the entry
does not exist.

## Task 3: Input Validation

- Branch: `feature/input-validation`
- Edit: `api/models/entry.py`, `api/routers/journal_router.py`
- Acceptance: all three commands below pass

```bash
uv run pytest tests/test_models.py::TestEntryCreateValidation
uv run pytest tests/test_models.py::TestEntryUpdateModel
uv run pytest tests/test_api.py::TestUpdateEntry
```

Add validation to `EntryCreate` so empty, whitespace-only, and
oversize (>256 char) fields are rejected and surrounding whitespace is
stripped. Hint: `Annotated[str, StringConstraints(...)]` from Pydantic.

Then create an `EntryUpdate` model in the same file and wire it into the
PATCH endpoint in `api/routers/journal_router.py`. "Optional" here means a field
may be **omitted**, not that a supplied value may be JSON `null`.

| PATCH input | Required behavior |
|-------------|-------------------|
| A field is omitted | Keep its stored value unchanged |
| A field contains a string | Strip surrounding whitespace, then require 1-256 characters |
| A field is `null`, empty, whitespace-only, or not a string | Return 422; do not modify the stored entry |
| The body is `{}` | Accept it and leave the three text fields unchanged |

Omitted fields should default to `None` inside the model. A field validator can
reject an explicitly supplied `None` without rejecting an omitted field.
Before calling the service, convert the model to a dictionary using
`model_dump(exclude_unset=True)`. The service expects a dictionary, not a Pydantic
model; dumping all fields would overwrite omitted values with defaults.
See FastAPI's [partial-update guide](https://fastapi.tiangolo.com/tutorial/body-updates/#using-pydantics-exclude_unset-parameter).

The pre-built update path sends only changed text fields to PostgreSQL. A single
`UPDATE` merges those fields into the current JSONB document and returns the
stored entry, so concurrent updates to different fields do not overwrite each
other. If two requests change the same field, the last database update wins.
Entry IDs and timestamps remain application-managed.

## Task 4: AI-Powered Entry Analysis

- Branch: `feature/ai-analysis`
- Edit: `api/services/llm_service.py`
- Acceptance: both commands below succeed, including the live provider check

```bash
uv run pytest tests/test_llm_service.py
uv run python -m scripts.verify_llm
```

The **POST /entries/{entry_id}/analyze** endpoint in
`api/routers/journal_router.py` is already wired up: it fetches the entry,
combines the fields into prompt text, calls `analyze_journal_entry()`, and
validates the result against `AnalysisResponse`. Your job is to implement
the LLM call itself in `api/services/llm_service.py`.

Use the [AI analysis guide](ai-analysis.md) for the required response format,
structured-output guidance, provider configuration, and error handling.
Mocked tests do not replace live verification.

## Task 5: Cloud CLI Setup (manual)

- Branch: `feature/cloud-cli-setup`
- Edit: `.devcontainer/devcontainer.json`
- Acceptance: your chosen `az --version`, `aws --version`, or `gcloud --version`
  command runs successfully in the rebuilt devcontainer

Uncomment exactly one of the cloud CLI features in
`.devcontainer/devcontainer.json`, rebuild the devcontainer, and
verify the CLI is installed.

## What the automated tests cover

| Task | Automated? | How the tests verify it |
|------|------------|-------------------------|
| 1 - Logging | Yes | `tests/test_logging.py` inspects the root logger state after importing `api.main` |
| 2a - GET single | Yes | `tests/test_api.py::TestGetSingleEntry` via the FastAPI test client |
| 2b - DELETE single | Yes | `tests/test_api.py::TestDeleteEntry` via the FastAPI test client |
| 3 - Input validation | Yes | `tests/test_models.py` unit tests and `tests/test_api.py::TestUpdateEntry` PATCH validation tests |
| 4 - AI analysis | Yes, plus a required live check | CI injects `MockAsyncOpenAI`; live verification runs locally |
| 5 - Cloud CLI | No | Manual verification in the rebuilt devcontainer |

## Data Schema

Each journal entry follows this structure. Text validation is part of Task 3,
not fully implemented in the starter:

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| id | string | Unique identifier (UUID) | Auto-generated |
| work | string | What did you work on today? | Required, strip whitespace, 1-256 characters |
| struggle | string | What's one thing you struggled with today? | Required, strip whitespace, 1-256 characters |
| intention | string | What will you study/work on tomorrow? | Required, strip whitespace, 1-256 characters |
| created_at | datetime | When entry was created | Auto-generated UTC |
| updated_at | datetime | When entry was last updated | Auto-updated UTC |

For optional database exploration, see [Explore Your Database](explore-database.md).
When a task is complete, [review and merge its PR](workflow.md#5-create-and-merge-a-pr-on-your-fork)
before starting the next one.

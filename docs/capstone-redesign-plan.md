# Capstone Redesign & CI Plan

> **Status:** Approved for implementation. All open questions resolved (see
> [Decisions](#decisions)). Nothing in this document is implemented yet aside
> from a small router stub fix already on `main`. Ships as a single PR with
> the commit structure in [Suggested PR structure](#suggested-pr-structure).

## Why this document exists

GitHub issue [#89](https://github.com/learntocloud/journal-starter/issues/89)
asked for a simple CI workflow. While scoping it, we uncovered a chain of
deeper problems in the capstone:

- Tests were written against a *completed reference implementation*, not
  against the stubs the starter actually ships with.
- One set of tests produced `AttributeError` at collection time on fresh forks
  (bad signal), another produced red → green signals for the wrong reasons
  (accidental signal).
- One of the five capstone tasks had no automated acceptance at all (Task 4:
  "add validators"), and another had a misleading one (Task 3: AI analysis —
  tests mocked away the exact thing the learner was supposed to build).
- Several real bugs in the shipped code that would confuse anyone trying to
  extend the starter (raw `dict` body on PATCH, wrong error codes, vestigial
  `AnalysisResponse` model, etc.).

Rather than patch symptoms, this plan redesigns the capstone tasks, rewrites
the tests to match them, fixes the underlying bugs, and adds CI — all as one
coherent change.

---

## Table of contents

1. [Goals and non-goals](#goals-and-non-goals)
2. [Audit of current state](#audit-of-current-state)
3. [Proposed task list](#proposed-task-list)
4. [Code changes in detail](#code-changes-in-detail)
5. [Test suite redesign](#test-suite-redesign)
6. [CI workflow](#ci-workflow)
7. [README changes](#readme-changes)
8. [Migration impact & rollout](#migration-impact--rollout)
9. [Open questions](#open-questions)
10. [Research references](#research-references)

---

## Decisions

Open questions from the original draft, resolved:

| # | Question | Decision |
|---|---|---|
| Q1 | Ship `EntryCreate` validators as stub or reference? | **Stub.** Task 3 teaches Pydantic v2 validators; shipping the answer defeats the point. |
| Q2 | POST `/entries` return 201 or 200? | **201.** REST-correct. We accept the breaking change to existing forks. |
| Q3 | LLM contract test in `test_service.py` or a new file? | **New file.** `tests/test_llm_service.py` injects a `MockAsyncOpenAI` into `analyze_journal_entry` via an added `client` parameter, following the [Azure-Samples/azure-search-openai-demo](https://github.com/Azure-Samples/azure-search-openai-demo) pattern. No fork secrets, no dedicated CI job, no new deps. |
| Q4 | Add a CI status badge to README? | **Yes.** |
| Q5 | Add a type checker to the lint job? | **Yes, pyright in basic mode.** Not `ty` (still alpha, not in Pylance yet). |
| Q6 | Ship a `pre-commit` config? | **Yes.** Included in this PR. |
| Q7 | Confirm job name `test` for learn-to-cloud-app's status-check hook? | Flagged; will confirm with maintainers before merge. |
| Q8 | Python version floor? | **3.14.** Bump from 3.11 to current stable. Starter repo, no ecosystem lock-in. |
| Q9 | Which LLM providers are supported? | **Any OpenAI-compatible API.** Default to GitHub Models. One SDK, one set of env vars, strict tests. |

**LLM verification approach.** Task 4 is verified by unit tests in
`tests/test_llm_service.py` that inject a `MockAsyncOpenAI` client
into `analyze_journal_entry`. The mock is ~30 lines of handwritten
Python in the test file itself — no new dependencies, no HTTP layer,
no CI secrets, no fork gymnastics. This follows the exact pattern
Microsoft's canonical reference
[Azure-Samples/azure-search-openai-demo](https://github.com/Azure-Samples/azure-search-openai-demo/blob/main/tests/test_mediadescriber.py)
uses to test OpenAI calls in its own test suite, maintained by
Pamela Fox.

The key insight: `analyze_journal_entry` takes an injectable
`client: AsyncOpenAI | None = None` parameter. Production code
(the router) calls it with no argument and gets a real client
built from env vars; tests pass a `MockAsyncOpenAI` that captures
`.create()` kwargs and returns typed `openai.types.ChatCompletion`
objects. The student's code path is identical in both cases —
only the network layer is stubbed. Dependency injection is a real
production pattern, not a test-only trick, so the learner walks
away having used it rather than having tolerated it.

Three assertions catch the three cheating modes we care about:

1. **`create_calls` is non-empty** — catches "return a hardcoded dict
   without calling the LLM at all".
2. **Entry text appears in the messages sent to the mock** — catches
   "call the LLM but with an empty or bogus prompt".
3. **The returned dict validates as `AnalysisResponse`** — catches
   wrong shape / wrong types. The router also declares
   `response_model=AnalysisResponse` as a defense-in-depth boundary
   check (fixes B11/B14).

This is strictly simpler than the fork-secret `verify-llm` job we
originally sketched, and it runs in the same `test` job as everything
else, on both upstream and fork CI. All CI stays hermetic (no API
keys ever, anywhere), forks get the same fast deterministic check,
and there's only one CI job to reason about. One green `test` job =
all five tasks done.

**Provider lockdown (Q9).** Learners pick any **OpenAI-compatible**
provider — GitHub Models (the default, free, no credit card), OpenAI
proper, Azure OpenAI, Groq, Together, OpenRouter, Fireworks, DeepInfra,
Ollama, LM Studio, vLLM, or any other OpenAI-compat endpoint. They all
speak the same protocol, so the starter mandates:

- **One SDK:** the `openai` Python package (added to `[project].dependencies`).
- **Three env vars:** `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`.
- **One `.env` file to document.** No CI secrets needed — tests use
  an injected mock client.
- **One code path** through `analyze_journal_entry` — deterministic
  client construction (or test-injected mock), not a switch statement
  over SDKs.

This is strict enough that tests can be specific (provider-agnostic
`AnalysisResponse` shape validation — no "match any of these five
  possible response keys" slop) but still lets the learner swap
providers with a one-line `.env` change. If "pick your own" were
truly open, the verify script would need a SDK switch and the tests
would have to be loose enough to accept anything vaguely JSON-shaped,
which defeats the point of having a Task 4 check at all.

**Python 3.14 (Q8).** The current shipped `pyproject.toml` floors at
Python 3.11, ruff targets `py311`, and `ty` is pinned to `3.11`. Bump
all of them to **3.14** in this PR. 3.14 is the current stable (released
October 2025), the starter has no downstream consumers that would break,
and learners get modern syntax (PEP 695 type params, PEP 750 t-strings,
free-threaded mode where supported) for free. CI runs
`uv python install 3.14`. Devcontainer base image gets bumped in the
same commit.

---

## Goals and non-goals

### Goals

1. **Every capstone task has an automated acceptance check.** No "look at it"
   gates. Tests, ruff, or a documented script run in CI.
2. **Every check starts red on a fresh fork and goes green when the task is
   done.** Including Task 4, via unit tests that inject a mock OpenAI
   client — no fork secrets, no special setup.
3. **All CI is hermetic** — no API keys required anywhere, upstream or
   fork. LLM tests use an injected mock client, following the
   [Azure-Samples/azure-search-openai-demo](https://github.com/Azure-Samples/azure-search-openai-demo)
   pattern.
4. **The shipped code follows current FastAPI / Pydantic v2 idioms.** No raw
   `dict` bodies, no vestigial models, no mismatched error codes.
5. **Fork CI is deterministic and fast** — if your fork is green, every
   task is done. No network flakiness, no rate-limit failures, no
   "model X got deprecated" surprise breakage.
6. **The task curve ramps.** Easy configuration → familiar endpoint → mirrored
   endpoint → validation → LLM → deployment. Each builds on the previous.

### Non-goals

- Rewriting the database layer (JSONB vs relational columns). The current
  design is idiomatic enough and changing it is out of scope.
- Adding a proper migration tool (Alembic). `database_setup.sql` plus `psql`
  is fine for a starter repo.
- Supporting non-OpenAI-compatible LLM providers (Anthropic's native SDK,
  Google Gemini's native SDK, etc.). Learners wanting those can still use
  them via their OpenAI-compat shims — see [Q9 decision](#decisions).
- Anything in Phase 4 cloud deployment. That's the next phase's job.

---

## Audit of current state

### Bugs and defects found (B1–B16)

| # | File / location | Problem | Severity |
|---|---|---|---|
| B1 | [tests/test_api.py](../tests/test_api.py) | `@patch("api.routers.journal_router.analyze_journal_entry")` targets an attribute that didn't exist on a fresh fork (no import), causing `AttributeError` at test collection. | **Fixed** in current `main` (import added to router). |
| B2 | [tests/test_api.py](../tests/test_api.py) | `test_analyze_entry_not_found` asserted 404 against a router that returned 501 — so it was red for the wrong reason on fresh forks. | **Fixed** in current `main` (router now does the 404 check). |
| B3 | [api/services/entry_service.py](../api/services/entry_service.py), [api/repositories/postgres_repository.py](../api/repositories/postgres_repository.py) | `update_entry` computes `updated_at` in *both* the service and the repo; the repo silently overwrites the service's value. Duplicated responsibility. | Low — same wallclock value, no visible symptom. |
| B4 | [api/routers/journal_router.py](../api/routers/journal_router.py) | `create_entry` wraps everything in `try/except Exception` and returns **400** for any failure. A DB outage returns 400. Should be 500; client-data errors are already 422 via FastAPI. | Medium — wrong HTTP semantics. |
| B5 | [api/routers/journal_router.py](../api/routers/journal_router.py) | `update_entry` takes `entry_update: dict` as the body — no Pydantic model, so `max_length=256` is silently bypassed on PATCH. | **High** — a stated constraint is not enforced. |
| B6 | [api/models/entry.py](../api/models/entry.py) | `Entry.created_at` / `updated_at` typed as `datetime \| None` but always have default factories. Stale `\| None`. | Low — type noise. |
| B7 | [api/models/entry.py](../api/models/entry.py) | Task 4 TODO comments ("add validators", "schema versioning", "sanitization") live on `Entry`, not `EntryCreate`, and aren't covered by any test. Vague task. | Medium — task has no acceptance. |
| B8 | [tests/conftest.py](../tests/conftest.py) | Autouse `cleanup_database` fixture runs against real Postgres for **every** test, including pure-Pydantic tests in `test_models.py`. Forces a DB for tests that shouldn't need one. | Medium — blocks hermetic unit tests. |
| B9 | [api/repositories/postgres_repository.py](../api/repositories/postgres_repository.py) | Module-level `raise ValueError` if `DATABASE_URL` missing — fires at import time. Combined with B8, nothing can be tested without Postgres. | Medium. |
| B10 | [tests/test_models.py](../tests/test_models.py) | `test_entry_create_empty_strings_allowed` locks in that empty-string entries are valid. Probably a bug (journal entries should have content). | Medium — documents a bug as a feature. |
| B11 | [api/models/entry.py](../api/models/entry.py), router | `AnalysisResponse` model is defined but **never used** by the analyze endpoint. The router returns the raw LLM dict without validation. | Medium — vestigial code, loss of type safety. |
| B12 | [api/services/entry_service.py](../api/services/entry_service.py) | `update_entry` merges dicts with `{**existing, **update, "id": ..., "updated_at": ...}`. Correct in practice but fragile — a client-supplied `created_at` in the update would slip through if the merge order ever changed. | Low. |
| B13 | [api/models/entry.py](../api/models/entry.py) | `id` is plain `str` with no UUID validation. `"not-a-real-uuid"` is accepted. | Low — consistent with the JSONB id storage. |
| B14 | [api/routers/journal_router.py](../api/routers/journal_router.py) | Analyze endpoint returns whatever dict the LLM call produces. If the learner's implementation returns `{"topics": "FastAPI"}` (string not list), the client sees garbage. | Medium — linked to B11. |
| B15 | [api/main.py](../api/main.py) | `load_dotenv(override=True)` is carefully placed *before* the `journal_router` import because downstream imports read `os.getenv("DATABASE_URL")` at import time. No comment explains why. Any learner reformatting imports breaks startup. | Medium — invisible landmine. |
| B16 | [api/main.py](../api/main.py) | Logging setup (Task 1) has no automated acceptance. Learner's only feedback is "did logs appear?". | Medium — Task 1 has no test. |

### What's already good

- [api/repositories/interface_repository.py](../api/repositories/interface_repository.py) is a clean ABC, correctly implemented.
- `EntryService` is a clean service layer with thoughtful logging.
- `PostgresDB` uses an async connection pool and handles JSON symmetrically.
- `test_models.py` is structurally a solid pure-unit test file (once B8 is fixed).
- `test_service.py` is a reasonable service-layer integration test.
- Separation between `EntryCreate` (input) and `Entry` (internal) is correct.

---

## Proposed task list

The redesign goes from 5 tasks to **5 tasks** (same count, different scope).
Logging gets a real test. "Data model improvements" becomes a concrete
validation task. AI analysis drops the router half (already done) and keeps
the LLM half. Cloud CLI stays unchanged.

### Task 1 — Logging setup

- **Branch:** `feature/logging-setup`
- **File:** [api/main.py](../api/main.py)
- **Change:** Configure a root logger at `INFO`, attach a console handler with
  a reasonable format, log "Journal API starting up" on import.
- **Acceptance (automated):** New `tests/test_logging.py` with three tests:
  - `test_root_logger_has_info_level` — asserts `logging.getLogger().level <= logging.INFO`.
  - `test_root_logger_has_handler` — asserts at least one `StreamHandler` is attached.
  - `test_journal_logger_propagates` — asserts the `journal` named logger (used by `EntryService`) is configured to propagate to root.
- **Red on fresh fork:** Yes — no `basicConfig` call means the root logger has
  `WARNING` level and no handler.
- **DB required:** No (new file marked `pytest.mark.no_db`).

### Task 2a — GET single entry

- **Branch:** `feature/get-single-entry`
- **File:** [api/routers/journal_router.py](../api/routers/journal_router.py)
- **Change:** Replace the 501 stub with a real implementation: fetch via
  `entry_service.get_entry(entry_id)`, 404 if `None`, return the entry.
- **Acceptance:** Existing `TestGetSingleEntry` tests. No changes needed.
- **Red on fresh fork:** Yes (`assert 501 == 200`, `assert 501 == 404`).
- **DB required:** Yes.

### Task 2b — DELETE single entry

- **Branch:** `feature/delete-entry`
- **File:** [api/routers/journal_router.py](../api/routers/journal_router.py)
- **Change:** Replace the 501 stub with: check existence via `get_entry`, 404
  if `None`, call `delete_entry`, return `{"detail": "Entry deleted successfully"}`.
- **Acceptance:** Existing `TestDeleteEntry` tests. No changes needed.
- **Red on fresh fork:** Yes.
- **DB required:** Yes.

### Task 3 — Input validation

*(Was Task 4, promoted from "vague" to "concrete".)*

- **Branch:** `feature/input-validation`
- **Files:** [api/models/entry.py](../api/models/entry.py), [api/routers/journal_router.py](../api/routers/journal_router.py)
- **Changes the learner makes:**
  1. Add `min_length=1` and `strip_whitespace` to the three string fields on
     `EntryCreate` (via `Field` or `StringConstraints`).
  2. Add a model-level `str_strip_whitespace=True` `ConfigDict` to `EntryCreate`.
  3. Create a new `EntryUpdate` model with `work`, `struggle`, `intention` all
     optional with the same constraints.
  4. Wire `EntryUpdate` into the PATCH router (replacing `entry_update: dict`).
- **Acceptance (automated):** New and modified tests:
  - `test_models.py::TestEntryCreateValidation::test_empty_string_rejected` (new).
  - `test_models.py::TestEntryCreateValidation::test_whitespace_only_rejected` (new).
  - `test_models.py::TestEntryCreateValidation::test_whitespace_stripped` (new).
  - `test_models.py::test_entry_create_empty_strings_allowed` **deleted** (B10).
  - `test_api.py::TestUpdateEntry::test_update_rejects_oversize_field` (new — B5).
  - `test_api.py::TestUpdateEntry::test_update_rejects_empty_string` (new).
- **Red on fresh fork:** Yes.
- **DB required:** Mixed — model tests are `no_db`, PATCH validation test needs DB.

### Task 4 — AI-powered entry analysis

- **Branch:** `feature/ai-analysis`
- **Files:** [api/services/llm_service.py](../api/services/llm_service.py) *only* — the router is already wired.
- **Changes the learner makes:**
  1. Implement `analyze_journal_entry(entry_id, entry_text, client=None)`
     using the `openai` Python SDK (or any **OpenAI-compatible** provider —
     see [Q9 decision](#decisions)). Return a dict matching
     `AnalysisResponse`. The shipped stub already includes the `client`
     parameter and the lazy default construction; the learner only fills
     in the prompt, the `chat.completions.create()` call, and the JSON
     parsing.
  2. Add `OPENAI_API_KEY` (and optionally `OPENAI_BASE_URL` /
     `OPENAI_MODEL`) to their local `.env`. **No GitHub secrets required.**
- **Acceptance (CI, runs everywhere):**
  - New `tests/test_llm_service.py` injects a `MockAsyncOpenAI` client
    into `analyze_journal_entry` and runs three deterministic
    assertions:
    1. `mock.create_calls` is non-empty — student's code actually
       called `client.chat.completions.create(...)`, not returned a
       hardcoded dict.
    2. The entry text appears somewhere in the `messages` kwarg of the
       captured call — student actually passed the entry to the LLM.
    3. The returned dict validates as `AnalysisResponse` — student
       returned the right shape.
  - These tests run in the regular `test` job, on both upstream and
    fork CI. No secrets, no network, no flakiness, no rate limits.
  - **New:** Router declares `response_model=AnalysisResponse` on the
    analyze endpoint (fixes B11, B14). Malformed dicts from the
    learner's implementation become FastAPI 500 responses with a
    Pydantic error detail — defense-in-depth on top of the unit tests.
- **Acceptance (regression guard, always-on):**
  - Existing `test_api.py::TestAnalyzeEntry` tests stay. They mock the
    LLM at the router layer and verify the router plumbing (fetch, 404,
    error mapping). On a fresh fork these **pass** (thanks to the
    router fix already on `main`). They're a regression guard against
    future router changes, not a capstone gate.
- **Red on fresh fork:** Yes — `tests/test_llm_service.py` fails on
  all three assertions because `analyze_journal_entry` raises
  `NotImplementedError` before it ever touches the mock.
- **DB required:** No. `tests/test_llm_service.py` is marked
  `pytestmark = pytest.mark.no_db` and doesn't need Postgres, though
  it runs in the regular `test` job alongside the DB-backed tests.

> **Design note.** We explored four rejected alternatives before
> landing here: (a) fork-only `verify-llm` CI job with real API calls
> (flaky, rate-limited, pays for student mistakes, non-deterministic,
> model deprecations break builds); (b) VCR cassettes (chicken-and-egg
> on fresh forks — no cassettes to start with); (c) [`respx`](https://lundberg.github.io/respx/)
> mocking at the httpx transport layer (extra dependency, couples
> tests to internal SDK URL patterns, returns raw JSON the SDK has to
> re-parse); (d) [`openai-responses-python`](https://github.com/mharrisb1/openai-responses-python)
> pytest plugin (too magic, not transferable knowledge). The pattern
> we landed on — injecting a handwritten `MockAsyncOpenAI` via a
> default parameter — is what Microsoft's own
> [azure-search-openai-demo](https://github.com/Azure-Samples/azure-search-openai-demo)
> does in `tests/test_mediadescriber.py`. Strictly simpler than any
> alternative: zero new dependencies, ~30 lines of mock in the test
> file, fast, deterministic, and the resulting student code uses
> dependency injection — a real production pattern.

### Task 5 — Cloud CLI setup

- **Branch:** `feature/cloud-cli-setup`
- **File:** `.devcontainer/devcontainer.json`
- **Change:** Uncomment one cloud CLI feature.
- **Acceptance:** Unchanged — devcontainer rebuild + `az --version` /
  `aws --version` / `gcloud --version`. Not testable in Python.
- **Red on fresh fork:** N/A (not tested).

---

## Code changes in detail

### 1. [api/models/entry.py](../api/models/entry.py)

**Remove** the stale `# TODO` comments on the `Entry` class and the `| None`
on `created_at` / `updated_at` (B6, B7).

**Replace** `EntryCreate` with a validated version using Pydantic v2
`StringConstraints`:

```python
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

# Constraint applied to every journal text field.
JournalText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=256,
    ),
]


class EntryCreate(BaseModel):
    """Model for creating a new journal entry (user input)."""
    model_config = ConfigDict(str_strip_whitespace=True)

    work: JournalText = Field(
        description="What did you work on today?",
        json_schema_extra={"example": "Studied FastAPI and built my first API endpoints"},
    )
    struggle: JournalText = Field(
        description="What's one thing you struggled with today?",
        json_schema_extra={"example": "Understanding async/await syntax and when to use it"},
    )
    intention: JournalText = Field(
        description="What will you study/work on tomorrow?",
        json_schema_extra={"example": "Practice PostgreSQL queries and database design"},
    )


class EntryUpdate(BaseModel):
    """Model for PATCH updates. All fields optional; same constraints as create."""
    model_config = ConfigDict(str_strip_whitespace=True)

    work: JournalText | None = None
    struggle: JournalText | None = None
    intention: JournalText | None = None
```

**Fix** the `Entry` model (drop stale TODOs, drop `| None` on timestamps):

```python
class Entry(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for the entry (UUID).",
    )
    work: JournalText = Field(description="What did you work on today?")
    struggle: JournalText = Field(description="What you struggled with today.")
    intention: JournalText = Field(description="What you'll work on tomorrow.")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when the entry was created.",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when the entry was last updated.",
    )
```

> **Note:** Per decision Q1, Task 3 ships as a stub. `EntryCreate` in the
> committed code keeps plain `str` fields (no `StringConstraints`), and the
> file carries a clear TODO pointing the learner at `Annotated`,
> `StringConstraints`, and the failing tests. `EntryUpdate` also ships as a
> TODO — the learner creates the model from scratch. The code block above is
> the **reference implementation** used to verify the tests once the task
> is complete; it is not what gets merged to `main`.

### 2. [api/routers/journal_router.py](../api/routers/journal_router.py)

**Fix** `create_entry` error handling (B4). Let FastAPI's validation handle
422s; only catch exceptions we can meaningfully translate:

```python
@router.post("/entries", status_code=201)
async def create_entry(
    entry_data: EntryCreate,
    entry_service: EntryService = Depends(get_entry_service),
):
    """Create a new journal entry."""
    entry = Entry(**entry_data.model_dump())
    created = await entry_service.create_entry(entry.model_dump())
    return {"detail": "Entry created successfully", "entry": created}
```

> FastAPI's default error handling turns unhandled exceptions into 500s. We
> drop the `try/except Exception` → 400 wrapper entirely. Note the
> `status_code=201` — per decision Q2, successful POSTs now return 201
> Created. See [Migration impact](#migration-impact--rollout) for the
> breaking-change implications.

**Fix** `update_entry` to use `EntryUpdate` (B5). This is part of Task 3 — it
ships as a stub that the learner completes. Reference implementation for the
test harness:

```python
@router.patch("/entries/{entry_id}")
async def update_entry(
    entry_id: str,
    entry_update: EntryUpdate,
    entry_service: EntryService = Depends(get_entry_service),
):
    """Update a journal entry."""
    update_data = entry_update.model_dump(exclude_unset=True)
    result = await entry_service.update_entry(entry_id, update_data)
    if result is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return result
```

**Fix** `analyze_entry` to validate output through `AnalysisResponse` (B11, B14):

```python
from api.models.entry import AnalysisResponse  # add to imports

@router.post("/entries/{entry_id}/analyze", response_model=AnalysisResponse)
async def analyze_entry(
    entry_id: str,
    entry_service: EntryService = Depends(get_entry_service),
):
    entry = await entry_service.get_entry(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")

    entry_text = f"{entry['work']} {entry['struggle']} {entry['intention']}"

    try:
        raw = await analyze_journal_entry(entry_id, entry_text)
    except NotImplementedError as e:
        raise HTTPException(
            status_code=501,
            detail="LLM analysis not yet implemented - see api/services/llm_service.py",
        ) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e!s}") from e

    # FastAPI validates the return through AnalysisResponse; malformed dicts
    # will raise and become 500 with a clear Pydantic error in the detail.
    return raw
```

### 3. [api/services/entry_service.py](../api/services/entry_service.py)

**Remove** the `updated_at = datetime.now(UTC)` line from the repo's
`update_entry` (B3); let the service layer own the timestamp. One-line change.

### 4. [api/main.py](../api/main.py)

Add the logging configuration (reference implementation; shipped as a stub):

```python
import logging

from dotenv import load_dotenv

# Load .env BEFORE importing anything that reads env vars at import time
# (e.g. api.repositories.postgres_repository reads DATABASE_URL).
load_dotenv(override=True)

# TODO (Task 1): Configure logging here.
# Reference: https://docs.python.org/3/howto/logging.html
# Steps:
#   1. Call logging.basicConfig(level=logging.INFO, format="...")
#   2. Log an INFO message on startup (e.g. "Journal API starting up")

from fastapi import FastAPI  # noqa: E402  (must come after load_dotenv)

from api.routers.journal_router import router as journal_router  # noqa: E402

app = FastAPI(
    title="Journal API",
    description="A simple journal API for tracking daily work, struggles, and intentions",
)
app.include_router(journal_router)
```

Adds the explanatory comment that was missing (fixes B15).

### 5. [api/repositories/postgres_repository.py](../api/repositories/postgres_repository.py)

Remove the `updated_at` override in `update_entry` (B3):

```python
async def update_entry(self, entry_id: str, updated_data: dict[str, Any]) -> None:
    """Persist an updated entry. The service layer owns the updated_at stamp."""
    updated_at = updated_data["updated_at"]
    data_json = json.dumps(updated_data, default=PostgresDB.datetime_serialize)

    async with self.pool.acquire() as conn:
        query = """
        UPDATE entries
        SET data = $2, updated_at = $3
        WHERE id = $1
        """
        await conn.execute(query, entry_id, data_json, updated_at)
```

### 6. `scripts/verify_llm.py` (new, optional local sanity check)

**Not a CI gate.** CI handles Task 4 via `tests/test_llm_service.py`
with an injected mock client. This script is an **optional** local
helper for eyeballing what the real model produces against the
student's implementation — a "does it actually say something
sensible" smoke test. Nothing in CI runs it; nothing in the capstone
grade depends on it.

```python
"""Optional: run your Task 4 implementation against a real LLM.

NOT a CI gate and NOT required to pass the capstone — CI validates
Task 4 with a mock client in tests/test_llm_service.py. Use this
script locally when you want to see what the real model produces,
not only the deterministic unit-test signal.

Usage:
    uv run python -m scripts.verify_llm

Requires OPENAI_API_KEY in your .env file. Respects OPENAI_BASE_URL
and OPENAI_MODEL if set.
"""
import asyncio
import os
import sys

from dotenv import load_dotenv
from pydantic import ValidationError

from api.models.entry import AnalysisResponse
from api.services.llm_service import analyze_journal_entry

load_dotenv()

SAMPLE_TEXT = (
    "Studied FastAPI and built my first API endpoints. "
    "I struggled with understanding async/await syntax. "
    "Tomorrow I'll practice PostgreSQL queries and database design."
)


async def main() -> int:
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not set in .env — cannot run live verification.")
        print("(This is a local helper, not a CI gate. The capstone tests")
        print(" in tests/test_llm_service.py run fine without this.)")
        return 1

    print("Calling analyze_journal_entry against the real LLM...")
    try:
        raw = await analyze_journal_entry("verify-llm-sample", SAMPLE_TEXT)
    except NotImplementedError:
        print("analyze_journal_entry raises NotImplementedError — Task 4 not done yet.")
        return 1

    print(f"Raw return value: {raw!r}")

    try:
        validated = AnalysisResponse.model_validate(raw)
    except ValidationError as e:
        print("Response does not match AnalysisResponse schema:")
        print(e)
        return 1

    print("OK — response validates.")
    print(f"  entry_id:  {validated.entry_id}")
    print(f"  sentiment: {validated.sentiment}")
    print(f"  summary:   {validated.summary}")
    print(f"  topics:    {validated.topics}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
```

### 7. `.pre-commit-config.yaml` (new, per decision Q6)

Pre-commit hooks give learners fast local feedback before pushing, and
reduce CI noise from trivial lint/format errors.

```yaml
# Run `uv run pre-commit install` once after cloning your fork.
# See https://pre-commit.com for details.
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

Also: add `pre-commit` to the `[project.optional-dependencies].dev` group in
[pyproject.toml](../pyproject.toml) so `uv sync --all-extras` picks it up.
Update the README "First-Time Setup" section with a one-liner about running
`uv run pre-commit install` after cloning.

### 8. [pyproject.toml](../pyproject.toml) (Python 3.14 + openai SDK)

Per decisions Q8, Q9, and Q5 (revisited), bump Python, add the mandated
LLM SDK, switch the type checker, and tighten the ruff config:

```toml
[project]
name = "journal-api"
version = "0.1.0"
description = "Journal API"
requires-python = ">=3.14"
dependencies = [
    "fastapi",
    "uvicorn",
    "python-dotenv",
    "asyncpg",
    "openai",           # Q9: mandated OpenAI-compatible SDK
]

[project.optional-dependencies]
dev = [
    "pytest>=9.0.2",
    "pytest-asyncio",
    "httpx",
    "ruff",
    "pyright",          # Q5 (revisited): type checker; basic mode, runs in CI
    "pre-commit",       # Q6: local hooks
]

[tool.ruff]
line-length = 100
target-version = "py314"    # was py311

[tool.ruff.lint]
# Rule set is curated for teaching — each family earns its keep by
# catching real bugs and/or nudging learners toward idiomatic Python.
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "I",      # isort
    "N",      # pep8-naming              (snake_case, CamelCase, etc.)
    "UP",     # pyupgrade                (modern syntax)
    "B",      # flake8-bugbear           (likely bugs)
    "C4",     # flake8-comprehensions    (idiomatic comprehensions)
    "DTZ",    # flake8-datetimez         (no naive datetimes)
    "SIM",    # flake8-simplify
    "RET",    # flake8-return            (cleaner return flow)
    "PT",     # flake8-pytest-style      (pytest best practices)
    "S",      # flake8-bandit            (security; DB + LLM app)
    "T20",    # flake8-print             (no print(); see Task 1 logging)
    "ASYNC",  # flake8-async             (codebase is fully async)
    "RUF",    # ruff-specific            (cleanups, ambiguous unicode)
]
ignore = [
    # Keep E501 disabled: `ruff format` owns line length, and the
    # formatter intentionally leaves some lines long (string literals,
    # URLs in comments). This is the ruff-recommended pattern when
    # you use the formatter. NO other rules are blanket-ignored.
    "E501",
]

[tool.ruff.lint.flake8-bugbear]
# B008 (function-call-in-default-argument) flags mutable default
# arguments — real bug category. FastAPI's Depends / Query / Path /
# Body / Header / Cookie / File / Form / Security are effectively
# sentinels, not mutable state, so whitelist *just them* instead of
# blanket-ignoring B008. A naked `def foo(x=list())` still gets caught.
extend-immutable-calls = [
    "fastapi.Depends",
    "fastapi.Query",
    "fastapi.Path",
    "fastapi.Body",
    "fastapi.Header",
    "fastapi.Cookie",
    "fastapi.File",
    "fastapi.Form",
    "fastapi.Security",
]

[tool.ruff.lint.per-file-ignores]
# pytest relies on assert statements; S101 would fire on every test.
"tests/**/*.py" = ["S101"]
# CLI scripts print by design (it's the whole point of verify_llm.py).
"scripts/**/*.py" = ["T201"]

[tool.ruff.lint.isort]
known-first-party = ["api"]

[tool.pyright]
# Basic mode is the pedagogical sweet spot: catches real errors
# (unresolved names, wrong arg types on annotated functions, Pydantic
# model misuse) without drowning untyped code in warnings. Learners
# can tighten to "standard" or "strict" after they land the capstone.
typeCheckingMode = "basic"
pythonVersion = "3.14"
include = ["api", "scripts", "tests"]
venvPath = "."
venv = ".venv"
```

### Why `pyright` instead of the `ty` that was in the previous config

`ty` (Astral's type checker) is still pre-1.0 and ships with known false
positives on FastAPI's decorator patterns. More importantly, it doesn't
yet power Pylance in VS Code, so learners wouldn't see its errors in
their editor in real time. `pyright` does:

- **Already running in every learner's VS Code.** Pylance is built on
  pyright, so configuring pyright via `[tool.pyright]` also configures
  the in-editor experience. Type errors surface *as they type*, not
  when they push to CI.
- **Stable.** No breaking changes between minor versions. Safe to ship
  to learners.
- **Fast.** Lint job adds ~3–5 seconds of wall time.
- **"Basic" mode is the right default** for a starter — it only flags
  code that's clearly broken, not code that's merely unannotated. As
  the codebase grows and learners add type hints, they get richer
  feedback automatically.

Once `ty` hits 1.0 and lands in Pylance, we should revisit. For now,
pyright is the pragmatic choice. `ty` is **removed** from dev extras.

### Ruff rule-set rationale

| Rule family | Why it's here |
|---|---|
| `E`, `W`, `F`, `I`, `UP` | Baseline Python hygiene; already in place. |
| `N` | Teaches PEP 8 naming conventions. Pedagogical. |
| `B` + `extend-immutable-calls` | Catches real bugs (mutable defaults, unused loop vars) **without** the FastAPI false positives. |
| `C4` | `list(x)` over `[x for x in x]`; teaches idiomatic constructs. |
| `DTZ` | No naive datetimes. Codebase already uses `datetime.now(UTC)` so this is cheap to turn on, and it teaches a real bug category. |
| `SIM` | Simplification rules; already in place. |
| `RET` | Cleaner return flow. Low noise, real teaching value. |
| `PT` | Pytest-specific best practices (fixture naming, `pytest.raises` usage). Directly relevant to the tests learners write. |
| `S` | Security rules. For a DB-backed API that talks to an LLM, this catches SQL injection patterns, hardcoded secrets, unsafe YAML loading, etc. |
| `T20` | **Crucial pedagogical link:** bans `print()` statements. Task 1 is "configure logging" — if `print()` is allowed, learners `print()` instead of using the logger and miss the point of Task 1 entirely. |
| `ASYNC` | Catches blocking calls inside async functions (e.g. `time.sleep` instead of `asyncio.sleep`, `requests.get` instead of `httpx.AsyncClient`). Codebase is fully async; this is a real bug class. |
| `RUF` | Ruff's own cleanup rules, including ambiguous unicode detection. Free wins. |

**Rules deliberately *not* enabled** (with reasons, so we don't re-litigate):

- `PL*` (pylint): too many opinionated rules, high noise-to-signal ratio
  for a learner repo.
- `ANN` (missing annotations): would fail loudly on every unstubbed
  function, drowning out the actual task failures.
- `D` (pydocstyle): docstring style is not a capstone goal, and forcing
  it creates busywork.
- `ERA` (eradicate): flags commented-out code, which conflicts with
  learner TODO comments.
- `PTH` (use pathlib): negligible value for a web API.
- `TCH` (type-checking imports): an advanced refactoring rule, too
  sophisticated for Python learners.

**Dropped dependencies** (cleanup alongside the bump):

- `aiohttp` — unused anywhere in the codebase.
- `sqlalchemy`, `psycopg2-binary` — vestigial; the project uses `asyncpg`
  directly.
- `pytest` from `[project].dependencies` — it's already in dev extras and
  doesn't belong as a runtime dep.
- `ty` — replaced by `pyright` per the Q5 revisit above.

**Devcontainer bump.** `.devcontainer/devcontainer.json` is updated in the
same commit to use a Python 3.14 base image (`mcr.microsoft.com/devcontainers/python:1-3.14-bookworm`
or equivalent). Learners who rebuild the container get 3.14 automatically.

**`api/services/llm_service.py` stub template.** The shipped stub shows
learners the OpenAI-compat client construction **and the injectable
`client` parameter**, so they know which SDK to use without needing to
dig through docs, and so the unit tests in `tests/test_llm_service.py`
can pass in a `MockAsyncOpenAI`:

```python
"""Task 4: Implement analyze_journal_entry using any OpenAI-compatible API.

This project mandates the OpenAI Python SDK, which works with:
  - GitHub Models (default, free, no credit card required)
  - OpenAI proper
  - Azure OpenAI
  - Groq, Together, OpenRouter, Fireworks, DeepInfra
  - Ollama, LM Studio, vLLM (local)
  - Anthropic via their OpenAI-compat endpoint

Set OPENAI_API_KEY, and optionally OPENAI_BASE_URL and OPENAI_MODEL
in your .env file.
"""
import os

from openai import AsyncOpenAI


def _default_client() -> AsyncOpenAI:
    """Construct the real OpenAI client from environment variables.

    Called lazily from analyze_journal_entry so tests can inject a
    MockAsyncOpenAI without ever triggering this code path.
    """
    return AsyncOpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.getenv("OPENAI_BASE_URL", "https://models.inference.ai.azure.com"),
    )


async def analyze_journal_entry(
    entry_id: str,
    entry_text: str,
    client: AsyncOpenAI | None = None,
) -> dict:
    """Analyze a journal entry using an OpenAI-compatible LLM.

    Args:
        entry_id: ID of the entry being analyzed (pass through to the result).
        entry_text: Combined work + struggle + intention text.
        client: OpenAI client. If None, a default one is constructed from
            env vars. Tests pass in a MockAsyncOpenAI here; production code
            in the router calls this with no `client` argument.

    Returns:
        A dict matching AnalysisResponse:
            {
                "entry_id":  str,   # pass through from the argument
                "sentiment": str,   # "positive" | "negative" | "neutral"
                "summary":   str,   # 1-2 sentence summary of the entry
                "topics":    list[str],  # 2-4 topic tags
            }

    TODO (Task 4):
      1. If `client is None`, call `_default_client()` to construct one.
      2. Build a messages list that includes `entry_text` somewhere
         (the unit tests check that the entry text reaches the LLM).
      3. Call `client.chat.completions.create(...)` with a model from
         OPENAI_MODEL (default "gpt-4o-mini") and your messages.
      4. Parse the assistant's JSON response with `json.loads()`.
      5. Return a dict with `entry_id`, `sentiment`, `summary`, `topics`.
    """
    raise NotImplementedError(
        "Task 4: implement analyze_journal_entry using the openai SDK. "
        "See tests/test_llm_service.py for the test contract."
    )
```

Three things to notice about this stub:

1. **`client` parameter with a `None` default.** The router calls it
   with no argument and gets a real client built from env vars; tests
   pass in a `MockAsyncOpenAI`. This is the Azure-Samples dependency
   injection pattern — same code path for real and test, no
   monkeypatching, no network interception.
2. **`_default_client()` is a separate function**, not inline inside
   `analyze_journal_entry`. That way the learner's `if client is None:
   client = _default_client()` line is the *only* place the real
   `AsyncOpenAI` is constructed, which keeps the function trivially
   testable.
3. **`os.environ["OPENAI_API_KEY"]`** (not `.get()`) is deliberate —
   it fails fast with a clear `KeyError` in real use if the env var is
   missing. Tests never reach `_default_client()` because they always
   pass `client=mock`.

---

## Test suite redesign

### `tests/conftest.py`

Split the autouse DB cleanup into an opt-out fixture. Tests that don't need a
DB mark themselves (or their whole file) with `pytest.mark.no_db`:

```python
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from api.main import app


def pytest_configure(config):
    """Register custom markers so pytest doesn't warn about them."""
    config.addinivalue_line(
        "markers",
        "no_db: test does not require a database connection",
    )


@pytest.fixture(autouse=True)
async def cleanup_database(request):
    """Clean the DB before and after each test, unless the test opts out."""
    if "no_db" in request.keywords:
        yield
        return
    # Lazy import so tests marked no_db don't need DATABASE_URL set
    from api.repositories.postgres_repository import PostgresDB

    async with PostgresDB() as db:
        await db.delete_all_entries()
    yield
    async with PostgresDB() as db:
        await db.delete_all_entries()


@pytest.fixture
async def test_db() -> AsyncGenerator:
    from api.repositories.postgres_repository import PostgresDB

    async with PostgresDB() as db:
        yield db


@pytest.fixture
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_entry_data() -> dict:
    return {
        "work": "Studied FastAPI and built my first API endpoints",
        "struggle": "Understanding async/await syntax and when to use it",
        "intention": "Practice PostgreSQL queries and database design",
    }


@pytest.fixture
async def created_entry(test_client: AsyncClient, sample_entry_data: dict) -> dict:
    response = await test_client.post("/entries", json=sample_entry_data)
    assert response.status_code in (200, 201)
    result = response.json()
    return result["entry"]
```

> **Key detail:** the lazy `from api.repositories...` import inside the fixture
> means `test_models.py` and `test_logging.py` (both `no_db`) don't trigger
> the module-level `DATABASE_URL` check in `postgres_repository.py`. They can
> run without Postgres.
>
> **But `test_client` still imports `api.main`**, which transitively imports
> the router → repository. So any API test still needs `DATABASE_URL`. That's
> fine — tests using `test_client` are integration tests by nature.

### `pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
markers =
    no_db: test does not require a database connection
```

> Per decision Q3, Task 4's acceptance lives in `tests/test_llm_service.py`
> as deterministic unit tests with an injected mock client. No
> `addopts` filter, no `pytest.mark.llm`, no "skipped when secret
> missing" footgun. All pytest tests run by default, on both
> upstream and fork CI.

### `tests/test_logging.py` (new)

```python
"""Tests for Task 1: logging configuration in api.main."""
import logging

import pytest

pytestmark = pytest.mark.no_db


def test_root_logger_is_configured_at_info():
    """Task 1: the root logger should be at INFO level or finer."""
    import api.main  # noqa: F401  (import triggers logging setup)

    root = logging.getLogger()
    assert root.level != 0 and root.level <= logging.INFO, (
        "Root logger should be configured at INFO (or finer). "
        "Did you call logging.basicConfig() in api/main.py?"
    )


def test_root_logger_has_handler():
    """Task 1: the root logger should have at least one handler attached."""
    import api.main  # noqa: F401

    root = logging.getLogger()
    assert len(root.handlers) >= 1, (
        "Root logger should have at least one handler. "
        "logging.basicConfig() attaches a StreamHandler by default."
    )


def test_journal_logger_propagates():
    """Task 1: the service-layer 'journal' logger should propagate to root."""
    import api.main  # noqa: F401

    journal_logger = logging.getLogger("journal")
    assert journal_logger.propagate is True
```

> These tests import `api.main` for side effects. `api.main` imports the
> router → repository → `DATABASE_URL` check. So **`test_logging.py`
> technically does need `DATABASE_URL` in the environment, despite being
> `no_db`.** This is OK in CI (the integration job has it set) and we
> document the limitation. If we wanted true hermetic logging tests we'd have
> to refactor the DB import chain — out of scope.

### `tests/test_models.py` changes

- Add `pytestmark = pytest.mark.no_db` at the top of the file.
- **Remove** `test_entry_create_empty_strings_allowed` (B10).
- **Add** a new `TestEntryCreateValidation` class:

```python
class TestEntryCreateValidation:
    """Task 3: input validation on EntryCreate."""

    def test_empty_string_rejected(self):
        with pytest.raises(ValidationError):
            EntryCreate(work="", struggle="valid", intention="valid")

    def test_whitespace_only_rejected(self):
        with pytest.raises(ValidationError):
            EntryCreate(work="   ", struggle="valid", intention="valid")

    def test_whitespace_stripped_from_valid_input(self):
        entry = EntryCreate(
            work="  Studied FastAPI  ",
            struggle="valid",
            intention="valid",
        )
        assert entry.work == "Studied FastAPI"


class TestEntryUpdateModel:
    """Task 3: EntryUpdate model with partial updates."""

    def test_all_fields_optional(self):
        # Importing inside the test so tests still collect on a fresh fork
        # where the learner hasn't added the model yet.
        from api.models.entry import EntryUpdate

        update = EntryUpdate()
        assert update.model_dump(exclude_unset=True) == {}

    def test_partial_update(self):
        from api.models.entry import EntryUpdate

        update = EntryUpdate(work="Updated work")
        assert update.model_dump(exclude_unset=True) == {"work": "Updated work"}

    def test_oversize_field_rejected(self):
        from api.models.entry import EntryUpdate

        with pytest.raises(ValidationError):
            EntryUpdate(work="a" * 300)
```

### `tests/test_api.py` changes

- The existing `TestCreateEntry`, `TestGetAllEntries`, `TestGetSingleEntry`,
  `TestUpdateEntry`, `TestDeleteEntry`, `TestDeleteAllEntries`, `TestAnalyzeEntry`
  stay, with two tweaks:
  - `test_create_entry_success` accepts `status_code in (200, 201)` since
    we're adding the 201 status to the router (see migration notes).
  - The `@patch` decorators in `TestAnalyzeEntry` stay pointing at
    `api.routers.journal_router.analyze_journal_entry` (the import is now
    present in the router after our earlier fix).
- **Add** new tests under `TestUpdateEntry`:

```python
async def test_update_rejects_oversize_field(
    self, test_client: AsyncClient, created_entry: dict
):
    """Task 3: PATCH must enforce the 256-char limit (previously bypassed)."""
    response = await test_client.patch(
        f"/entries/{created_entry['id']}",
        json={"work": "a" * 300},
    )
    assert response.status_code == 422


async def test_update_rejects_empty_string(
    self, test_client: AsyncClient, created_entry: dict
):
    """Task 3: PATCH must reject empty strings (whitespace-only included)."""
    response = await test_client.patch(
        f"/entries/{created_entry['id']}",
        json={"work": "   "},
    )
    assert response.status_code == 422
```

### `tests/test_llm_service.py` (new)

Task 4's acceptance check. Injects a `MockAsyncOpenAI` into
`analyze_journal_entry` via its `client` parameter and asserts on
what the student's code does with it.

No new dependencies. The mock is ~30 lines of handwritten Python in
this file, modeled directly on
[`tests/test_mediadescriber.py`](https://github.com/Azure-Samples/azure-search-openai-demo/blob/main/tests/test_mediadescriber.py)
in `Azure-Samples/azure-search-openai-demo` — the canonical
Microsoft reference for testing OpenAI Python SDK code.

```python
"""Tests for Task 4: LLM-powered entry analysis.

These tests inject a MockAsyncOpenAI client into analyze_journal_entry,
following the pattern used by Azure-Samples/azure-search-openai-demo
(tests/test_mediadescriber.py). The mock captures calls and returns
real openai.types objects, so the student's code path is exercised
exactly as it would be against a real provider — only the network
layer is stubbed.

No new test dependencies are required; the mock is ~30 lines of
handwritten Python in this file.
"""
import json

import pytest
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice
from openai.types.completion_usage import CompletionUsage

from api.models.entry import AnalysisResponse
from api.services.llm_service import analyze_journal_entry

pytestmark = pytest.mark.no_db


# ---------------------------------------------------------------------
# Mock OpenAI client
#
# Mirrors tests/test_mediadescriber.py in Azure-Samples/azure-search-openai-demo.
# We construct real openai.types objects so the student's typed attribute
# access (completion.choices[0].message.content) works unchanged.
# ---------------------------------------------------------------------

def _make_completion(content: str) -> ChatCompletion:
    return ChatCompletion(
        id="chatcmpl-test",
        object="chat.completion",
        created=0,
        model="test-model",
        choices=[
            Choice(
                index=0,
                finish_reason="stop",
                message=ChatCompletionMessage(role="assistant", content=content),
            )
        ],
        usage=CompletionUsage(
            prompt_tokens=10, completion_tokens=20, total_tokens=30
        ),
    )


class MockChatCompletions:
    def __init__(self, response: ChatCompletion) -> None:
        self.response = response
        self.create_calls: list[dict] = []

    async def create(self, **kwargs) -> ChatCompletion:
        self.create_calls.append(kwargs)
        return self.response


class MockChat:
    def __init__(self, completions: MockChatCompletions) -> None:
        self.completions = completions


class MockAsyncOpenAI:
    def __init__(self, response: ChatCompletion) -> None:
        self._completions = MockChatCompletions(response)
        self.chat = MockChat(self._completions)

    @property
    def create_calls(self) -> list[dict]:
        return self._completions.create_calls


# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------

SAMPLE_ENTRY_TEXT = (
    "Studied FastAPI today. Struggled with async/await syntax. "
    "Tomorrow I'll practice PostgreSQL queries."
)

VALID_ANALYSIS_JSON = json.dumps(
    {
        "sentiment": "positive",
        "summary": "Reflected on FastAPI study and async concepts.",
        "topics": ["FastAPI", "async"],
    }
)


async def test_analyze_entry_actually_calls_llm():
    """Student's code must actually call the LLM — no hardcoded dict shortcut."""
    client = MockAsyncOpenAI(_make_completion(VALID_ANALYSIS_JSON))

    await analyze_journal_entry("entry-1", SAMPLE_ENTRY_TEXT, client=client)

    assert len(client.create_calls) >= 1, (
        "Expected analyze_journal_entry to call client.chat.completions.create() "
        "at least once. If you're returning a hardcoded dict without calling "
        "the LLM, this will fail."
    )


async def test_analyze_entry_sends_entry_text_in_prompt():
    """The entry text must actually make it into the messages sent to the LLM."""
    client = MockAsyncOpenAI(_make_completion(VALID_ANALYSIS_JSON))

    await analyze_journal_entry("entry-1", SAMPLE_ENTRY_TEXT, client=client)

    call = client.create_calls[0]
    assert "messages" in call, "Expected `messages` kwarg in the create() call"

    all_content = " ".join(
        msg["content"]
        for msg in call["messages"]
        if isinstance(msg.get("content"), str)
    )
    assert "FastAPI" in all_content, (
        f"Expected the entry text to appear in the prompt messages. "
        f"Got messages with content: {all_content!r}"
    )


async def test_analyze_entry_returns_valid_analysis_response():
    """The returned dict must validate against AnalysisResponse."""
    client = MockAsyncOpenAI(_make_completion(VALID_ANALYSIS_JSON))

    result = await analyze_journal_entry(
        "entry-1", SAMPLE_ENTRY_TEXT, client=client
    )

    validated = AnalysisResponse.model_validate(result)
    assert validated.entry_id == "entry-1"
    assert validated.sentiment in {"positive", "negative", "neutral"}
    assert validated.summary
    assert isinstance(validated.topics, list) and len(validated.topics) >= 1
```

> **Why real `openai.types` objects in the mock return value?** Because
> the student's code will do things like
> `completion.choices[0].message.content` — typed attribute access on
> Pydantic models, not dict key lookup. Returning plain dicts would
> break the student's code the moment they write it against real docs.
> Constructing real `ChatCompletion` / `Choice` / `ChatCompletionMessage`
> objects makes the mock code path byte-identical to production; the
> only difference is who's on the other end of `.create()`. This is
> exactly what Pamela Fox does in Azure-Samples.

### `tests/test_service.py` changes

**No changes.** The existing service layer integration tests stay
exactly as they are — they cover the DB-backed portions of
`EntryService` and don't touch the LLM. Task 4's LLM contract test
lives in `tests/test_llm_service.py` (new, above).

---

## CI workflow

### `.github/workflows/ci.yml` (new)

Two jobs:

- **lint** — fast, no Postgres. Runs `ruff check`, `ruff format --check`,
  and `pyright` (basic mode).
- **test** — Postgres service container, runs `pytest`. Includes
  `tests/test_llm_service.py` which validates Task 4 with an injected
  mock OpenAI client — no API keys, no network, no fork secrets.

Each job appears as a **separate check** in the GitHub Actions UI
(`CI / lint`, `CI / test`), so learners get a distinct red/green
signal per task cluster rather than one monolithic "test" status.
The same workflow runs identically on upstream and fork CI —
hermetic, deterministic, no secrets anywhere.

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

# Read-only permissions; no secrets needed for the default run.
permissions:
  contents: read

# Cancel superseded runs on the same ref (e.g. force-pushes on a PR branch).
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v6
        with:
          enable-cache: true

      - name: Set up Python
        run: uv python install 3.14

      - name: Install dependencies
        run: uv sync --locked --all-extras

      - name: Ruff check
        run: uv run ruff check .

      - name: Ruff format check
        run: uv run ruff format --check .

      - name: Pyright type check
        run: uv run pyright

  test:
    name: Test
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: career_journal
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    env:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: career_journal
      DATABASE_URL: postgresql://postgres:postgres@localhost:5432/career_journal

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v6
        with:
          enable-cache: true

      - name: Set up Python
        run: uv python install 3.14

      - name: Install dependencies
        run: uv sync --locked --all-extras

      - name: Initialize database schema
        run: |
          PGPASSWORD=postgres psql \
            -h localhost -U postgres -d career_journal \
            -f database_setup.sql

      - name: Run tests
        run: uv run pytest -v
```

### Key CI design decisions

- **`permissions: contents: read`** at workflow level — least-privilege.
- **`concurrency` block** — force-pushes cancel stale runs.
- **`uv sync --locked --all-extras`** — uses `uv.lock`, installs dev extras
  (`pytest`, `httpx`, `ruff`, `pyright`, `pre-commit`).
- **Service container over manual Docker** — GitHub Actions' `services:`
  block handles health-checks and cleanup.
- **`@v6` of `setup-uv`** — current stable as of research.
- **`uv python install 3.14`** — matches the bumped `pyproject.toml` floor
  (Q8). 3.14 is the current stable.
- **No `ty check`** — per Q5 (revisited); `ty` is still pre-1.0 and
  isn't in Pylance yet. We use `pyright` instead, which powers VS
  Code's Python extension and gives learners in-editor feedback.
- **`pyright` runs in the lint job.** Basic mode. Catches real type
  errors without drowning untyped stubs in warnings. See
  [`[tool.pyright]` config](#8-pyprojecttoml-python-314--openai-sdk--pyright--curated-ruff).
- **No matrix** — one Python version, one OS. Easy to add later.
- **No `pull_request_target`** — default `pull_request` is correct for a
  secrets-free upstream; see our earlier conversation on why
  `pull_request_target` is a foot-gun.
- **No secrets anywhere.** Task 4's acceptance test uses an injected
  `MockAsyncOpenAI` in `tests/test_llm_service.py` (following the
  [Azure-Samples/azure-search-openai-demo](https://github.com/Azure-Samples/azure-search-openai-demo)
  pattern). Both upstream and fork CI run the identical workflow with
  zero API keys, zero network calls to LLM providers, zero flakiness.
  `scripts/verify_llm.py` exists as an *optional* local helper for
  eyeballing real model output but is never invoked by CI.

---

## README changes

### New "CI" section

Added under "Development Workflow", after "First-Time Setup". Includes a
status badge at the very top of the README (per decision Q4):

```markdown
<!-- Top of README, under the title -->
[![CI](https://github.com/learntocloud/journal-starter/actions/workflows/ci.yml/badge.svg)](https://github.com/learntocloud/journal-starter/actions/workflows/ci.yml)
```

```markdown
## 🤖 Continuous Integration

This repo runs automated checks on every push and pull request. On a **fresh
fork**, you'll see a red ❌ next to your first commit on GitHub. **That's
expected** — the five tasks below are deliberately unfinished. As you
implement each task, more checks go green. When everything is green, your
capstone is done.

Two checks run:

- **Lint** — `ruff check`, `ruff format --check`, and `pyright` (basic
  type checking) across the codebase. Your VS Code editor is already
  running pyright under the hood via Pylance, so any type errors CI
  catches will also be visible inline as you code.
- **Test** — `pytest` against a Postgres service container. Includes
  `tests/test_llm_service.py`, which validates Task 4 with an
  injected mock OpenAI client — no API keys, no network, no flaky
  rate limits.

You can see what CI runs by looking at [`.github/workflows/ci.yml`](.github/workflows/ci.yml).
Run the same checks locally before pushing:

    uv run ruff check .
    uv run ruff format --check .
    uv run pyright
    uv run pytest

> **Optional local helper:** `uv run python -m scripts.verify_llm`
> runs your Task 4 implementation against a real LLM and prints what
> it returns. Not a CI gate and not required to pass the capstone —
> CI uses a mock client — but useful if you want to eyeball the
> actual model output. Needs `OPENAI_API_KEY` in your `.env`.
```

### Updated "First-Time Setup" expected output

Replace the stale "7 failed, 30 passed" block with the accurate baseline
after all redesign changes. Exact numbers will be determined during
implementation; the shape is:

```
FAILED tests/test_logging.py::test_root_logger_is_configured_at_info
FAILED tests/test_logging.py::test_root_logger_has_handler
FAILED tests/test_logging.py::test_journal_logger_propagates
FAILED tests/test_api.py::TestGetSingleEntry::test_get_entry_by_id_success
FAILED tests/test_api.py::TestGetSingleEntry::test_get_entry_not_found
FAILED tests/test_api.py::TestDeleteEntry::test_delete_entry_success
FAILED tests/test_api.py::TestDeleteEntry::test_delete_entry_not_found
FAILED tests/test_models.py::TestEntryCreateValidation::test_empty_string_rejected
FAILED tests/test_models.py::TestEntryCreateValidation::test_whitespace_only_rejected
FAILED tests/test_models.py::TestEntryCreateValidation::test_whitespace_stripped_from_valid_input
FAILED tests/test_models.py::TestEntryUpdateModel::test_all_fields_optional
FAILED tests/test_models.py::TestEntryUpdateModel::test_partial_update
FAILED tests/test_models.py::TestEntryUpdateModel::test_oversize_field_rejected
FAILED tests/test_api.py::TestUpdateEntry::test_update_rejects_oversize_field
FAILED tests/test_api.py::TestUpdateEntry::test_update_rejects_empty_string
============ ~15 failed, ~N passed ============
```

### Updated "Development Tasks" section

Five tasks, each with explicit acceptance:

- **Task 1:** Configure logging. Acceptance: `tests/test_logging.py` passes.
- **Task 2a:** GET /entries/{id}. Acceptance: `TestGetSingleEntry` passes.
- **Task 2b:** DELETE /entries/{id}. Acceptance: `TestDeleteEntry` passes.
- **Task 3:** Input validation. Acceptance: `TestEntryCreateValidation`,
  `TestEntryUpdateModel`, and new `TestUpdateEntry` validation tests pass.
- **Task 4:** AI analysis. Acceptance: `tests/test_llm_service.py`
  passes. Learner implements `analyze_journal_entry` using the `openai`
  Python SDK (or any OpenAI-compatible provider — see the provider list
  in the Task 4 setup section). The tests inject a `MockAsyncOpenAI`
  client and verify the student's code calls the LLM, passes the entry
  text in the prompt, and returns a dict matching `AnalysisResponse`.
  For optional live-model verification, set `OPENAI_API_KEY` in your
  `.env` and run `uv run python -m scripts.verify_llm`.
- **Task 5:** Cloud CLI setup. Acceptance: manual (`az --version`, etc.).

### New "What the tests actually cover" subsection

```markdown
### What the automated tests cover

CI verifies **four of the five tasks** automatically, on both upstream
and fork runs, with zero secrets and zero network calls to LLM providers:

| Task | Automated? | How |
|---|---|---|
| 1 – Logging | ✅ Yes | `tests/test_logging.py` inspects the root logger |
| 2a – GET endpoint | ✅ Yes | Integration test hits the endpoint |
| 2b – DELETE endpoint | ✅ Yes | Integration test hits the endpoint |
| 3 – Input validation | ✅ Yes | Model tests + PATCH integration tests |
| 4 – AI analysis | ✅ Yes | `tests/test_llm_service.py` injects a `MockAsyncOpenAI` into `analyze_journal_entry` and asserts (1) the student's code calls the LLM, (2) the entry text reaches the prompt, (3) the return value matches `AnalysisResponse`. Follows the [Azure-Samples/azure-search-openai-demo](https://github.com/Azure-Samples/azure-search-openai-demo) pattern. |
| 5 – Cloud CLI | ❌ No | Devcontainer change; rebuild and run `az --version` / `aws --version` / `gcloud --version` |

A green CI run means tasks 1–4 are done for real. Task 5 is the only
one that requires manual verification.
```

### Task 4 setup subsection (new)

```markdown
### Task 4 setup: picking a provider

This project mandates the **OpenAI Python SDK** — but that's not the same
as mandating OpenAI the company. The `openai` package works with any
OpenAI-compatible provider:

| Provider | Cost | Notes |
|---|---|---|
| **GitHub Models** (default) | Free | No credit card. Use your GitHub PAT with Models read access as `OPENAI_API_KEY`. |
| OpenAI | Paid | Set `OPENAI_BASE_URL` back to default. |
| Azure OpenAI | Paid | Set `OPENAI_BASE_URL` to your Azure endpoint. |
| Groq / Together / OpenRouter / Fireworks / DeepInfra | Paid (cheap) | Set `OPENAI_BASE_URL` to their endpoint; use their model IDs. |
| Ollama / LM Studio / vLLM | Free (local) | Runs on your machine. |
| Anthropic (via OpenAI-compat endpoint) | Paid | Use their OpenAI-compat base URL. |

**Local setup (all you need):**

1. **Get a key.** Default path: a GitHub Models PAT, free, no credit
   card. Go to https://github.com/settings/tokens and create a
   fine-grained token with **read** access to **Models**.
2. **Add it to your `.env` file:**
    ```
    OPENAI_API_KEY=<your-pat>
    # Optional, only if you're not using GitHub Models:
    # OPENAI_BASE_URL=https://api.openai.com/v1
    # OPENAI_MODEL=gpt-4o-mini
    ```
3. **Implement `analyze_journal_entry`** in
   `api/services/llm_service.py`. The shipped stub already accepts an
   injectable `client` parameter — leave that signature as-is; it's
   what the unit tests rely on.
4. **Run the tests.** `uv run pytest tests/test_llm_service.py -v`
   should go green. These tests use a `MockAsyncOpenAI` — they **do
   not** call the real LLM, so they run fast, deterministically, and
   without using your API quota.
5. **(Optional) Eyeball the real output.**
   `uv run python -m scripts.verify_llm` calls your real LLM with a
   canned journal entry and prints the response. Not required to pass
   the capstone; just helpful for sanity-checking that your prompt
   gives sensible output in practice.

> **No GitHub Actions secrets needed.** CI runs the same
> `tests/test_llm_service.py` as you do locally, with the same mock
> client. Upstream `learntocloud/journal-starter` CI and your fork's
> CI behave identically — no API keys anywhere, no fork-specific
> setup, no "did I add the secret right?" debugging.

> **Local-only providers work fine.** Ollama / LM Studio / vLLM run
> on your machine; because CI uses a mock client, there's no need for
> them to be reachable from GitHub Actions. Your `analyze_journal_entry`
> just has to work against any OpenAI-compat endpoint, which local
> servers all provide.
```

---

## Migration impact & rollout

### Breaking changes for existing forks

This plan deliberately breaks a few things. Anyone with a mid-capstone fork
will hit:

1. **POST `/entries` now returns 201 Created** instead of 200 OK (decision
   Q2). Any client or test asserting `== 200` on create is broken; update
   to `in (200, 201)` or `== 201`. This is the most visible breaking change.
2. **`update_entry` signature change** — from `dict` to `EntryUpdate`. If a
   learner already implemented `update_entry` with the raw dict (they
   shouldn't have — it was already working — but they might have extended
   it), they'll need to adapt.
3. **Logging test now present** — a learner who already implemented logging
   should pass it, but if they used a non-standard config (e.g. a file
   handler only, no console) they might fail the handler assertion.
4. **Empty-string test deleted, stricter validation added** — a learner who
   was relying on empty-string entries being valid is now broken.
5. **Task 4 signature change.** `analyze_journal_entry` now takes an
   optional `client: AsyncOpenAI | None = None` parameter. Learners
   who already implemented the function without this parameter need
   to add it so `tests/test_llm_service.py` can inject a mock. The
   one-line fix: add `client: AsyncOpenAI | None = None` to the
   signature and start the body with
   `if client is None: client = _default_client()`. **No GitHub
   Actions secret required** — tests use a mock, not a real key.
6. **Python 3.14 required (Q8).** `pyproject.toml` now floors at 3.14.
   Forks on Python 3.11–3.13 need to rebuild their devcontainer (or
   re-run `uv python install 3.14` locally). No code changes are
   strictly required to be 3.14-compatible, but anything that happened
   to depend on 3.11-specific behavior (unlikely in this codebase) will
   need attention.
7. **`openai` is now a required dependency (Q9).** Forks that used a
   different SDK (`anthropic`, `google-generativeai`, raw `httpx`,
   etc.) need to rewrite their `analyze_journal_entry` against the
   `openai` Python SDK. For most learners this is a small change
   because OpenAI-compat is the de facto standard and all the major
   providers support it. Learners using purely Anthropic-native or
   Gemini-native features will need to switch to the OpenAI-compat
   endpoints those providers offer.
8. **Dropped dependencies.** `aiohttp`, `sqlalchemy`, `psycopg2-binary`,
   and `ty` are removed from `pyproject.toml`. Any fork that imported
   these directly (none should) will break.

**Mitigation:** document the breaking changes in the PR description and the
changelog. Learners with in-progress work can either rebase their branch or
stay on the old commit until they're done.

### Suggested PR structure

Ship as **one PR** per user request, organized into logical commits. Each
commit leaves the repo buildable.

1. `docs: add capstone redesign plan`
2. `chore(deps): bump to Python 3.14, curate ruff rules, add pyright, mandate openai SDK` *(Q5, Q8, Q9)*
3. `fix(router): return 201 on create, drop overeager try/except` *(B4, Q2)*
4. `fix(models): drop stale TODOs and Entry | None timestamps` *(B6, B7)*
5. `fix(repo): stop overwriting service's updated_at` *(B3)*
6. `refactor(router): wire AnalysisResponse through analyze endpoint` *(B11, B14)*
7. `feat(models): add EntryUpdate and EntryCreate validation stubs`
8. `feat(router): use EntryUpdate on PATCH` *(B5)*
9. `test: split no_db marker and add Task 3 validation tests`
10. `test: add test_logging.py for Task 1`
11. `feat(llm_service): add injectable client parameter stub for Task 4`
12. `test: add test_llm_service.py with MockAsyncOpenAI (Azure-Samples pattern)`
13. `feat: add scripts/verify_llm.py as optional local helper`
14. `chore: add pre-commit config and ruff hooks` *(Q6)*
15. `ci: add GitHub Actions workflow with lint and test jobs`
16. `docs: rewrite README task list and add CI section`

The final commit leaves the repo with the documented fresh-fork red → green
behavior:

- Upstream `learntocloud/journal-starter`: lint + test jobs green.
- Fresh fork before any task: lint green, test red (~18 failing tests
  across Tasks 1–4 — ~15 from Tasks 1–3 plus 3 from
  `tests/test_llm_service.py`).
- Fresh fork after all tasks: everything green.
- **Upstream and fork CI are byte-identical.** No fork-specific jobs,
  no secrets anywhere, no "did I configure my fork right?" debugging.

---

## Open questions

**All resolved.** See the [Decisions](#decisions) table at the top of the
document for the summary. Full rationale for each is preserved below for
archival purposes.

### Q1. Should `EntryCreate` validation ship as a stub or as the reference?

**Resolved: B (stub).** The whole point of Task 3 is learning Pydantic v2
validators. Shipping the answer would make the task a copy-paste exercise.

### Q2. Should POST `/entries` return 201 or 200?

**Resolved: 201.** REST-correct. We accept the breaking change to existing
forks and document it clearly in the PR description and migration notes.

### Q3. Should the LLM contract test live in `test_service.py` or a new file?

**Resolved: new file — `tests/test_llm_service.py` — using a `MockAsyncOpenAI`
injected via an added `client` parameter on `analyze_journal_entry`.**

This is the third different answer to Q3 across the life of this plan,
and it's worth writing down why each earlier position failed so we
don't cycle back to them.

**First attempt: "put an LLM contract test in `test_service.py` that
hits the real API, gated by a `pytest.mark.llm` skip."** Rejected
because `skipif(no OPENAI_API_KEY)` reads as green in CI when it was
silently skipped. Learners never discover they haven't finished the
task.

**Second attempt: "fork-only `verify-llm` CI job running
`scripts/verify_llm.py` against the real API, gated by
`github.repository_owner != 'learntocloud'`."** Better in that skipped
runs show up distinctly in the GitHub UI, but three fundamental
problems remained: (a) **flakiness** — real API calls rate-limit,
timeout, return content-filtered responses, and break when models get
deprecated; Task 4 would go red for reasons that aren't the
student's fault; (b) **secrets-setup friction** — students would
have to correctly configure `OPENAI_API_KEY` as an Actions secret on
their fork before they could get any Task 4 signal at all; (c) **the
"upstream never pays" framing was weak reasoning** — the real issue
is that *all* CI (upstream and fork) should be deterministic, not
that upstream is special.

**Third attempt (resolved): inject a mock OpenAI client.** We went
looking for how production codebases solve this and found
[Azure-Samples/azure-search-openai-demo](https://github.com/Azure-Samples/azure-search-openai-demo)
— Microsoft's canonical reference for OpenAI Python SDK usage,
maintained by Pamela Fox. Their `tests/test_mediadescriber.py` uses
exactly this pattern: a handwritten `MockAsyncOpenAI` class
(`MockAsyncOpenAI` + `MockResponses` with a `create_calls` list),
injected into the code under test via a constructor argument.
No `respx`, no `pytest-httpserver`, no `vcrpy`, no
`openai-responses-python` plugin — just plain Python.

We adopt the same pattern, with one adaptation: because
`analyze_journal_entry` is a module-level function (not a class),
the mock is injected via an added `client: AsyncOpenAI | None = None`
parameter. The router calls it with no argument (real client
constructed from env vars); tests pass a `MockAsyncOpenAI`. Same
code path, different collaborator.

Why this is strictly better than every prior attempt:

- **Deterministic.** No network, no rate limits, no flakiness, no
  model deprecations breaking builds.
- **Hermetic.** No API keys anywhere in CI, upstream or fork.
- **Fast.** Tests run in milliseconds.
- **Zero new dependencies.** The mock is ~30 lines of handwritten
  Python in the test file itself.
- **Teaches dependency injection**, a real production pattern, rather
  than teaching "how to configure GitHub Actions secrets."
- **Catches the three cheating modes we care about** (hardcoded dict,
  empty/bogus prompt, wrong return shape) with three cheap assertions.
- **Grounded in Microsoft's own reference implementation**, not a
  blog post.

We also keep `scripts/verify_llm.py` as an **optional** local helper
(no CI role) for learners who want to eyeball real model output
against their implementation. It's not a gate and not on the
acceptance path.

### Q4. Add a CI status badge to README?

**Resolved: yes.** Included in the README CI section, at the top of the
file under the title.

### Q5. Add a type checker to the lint job?

**Resolved: yes, pyright in basic mode. Not `ty`.**

Original call was "no, ty is noisy, follow-up PR." Revisited when we
realized (a) type checking genuinely teaches better code and belongs
in a learning repo, and (b) `ty` ≠ "type checking" — `ty` is one
specific (pre-1.0) implementation. The broader decision is worth
revisiting even if `ty` specifically isn't ready.

We use **pyright** because:

- **It already runs in every learner's VS Code** (Pylance is built on
  pyright), so our `[tool.pyright]` config also tunes the in-editor
  experience. Learners see type errors as they type, not when they
  push to CI.
- **It's stable** — no breaking changes between minor versions. Safe
  to ship to learners.
- **"Basic" mode is pedagogically right** for a starter: it catches
  real errors (unresolved names, wrong arg types on annotated
  functions, Pydantic model misuse) without yelling about every
  un-annotated function parameter. As learners add type hints, they
  get richer feedback automatically.
- **It's fast.** Adds ~3–5 seconds to the lint job.

Why not `ty`:

- Still pre-1.0. Breaking changes between releases are expected.
- Not yet running inside Pylance, so the in-editor experience
  wouldn't match CI. Learners would hit "works in my editor, red in
  CI" confusion.
- Known false positives on FastAPI's decorator-heavy idioms.

We remove `ty` from dev extras and add `pyright`. A `[tool.pyright]`
section in `pyproject.toml` configures include paths, Python version,
and the `basic` type-checking mode. The CI lint job runs
`uv run pyright` after the ruff checks. **Once `ty` hits 1.0 and
lands in Pylance, revisit.**

### Q6. Should we ship a `pre-commit` config?

**Resolved: yes.** Included in this PR as `.pre-commit-config.yaml` with
`astral-sh/ruff-pre-commit` hooks for lint + format. `pre-commit` goes
into the `dev` extras of `pyproject.toml`, and the README gets a one-line
setup hint (`uv run pre-commit install`).

### Q7. Is the workflow job name `test` what learn-to-cloud-app's status-check hook expects?

**Not yet resolved.** Will confirm with maintainers before merge.

Issue #89 mentioned a downstream use case: the Phase 3 verification in
learn-to-cloud-app could replace its LLM-based code analyzer with a GitHub
API call that checks CI status on the learner's fork. This plan enables that
use case. We should ping the maintainers to confirm it's still the intended
direction before finalizing the job name (`test`) and badge. If they confirm,
name the test job exactly `test` so the downstream check can look for
`CI / test`, and leave a comment in `ci.yml` noting the contract.

### Q8. What Python version should we target?

**Resolved: 3.14.** The current shipped `pyproject.toml` floors at 3.11,
which was the current stable when the repo was created. 3.14 is the
current stable release (October 2025) and there's no reason a starter
repo should be two minor versions behind; it's not constrained by any
downstream consumer. Learners get modern syntax (PEP 695 type
parameters, PEP 750 t-strings, the free-threaded mode where supported)
and the latest type-checker ergonomics. CI runs
`uv python install 3.14`; the devcontainer base image is bumped to
`mcr.microsoft.com/devcontainers/python:1-3.14-bookworm` in the same
commit.

No code in the current codebase actually requires >=3.14 features —
the bump is about ecosystem currency and forward signaling, not unlocking
specific language features.

### Q9. Which LLM providers do we support?

**Resolved: any OpenAI-compatible API, default to GitHub Models.**

The original "learners pick their own provider" position is a trap:
`analyze_journal_entry` would need a switch over multiple SDKs
(`openai`, `anthropic`, `google-generativeai`, raw `httpx`, etc.),
and the test mock would need to be SDK-specific. Provider-agnostic
tests would have to accept anything vaguely JSON-shaped. Loose
tests = no real signal.

The sweet spot: **mandate the `openai` Python SDK**, which speaks the
OpenAI-compat protocol that every serious provider in 2026 supports.
Learners get real choice:

- **GitHub Models** (the default) — free, no credit card, accessible
  with a fine-grained GitHub PAT. Perfect for capstone learners.
- **OpenAI, Azure OpenAI** — obvious.
- **Groq, Together, OpenRouter, Fireworks, DeepInfra** — cheap,
  high-performance, all OpenAI-compat.
- **Ollama, LM Studio, vLLM** — free, local. Work fine because CI
  uses a mock client — there's nothing for GitHub Actions to reach.
- **Anthropic** — via their OpenAI-compat endpoint.

The starter mandates exactly three env vars (`OPENAI_API_KEY`,
`OPENAI_BASE_URL`, `OPENAI_MODEL`), one SDK, one code path through
`analyze_journal_entry`, and **zero CI secrets** (the mock client
handles CI; the real client handles production). The
`AnalysisResponse` validation stays strict regardless of provider —
it's checking the *shape the learner returns from
`analyze_journal_entry`*, not the raw LLM response, so tests don't
get looser to accommodate provider variance.

`openai` is added to `[project].dependencies`. The shipped stub
`api/services/llm_service.py` shows learners the OpenAI-compat client
construction, the injectable `client` parameter, and the contract
with `tests/test_llm_service.py` (without implementing the prompt or
parsing) so they know which SDK to use without having to guess.

---

## Research references

Sources consulted via Tavily and Context7 while writing this plan:

### FastAPI
- [FastAPI Body Updates tutorial](https://fastapi.tiangolo.com/tutorial/body-updates)
  — the canonical `model_dump(exclude_unset=True)` + `model_copy(update=...)`
  PATCH pattern. Confirmed that a separate `Update` model with all-optional
  fields is the idiomatic Pydantic-v2 approach.
- [FastAPI SQL Databases tutorial](https://fastapi.tiangolo.com/tutorial/sql-databases)
  — `HeroUpdate` pattern; separate create/update/public models.

### Pydantic v2
- [`StringConstraints`](https://docs.pydantic.dev/latest/api/types) — the
  `Annotated[str, StringConstraints(...)]` pattern is the modern v2 way to
  express string constraints declaratively. Preferred over `constr()` (which
  still works but is less composable).
- [`ConfigDict` string options](https://docs.pydantic.dev/latest/api/config)
  — `str_strip_whitespace`, `str_min_length`, `str_max_length` are
  model-wide shortcuts. Good for the "every field has the same shape" case.
- [Model validators](https://docs.pydantic.dev/latest/examples/custom_validators)
  — `@model_validator(mode="after")` for cross-field checks. Not needed for
  Task 3 but good reference.

### pytest / pytest-asyncio
- [pytest-asyncio docs](https://pytest-asyncio.readthedocs.io/en/stable/)
  — with `asyncio_mode = auto` in `pytest.ini` (which this repo uses), the
  `@pytest.mark.asyncio` decorator is not required on individual tests.
- Custom marker registration via `pytest_configure` to avoid "unknown marker"
  warnings. We use this for `no_db` and `llm`.
- `pytestmark = pytest.mark.no_db` at module level applies the marker to
  every test in the file. Clean for `test_models.py` and `test_logging.py`.

### GitHub Actions + Postgres + uv
- [Simon Willison's "Running tests against PostgreSQL in a service container"](https://til.simonwillison.net/github-actions/postgresq-service-container)
  — definitive minimal example of the `services: postgres:` pattern with
  health checks.
- [Russ Poldrack's "Automated testing with GitHub Actions"](https://russpoldrack.substack.com/p/automated-testing-with-github-actions)
  — modern `uv sync --locked --all-extras --dev` + `astral-sh/setup-uv@v6`
  pattern.
- [OneUptime "Integration Testing in GitHub Actions"](https://oneuptime.com/blog/post/2025-12-20-integration-testing-github-actions/view)
  — best practices: health checks, dependency caching, realistic data,
  cleanup.

### LLM integration testing strategy

Extended research on how production codebases test OpenAI SDK calls.
Informed the Q3 decision (the third and final revision).

- **[Azure-Samples/azure-search-openai-demo](https://github.com/Azure-Samples/azure-search-openai-demo)**
  — the canonical Microsoft reference for OpenAI Python SDK usage,
  maintained by Pamela Fox. Directly sourced the `MockAsyncOpenAI`
  pattern from
  [`tests/test_mediadescriber.py`](https://github.com/Azure-Samples/azure-search-openai-demo/blob/main/tests/test_mediadescriber.py)
  (handwritten mock with `create_calls` capture, injected via
  constructor) and the `mock_openai_chatcompletion` monkeypatch
  fixture from
  [`tests/conftest.py`](https://github.com/Azure-Samples/azure-search-openai-demo/blob/main/tests/conftest.py).
  Also confirms our Q8 call: the repo bumped to Python 3.14 via
  [#2787](https://github.com/Azure-Samples/azure-search-openai-demo/pull/2787)
  six months before our bump. This repo is the primary source for
  the resolved Q3 strategy.
- [Pamela Fox, "Mocking async openai package calls with pytest"](https://blog.pamelafox.org/2024/06/mocking-async-openai-package-calls-with.html)
  — the same author's blog-post companion to the production pattern
  in the repo above. Explains the "monkeypatch `openai_client.responses.create`
  with a mock async function" approach for integration tests where
  the client is held in app config.
- [`respx`](https://lundberg.github.io/respx/) (Context7: `/lundberg/respx`,
  161 snippets) — mocks httpx at the transport layer, which is what
  the openai SDK runs on. Evaluated and rejected for this project:
  adds a dependency, couples tests to internal SDK URL patterns,
  returns raw JSON the SDK has to re-parse. Good tool but heavier
  than we need.
- [`openai-responses-python`](https://github.com/mharrisb1/openai-responses-python)
  (Context7: `/mharrisb1/openai-responses-python`, 103 snippets) —
  pytest plugin built on top of respx with typed routes. Evaluated
  and rejected: too much magic, not transferable learning.
- [`pytest-httpserver`](https://github.com/csernazs/pytest-httpserver)
  — real HTTP server in a separate thread. Evaluated and rejected:
  SDK-agnostic nature would let students use `requests` instead of
  the mandated `openai` package without being caught.
- [LangChain `FakeListChatModel`](https://python.langchain.com/docs/integrations/chat/fake)
  — dependency-injection pattern that requires LangChain-specific
  wiring. Rejected because we don't want to pull LangChain into a
  starter repo just for a mock.
- [Confident AI, "LLM Testing in 2026: Top Methods and Strategies"](https://www.confident-ai.com/blog/llm-testing-in-2025-top-methods-and-strategies)
  — industry overview; confirms the "mock at the SDK layer, validate
  deterministically" pattern is standard for testing code *around* an
  LLM (as opposed to testing the LLM itself, which needs a different
  toolkit).
- [Galileo, "LLM Integration Testing Strategies"](https://galileo.ai/blog/llm-integration-testing-strategies)
  — reinforces the decomposition: deterministic tests for integration
  logic (our Task 4 contract), non-deterministic evals for prompt
  quality (out of scope for this capstone).

### Python 3.14 migration
- [Python 3.14 release notes](https://docs.python.org/3.14/whatsnew/3.14.html)
  — confirms the language features mentioned in the Q8 rationale
  (PEP 695 type parameters are 3.12+, PEP 750 t-strings are 3.14,
  the experimental free-threaded mode is 3.13+).
- [Azure-Samples/azure-search-openai-demo PR #2787](https://github.com/Azure-Samples/azure-search-openai-demo/pull/2787)
  — "Add Python 3.14 support and drop Python 3.9" — prior art from
  a Microsoft-maintained reference codebase, merged six months
  before our bump. Validates the timing of the version floor.

---

## Approval checklist

Before implementation starts, please confirm:

- [ ] Task list (Tasks 1–5) is acceptable.
- [ ] The breaking changes in [Migration impact](#migration-impact--rollout) are acceptable.
- [ ] Open questions Q1 (ship validators as stub) answered.
- [ ] Open question Q2 (POST status code) answered.
- [ ] Open question Q4 (status badge) answered.
- [ ] One PR vs multiple PRs — user has indicated one PR; confirm.
- [ ] Ready to proceed with commit-by-commit implementation as listed in
      [Suggested PR structure](#suggested-pr-structure).

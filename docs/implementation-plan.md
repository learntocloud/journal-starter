# Capstone Redesign — Implementation Plan

Concrete work order for the single PR that ships the capstone redesign.
For rationale, audit findings, and rejected alternatives, see
[capstone-redesign-plan.md](capstone-redesign-plan.md).

## Overview

One PR that:

- Bumps Python to 3.14, mandates the `openai` SDK, curates ruff rules,
  switches type checker to `pyright` (basic mode).
- Fixes ~8 shipped-code bugs in router, models, repository.
- Adds input validation stubs (Task 3) and LLM service DI stub (Task 4).
- Rewrites the test suite: `no_db` marker, new `test_logging.py`,
  new `test_llm_service.py` with a handwritten `MockAsyncOpenAI`.
- Adds `.github/workflows/ci.yml` with two jobs: **lint** and **test**.
- Adds `.pre-commit-config.yaml`, `scripts/verify_llm.py` (optional
  local helper), CI badge, and rewrites the README task list.

Target behavior after the PR lands:

- **Upstream `learntocloud/journal-starter`:** both CI jobs green.
- **Fresh fork before any task:** lint green, test red (~18 failing
  tests across Tasks 1–4).
- **Fresh fork after all tasks:** everything green.
- **Upstream and fork CI are byte-identical.** No secrets, no
  fork-specific jobs.

---

## Task acceptance (what each task means after this PR)

| Task | Scope | Acceptance check |
|---|---|---|
| 1 — Logging | `api/main.py` | `tests/test_logging.py` passes |
| 2a — GET single | `api/routers/journal_router.py` | `TestGetSingleEntry` passes |
| 2b — DELETE single | `api/routers/journal_router.py` | `TestDeleteEntry` passes |
| 3 — Input validation | `api/models/entry.py`, PATCH router | `TestEntryCreateValidation`, `TestEntryUpdateModel`, new `TestUpdateEntry` cases pass |
| 4 — AI analysis | `api/services/llm_service.py` | `tests/test_llm_service.py` passes (3 tests, mock client) |
| 5 — Cloud CLI | `.devcontainer/devcontainer.json` | Manual (`az --version` / `aws --version` / `gcloud --version`) |

---

## Files to create or edit

### `pyproject.toml`

```toml
[project]
name = "journal-api"
version = "0.1.0"
description = "Journal API"
requires-python = ">=3.14"
dependencies = [
    "fastapi",
    "uvicorn",
    "asyncpg",
    "pydantic>=2",
    "python-dotenv",
    "openai",
]

[project.optional-dependencies]
dev = [
    "pytest>=9.0.2",
    "pytest-asyncio",
    "httpx",
    "ruff",
    "pyright",
    "pre-commit",
]

[tool.ruff]
line-length = 100
target-version = "py314"

[tool.ruff.lint]
select = [
    "E", "W", "F", "I", "UP", "N", "B", "C4", "DTZ",
    "SIM", "RET", "PT", "S", "T20", "ASYNC", "RUF",
]
ignore = ["E501"]

[tool.ruff.lint.flake8-bugbear]
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
"tests/**/*.py" = ["S101"]
"scripts/**/*.py" = ["T201"]

[tool.ruff.lint.isort]
known-first-party = ["api"]

[tool.pyright]
typeCheckingMode = "basic"
pythonVersion = "3.14"
include = ["api", "scripts", "tests"]
venvPath = "."
venv = ".venv"
```

**Drop:** `aiohttp`, `sqlalchemy`, `psycopg2-binary`, `ty`, and `pytest`
from `[project].dependencies` (it's in `dev` extras).

### `.devcontainer/devcontainer.json`

Bump base image to `mcr.microsoft.com/devcontainers/python:1-3.14-bookworm`.

### `api/models/entry.py`

- Drop stale `# TODO` comments on `Entry` class.
- Drop `| None` on `Entry.created_at` / `Entry.updated_at`.
- **Ship `EntryCreate` as a stub** with plain `str` fields and a TODO
  pointing at `Annotated[str, StringConstraints(...)]`. Do NOT ship the
  reference implementation.
- **Ship `EntryUpdate` as a TODO** — the learner creates it from scratch.

Reference implementation (used only to verify tests pass; not merged):

```python
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

JournalText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=256,
    ),
]


class EntryCreate(BaseModel):
    work: JournalText
    struggle: JournalText
    intention: JournalText


class EntryUpdate(BaseModel):
    work: JournalText | None = None
    struggle: JournalText | None = None
    intention: JournalText | None = None
```

### `api/routers/journal_router.py`

- `create_entry`: remove `try/except Exception → 400`; add `status_code=201`.
- `update_entry`: replace `entry_update: dict` with `entry_update: EntryUpdate`
  (ships as stub — learner wires `EntryUpdate` in as part of Task 3).
- `analyze_entry`: add `response_model=AnalysisResponse` and
  `from api.models.entry import AnalysisResponse` to imports.

### `api/services/entry_service.py`

No change — service already owns `updated_at`.

### `api/repositories/postgres_repository.py`

Delete the `updated_at = datetime.now(UTC)` line in `update_entry` (B3).
Service layer owns the timestamp.

### `api/main.py`

Ships as a stub with the logging TODO. The `load_dotenv` call must stay
before the router import; add an explanatory comment (B15).

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

from fastapi import FastAPI  # noqa: E402

from api.routers.journal_router import router as journal_router  # noqa: E402

app = FastAPI(
    title="Journal API",
    description="A simple journal API for tracking daily work, struggles, and intentions",
)
app.include_router(journal_router)
```

### `api/services/llm_service.py` (stub)

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
                "entry_id":  str,
                "sentiment": str,   # "positive" | "negative" | "neutral"
                "summary":   str,
                "topics":    list[str],
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

---

## Test suite changes

### `tests/conftest.py`

Register the `no_db` marker, make `cleanup_database` opt-out, keep all
Postgres imports lazy.

```python
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from api.main import app


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "no_db: test does not require a database connection",
    )


@pytest.fixture(autouse=True)
async def cleanup_database(request):
    if "no_db" in request.keywords:
        yield
        return
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
    return response.json()["entry"]
```

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

### `tests/test_logging.py` (new)

```python
"""Tests for Task 1: logging configuration in api.main."""
import logging

import pytest

pytestmark = pytest.mark.no_db


def test_root_logger_is_configured_at_info():
    import api.main  # noqa: F401

    root = logging.getLogger()
    assert root.level != 0 and root.level <= logging.INFO, (
        "Root logger should be configured at INFO (or finer). "
        "Did you call logging.basicConfig() in api/main.py?"
    )


def test_root_logger_has_handler():
    import api.main  # noqa: F401

    root = logging.getLogger()
    assert len(root.handlers) >= 1, (
        "Root logger should have at least one handler."
    )


def test_journal_logger_propagates():
    import api.main  # noqa: F401

    journal_logger = logging.getLogger("journal")
    assert journal_logger.propagate is True
```

### `tests/test_models.py` changes

- Add `pytestmark = pytest.mark.no_db` at top of file.
- Delete `test_entry_create_empty_strings_allowed` (B10).
- Add `TestEntryCreateValidation`:
  - `test_empty_string_rejected`
  - `test_whitespace_only_rejected`
  - `test_whitespace_stripped_from_valid_input`
- Add `TestEntryUpdateModel`:
  - `test_all_fields_optional`
  - `test_partial_update`
  - `test_oversize_field_rejected`

`EntryUpdate` imports must be inside each test so collection doesn't
fail on fresh forks before the learner creates the model.

### `tests/test_api.py` changes

- `test_create_entry_success`: accept `status_code in (200, 201)`.
- `TestAnalyzeEntry` `@patch` target stays
  `api.routers.journal_router.analyze_journal_entry` (import already
  present after earlier fix).
- Add under `TestUpdateEntry`:
  - `test_update_rejects_oversize_field` — PATCH with 300-char `work`
    expects 422.
  - `test_update_rejects_empty_string` — PATCH with whitespace-only
    `work` expects 422.

### `tests/test_service.py`

No changes.

### `tests/test_llm_service.py` (new)

```python
"""Tests for Task 4: LLM-powered entry analysis.

Injects a MockAsyncOpenAI client into analyze_journal_entry, following
the pattern used by Azure-Samples/azure-search-openai-demo
(tests/test_mediadescriber.py). The mock captures calls and returns
real openai.types objects, so the student's code path is exercised
exactly as it would be against a real provider — only the network
layer is stubbed.
"""
import json

import pytest
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice
from openai.types.completion_usage import CompletionUsage

from api.models.entry import AnalysisResponse
from api.services.llm_service import analyze_journal_entry

pytestmark = pytest.mark.no_db


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
    client = MockAsyncOpenAI(_make_completion(VALID_ANALYSIS_JSON))

    await analyze_journal_entry("entry-1", SAMPLE_ENTRY_TEXT, client=client)

    assert len(client.create_calls) >= 1, (
        "Expected analyze_journal_entry to call "
        "client.chat.completions.create() at least once."
    )


async def test_analyze_entry_sends_entry_text_in_prompt():
    client = MockAsyncOpenAI(_make_completion(VALID_ANALYSIS_JSON))

    await analyze_journal_entry("entry-1", SAMPLE_ENTRY_TEXT, client=client)

    call = client.create_calls[0]
    assert "messages" in call

    all_content = " ".join(
        msg["content"]
        for msg in call["messages"]
        if isinstance(msg.get("content"), str)
    )
    assert "FastAPI" in all_content


async def test_analyze_entry_returns_valid_analysis_response():
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

---

## `.github/workflows/ci.yml` (new)

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

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

---

## `.pre-commit-config.yaml` (new)

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.14.2  # pin at implementation time
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format
```

README gets a one-liner: `uv run pre-commit install` after cloning.

---

## `scripts/verify_llm.py` (new, optional local helper)

Not a CI gate. Stand-alone script that loads `.env`, builds a sample
entry, calls `analyze_journal_entry` with the real client, prints the
result, and validates against `AnalysisResponse`. Exits non-zero if
`OPENAI_API_KEY` is missing or if the result doesn't validate.

Usage: `uv run python -m scripts.verify_llm`.

---

## README changes

1. Add CI status badge under the title (per Q4).
2. New "Continuous Integration" section explaining the two checks
   (lint, test) and how to run them locally.
3. Rewrite "First-Time Setup" expected-output block to match the new
   fresh-fork baseline (~18 failing tests).
4. Rewrite "Development Tasks" — each task gets an explicit
   acceptance check (see task table above).
5. New "What the automated tests cover" table (tasks 1–4 auto,
   task 5 manual).
6. New "Task 4 setup" subsection — provider table, `.env` setup
   (no GitHub Actions secrets needed).
7. Add `uv run pre-commit install` to "First-Time Setup".

---

## Commit sequence

Ship as one PR, organized into these commits. Each commit leaves the
repo buildable.

1. `docs: add capstone redesign plan`
2. `chore(deps): bump to Python 3.14, curate ruff rules, add pyright, mandate openai SDK`
3. `fix(router): return 201 on create, drop overeager try/except`
4. `fix(models): drop stale TODOs and Entry | None timestamps`
5. `fix(repo): stop overwriting service's updated_at`
6. `refactor(router): wire AnalysisResponse through analyze endpoint`
7. `feat(models): add EntryUpdate and EntryCreate validation stubs`
8. `feat(router): use EntryUpdate on PATCH`
9. `test: split no_db marker and add Task 3 validation tests`
10. `test: add test_logging.py for Task 1`
11. `feat(llm_service): add injectable client parameter stub for Task 4`
12. `test: add test_llm_service.py with MockAsyncOpenAI`
13. `feat: add scripts/verify_llm.py as optional local helper`
14. `chore: add pre-commit config and ruff hooks`
15. `ci: add GitHub Actions workflow with lint and test jobs`
16. `docs: rewrite README task list and add CI section`

---

## Expected red → green behavior

**Upstream `learntocloud/journal-starter` after this PR:**
- `CI / lint` ✅
- `CI / test` ✅

**Fresh fork before any task is done:**
- `CI / lint` ✅
- `CI / test` ❌ — approximately:
  - 3 fails in `tests/test_logging.py` (Task 1)
  - 4 fails in `tests/test_api.py::TestGetSingleEntry` / `TestDeleteEntry` (Task 2a/2b)
  - 6 fails in `tests/test_models.py::TestEntryCreateValidation` + `TestEntryUpdateModel` (Task 3)
  - 2 fails in `tests/test_api.py::TestUpdateEntry` PATCH validation (Task 3)
  - 3 fails in `tests/test_llm_service.py` (Task 4)
  - Total: ~18 failing tests

**Fresh fork after all tasks complete:**
- `CI / lint` ✅
- `CI / test` ✅
- Task 5 verified manually via `az --version` / `aws --version` /
  `gcloud --version` in the rebuilt devcontainer.

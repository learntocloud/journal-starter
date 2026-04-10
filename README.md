# Topic 5: Capstone - Journal API

[![CI](https://github.com/learntocloud/journal-starter/actions/workflows/ci.yml/badge.svg)](https://github.com/learntocloud/journal-starter/actions/workflows/ci.yml)

Welcome to your Python capstone project! You'll be working with a **FastAPI + PostgreSQL** application that helps people track their daily learning journey. This will prepare you for deploying to the cloud in the next phase.

By the end of this capstone, your API should be working locally and ready for cloud deployment.

## ⚠️ Important: This Is a Template Repository

**Do NOT open Pull Requests against this repository (`learntocloud/journal-starter`).**

This repo is a starter template. Your work should happen on **your own fork**:

1. **Fork** this repo to your GitHub account (click the "Fork" button at the top right).
2. **Clone your fork** — not this repo.
3. Do all your work and open PRs on **your fork** (`github.com/YOUR_USERNAME/journal-starter`).

PRs opened against `learntocloud/journal-starter` will be closed without review.

---

## Table of Contents

- [Getting Started](#-getting-started)
- [Development Workflow](#-development-workflow)
- [Continuous Integration](#-continuous-integration)
- [Development Tasks](#-development-tasks)
- [Data Schema](#-data-schema)
- [AI Analysis Guide](#-ai-analysis-guide)
- [Troubleshooting](#-troubleshooting)
- [Extras](#-extras)
- [License](#-license)

## 🚀 Getting Started

### Prerequisites

- Git installed on your machine
- Docker Desktop installed and running
- VS Code with the Dev Containers extension

### 1. Fork and Clone the Repository

Run these commands on your **host machine** (your local terminal, not inside a container):

1. **Fork this repository** to your GitHub account by clicking the "Fork" button at the top right of this page. This creates your own copy of the project under your GitHub account.

   > ⚠️ **Important:** Always clone **your fork**, not this original repository. All your work and Pull Requests should happen on your fork. Do **not** open PRs against the original `learntocloud/journal-starter` repo.

1. **Clone your fork** to your local machine (replace `YOUR_USERNAME` with your actual GitHub username):

   ```bash
   git clone https://github.com/YOUR_USERNAME/journal-starter.git
   ```

   **Verify your remote** points to your fork (not `learntocloud`):
   ```bash
   git remote -v
   # Should show: origin  https://github.com/YOUR_USERNAME/journal-starter.git
   ```

1. **Navigate into the project folder**:

   ```bash
   cd journal-starter
   ```

1. **Open in VS Code**:

   ```bash
   code .
   ```

> 💡 **Enable GitHub Actions on your fork:** Forks have GitHub Actions workflows disabled by default. Go to the **Actions** tab on your fork and click **"I understand my workflows, go ahead and enable them"** to activate CI.

### 2. Configure Your Environment (.env)

Environment variables live in a `.env` file (which is **git-ignored** so you don't accidentally commit secrets). This repo ships with a template named `.env-sample`.

Copy the sample file to create your real `.env`. Run this from the **project root on your host machine**:

```bash
cp .env-sample .env
```

The sample already contains `DATABASE_URL` (pointing at the devcontainer's
Postgres service) and a placeholder for `OPENAI_API_KEY`. Leave the
placeholder in place for Tasks 1–3; you'll replace it with a real token
from your chosen LLM provider when you reach [Task 4](#task-4--ai-powered-entry-analysis).

> **Why is the placeholder needed?** The app uses [`pydantic-settings`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
> to validate configuration at startup. If `OPENAI_API_KEY` is missing
> entirely, `Settings()` raises a `ValidationError` before FastAPI boots.
> Any non-empty string satisfies that validation — tests never call a real
> LLM because Task 4 is exercised with an injected mock client.

### 3. Set Up Your Development Environment

1. **Install the Dev Containers extension** in VS Code (if not already installed)
2. **Reopen in container**: When VS Code detects the `.devcontainer` folder, click "Reopen in Container"
   - Or use Command Palette (`Cmd/Ctrl + Shift + P`): `Dev Containers: Reopen in Container`
3. **Wait for setup**: The API container will automatically install Python, dependencies, and configure your environment.
   The PostgreSQL Database container will also automatically be created.

### 4. Verify the PostgreSQL Database Is Running

In a terminal on your **host machine** (not inside VS Code), run:

```bash
docker ps
```

You should see the postgres service running.

### 5. Run the API

In the **VS Code terminal** (inside the dev container), verify you're in the **project root**:

```bash
pwd
# Should output: /workspaces/journal-starter (or similar)
```

Then start the API from the **project root**:

```bash
./start.sh
```

### 6. Test Everything Works! 🎉

1. **Visit the API docs**: http://localhost:8000/docs
1. **Create your first entry** In the Docs UI Use the POST `/entries` endpoint to create a new journal entry.
1. **View your entries** using the GET `/entries` endpoint to see what you've created!

**🎯 Once you can create and see entries, you're ready to start the development tasks!**

## 🔄 Development Workflow

This project comes with several features **already built** for you — creating entries, listing entries, updating, and deleting all entries. The remaining features are left for you to implement.

We have provided tests so you can verify your implementations are correct without manual testing. **When you first run the tests, some will pass (for the pre-built features) and some will fail (for the features you need to build).** Your goal is to make all tests pass.

> 📍 **Where to run commands:** All commands in this section should be run from the **project root** in the **VS Code terminal** (inside the dev container). Do **not** `cd` into subdirectories like `api/` or `tests/` — run everything from the top-level project folder.

### First-Time Setup

From the **project root** in the VS Code terminal, install dev dependencies:

```bash
uv sync --all-extras
```

Install the pre-commit hooks so ruff runs automatically on every commit:

```bash
uv run pre-commit install
```

Then run the tests to see the starting state:

```bash
uv run pytest
```

You should see output with **18 failing** tests — one group per task you
still have to complete:

```
FAILED tests/test_logging.py::test_root_logger_is_configured_at_info
FAILED tests/test_logging.py::test_api_main_installs_stream_handler_with_formatter
FAILED tests/test_logging.py::test_api_main_emits_startup_log
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
FAILED tests/test_llm_service.py::test_analyze_entry_actually_calls_llm
FAILED tests/test_llm_service.py::test_analyze_entry_sends_entry_text_in_prompt
FAILED tests/test_llm_service.py::test_analyze_entry_returns_valid_analysis_response
===================== 18 failed, 32 passed =====================
```

The passing tests cover features that are **already built** for you
(creating entries, listing entries, updating, deleting all entries).
The 18 failing tests correspond to Tasks 1–4 below — your job is to
turn all of them green.

### For Each Task

1. **Create a branch**

   [Branches](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-branches) let you work on features in isolation without affecting the main codebase. From the **project root**, create one for each task:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Implement the feature**

   Write your code in the `api/` directory. Check the TODO comments in the files for guidance on what to implement.

3. **Run the tests**

   After implementing a feature, run the tests from the **project root** to check if your implementation is correct:
   ```bash
   uv run pytest
   ```
   [pytest](https://docs.pytest.org/) is a testing framework that runs automated tests to verify your code works as expected.

   - **Tests failing?** Read the error messages — they tell you exactly what's wrong (e.g., `assert 501 == 200` means your endpoint is still returning "Not Implemented").
   - **Tests passing?** Great, your implementation is correct! Move on to the next step.

   **Example: Before implementing GET /entries/{entry_id}:**
   ```
   FAILED tests/test_api.py::TestGetSingleEntry::test_get_entry_by_id_success - assert 501 == 200
   FAILED tests/test_api.py::TestGetSingleEntry::test_get_entry_not_found - assert 501 == 404
   ```

   **After implementing it correctly:**
   ```
   tests/test_api.py::TestGetSingleEntry::test_get_entry_by_id_success PASSED
   tests/test_api.py::TestGetSingleEntry::test_get_entry_not_found PASSED
   ```

   > 💡 **Tip:** Use `uv run pytest -v` for verbose output to see each test's pass/fail status, or `uv run pytest -v --tb=short` to also see concise error details.

   **Run the linter** from the **project root** to check code style and catch common mistakes:
   ```bash
   uv run ruff check .
   ```
   A linter is a tool that analyzes your code for potential errors, bugs, and style issues without running it. [Ruff](https://docs.astral.sh/ruff/) is a fast Python linter that checks for things like unused imports, incorrect syntax, and code that doesn't follow [Python style conventions (PEP 8)](https://pep8.org/).

   **Run the formatter** to auto-format your code (CI also checks formatting):
   ```bash
   uv run ruff format .
   ```

   > 💡 **Tip:** If you ran `uv run pre-commit install` earlier, both `ruff check` and `ruff format` run automatically on every commit.

   **Run the type checker** from the **project root** to ensure proper type annotations:
   ```bash
   uv run pyright
   ```
   A type checker verifies that your code uses [type hints](https://docs.python.org/3/library/typing.html) correctly. Type hints (like `def get_entry(entry_id: str) -> dict:`) help catch bugs early by ensuring you're passing the right types of data to functions. [Pyright](https://github.com/microsoft/pyright) is Microsoft's fast Python type checker.

4. **Commit and push** (only after tests pass!)

   Once the tests for your feature are passing, [commit](https://docs.github.com/en/get-started/using-git/about-commits) your changes and push to GitHub. Run from the **project root**:

   ```bash
   git add .
   ```

   ```bash
   git commit -m "Implement feature X"
   ```

   ```bash
   git push -u origin feature/your-feature-name
   ```

5. **Create a Pull Request (on your fork)**

   Go to **your fork** on GitHub (`github.com/YOUR_USERNAME/journal-starter`) and open a [Pull Request (PR)](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) to merge your feature branch into **your own** `main` branch.

   > ⚠️ **Do NOT open PRs against the original `learntocloud/journal-starter` repository.** Your PR should merge into your fork's `main` branch. When creating the PR, make sure the "base repository" is `YOUR_USERNAME/journal-starter`, not `learntocloud/journal-starter`.

   Example:

   ![Core Base Repository Selection](docs/pr_example.png)

> ⚠️ Do not modify the test files. Make the tests pass by implementing features in the `api/` directory. If a test is failing, it means there's something left to implement — read the error message for clues!

## 🤖 Continuous Integration

Every push and pull request runs the GitHub Actions workflow in
`.github/workflows/ci.yml`, which has two jobs:

| Job  | What it checks | How to reproduce locally |
|------|----------------|--------------------------|
| `lint` | `ruff check`, `ruff format --check`, `pyright` | `uv run ruff check . && uv run ruff format --check . && uv run pyright` |
| `test` | `pytest -v` against a real Postgres 16 service container, with `database_setup.sql` applied | `uv run pytest -v` |

Both jobs run on every push to `main` and every PR. Your fork will
show two green checks on a PR once **all** your implementations are complete
(i.e., Tasks 1–4 are finished). Intermediate PRs that cover only some
tasks will still have failing tests in CI — that's expected.
No secrets are required — the `test` job uses a disposable Postgres
service container, and Task 4 is exercised entirely with an injected
mock OpenAI client so CI never calls a real LLM.

## 🎯 Development Tasks

Each task below has a single acceptance check: the listed tests must
pass (or the listed manual command must succeed for Task 5).

### Task 1 — Logging Setup

- Branch: `feature/logging-setup`
- Edit: `api/main.py`
- Acceptance: `uv run pytest tests/test_logging.py` passes

Configure `logging.basicConfig()` in `api/main.py` so the root logger
ends up at INFO with at least one handler attached. The `journal`
logger used throughout the service layer must continue to propagate.

### Task 2a — GET Single Entry Endpoint

- Branch: `feature/get-single-entry`
- Edit: `api/routers/journal_router.py`
- Acceptance: `uv run pytest tests/test_api.py::TestGetSingleEntry` passes

Implement **GET /entries/{entry_id}** to fetch an entry via
`entry_service.get_entry(entry_id)` and return 404 when not found.

### Task 2b — DELETE Single Entry Endpoint

- Branch: `feature/delete-entry`
- Edit: `api/routers/journal_router.py`
- Acceptance: `uv run pytest tests/test_api.py::TestDeleteEntry` passes

Implement **DELETE /entries/{entry_id}**, returning 404 when the entry
does not exist.

### Task 3 — Input Validation

- Branch: `feature/input-validation`
- Edit: `api/models/entry.py`, `api/routers/journal_router.py`
- Acceptance:
  - `uv run pytest tests/test_models.py::TestEntryCreateValidation` passes
  - `uv run pytest tests/test_models.py::TestEntryUpdateModel` passes
  - `uv run pytest tests/test_api.py::TestUpdateEntry::test_update_rejects_oversize_field` passes
  - `uv run pytest tests/test_api.py::TestUpdateEntry::test_update_rejects_empty_string` passes

Add validation to `EntryCreate` so empty, whitespace-only, and
oversize (>256 char) fields are rejected and surrounding whitespace is
stripped. Hint: `Annotated[str, StringConstraints(...)]` from Pydantic.

Then create an `EntryUpdate` model in the same file with all three
fields optional and the same validation rules, and wire it into the
PATCH endpoint in `api/routers/journal_router.py`.

### Task 4 — AI-Powered Entry Analysis

- Branch: `feature/ai-analysis`
- Edit: `api/services/llm_service.py`
- Acceptance: `uv run pytest tests/test_llm_service.py` passes

The **POST /entries/{entry_id}/analyze** endpoint in
`api/routers/journal_router.py` is already wired up — it fetches the
entry, combines the fields into prompt text, calls
`analyze_journal_entry()`, and maps errors to appropriate HTTP responses.
Your job is to implement the LLM call itself in
`api/services/llm_service.py`.

See [AI Analysis Guide](#-ai-analysis-guide) below for the expected
response format and LLM provider setup.

### Task 5 — Cloud CLI Setup (manual)

- Branch: `feature/cloud-cli-setup`
- Edit: `.devcontainer/devcontainer.json`
- Acceptance: `az --version` / `aws --version` / `gcloud --version`
  runs successfully in the rebuilt devcontainer

Uncomment exactly one of the cloud CLI features in
`.devcontainer/devcontainer.json`, rebuild the devcontainer, and
verify the CLI is installed.

### What the automated tests cover

| Task | Automated? | How the tests verify it |
|------|------------|-------------------------|
| 1 — Logging | ✅ | `tests/test_logging.py` inspects the root logger state after importing `api.main` |
| 2a — GET single | ✅ | `tests/test_api.py::TestGetSingleEntry` via the FastAPI test client |
| 2b — DELETE single | ✅ | `tests/test_api.py::TestDeleteEntry` via the FastAPI test client |
| 3 — Input validation | ✅ | `tests/test_models.py` unit tests + `tests/test_api.py::TestUpdateEntry` PATCH validation tests |
| 4 — AI analysis | ✅ | `tests/test_llm_service.py` injects `MockAsyncOpenAI`; no real network calls |
| 5 — Cloud CLI | ❌ | Manual verification: run `az --version` / `aws --version` / `gcloud --version` in the rebuilt devcontainer |

## 📊 Data Schema

Each journal entry follows this structure:

| Field       | Type      | Description                                | Validation                   |
|-------------|-----------|--------------------------------------------|------------------------------|
| id          | string    | Unique identifier (UUID)                   | Auto-generated               |
| work        | string    | What did you work on today?                | Required, max 256 characters |
| struggle    | string    | What's one thing you struggled with today? | Required, max 256 characters |
| intention   | string    | What will you study/work on tomorrow?      | Required, max 256 characters |
| created_at  | datetime  | When entry was created                     | Auto-generated UTC           |
| updated_at  | datetime  | When entry was last updated                | Auto-updated UTC             |

## 🤖 AI Analysis Guide

For **Task 4: AI-Powered Entry Analysis**, your endpoint should return this format:

```json
{
  "entry_id": "123e4567-e89b-12d3-a456-426614174000",
  "sentiment": "positive",
  "summary": "The learner made progress with FastAPI and database integration. They're excited to continue learning about cloud deployment.",
  "topics": ["FastAPI", "PostgreSQL", "API development", "cloud deployment"],
  "created_at": "2025-12-25T10:30:00Z"
}
```

### Task 4 setup

This project mandates the [OpenAI Python SDK](https://github.com/openai/openai-python),
which works as a drop-in client for any OpenAI-compatible provider:

| Provider | Cost | Notes |
|----------|------|-------|
| **GitHub Models** (default, recommended) | Free | Uses your GitHub account, no credit card needed |
| OpenAI proper | Paid | Standard api.openai.com |
| Azure OpenAI | Paid | Your Azure subscription |
| Groq / Together / OpenRouter / Fireworks / DeepInfra | Varies | All expose OpenAI-compatible endpoints |
| Ollama / LM Studio / vLLM | Free (local) | Run a model on your own machine |

Configure your provider via `.env` — **no GitHub Actions secrets are
required**, because CI uses an injected mock OpenAI client:

```
OPENAI_API_KEY=<your token or api key>
OPENAI_BASE_URL=https://models.inference.ai.azure.com
OPENAI_MODEL=gpt-4o-mini
```

These variables are loaded by [`api/config.py`](api/config.py)'s `Settings`
class. If you mistype a variable name, `Settings()` will raise a
`ValidationError` at app startup naming the missing field — no silent
`None` from `os.getenv` that crashes later.

Optional: once your implementation compiles, sanity-check it against
a real provider with the bundled helper script:

```bash
uv run python -m scripts.verify_llm
```

> **Phase 4 preview:** In Phase 4, you'll migrate this same code to a
> cloud AI platform (Azure OpenAI, AWS Bedrock, or GCP Vertex AI).
> Since they all support the OpenAI SDK, the migration is just an
> environment variable change — no code rewrite needed.
## 🔧 Troubleshooting

**API won't start?**
- Make sure you're running `./start.sh` from the **project root** inside the dev container
- Check PostgreSQL is running: `docker ps` (on your **host machine**)
- Restart the database: `docker restart your-postgres-container-name` (on your **host machine**)

**`pydantic_core._pydantic_core.ValidationError` on startup?**
- One of the required env vars in your `.env` file is missing or mistyped.
  The error message names the field (e.g. `database_url` or `openai_api_key`).
  Add it to `.env` — the defaults in [`.env-sample`](.env-sample) are a good
  starting point — and restart.

**Can't connect to database?**
- Verify `.env` file exists with correct `DATABASE_URL`
- Restart dev container: `Dev Containers: Rebuild Container`

**Dev container won't open?**
- Ensure Docker Desktop is running
- Try: `Dev Containers: Rebuild and Reopen in Container`

## 📚 Extras

- [Explore Your Database](docs/explore-database.md) - Connect to PostgreSQL and run queries directly

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

Contributions welcome! [Open an issue](https://github.com/learntocloud/journal-starter/issues) to get started.

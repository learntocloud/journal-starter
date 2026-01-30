# Topic 5: Capstone - Journal API

Welcome to your Python capstone project! You'll be working with a **FastAPI + PostgreSQL** application that helps people track their daily learning journey. This will prepare you for deploying to the cloud in the next phase.

By the end of this capstone, your API should be working locally and ready for cloud deployment.

## Table of Contents

- [Getting Started](#-getting-started)
- [Development Workflow](#-development-workflow)
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

1. **Fork this repository** to your GitHub account by clicking the "Fork" button
1. **Clone your fork** to your local machine:

   ```bash
   git clone https://github.com/YOUR_USERNAME/journal-starter.git
   cd journal-starter
   ```

1. **Open in VS Code**:

   ```bash
   code .
   ```

### 2. Configure Your Environment (.env)

Environment variables live in a `.env` file (which is **git-ignored** so you don't accidentally commit secrets). This repo ships with a template named `.env-sample`.

Copy the sample file to create your real `.env` (run from project root):

```bash
cp .env-sample .env
```

### 3. Set Up Your Development Environment

1. **Install the Dev Containers extension** in VS Code (if not already installed)
2. **Reopen in container**: When VS Code detects the `.devcontainer` folder, click "Reopen in Container"
   - Or use Command Palette (`Cmd/Ctrl + Shift + P`): `Dev Containers: Reopen in Container`
3. **Wait for setup**: The API container will automatically install Python, dependencies, and configure your environment.
   The PostgreSQL Database container will also automatically be created.

### 4. Verify the PostgreSQL Database Is Running

In a terminal **outside of VS Code** (on your host machine), run:

```bash
docker ps
```

You should see the postgres service running.

### 5. Run the API

In the **VS Code terminal** (inside the dev container), verify you're in the project root:

```bash
pwd
# Should output: /workspaces/journal-starter (or similar)
```

Then start the API:

```bash
./start.sh
```

### 6. Test Everything Works! 🎉

1. **Visit the API docs**: http://localhost:8000/docs
1. **Create your first entry** In the Docs UI Use the POST `/entries` endpoint to create a new journal entry.
1. **View your entries** using the GET `/entries` endpoint to see what you've created!

**🎯 Once you can create and see entries, you're ready to start the development tasks!**

## 🔄 Development Workflow

We have provided tests so you can verify your implementations are correct without manual testing. As you implement each feature, the tests will tell you if your code works as expected.

All commands in this section should be run from the **project root** in the VS Code terminal (inside the dev container).

### First-Time Setup

Install dev dependencies before running tests for the first time:

```bash
uv sync --all-extras
```

### For Each Task

1. **Create a branch**

   [Branches](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-branches) let you work on features in isolation without affecting the main codebase. Create one for each task:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Implement the feature**

   Write your code in the `api/` directory. Check the TODO comments in the files for guidance on what to implement.

3. **Verify your work**

   **Run the tests** to check your implementation is correct:
   ```bash
   uv run pytest
   ```
   [pytest](https://docs.pytest.org/) is a testing framework that runs automated tests to verify your code works as expected. Tests will be skipped for features you haven't implemented yet. As you complete tasks, skipped tests will start passing.

   **Run the linter** to check code style and catch common mistakes:
   ```bash
   uv run ruff check api/
   ```
   A linter is a tool that analyzes your code for potential errors, bugs, and style issues without running it. [Ruff](https://docs.astral.sh/ruff/) is a fast Python linter that checks for things like unused imports, incorrect syntax, and code that doesn't follow [Python style conventions (PEP 8)](https://pep8.org/).

   **Run the type checker** to ensure proper type annotations:
   ```bash
   uv run ty check api/
   ```
   A type checker verifies that your code uses [type hints](https://docs.python.org/3/library/typing.html) correctly. Type hints (like `def get_entry(entry_id: str) -> dict:`) help catch bugs early by ensuring you're passing the right types of data to functions. [ty](https://github.com/astral-sh/ty) is a fast Python type checker.

4. **Commit and push**

   [Committing](https://docs.github.com/en/get-started/using-git/about-commits) saves your changes to Git. Pushing uploads them to GitHub so you can create a Pull Request:
   ```bash
   git add .
   git commit -m "Implement feature X"
   git push -u origin feature/your-feature-name
   ```

5. **Create a Pull Request**

   On GitHub, open a [Pull Request (PR)](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) to merge your feature branch into `main`. This is where code review happens. Once approved, merge the PR.

> ⚠️ Do not modify the test files. Make the tests pass by implementing features in the `api/` directory.

## 🎯 Development Tasks

### 1. Logging Setup

- Branch: `feature/logging-setup`
- [ ] Configure logging in `api/main.py`

### 2. API Implementation

#### Task 2a: GET Single Entry Endpoint

- Branch: `feature/get-single-entry`
- [ ] Implement **GET /entries/{entry_id}** in `api/routers/journal_router.py`

#### Task 2b: DELETE Single Entry Endpoint

- Branch: `feature/delete-entry`
- [ ] Implement **DELETE /entries/{entry_id}** in `api/routers/journal_router.py`

### 3. AI-Powered Entry Analysis

- Branch: `feature/ai-analysis`
- [ ] Implement `analyze_journal_entry()` in `api/services/llm_service.py`
- [ ] Implement **POST /entries/{entry_id}/analyze** in `api/routers/journal_router.py`

This endpoint should return sentiment, a 2-sentence summary, and 2-4 key topics. See [AI Analysis Guide](#-ai-analysis-guide) below for details on the expected response format and LLM provider setup.

### 4. Data Model Improvements (Optional)

- Branch: `feature/data-model-improvements`  
- [ ] Add validators to `api/models/entry.py`

### 5. Cloud CLI Setup (Required for Deployment)

- Branch: `feature/cloud-cli-setup`
- [ ] Uncomment one CLI tool in `.devcontainer/devcontainer.json`

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

For **Task 3: AI-Powered Entry Analysis**, your endpoint should return this format:

```json
{
  "entry_id": "123e4567-e89b-12d3-a456-426614174000",
  "sentiment": "positive",
  "summary": "The learner made progress with FastAPI and database integration. They're excited to continue learning about cloud deployment.",
  "topics": ["FastAPI", "PostgreSQL", "API development", "cloud deployment"],
  "created_at": "2025-12-25T10:30:00Z"
}
```

**LLM Provider Setup:**

1. Choose a provider and read their docs: [OpenAI](https://platform.openai.com/docs) | [Anthropic](https://docs.anthropic.com) | [Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/) | [AWS Bedrock](https://docs.aws.amazon.com/bedrock/) | [GCP Vertex AI](https://cloud.google.com/vertex-ai/docs)
2. Add required environment variables to your `.env` file
3. Add your SDK to `pyproject.toml` and run `uv sync`

## 🔧 Troubleshooting

**API won't start?**
- Check PostgreSQL is running: `docker ps` (on host machine)
- Restart the database: `docker restart your-postgres-container-name`

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

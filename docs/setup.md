# Getting Started

[README](../README.md) > Setup > [Development workflow](workflow.md) > [Tasks](tasks.md)

Follow this guide from a fresh fork to a running API. If something fails, use
the [troubleshooting guide](troubleshooting.md) before continuing.

## Prerequisites

See the [prerequisites in the README](../README.md#prerequisites).

## 1. Fork and Clone the Repository

Run these commands on your **host machine** (your local terminal, not inside a
container).

1. **Fork this repository** to your GitHub account using the "Fork" button.
2. **Clone your fork**, replacing `YOUR_USERNAME` with your GitHub username:

   ```bash
   git clone https://github.com/YOUR_USERNAME/journal-starter.git &&
   cd journal-starter
   ```

3. **Verify your remote** points to your fork:

   ```bash
   git remote -v
   # Should show: origin  https://github.com/YOUR_USERNAME/journal-starter.git
   ```

4. **Open in VS Code**:

   ```bash
   code .
   ```

> **Work on your own fork.** Do not open PRs against the original
> `learntocloud/journal-starter` repository. Your PRs should target your fork.

Enable GitHub Actions on your fork: go to its **Actions** tab and, if prompted,
click **"I understand my workflows, go ahead and enable them"**.

## 2. Configure Your Environment

Copy the sample file from the **project root on your host machine**:

```bash
cp .env-sample .env
```

The `.env` file is git-ignored. Do not commit it or other secrets.
The sample contains `DATABASE_URL` for the application database,
`TEST_DATABASE_URL` for a separate test database, and placeholders for the three
`OPENAI_*` settings. Leave those placeholders in place for Tasks 1-3; configure
your provider when you reach [Task 4](ai-analysis.md#task-4-setup).

All settings are required because the API validates configuration at startup.
Tests use an injected mock client rather than contacting the placeholder endpoint.
See [settings troubleshooting](troubleshooting.md#missing-or-invalid-settings)
if startup reports a missing field.

## 3. Open the Development Container

1. Install the Dev Containers extension in VS Code if needed.
2. Select **Reopen in Container**, or open the Command Palette
   (`Cmd/Ctrl + Shift + P`) and choose **Dev Containers: Reopen in Container**.
3. Wait for setup. The development container provides Python and uv; a separate
   container runs PostgreSQL. You will install Python dependencies in step 5.

### Where things run

| Location | What it provides |
|----------|------------------|
| Your host machine | VS Code, Git, and Docker Desktop; run Docker commands here |
| Development container | Python, uv, the API, tests, and your chosen cloud CLI; use the VS Code terminal here |
| PostgreSQL container | The `career_journal` application database and separate `career_journal_test` database |
| Named Docker volume (`postgres_data`) | Database files that survive container restarts and rebuilds |

The repository, including `.env`, is mounted at `/workspaces` in the development
container. Application and test settings read that file from the project root.
PostgreSQL receives initialization settings through Compose's `env_file`;
the development container deliberately does not. Explicitly exported
environment variables still override `.env`, as they do in cloud deployments.

Compose waits for PostgreSQL to be healthy before starting the development
container. The API creates one shared connection pool per server process at
startup and closes it at shutdown. Invalid settings or an unreachable database
prevent startup rather than failing on the first request.

> **Already have a devcontainer or database volume?** Follow
> [the existing-devcontainer upgrade instructions](troubleshooting.md#upgrading-an-existing-devcontainer).
> Rebuilding preserves the volume and does not rerun database initialization.
> Do not delete the volume to troubleshoot: it contains your journal entries.

## 4. Verify PostgreSQL Is Running

In a terminal on your **host machine**, run:

```bash
docker ps
```

You should see the PostgreSQL service running.

## 5. Run the API

In the **VS Code terminal inside the development container**, verify you are
in the **project root**:

```bash
pwd
# Should output: /workspaces
```

Install the project dependencies, including the default `dev` group of testing
and code-quality tools:

```bash
uv sync
```

Then start the API:

```bash
uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

| Part of the command | Meaning |
|---------------------|---------|
| `uv run uvicorn` | Run Uvicorn in the project's Python environment; uv also keeps required dependencies synchronized |
| `api.main:app` | Import the `app` object from `api/main.py` |
| `--reload` | Restart automatically when Python code changes; for development, not production |
| `--host 0.0.0.0` | Listen on all container network interfaces so the API is reachable through the forwarded port |
| `--port 8000` | Listen on port 8000, forwarded to your host by the devcontainer |

This application has no authentication or per-user isolation. Keep it in a
controlled learning environment; do not expose the API publicly.

Leave this terminal running while using the API. Use another VS Code terminal
for tests and other commands. Stop the server with `Ctrl+C` and run the same
command to restart it. For configuration changes, follow
[Restarting versus rebuilding](troubleshooting.md#restarting-versus-rebuilding).

## 6. Create and View an Entry

1. Visit the API docs at http://localhost:8000/docs.
2. Use **POST `/entries`** to create a journal entry.
3. Use **GET `/entries`** to see your entry.

Once you can create and see entries, continue to the
[development workflow](workflow.md) to prepare your tools and begin the tasks.

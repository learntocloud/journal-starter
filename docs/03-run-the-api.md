# Chapter 3: Run the API

[Home](../README.md) · **Chapter 3 of 10**

Run every command in this chapter from the **project root inside the
devcontainer**.

## 1. Install the Project

```bash
uv sync
uv run pre-commit install
```

`uv sync` installs the application and development dependencies. The pre-commit
hook runs Ruff when you commit.

In VS Code, run **Python: Select Interpreter** from the Command Palette and
choose `.venv/bin/python`. If it is not listed, choose **Enter interpreter path**
and enter `/workspaces/.venv/bin/python`. This makes editor tests and debugging
use the same project dependencies as `uv run`.

## 2. Check the Starter

Run the tests for functionality that is already supplied:

```bash
uv run pytest -m 'not exercise'
```

These tests should pass. The full suite intentionally includes unfinished
exercise tests and will fail until you complete the capstone.

Tests use `TEST_DATABASE_URL` and erase data in the dedicated test database.
The running API uses `DATABASE_URL`, so its entries are preserved. Never put
personal data in either database.
Run database-backed tests serially; concurrent runs need separate dedicated
test databases. See [test database safety](reference/testing-and-ci.md#test-database-safety)
for the safeguards and cleanup behavior.

## 3. Start the API

```bash
uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Leave this terminal running. Open another VS Code terminal for later commands.
Stop the API with `Ctrl+C`.

This API has no authentication. Keep it in the local learning environment.

## 4. Create Your First Entry

1. Open <http://localhost:8000/docs>.
2. Use **POST `/entries`** to create a made-up entry.
3. Use **GET `/entries`** to confirm it was saved.

Use synthetic content that you would be comfortable sending to an AI provider
later in the capstone.

## Before You Continue

You should now have:

- A passing starter-safeguards test run
- A running API
- One synthetic journal entry visible through GET `/entries`

---

[← Previous: Project setup](02-project-setup.md) ·
[Next: Build GET for one entry →](04-get-entry.md)

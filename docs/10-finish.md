# Chapter 10: Finish the Capstone

[Home](../README.md) · **Chapter 10 of 10**

Confirm the complete project and required environment checks.

## 1. Run the Full Test Suite

From your updated `main` branch:

```bash
git checkout main &&
git pull --ff-only origin main &&
uv run pytest
```

All tests should now pass. Do not change supplied tests to hide failures.

## 2. Run Code Quality

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
```

## 3. Confirm the Live AI Integration

With your provider settings still in `.env`:

```bash
uv run python -m scripts.verify_llm
```

This sends only the bundled synthetic sample.

## 4. Confirm the Cloud CLI

Run the command for the CLI you added in [Chapter 2](02-project-setup.md):

```bash
az --version
# or: aws --version
# or: gcloud --version
```

No cloud login or deployment is required.

## Completion Checklist

- All exercise pull requests were merged into your fork's `main`
- The input-validation PR explains the partial update observed in the debugger
- The full test suite passes
- Ruff and Pyright pass
- Live AI verification succeeds
- One cloud CLI runs inside the devcontainer
- `.env` and provider credentials were not committed

You have completed the Phase 3 Journal API capstone and prepared the project for
the next phase's cloud deployment work.

---

[← Previous: AI-powered analysis](09-ai-analysis.md) ·
[Return home](../README.md)

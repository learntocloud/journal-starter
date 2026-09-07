# Chapter 10: Finish the Capstone

[Home](../README.md) · **Chapter 10 of 10**

In this chapter, you will confirm that the complete project works on your merged
`main` branch and that your environment is ready for the next phase.

## 1. Update Your Main Branch

1. Make sure your AI analysis pull request is merged, then check your working tree:

   ```bash
   git status
   ```

   It should be clean before you continue.

2. Switch to `main`:

   ```bash
   git checkout main
   ```

3. Pull the merged changes:

   ```bash
   git pull origin main
   ```

## 2. Run the Full Test Suite

1. Run all tests:

   ```bash
   uv run pytest
   ```

   All tests should now pass, including every exercise.

2. Read the test summary. Resolve any failures before marking the capstone complete.

## 3. Run Code Quality

1. Run Ruff:

   ```bash
   uv run ruff check .
   ```

2. Confirm the code is formatted:

   ```bash
   uv run ruff format --check .
   ```

3. Run Pyright:

   ```bash
   uv run pyright
   ```

## 4. Confirm the Live AI Integration

1. With your provider settings still in `.env`, run:

   ```bash
   uv run python -m scripts.verify_llm
   ```

2. Confirm that the output includes `Validated AnalysisResponse:` and the
   bundled sample's analysis.

## 5. Confirm the Cloud CLI

Run only the step for the CLI you installed:

1. If you installed the Azure CLI, run:

   ```bash
   az --version
   ```

2. If you installed the AWS CLI, run:

   ```bash
   aws --version
   ```

3. If you installed the Google Cloud CLI, run:

   ```bash
   gcloud --version
   ```

Your selected command should print version information. No cloud login or
deployment is required.

## Completion Checklist

- All exercise pull requests are merged into your fork's `main`.
- The input-validation pull request explains the partial update observed in the debugger.
- The logging pull request includes a log sample and your observations.
- The AI analysis pull request includes successful live verification.
- The full test suite passes.
- Ruff and Pyright pass.
- Live AI verification succeeds on the merged code.
- One cloud CLI runs inside the development container.
- `.env` and provider credentials were not committed.

Once all items are complete, you have finished the Phase 3 Journal API capstone
and prepared the project for the next phase's cloud deployment work.

---

[← Previous: AI-powered analysis](09-ai-analysis.md) ·
[Return home](../README.md)

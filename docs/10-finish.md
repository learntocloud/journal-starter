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

## 6. Update Your CI Badge

The CI badge in `README.md` currently reports the upstream starter's status.
Point it to your fork so visitors see the status of your own `main` branch.

1. Create a branch from your updated `main`:

   ```bash
   git checkout -b docs/ci-badge
   ```

2. Open `README.md` and replace the CI badge line with:

   ```markdown
   [![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/OWNER/REPO/actions/workflows/ci.yml)
   ```

   Replace `OWNER/REPO` in **both URLs** with your GitHub username or organization
   and repository name, such as `Your_Username/journal-starter`. The
   `?branch=main` parameter keeps the badge focused on your main branch.
   No workflow changes are needed.

3. Review, commit, and push the README change:

   ```bash
   git diff -- README.md
   git add README.md
   git commit -m "Point CI badge to my fork"
   git push -u origin docs/ci-badge
   ```

4. Open a pull request within your fork: select your fork for both the base and
   head repositories, `main` as the base branch, and `docs/ci-badge` as the compare
   branch. Add exactly one task label, `task:setup`, for this documentation change.

5. Open your fork's **Actions** tab and enable workflows if GitHub prompts you.
   Wait for CI to pass, review the pull request, and merge it.

6. After the CI run on `main` finishes, check your fork's README on GitHub.
   Confirm the badge shows your CI status and clicking it opens your fork's
   CI workflow page, not upstream's.

7. Return to `main` and pull the merged change:

   ```bash
   git checkout main
   git pull origin main
   ```

## Completion Checklist

- All exercise pull requests are merged into your fork's `main`.
- The input-validation pull request explains the partial update observed in the debugger.
- The logging pull request includes a log sample and your observations.
- The AI analysis pull request includes successful live verification.
- The full test suite passes.
- Ruff and Pyright pass.
- Live AI verification succeeds on the merged code.
- One cloud CLI runs inside the development container.
- The README CI badge shows your fork's `main` status and links to your workflow.
- `.env` and provider credentials were not committed.

Once all items are complete, you have finished the Phase 3 Journal API capstone
and prepared the project for the next phase's cloud deployment work.

---

[← Previous: AI-powered analysis](09-ai-analysis.md) ·
[Return home](../README.md)

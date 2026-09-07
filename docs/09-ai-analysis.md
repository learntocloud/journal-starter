# Chapter 9: Build AI-Powered Analysis

[Home](../README.md) · **Chapter 9 of 10**

Implement the service behind **POST `/entries/{entry_id}/analyze`**.

## Before You Begin

- Continue on: `feature/ai-analysis`
- PR label: `task:analysis`
- Edit: `api/services/llm_service.py`

The router already fetches the entry, combines its fields, calls
`analyze_journal_entry()`, and maps service failures to safe HTTP responses.

## Response Contract

Return an `AnalysisResponse` containing:

```json
{
  "entry_id": "123e4567-e89b-12d3-a456-426614174000",
  "sentiment": "positive",
  "summary": "The learner made progress with FastAPI. They are ready to continue.",
  "topics": ["FastAPI", "PostgreSQL"],
  "created_at": "2025-12-25T10:30:00Z"
}
```

The model enforces:

- `sentiment`: exactly `positive`, `negative`, or `neutral`
- `summary`: a nonempty trimmed string
- `topics`: 2-4 nonempty trimmed strings

Aim for two summary sentences, but do not implement strict sentence counting.

## 1. Make the Request

Use `client.responses.create()` with:

- The model from `Settings`
- The full journal text
- Separate instructions and user content where possible
- A request for `sentiment`, `summary`, and `topics`
- Structured JSON output

Prefer strict JSON Schema output:

```python
text={
    "format": {
        "type": "json_schema",
        "name": "journal_analysis",
        "strict": True,
        "schema": analysis_schema,
    }
}
```

Require all three generated fields and set `additionalProperties` to `False`.
If your model supports JSON mode but not strict structured output,
`text={"format": {"type": "json_object"}}` is an alternative. Do not use the
Chat Completions `response_format` parameter with the Responses API.

## 2. Parse and Validate

Before returning:

1. Reject incomplete responses, refusals, and empty `output_text` with
   `InvalidAnalysisResponseError`.
2. Parse `output_text` as JSON.
3. Reject arrays, `null`, and scalar values before accessing object fields.
4. Reconstruct the result from only `sentiment`, `summary`, and `topics`.
5. Add the function's `entry_id`; never accept an ID or timestamp from the
   provider.
6. Validate with `AnalysisResponse` and return its dictionary representation.

Do not invent defaults or return a success-shaped response when parsing or
validation fails.

## 3. Manage the Client

`analyze_journal_entry()` accepts an optional `AsyncOpenAI` client.

- Close a client created by the service on success and failure.
- Leave a caller-supplied client open because the caller owns it.
- Use the supplied timeout and retry configuration.

Let JSON, Pydantic, and OpenAI SDK errors reach the router's existing error
mapping. Do not include raw provider messages, journal content, settings, or
credentials in logs or client responses.

## 4. Run the Checks

Run the mocked service tests:

```bash
uv run pytest tests/test_llm_service.py
```

Then verify your real provider with the bundled synthetic sample:

```bash
uv run python -m scripts.verify_llm
```

The live check is required. Passing mocked tests does not confirm that your
credentials, endpoint, model, or structured-output format work together.

Finally, run code quality:

```bash
uv run ruff check .
uv run ruff format .
uv run pyright
```

## Finish the Chapter

```bash
git add .
git commit -m "Implement AI entry analysis"
git push -u origin feature/ai-analysis
```

Then:

1. Open a pull request to your fork's `main`.
2. Add exactly one task label: `task:analysis`.
3. Include the successful live verification in the pull request description.
4. Wait for CI, review the diff, and merge the pull request.

---

[← Previous: AI provider setup](08-ai-setup.md) ·
[Next: Finish the capstone →](10-finish.md)

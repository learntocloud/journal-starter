"""Optional local helper for Task 4.

Runs ``analyze_journal_entry`` against the real OpenAI client configured
via environment variables, prints the result, and validates that it
matches ``AnalysisResponse``.

Usage:
    uv run python -m scripts.verify_llm

This script is NOT part of CI. It exists so learners can sanity-check
their Task 4 implementation against a real LLM provider before wiring
anything into the API.
"""

from __future__ import annotations

import asyncio
import json
import sys

from pydantic import ValidationError

from api.config import get_settings
from api.models.entry import AnalysisResponse
from api.services.llm_service import analyze_journal_entry

SAMPLE_ENTRY_ID = "verify-llm-sample"
SAMPLE_ENTRY_TEXT = (
    "Studied FastAPI and wired up the PATCH endpoint. "
    "Struggled with understanding how async/await interacts with dependency "
    "injection. Tomorrow I'll practice writing PostgreSQL queries directly "
    "against the journal schema."
)


async def main() -> int:
    try:
        get_settings()
    except ValidationError as exc:
        print(
            "ERROR: application settings are invalid. "
            "Check your .env file has OPENAI_API_KEY (and DATABASE_URL) set.\n"
            f"{exc}",
            file=sys.stderr,
        )
        return 1

    print(f"Calling analyze_journal_entry for entry_id={SAMPLE_ENTRY_ID!r}...")
    result = await analyze_journal_entry(SAMPLE_ENTRY_ID, SAMPLE_ENTRY_TEXT)

    print("Raw result:")
    print(json.dumps(result, indent=2, default=str))

    try:
        validated = AnalysisResponse.model_validate(result)
    except Exception as exc:
        print(f"ERROR: result does not validate against AnalysisResponse: {exc}", file=sys.stderr)
        return 2

    print("\nValidated AnalysisResponse:")
    print(f"  entry_id:  {validated.entry_id}")
    print(f"  sentiment: {validated.sentiment}")
    print(f"  summary:   {validated.summary}")
    print(f"  topics:    {validated.topics}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

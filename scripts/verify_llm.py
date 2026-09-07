"""Required local live verification for Task 4.

Runs ``analyze_journal_entry`` against the real OpenAI client configured
via environment variables, prints the result, and validates that it
matches ``AnalysisResponse``.

Usage:
    uv run python -m scripts.verify_llm

This script is not part of CI, which remains mocked and credential-free.
Learners must run it against a supported live LLM provider to complete
Task 4.
"""

from __future__ import annotations

import asyncio
import sys
from json import JSONDecodeError

from openai import OpenAIError
from pydantic import ValidationError

from api.config import get_settings
from api.models.entry import AnalysisResponse
from api.services.llm_service import InvalidAnalysisResponseError, analyze_journal_entry

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
            "Check your .env file has DATABASE_URL, OPENAI_API_KEY, "
            "OPENAI_BASE_URL, and OPENAI_MODEL set.\n"
            f"{exc}",
            file=sys.stderr,
        )
        return 1

    print(f"Calling analyze_journal_entry for entry_id={SAMPLE_ENTRY_ID!r}...")
    try:
        result = await analyze_journal_entry(SAMPLE_ENTRY_ID, SAMPLE_ENTRY_TEXT)
    except NotImplementedError:
        print("ERROR: complete Task 4 in api/services/llm_service.py first.", file=sys.stderr)
        return 3
    except OpenAIError as exc:
        print(f"ERROR: provider request failed ({type(exc).__name__}).", file=sys.stderr)
        return 3
    except (JSONDecodeError, InvalidAnalysisResponseError, ValidationError) as exc:
        print(f"ERROR: provider returned invalid analysis ({type(exc).__name__}).", file=sys.stderr)
        return 2

    try:
        validated = AnalysisResponse.model_validate(result)
    except ValidationError as exc:
        print(f"ERROR: result does not validate against AnalysisResponse: {exc}", file=sys.stderr)
        return 2

    if validated.entry_id != SAMPLE_ENTRY_ID:
        print("ERROR: analysis returned an unexpected entry_id.", file=sys.stderr)
        return 2

    print("\nValidated AnalysisResponse:")
    print(f"  entry_id:  {validated.entry_id}")
    print(f"  sentiment: {validated.sentiment}")
    print(f"  summary:   {validated.summary}")
    print(f"  topics:    {validated.topics}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

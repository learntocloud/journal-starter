"""Chapter 9: Implement journal analysis using the OpenAI Responses API.

This project mandates the OpenAI Python SDK and a provider that supports the
Responses API, such as:
  - Microsoft Foundry Models
  - OpenAI proper

Set OPENAI_API_KEY, OPENAI_BASE_URL, and OPENAI_MODEL in your .env file.
Settings are loaded by ``api.config.Settings``.
"""

import httpx
from openai import AsyncOpenAI

from api.config import get_settings


class InvalidAnalysisResponseError(ValueError):
    """The provider did not return a complete, usable analysis."""


def _default_client() -> AsyncOpenAI:
    """Construct the real OpenAI client from application settings.

    Called lazily from ``analyze_journal_entry`` so tests can inject a
    client with a mocked HTTP transport without triggering this code path.
    """
    settings = get_settings()
    return AsyncOpenAI(
        api_key=settings.openai_api_key.get_secret_value(),
        base_url=settings.openai_base_url,
        timeout=httpx.Timeout(60.0, connect=5.0),
        max_retries=1,
    )


async def analyze_journal_entry(
    entry_id: str,
    entry_text: str,
    client: AsyncOpenAI | None = None,
) -> dict[str, object]:
    """Analyze a journal entry using the OpenAI Responses API.

    Args:
        entry_id: ID of the entry being analyzed (pass through to the result).
        entry_text: Combined work + struggle + intention text.
        client: OpenAI client. If None, a default one is constructed from
            application settings. Tests inject a client with a mocked transport;
            the router calls this with no ``client`` argument. Caller-supplied
            clients are left open for reuse.

    Returns:
        A dict validated by the Pydantic AnalysisResponse class:
            {
                "entry_id":  str,
                "sentiment": str,   # "positive" | "negative" | "neutral"
                "summary":   str,
                "topics":    list[str],
                "created_at": datetime,
            }
        AnalysisResponse generates created_at; the AI does not supply it.

    TODO: Implement AI analysis (Chapter 9).
      1. Define a JSON Schema for sentiment, summary, and topics.
      2. Await client.responses.create() using get_settings().openai_model
         and the full entry_text. Request structured JSON output.
      3. Reject unfinished responses, refusals, and blank output_text with
         InvalidAnalysisResponseError.
      4. Parse output_text with json.loads() and require a dictionary.
      5. Validate only the generated fields plus the supplied entry_id with
         AnalysisResponse. Do not accept provider-generated IDs or timestamps.
      6. Convert the validated model with model_dump(), set request_failed to
         False, and return the dictionary. Let request and validation errors
         propagate rather than returning fallback analysis.

    Replace the NotImplementedError inside try with your implementation.
    Client setup and cleanup are supplied; leave them unchanged. owns_client
    tracks who created the client. request_failed preserves the original error
    if cleanup also fails. See docs/09-ai-analysis.md for examples and checks.
    """
    owns_client = client is None
    if client is None:
        client = _default_client()

    request_failed = True
    try:
        raise NotImplementedError(
            "Chapter 9: implement the request and validation here. "
            "See docs/09-ai-analysis.md for the walkthrough."
        )
    finally:
        if owns_client:
            try:
                await client.close()
            except Exception:
                if not request_failed:
                    raise

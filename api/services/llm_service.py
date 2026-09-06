"""Task 4: Implement analyze_journal_entry using the OpenAI Responses API.

This project mandates the OpenAI Python SDK and a provider that supports the
Responses API, such as:
  - Microsoft Foundry Models
  - OpenAI proper

Set OPENAI_API_KEY, OPENAI_BASE_URL, and OPENAI_MODEL in your .env file.
Settings are loaded by ``api.config.Settings``.
"""

from openai import AsyncOpenAI

from api.config import get_settings


def _default_client() -> AsyncOpenAI:
    """Construct the real OpenAI client from application settings.

    Called lazily from ``analyze_journal_entry`` so tests can inject a
    ``MockAsyncOpenAI`` without ever triggering this code path.
    """
    settings = get_settings()
    return AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )


async def analyze_journal_entry(
    entry_id: str,
    entry_text: str,
    client: AsyncOpenAI | None = None,
) -> dict:
    """Analyze a journal entry using the OpenAI Responses API.

    Args:
        entry_id: ID of the entry being analyzed (pass through to the result).
        entry_text: Combined work + struggle + intention text.
        client: OpenAI client. If None, a default one is constructed from
            application settings. Tests pass in a MockAsyncOpenAI here; production code
            in the router calls this with no ``client`` argument.

    Returns:
        A dict matching AnalysisResponse:
            {
                "entry_id":  str,
                "sentiment": str,   # "positive" | "negative" | "neutral"
                "summary":   str,
                "topics":    list[str],
            }

    TODO (Task 4):
      1. If ``client is None``, call ``_default_client()``. Close clients you
         create when finished; do not close a client supplied by the caller.
      2. Include the full ``entry_text`` in the input and instruct the model to
         return JSON containing sentiment, summary, and topics. Request the
         allowed sentiments, a brief summary (aim for two sentences), and 2-4
         nonempty topics.
      3. Call ``client.responses.create(...)`` with ``get_settings().openai_model``.
         Prefer structured output via ``text={"format": {"type": "json_schema",
         ...}}`` on a supported model. JSON mode is an alternative, but it does
         not enforce your schema. See README.md's "Requesting structured output".
      4. Reject incomplete responses, refusals, or empty output rather than
         inventing a successful analysis. ``output_text`` is a string, not a
         guarantee of JSON; parsing malformed output with ``json.loads()`` must
         fail explicitly. Do not swallow provider or parsing errors.
      5. Add ``entry_id`` from the function argument, not from model output.
         Validate the result with ``AnalysisResponse`` and return its dictionary
         representation. The response model supplies ``created_at``.
    """
    raise NotImplementedError(
        "Task 4: implement analyze_journal_entry using the openai SDK. "
        "See tests/test_llm_service.py for the test contract."
    )

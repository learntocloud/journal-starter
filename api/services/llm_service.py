"""Task 4: Implement analyze_journal_entry using any OpenAI-compatible API.

This project mandates the OpenAI Python SDK, which works with:
  - GitHub Models (default, free, no credit card required)
  - OpenAI proper
  - Azure OpenAI
  - Groq, Together, OpenRouter, Fireworks, DeepInfra
  - Ollama, LM Studio, vLLM (local)
  - Anthropic via their OpenAI-compat endpoint

Set OPENAI_API_KEY, and optionally OPENAI_BASE_URL and OPENAI_MODEL
in your .env file.
"""

import os

from openai import AsyncOpenAI


def _default_client() -> AsyncOpenAI:
    """Construct the real OpenAI client from environment variables.

    Called lazily from analyze_journal_entry so tests can inject a
    MockAsyncOpenAI without ever triggering this code path.
    """
    return AsyncOpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.getenv("OPENAI_BASE_URL", "https://models.inference.ai.azure.com"),
    )


async def analyze_journal_entry(
    entry_id: str,
    entry_text: str,
    client: AsyncOpenAI | None = None,
) -> dict:
    """Analyze a journal entry using an OpenAI-compatible LLM.

    Args:
        entry_id: ID of the entry being analyzed (pass through to the result).
        entry_text: Combined work + struggle + intention text.
        client: OpenAI client. If None, a default one is constructed from
            env vars. Tests pass in a MockAsyncOpenAI here; production code
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
      1. If ``client is None``, call ``_default_client()`` to construct one.
      2. Build a messages list that includes ``entry_text`` somewhere
         (the unit tests check that the entry text reaches the LLM).
      3. Call ``client.chat.completions.create(...)`` with a model from
         OPENAI_MODEL (default "gpt-4o-mini") and your messages.
      4. Parse the assistant's JSON response with ``json.loads()``.
      5. Return a dict with ``entry_id``, ``sentiment``, ``summary``, ``topics``.
    """
    raise NotImplementedError(
        "Task 4: implement analyze_journal_entry using the openai SDK. "
        "See tests/test_llm_service.py for the test contract."
    )

"""Task 4: Implement analyze_journal_entry using any OpenAI-compatible API.

This project mandates the OpenAI Python SDK, which works with:
  - GitHub Models (default, free, no credit card required)
  - OpenAI proper
  - Azure OpenAI
  - Groq, Together, OpenRouter, Fireworks, DeepInfra
  - Ollama, LM Studio, vLLM (local)
  - Anthropic via their OpenAI-compat endpoint

Set OPENAI_API_KEY, and optionally OPENAI_BASE_URL and OPENAI_MODEL
in your .env file. Settings are loaded by ``api.config.Settings``.
"""

import json

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

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
    """Analyze a journal entry using an OpenAI-compatible LLM.

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
      1. If ``client is None``, call ``_default_client()`` to construct one.
      2. Build a messages list that includes ``entry_text`` somewhere
         (the unit tests check that the entry text reaches the LLM).
      3. Call ``client.chat.completions.create(...)`` with a model name
         (use ``get_settings().openai_model`` — defaults to "gpt-4o-mini").
      4. Parse the assistant's JSON response with ``json.loads()``.
      5. Return a dict with ``entry_id``, ``sentiment``, ``summary``, ``topics``.
    """

    if client is None:
        client = _default_client()

    messages: list[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant that analyzes journal entries. "
                "You will receive a journal entry and must return a JSON object "
                "with the following fields: sentiment (one of 'positive', 'negative', 'neutral'), "
                "summary (a brief summary of the entry), and topics (a list of key topics)."
            ),
        },
        {
            "role": "user",
            "content": entry_text,
        },
    ]

    kwargs = {
        "model": get_settings().openai_model,
        "messages": messages,
    }

    # Only inject response_format if using an OpenAI model that supports it
    if "gpt" in get_settings().openai_model:
        kwargs["response_format"] = {"type": "json_object"}

    response = await client.chat.completions.create(**kwargs)

    # The response from the LLM is expected to be a JSON string in the content of the assistant's message.
    assistant_message = response.choices[0].message.content or "{}"

    clean_json = (
        assistant_message.strip()
        .removeprefix("```json")
        .removeprefix("```")
        .removesuffix("```")
        .strip()
    )
    analysis_data = json.loads(clean_json)
    return {
        "entry_id": entry_id,
        # **json.loads(assistant_message),
        "sentiment": analysis_data.get("sentiment", ""),
        "summary": analysis_data.get("summary", ""),
        "topics": analysis_data.get("topics", []),
    }

    raise NotImplementedError(
        "Task 4: implement analyze_journal_entry using the openai SDK. "
        "See tests/test_llm_service.py for the test contract."
    )

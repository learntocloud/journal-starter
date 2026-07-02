import json
from typing import Any

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
    client: Any | None = None,
) -> dict:
    if client is None:
        client = _default_client()

    completion = await client.chat.completions.create(
        model=get_settings().openai_model,
        messages=[
            {
                "role": "system",
                "content": "Your are a helpul summary assistant. I need you to analyze my journal entry and based off that return a sentiment, summary and topic field.",
            },
            {
                "role": "user",
                "content": f"Analyze the following journal entry: \n{entry_text}\nReturn ONLY valid JSON containing: \n- sentiment\n- summary\n- topics",
            },
        ],
    )

    text_response = completion.choices[0].message.content
    if text_response is None:
        raise ValueError("LLM returned no content in the response.")
    analysis = json.loads(text_response)

    return {
        "entry_id": entry_id,
        "sentiment": analysis.get("sentiment"),
        "summary": analysis.get("summary"),
        "topics": analysis.get("topics"),
    }

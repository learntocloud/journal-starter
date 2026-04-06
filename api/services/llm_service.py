import json
import os
from datetime import datetime, timezone

from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.environ.get("OPENAI_BASE_URL", "https://models.inference.ai.azure.com"),
)

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


async def analyze_journal_entry(entry_id: str, entry_text: str) -> dict:
    """Analyze a journal entry using the OpenAI API."""
    prompt = f"""Analyze this journal entry and respond ONLY with a JSON object, no markdown:
{{
  "sentiment": "positive" or "negative" or "neutral",
  "summary": "2 sentence summary of the entry",
  "topics": ["topic1", "topic2", "topic3"]
}}

Journal entry:
{entry_text}"""

    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that analyzes journal entries. Always respond with valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    result = json.loads(raw)

    return {
        "entry_id": entry_id,
        "sentiment": result["sentiment"],
        "summary": result["summary"],
        "topics": result["topics"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
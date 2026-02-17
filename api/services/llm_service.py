
# TODO: Import your chosen LLM SDK
# from openai import OpenAI
# import anthropic
# import boto3
# from google.cloud import aiplatform
import json
from datetime import UTC, datetime

from openai import OpenAI

client = OpenAI()

async def analyze_journal_entry(entry_id: str, entry_text: str) -> dict:
    """
    Analyze a journal entry using your chosen LLM API.

    Args:
        entry_id: The ID of the journal entry being analyzed
        entry_text: The combined text of the journal entry (work + struggle + intention)

    Returns:
        dict with keys:
            - entry_id: ID of the analyzed entry
            - sentiment: "positive" | "negative" | "neutral"
            - summary: 2 sentence summary of the entry
            - topics: list of 2-4 key topics mentioned
            - created_at: timestamp when the analysis was created

    TODO: Implement this function using your chosen LLM provider.
    See the Learn to Cloud curriculum for guidance on:
    - Setting up your LLM API client
    - Crafting effective prompts
    - Handling structured JSON output
    """
    response = client.chat.completions.create(
        model="gpt-4.1",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "Analyze the journal entry and return ONLY valid JSON with this structure:\n"
                    "{\n"
                    '  "sentiment": "positive | negative | neutral",\n'
                    '  "summary": "Exactly 2 sentences.",\n'
                    '  "topics": ["2-4 short topic strings"]\n'
                    "}\n"
                    "Do not include any extra text."},
            {"role": "user", "content": entry_text},
            ],
        )
    result=json.loads(response.choices[0].message.content)
    
    return {
        "entry_id": entry_id,
        "sentiment": result["sentiment"],
        "summary": result["summary"],
        "topics": result["topics"],
        "created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    

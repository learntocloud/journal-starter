import json
import os

import openai
from dotenv import load_dotenv
from fastapi import HTTPException


async def analyze_journal_entry(entry_id: str, entry_text: str) -> dict:

    # Setup LLM API client
    load_dotenv(override=True)
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://models.inference.ai.azure.com")
    client = openai.OpenAI(base_url=OPENAI_BASE_URL, api_key=GITHUB_TOKEN)
    MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    try:  # Try block for LLM API handling
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an assistant that analyzes journal entries. "
                        "Extract the sentiment, summarize the content, and identify key topics."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Analyze the following journal entry from {entry_id}:\n\n{entry_text}\n\n"
                        "Return a JSON object with the following structure:\n"
                        "{\n"
                        '  "entry_id": "<the ID of the entry>",\n'
                        '  "sentiment": "<positive|negative|neutral>",\n'
                        '  "summary": "<2 sentence summary of the entry>",\n'
                        '  "topics": ["<list of 2-4 key topics mentioned separated with comma>"],\n'
                        '  "created_at": "<timestamp when analysis was created>"\n'
                        "}"
                    ),
                },
            ],
            temperature=0.5,
        )
        analysis_result = response.choices[0].message.content
        result = json.loads(analysis_result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

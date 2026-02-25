
# TODO: Import your chosen LLM SDK
# from openai import OpenAI
# import anthropic
# import boto3
# from google.cloud import aiplatform

import os
import openai
from dotenv import load_dotenv

import json


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
    # Setup LLM API client
    load_dotenv(override=True)
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    OPENAI_BASE_URL = os.getenv(
        "OPENAI_BASE_URL", "https://models.inference.ai.azure.com")
    client = openai.OpenAI(base_url=OPENAI_BASE_URL, api_key=GITHUB_TOKEN)
    MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

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
            }
        ],
        temperature=0.5,

    )
    analysis_result = response.choices[0].message.content
    try:
        result_dict = json.loads(analysis_result)
    except json.JSONDecodeError:
        # Handle the error or return the raw string if parsing fails
        result_dict = analysis_result
    return result_dict
    """
        raise NotImplementedError(
            "Implement this function using your chosen LLM API. "
            "See the Learn to Cloud curriculum for guidance."
        )
    """

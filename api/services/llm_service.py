import os
from typing import Optional

# TODO: Import your chosen LLM SDK
# from openai import OpenAI
# import anthropic
# import boto3
# from google.cloud import aiplatform

async def analyze_journal_entry(entry_text: str) -> dict:
    """
    Analyze a journal entry using your chosen LLM API.
    
    Args:
        entry_text: The combined text of the journal entry (work + struggle + intention)
    
    Returns:
        dict with keys:
            - sentiment: "positive" | "negative" | "neutral"
            - summary: 2 sentence summary of the entry
            - topics: list of 2-4 key topics mentioned
    
    TODO: Implement this function using your chosen LLM provider.
    See the Learn to Cloud curriculum for guidance on:
    - Setting up your LLM API client
    - Crafting effective prompts
    - Handling structured JSON output
    """
    raise NotImplementedError(
        "Implement this function using your chosen LLM API. "
        "See the Learn to Cloud curriculum for guidance."
    )

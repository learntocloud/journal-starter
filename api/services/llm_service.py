
# TODO: Import your chosen LLM SDK
import json
import logging
import os

import openai

# import anthropic
# import boto3
# from google.cloud import aiplatform


# Initialize OpenAI client at module level
_openai_client = openai.OpenAI(base_url=os.getenv(
    "OPENAI_BASE_URL"), api_key=os.getenv("OPENAI_API_KEY"))
logging.info(f"open api key: {os.getenv('OPENAI_API_KEY')}")
logging.info(f"LLMService initialized with OpenAI base URL: {os.getenv('OPENAI_BASE_URL')}")


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
    response = _openai_client.chat.completions.create(
        model=os.getenv("GITHUB_MODEL"),
        temperature=0.7,
        messages=[
            {"role": "system", "content": "Analyze the input journal entry and provide a structured response for sentiment, summary, and list of topics covered. The response should be ONLY valid JSON with the following keys: entry_id, sentiment, summary, topics, created_at. Sentiment should be one of: positive, negative, neutral. Summary should be 2 sentences. Topics should be a list of 2-4 key topics mentioned in the entry. Do not include any text before or after the JSON."},
            {"role": "user", "content": f"entry_id: {entry_id}\n{entry_text}"}
        ],
    )

    content = response.choices[0].message.content.strip()
    print(f"Response from github:\n{content}")

    # Remove markdown code fence if present
    if content.startswith("```json"):
        content = content[7:]  # Remove ```json
    if content.startswith("```"):
        content = content[3:]  # Remove ```
    if content.endswith("```"):
        content = content[:-3]  # Remove trailing ```
    content = content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON response: {e}\nContent: {content}")
        raise ValueError(f"LLM response was not valid JSON: {e}") from e


class LLMService:
    def __init__(self):
        """
        Initialize your LLM API client here.

        For example, if using OpenAI:
        self.client = OpenAI()

        If using Anthropic:
        self.client = anthropic.Client()

        If using AWS Bedrock:
        self.client = boto3.client('bedrock')

        If using Google Vertex AI:
        aiplatform.init()
        self.client = aiplatform.gapic.PredictionServiceClient()
        """
        self.openai_client = _openai_client

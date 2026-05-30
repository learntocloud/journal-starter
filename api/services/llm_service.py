import json
import logging
import os

import openai

from api.telemetry import tracer

# import anthropic
# import boto3
# from google.cloud import aiplatform


# Initialize OpenAI client lazily.
_openai_client = None


def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "Missing OPENAI_API_KEY. Set OPENAI_API_KEY or pass a client explicitly."
        )
    client = openai.OpenAI(
        base_url=os.getenv("OPENAI_BASE_URL"), api_key=api_key
    )
    logging.info(f"LLMService initialized with OpenAI base URL: {os.getenv('OPENAI_BASE_URL')}")
    return client


async def analyze_journal_entry(
    entry_id: str,
    entry_text: str,
    client=None,
) -> dict:
    """Analyze a journal entry using an OpenAI-compatible LLM.

    Args:
    entry_id: The ID of the journal entry being analyzed
    entry_text: The combined text of the journal entry (work + struggle + intention)
    client: Optional OpenAI client to use (for testing)

    Returns:
    dict with keys:
        - entry_id: ID of the analyzed entry
        - sentiment: "positive" | "negative" | "neutral"
        - summary: 2 sentence summary of the entry
        - topics: list of 2-4 key topics mentioned
        - created_at: timestamp when the analysis was created

    """
    # Use provided client or fall back to a lazily created client
    if client is not None:
        api_client = client
    else:
        api_client = _openai_client or get_openai_client()

    # Trace the sentiment analysis work with a dedicated span.
    with tracer.start_as_current_span("llm.analyze_sentiment") as span:
        span.set_attribute("llm.entry_id", entry_id)
        span.set_attribute("llm.model", os.getenv("GITHUB_MODEL", "gpt-4"))
        span.set_attribute("llm.text_length", len(entry_text))

        # Handle both sync (real OpenAI) and async (mock) clients
        if hasattr(api_client.chat.completions, "create"):
            create_result = api_client.chat.completions.create(
                model=os.getenv("GITHUB_MODEL", "gpt-4"),
                temperature=0.7,
                messages=[
                    {
                        "role": "system",
                        "content": "Analyze the input journal entry and provide a structured response for sentiment, summary, and list of topics covered. The response should be ONLY valid JSON with the following keys: entry_id, sentiment, summary, topics, created_at. Sentiment should be one of: positive, negative, neutral. Summary should be 2 sentences. Topics should be a list of 2-4 key topics mentioned in the entry. Do not include any text before or after the JSON.",
                    },
                    {"role": "user", "content": f"entry_id: {entry_id}\n{entry_text}"},
                ],
            )
            # Check if result is a coroutine (async mock) and await if needed
            import inspect

            if inspect.iscoroutine(create_result):
                response = await create_result
            else:
                response = create_result
        else:
            raise ValueError("Client does not have chat.completions.create method")

        content = (response.choices[0].message.content or "").strip()
        logging.debug(f"Response from github:\n{content}")

        # Remove markdown code fence if present
        if content.startswith("```json"):
            content = content[7:]  # Remove ```json
        if content.startswith("```"):
            content = content[3:]  # Remove ```
        if content.endswith("```"):
            content = content[:-3]  # Remove trailing ```
        content = content.strip()

        try:
            result = json.loads(content)
            # Ensure entry_id and created_at are in the result
            if "entry_id" not in result:
                result["entry_id"] = entry_id
            if "created_at" not in result:
                from datetime import UTC, datetime

                result["created_at"] = datetime.now(UTC).isoformat()
            sentiment = result.get("sentiment")
            if sentiment:
                span.set_attribute("llm.sentiment", sentiment)
            return result
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON response: {e}\nContent: {content}")
            span.set_attribute("llm.error", True)
            span.set_attribute("llm.error.message", str(e))
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

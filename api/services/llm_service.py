import json
from datetime import UTC, datetime
from typing import Literal

import boto3
from pydantic import BaseModel, Field

brt = boto3.client("bedrock-runtime", region_name="us-east-1")
model_id = "us.anthropic.claude-opus-4-5-20251101-v1:0"

class JournalAnalysis(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    summary: str = Field(..., description="A 2 sentence summary of the journal entry")
    topics: list[str] = Field(..., description="A list of 2-4 key topics mentioned in the entry")
    model_config = {"extra": "forbid"}

async def analyze_journal_entry(entry_id: str, entry_text: str) -> dict:
    """Analyze a journal entry using Amazon Bedrock."""
    system_message = "You are a sentiment analyzer for journal entries."
    prompt = f"""Analyze the following journal entry:

    {entry_text}"""

    response = brt.converse(
        modelId=model_id,
        system=[{"text": system_message}],
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={
            "maxTokens": 512,
            "temperature": 0.5
        },
        outputConfig={
            "textFormat": {
                "type": "json_schema",
                "structure": {
                    "jsonSchema": {
                        "name": "journal_analysis",
                        "schema": json.dumps(JournalAnalysis.model_json_schema())
                    }
                }
            }
        }
    )

    response_text = response["output"]["message"]["content"][0]["text"]
    result = JournalAnalysis.model_validate_json(response_text)
    return {
        "entry_id": entry_id,
        **result.model_dump(),
        "created_at": datetime.now(UTC).isoformat()
    }

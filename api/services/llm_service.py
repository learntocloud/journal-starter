
# TODO: Import your chosen LLM SDK
import json
import os
from openai import OpenAI

from api.services import entry_service
# import anthropic
# import boto3
# from google.cloud import aiplatform
client = OpenAI(
    base_url=os.environ["OPENAI_BASE_URL"], api_key=os.environ["OPENAI_API_KEY"])
MODEL_NAME = os.environ["OPENAI_MODEL"]


async def analyze_journal_entry(entry_id: str, entry_text: str, ) -> dict:

    response = client.chat.completions.create(
        model=MODEL_NAME,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a journal analysis engine.\n"
                    "Extract ONLY the following fields:\n"
                    "- sentiment (positive | negative | neutral)\n"
                    "- summary (exactly 2 sentences)\n"
                    "- topics (array of 2-4 strings)\n\n"
                    "Return STRICT JSON with keys:\n"
                    "sentiment, summary, topics\n\n"
                    "Do NOT include entry_id or created_at.\n"
                    "Do NOT include explanations.\n"
                    "Do NOT include markdown.\n"
                    "Do NOT include extra fields."
                )
            },
            {"role": "user", "content": entry_text}
        ]
    )

    llm_data = json.loads(response.choices[0].message.content)

    # 🔒 Schema-controlled output
    result = {
        "entry_id": "",
        "sentiment": llm_data["sentiment"],
        "summary": llm_data["summary"],
        "topics": llm_data["topics"],
        "created_at": ""
    }

    return result

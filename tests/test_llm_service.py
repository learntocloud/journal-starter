"""Tests for Task 4: LLM-powered entry analysis.

Injects a MockAsyncOpenAI client into analyze_journal_entry, following
the pattern used by Azure-Samples/azure-search-openai-demo
(tests/test_mediadescriber.py). The mock captures calls and returns
a real ``openai.types.responses.Response`` object, so the student's
Responses API code path is exercised without making a network call.
"""

import json

import pytest
from openai.types.responses import Response

from api.models.entry import AnalysisResponse
from api.services.llm_service import analyze_journal_entry

pytestmark = pytest.mark.no_db


def _make_response(output_text: str) -> Response:
    return Response.model_validate(
        {
            "id": "resp_test",
            "created_at": 0,
            "model": "test-model",
            "object": "response",
            "output": [
                {
                    "id": "msg_test",
                    "content": [
                        {
                            "annotations": [],
                            "text": output_text,
                            "type": "output_text",
                        }
                    ],
                    "role": "assistant",
                    "status": "completed",
                    "type": "message",
                }
            ],
            "parallel_tool_calls": False,
            "tool_choice": "auto",
            "tools": [],
        }
    )


class MockResponses:
    def __init__(self, response: Response) -> None:
        self.response = response
        self.create_calls: list[dict] = []

    async def create(self, **kwargs) -> Response:
        self.create_calls.append(kwargs)
        return self.response


class MockAsyncOpenAI:
    def __init__(self, response: Response) -> None:
        self.responses = MockResponses(response)

    @property
    def create_calls(self) -> list[dict]:
        return self.responses.create_calls


SAMPLE_ENTRY_TEXT = (
    "Studied FastAPI today. Struggled with async/await syntax. "
    "Tomorrow I'll practice PostgreSQL queries."
)

VALID_ANALYSIS_JSON = json.dumps(
    {
        "sentiment": "positive",
        "summary": "Reflected on FastAPI study and async concepts.",
        "topics": ["FastAPI", "async"],
    }
)


async def test_analyze_entry_actually_calls_llm():
    client = MockAsyncOpenAI(_make_response(VALID_ANALYSIS_JSON))

    await analyze_journal_entry("entry-1", SAMPLE_ENTRY_TEXT, client=client)  # type: ignore[arg-type]

    assert len(client.create_calls) >= 1, (
        "Expected analyze_journal_entry to call client.responses.create() at least once."
    )


async def test_analyze_entry_sends_entry_text_in_prompt():
    client = MockAsyncOpenAI(_make_response(VALID_ANALYSIS_JSON))

    await analyze_journal_entry("entry-1", SAMPLE_ENTRY_TEXT, client=client)  # type: ignore[arg-type]

    call = client.create_calls[0]
    assert "input" in call
    assert "FastAPI" in json.dumps(call["input"])


async def test_analyze_entry_returns_valid_analysis_response():
    client = MockAsyncOpenAI(_make_response(VALID_ANALYSIS_JSON))

    result = await analyze_journal_entry("entry-1", SAMPLE_ENTRY_TEXT, client=client)  # type: ignore[arg-type]

    validated = AnalysisResponse.model_validate(result)
    assert validated.entry_id == "entry-1"
    assert validated.sentiment in {"positive", "negative", "neutral"}
    assert validated.summary
    assert isinstance(validated.topics, list)
    assert len(validated.topics) >= 1

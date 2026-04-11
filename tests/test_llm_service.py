"""Tests for Task 4: LLM-powered entry analysis.

Injects a MockAsyncOpenAI client into analyze_journal_entry, following
the pattern used by Azure-Samples/azure-search-openai-demo
(tests/test_mediadescriber.py). The mock captures calls and returns
real openai.types objects, so the student's code path is exercised
exactly as it would be against a real provider — only the network
layer is stubbed.
"""

import json

import pytest
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice
from openai.types.completion_usage import CompletionUsage

from api.models.entry import AnalysisResponse
from api.services.llm_service import analyze_journal_entry

pytestmark = pytest.mark.no_db


def _make_completion(content: str) -> ChatCompletion:
    return ChatCompletion(
        id="chatcmpl-test",
        object="chat.completion",
        created=0,
        model="test-model",
        choices=[
            Choice(
                index=0,
                finish_reason="stop",
                message=ChatCompletionMessage(role="assistant", content=content),
            )
        ],
        usage=CompletionUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
    )


class MockChatCompletions:
    def __init__(self, response: ChatCompletion) -> None:
        self.response = response
        self.create_calls: list[dict] = []

    async def create(self, **kwargs) -> ChatCompletion:
        self.create_calls.append(kwargs)
        return self.response


class MockChat:
    def __init__(self, completions: MockChatCompletions) -> None:
        self.completions = completions


class MockAsyncOpenAI:
    def __init__(self, response: ChatCompletion) -> None:
        self._completions = MockChatCompletions(response)
        self.chat = MockChat(self._completions)

    @property
    def create_calls(self) -> list[dict]:
        return self._completions.create_calls


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
    client = MockAsyncOpenAI(_make_completion(VALID_ANALYSIS_JSON))

    await analyze_journal_entry("entry-1", SAMPLE_ENTRY_TEXT, client=client)  # type: ignore[arg-type]

    assert len(client.create_calls) >= 1, (
        "Expected analyze_journal_entry to call client.chat.completions.create() at least once."
    )


async def test_analyze_entry_sends_entry_text_in_prompt():
    client = MockAsyncOpenAI(_make_completion(VALID_ANALYSIS_JSON))

    await analyze_journal_entry("entry-1", SAMPLE_ENTRY_TEXT, client=client)  # type: ignore[arg-type]

    call = client.create_calls[0]
    assert "messages" in call

    all_content = " ".join(
        msg["content"] for msg in call["messages"] if isinstance(msg.get("content"), str)
    )
    assert "FastAPI" in all_content


async def test_analyze_entry_returns_valid_analysis_response():
    client = MockAsyncOpenAI(_make_completion(VALID_ANALYSIS_JSON))

    result = await analyze_journal_entry("entry-1", SAMPLE_ENTRY_TEXT, client=client)  # type: ignore[arg-type]

    validated = AnalysisResponse.model_validate(result)
    assert validated.entry_id == "entry-1"
    assert validated.sentiment in {"positive", "negative", "neutral"}
    assert validated.summary
    assert isinstance(validated.topics, list)
    assert len(validated.topics) >= 1

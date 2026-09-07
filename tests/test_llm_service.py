"""Task 4 acceptance tests using the real SDK and an offline HTTP transport."""

import json
from datetime import UTC, datetime

import httpx
import pytest
from openai import AsyncOpenAI, InternalServerError
from pydantic import ValidationError

from api.config import get_settings
from api.models.entry import AnalysisResponse
from api.services import llm_service
from api.services.llm_service import InvalidAnalysisResponseError, analyze_journal_entry

pytestmark = pytest.mark.no_db

SAMPLE_ENTRY_TEXT = (
    "Studied FastAPI today. Struggled with async/await syntax. "
    "Tomorrow I'll practice PostgreSQL queries."
)
ANALYSES = [
    {
        "sentiment": "positive",
        "summary": "Practiced APIs. Plans to learn SQL next.",
        "topics": ["FastAPI", "SQL"],
    },
    {
        "sentiment": "negative",
        "summary": "Debugging was frustrating. A smaller experiment may help.",
        "topics": ["debugging", "experiments", "resilience"],
    },
]


def make_response(output_text: str) -> dict:
    return {
        "id": "resp_test",
        "created_at": 0,
        "model": "test-model",
        "object": "response",
        "status": "completed",
        "output": [
            {
                "id": "msg_test",
                "role": "assistant",
                "status": "completed",
                "type": "message",
                "content": [{"annotations": [], "text": output_text, "type": "output_text"}],
            }
        ],
        "parallel_tool_calls": False,
        "tool_choice": "auto",
        "tools": [],
    }


@pytest.fixture
async def provider_client():
    clients = []

    def create(payload: dict, status: int = 200):
        requests = []

        def respond(request: httpx.Request):
            assert request.method == "POST"
            assert request.url.path == "/v1/responses"
            requests.append(json.loads(request.content))
            return httpx.Response(status, json=payload)

        client = AsyncOpenAI(
            api_key="test-placeholder",
            base_url="https://example.invalid/v1",
            max_retries=0,
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)),
        )
        clients.append(client)
        return client, requests

    yield create
    for client in clients:
        await client.close()


async def test_default_client_has_bounded_timeout_and_retries():
    client = llm_service._default_client()
    try:
        assert client.api_key == get_settings().openai_api_key.get_secret_value()
        assert str(client.base_url).rstrip("/") == get_settings().openai_base_url.rstrip("/")
        assert client.max_retries == 1
        assert isinstance(client.timeout, httpx.Timeout)
        assert client.timeout.connect == 5.0
        assert client.timeout.read == 60.0
        assert client.timeout.write == 60.0
        assert client.timeout.pool == 60.0
    finally:
        await client.close()


@pytest.mark.exercise
class TestAnalysisImplementation:
    @pytest.mark.parametrize("generated", ANALYSES)
    async def test_uses_provider_content_and_requests_json(self, provider_client, generated):
        client, requests = provider_client(make_response(json.dumps(generated)))
        result = await analyze_journal_entry("entry-1", SAMPLE_ENTRY_TEXT, client=client)
        assert isinstance(result, dict)
        validated = AnalysisResponse.model_validate(result)
        assert validated.entry_id == "entry-1"
        assert validated.sentiment == generated["sentiment"]
        assert validated.summary == generated["summary"]
        assert validated.topics == generated["topics"]
        assert len(requests) == 1
        request = requests[0]
        assert request["model"] == get_settings().openai_model
        assert SAMPLE_ENTRY_TEXT in json.dumps(request["input"])
        output_format = request["text"]["format"]
        assert output_format["type"] in {"json_schema", "json_object"}
        if output_format["type"] == "json_schema":
            schema = output_format["schema"]
            assert output_format["strict"] is True
            assert schema["type"] == "object"
            assert set(schema["properties"]) == {"sentiment", "summary", "topics"}
            assert set(schema["required"]) == {"sentiment", "summary", "topics"}
            assert schema["additionalProperties"] is False
        assert not client.is_closed()

    @pytest.mark.parametrize("created_at", ["2000-01-01T00:00:00Z", "not-a-timestamp", None])
    async def test_provider_cannot_overwrite_server_metadata(self, provider_client, created_at):
        generated = {
            **ANALYSES[0],
            "entry_id": "provider-forged-id",
            "created_at": created_at,
        }
        client, _ = provider_client(make_response(json.dumps(generated)))
        before = datetime.now(UTC)
        result = await analyze_journal_entry("actual-entry-id", SAMPLE_ENTRY_TEXT, client=client)
        validated = AnalysisResponse.model_validate(result)
        assert validated.entry_id == "actual-entry-id"
        assert before <= validated.created_at <= datetime.now(UTC)

    @pytest.mark.parametrize("text", ["not JSON", '{"sentiment":'])
    async def test_malformed_json_fails(self, provider_client, text):
        client, _ = provider_client(make_response(text))
        with pytest.raises(json.JSONDecodeError):
            await analyze_journal_entry("entry-1", SAMPLE_ENTRY_TEXT, client=client)
        assert not client.is_closed()

    @pytest.mark.parametrize("text", ["null", "[]", '"a string"', "42", "true", "{}"])
    async def test_nonobject_json_fails(self, provider_client, text):
        client, _ = provider_client(make_response(text))
        with pytest.raises((ValidationError, InvalidAnalysisResponseError)):
            await analyze_journal_entry("entry-1", SAMPLE_ENTRY_TEXT, client=client)
        assert not client.is_closed()

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("sentiment", "mixed"),
            ("summary", ""),
            ("summary", " \t\n "),
            ("topics", []),
            ("topics", ["one"]),
            ("topics", ["one", "two", "three", "four", "five"]),
            ("topics", ["valid", ""]),
            ("topics", ["valid", 123]),
        ],
    )
    async def test_invalid_generated_content_fails(self, provider_client, field, value):
        generated = {**ANALYSES[0], field: value}
        client, _ = provider_client(make_response(json.dumps(generated)))
        with pytest.raises(ValidationError):
            await analyze_journal_entry("entry-1", SAMPLE_ENTRY_TEXT, client=client)

    @pytest.mark.parametrize("field", ["sentiment", "summary", "topics"])
    async def test_missing_generated_fields_fail(self, provider_client, field):
        generated = {key: value for key, value in ANALYSES[0].items() if key != field}
        client, _ = provider_client(make_response(json.dumps(generated)))
        with pytest.raises((ValidationError, InvalidAnalysisResponseError)):
            await analyze_journal_entry("entry-1", SAMPLE_ENTRY_TEXT, client=client)

    @pytest.mark.parametrize("kind", ["incomplete", "refusal", "no-output", "empty", "whitespace"])
    async def test_unusable_provider_response_fails(self, provider_client, kind):
        payload = make_response(json.dumps(ANALYSES[0]))
        if kind == "incomplete":
            payload["status"] = "incomplete"
            payload["incomplete_details"] = {"reason": "max_output_tokens"}
        elif kind == "refusal":
            payload["output"][0]["content"] = [{"type": "refusal", "refusal": "Cannot comply"}]
        elif kind == "no-output":
            payload["output"] = []
        else:
            payload["output"][0]["content"][0]["text"] = "" if kind == "empty" else " \t\n "
        client, _ = provider_client(payload)
        with pytest.raises(InvalidAnalysisResponseError):
            await analyze_journal_entry("entry-1", SAMPLE_ENTRY_TEXT, client=client)
        assert not client.is_closed()

    @pytest.mark.parametrize("outcome", ["success", "invalid-json", "provider-error"])
    async def test_owned_client_closed_after_success_or_failure(
        self,
        provider_client,
        monkeypatch,
        outcome,
    ):
        payload = make_response(json.dumps(ANALYSES[0]) if outcome == "success" else "not JSON")
        status = 200
        if outcome == "provider-error":
            payload = {"error": {"message": "synthetic provider failure", "type": "server_error"}}
            status = 500
        client, requests = provider_client(payload, status)
        monkeypatch.setattr(llm_service, "_default_client", lambda: client)
        if outcome == "success":
            await analyze_journal_entry("entry-1", SAMPLE_ENTRY_TEXT)
        else:
            error_type = json.JSONDecodeError if outcome == "invalid-json" else InternalServerError
            with pytest.raises(error_type):
                await analyze_journal_entry("entry-1", SAMPLE_ENTRY_TEXT)
        assert len(requests) == 1
        assert client.is_closed()

    async def test_caller_client_remains_open_after_provider_failure(self, provider_client):
        client, _ = provider_client(
            {"error": {"message": "synthetic provider failure", "type": "server_error"}},
            500,
        )
        with pytest.raises(InternalServerError):
            await analyze_journal_entry("entry-1", SAMPLE_ENTRY_TEXT, client=client)
        assert not client.is_closed()

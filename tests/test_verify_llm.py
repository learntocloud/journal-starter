import json
from unittest.mock import AsyncMock

import pytest
from httpx import Request, Response
from openai import APIConnectionError, APITimeoutError, AuthenticationError, RateLimitError
from pydantic import ValidationError

from api.models.entry import AnalysisResponse
from api.services.llm_service import InvalidAnalysisResponseError
from scripts import verify_llm

pytestmark = pytest.mark.no_db
PRIVATE_MARKER = "fake-private-diagnostic-marker"
PROVIDER_REQUEST = Request("POST", "https://example.invalid/v1/responses")


@pytest.fixture
def analysis_result(monkeypatch):
    monkeypatch.setattr(verify_llm, "get_settings", lambda: None)
    return {
        "entry_id": verify_llm.SAMPLE_ENTRY_ID,
        "sentiment": "positive",
        "summary": "The learner made progress. They plan to practice APIs next.",
        "topics": ["APIs", "learning"],
    }


async def test_verification_accepts_valid_analysis(monkeypatch, analysis_result):
    analyze = AsyncMock(return_value=analysis_result)
    monkeypatch.setattr(verify_llm, "analyze_journal_entry", analyze)

    assert await verify_llm.main() == 0
    analyze.assert_awaited_once_with(verify_llm.SAMPLE_ENTRY_ID, verify_llm.SAMPLE_ENTRY_TEXT)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("sentiment", "mixed"),
        ("entry_id", "not-the-sample-entry"),
    ],
)
async def test_verification_rejects_invalid_analysis(
    monkeypatch, analysis_result, capsys, field, value
):
    analysis_result[field] = value
    monkeypatch.setattr(
        verify_llm, "analyze_journal_entry", AsyncMock(return_value=analysis_result)
    )

    assert await verify_llm.main() == 2
    output = capsys.readouterr()
    assert output.err
    assert analysis_result["summary"] not in output.out + output.err


async def test_verification_does_not_print_raw_invalid_provider_result(monkeypatch, capsys):
    result = {
        "entry_id": verify_llm.SAMPLE_ENTRY_ID,
        "sentiment": "private-test-marker",
        "summary": "private-test-marker",
        "topics": ["private-test-marker"],
    }
    monkeypatch.setattr(verify_llm, "analyze_journal_entry", AsyncMock(return_value=result))
    assert await verify_llm.main() == 2
    output = capsys.readouterr()
    assert "private-test-marker" not in output.out + output.err


async def test_verification_propagates_unknown_programming_errors(monkeypatch):
    monkeypatch.setattr(
        verify_llm,
        "analyze_journal_entry",
        AsyncMock(side_effect=RuntimeError("provider failed")),
    )
    with pytest.raises(RuntimeError, match="provider failed"):
        await verify_llm.main()


@pytest.mark.parametrize(
    ("error", "status"),
    [
        (
            AuthenticationError(
                PRIVATE_MARKER,
                response=Response(401, request=PROVIDER_REQUEST),
                body={"private": PRIVATE_MARKER},
            ),
            3,
        ),
        (
            RateLimitError(
                PRIVATE_MARKER,
                response=Response(429, request=PROVIDER_REQUEST),
                body={"private": PRIVATE_MARKER},
            ),
            3,
        ),
        (APIConnectionError(message=PRIVATE_MARKER, request=PROVIDER_REQUEST), 3),
        (APITimeoutError(request=PROVIDER_REQUEST), 3),
        (json.JSONDecodeError(PRIVATE_MARKER, PRIVATE_MARKER, 0), 2),
        (InvalidAnalysisResponseError(PRIVATE_MARKER), 2),
    ],
)
async def test_known_service_errors_have_safe_diagnostics(monkeypatch, capsys, error, status):
    monkeypatch.setattr(
        verify_llm,
        "analyze_journal_entry",
        AsyncMock(side_effect=error),
    )
    assert await verify_llm.main() == status
    output = capsys.readouterr()
    assert type(error).__name__ in output.err
    assert PRIVATE_MARKER not in output.out + output.err
    assert str(error) not in output.out + output.err
    assert "Traceback" not in output.out + output.err


async def test_service_validation_errors_have_safe_diagnostics(monkeypatch, capsys):
    with pytest.raises(ValidationError) as captured:
        AnalysisResponse.model_validate(
            {
                "entry_id": verify_llm.SAMPLE_ENTRY_ID,
                "sentiment": PRIVATE_MARKER,
                "summary": PRIVATE_MARKER,
                "topics": [PRIVATE_MARKER],
            }
        )
    monkeypatch.setattr(
        verify_llm,
        "analyze_journal_entry",
        AsyncMock(side_effect=captured.value),
    )
    assert await verify_llm.main() == 2
    output = capsys.readouterr()
    assert "ValidationError" in output.err
    assert PRIVATE_MARKER not in output.out + output.err
    assert str(captured.value) not in output.out + output.err
    assert "Traceback" not in output.out + output.err


async def test_unfinished_analysis_has_safe_task_guidance(monkeypatch, capsys):
    monkeypatch.setattr(
        verify_llm,
        "analyze_journal_entry",
        AsyncMock(side_effect=NotImplementedError(PRIVATE_MARKER)),
    )
    assert await verify_llm.main() == 3
    output = capsys.readouterr()
    assert "Task 4" in output.err
    assert PRIVATE_MARKER not in output.out + output.err
    assert "Traceback" not in output.out + output.err

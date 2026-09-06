from unittest.mock import AsyncMock

import pytest

from scripts import verify_llm

pytestmark = pytest.mark.no_db


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
        ("summary", ""),
        ("summary", " \t\n "),
        ("topics", []),
        ("topics", ["one"]),
        ("topics", ["one", "two", "three", "four", "five"]),
        ("topics", ["valid", ""]),
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
    assert "does not validate against AnalysisResponse" in capsys.readouterr().err

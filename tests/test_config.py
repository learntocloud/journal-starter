import pytest

from api.config import get_settings
from tests.database_settings import DatabaseTestSettings

pytestmark = pytest.mark.no_db

DOTENV = """\
DATABASE_URL=postgresql://postgres/career_journal
TEST_DATABASE_URL=postgresql://postgres/career_journal_test
OPENAI_API_KEY=placeholder
OPENAI_BASE_URL=https://example.invalid/v1
OPENAI_MODEL=placeholder
"""


@pytest.fixture
def dotenv_file(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    for name in (
        "DATABASE_URL",
        "TEST_DATABASE_URL",
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "OPENAI_MODEL",
    ):
        monkeypatch.delenv(name, raising=False)
    path = tmp_path / ".env"
    path.write_text(DOTENV, encoding="utf-8")
    get_settings.cache_clear()
    try:
        yield path
    finally:
        get_settings.cache_clear()


def test_dotenv_changes_load_after_settings_cache_reset(dotenv_file):
    settings = get_settings()
    assert settings.database_url == "postgresql://postgres/career_journal"
    assert settings.openai_model == "placeholder"
    test_settings = DatabaseTestSettings()  # type: ignore[call-arg]
    assert test_settings.test_database_url == "postgresql://postgres/career_journal_test"

    dotenv_file.write_text(
        DOTENV.replace("placeholder", "replacement").replace(
            "https://example.invalid", "https://replacement.invalid"
        ),
        encoding="utf-8",
    )
    assert get_settings().openai_model == "placeholder"

    get_settings.cache_clear()
    updated = get_settings()
    assert updated.openai_api_key == "replacement"
    assert updated.openai_base_url == "https://replacement.invalid/v1"
    assert updated.openai_model == "replacement"


def test_exported_environment_overrides_dotenv(dotenv_file, monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "deployment-model")
    assert get_settings().openai_model == "deployment-model"

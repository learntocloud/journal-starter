import pytest
from pydantic import SecretStr, ValidationError

from api.config import Settings, get_settings
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
    assert updated.openai_api_key.get_secret_value() == "replacement"
    assert updated.openai_base_url == "https://replacement.invalid/v1"
    assert updated.openai_model == "replacement"


def test_exported_environment_overrides_dotenv(dotenv_file, monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "deployment-model")
    assert get_settings().openai_model == "deployment-model"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("database_url", ""),
        ("database_url", "not-a-url"),
        ("database_url", "https://example.invalid/database"),
        ("database_url", "postgresql://localhost"),
        ("database_url", "postgresql://localhost/"),
        ("database_url", "postgresql://localhost?sslmode=require"),
        ("openai_base_url", ""),
        ("openai_base_url", "not-a-url"),
        ("openai_base_url", "ftp://example.invalid"),
        ("openai_api_key", ""),
        ("openai_api_key", " \t\n "),
        ("openai_model", ""),
        ("openai_model", " \t\n "),
    ],
)
def test_rejects_invalid_required_settings(field, value):
    with pytest.raises(ValidationError):
        Settings(**{field: value})


@pytest.mark.parametrize(
    "name",
    ["DATABASE_URL", "OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_MODEL"],
)
def test_requires_every_setting(name, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv(name)
    with pytest.raises(ValidationError):
        get_settings()


def test_strips_model_name_and_keeps_key_secret():
    settings = Settings.model_validate(
        {
            **get_settings().model_dump(),
            "openai_model": "  deployed-model  ",
            "openai_api_key": "test-only-key",
        }
    )
    assert settings.openai_model == "deployed-model"
    assert isinstance(settings.openai_api_key, SecretStr)
    assert settings.openai_api_key.get_secret_value() == "test-only-key"
    assert "test-only-key" not in repr(settings)
    assert "test-only-key" not in str(settings.openai_api_key)
    assert "test-only-key" not in settings.model_dump_json()


def test_database_credentials_are_hidden_in_repr_and_validation_errors():
    marker = "test-only-private-marker"
    settings = Settings.model_validate(
        {
            **get_settings().model_dump(),
            "database_url": f"postgresql://learner:{marker}@localhost/journal",
        }
    )
    assert marker not in repr(settings)
    with pytest.raises(ValidationError) as error:
        Settings.model_validate(
            {
                **get_settings().model_dump(),
                "database_url": f"notpostgres://learner:{marker}@localhost/journal",
            }
        )
    assert marker not in str(error.value)
    with pytest.raises(ValidationError) as error:
        Settings.model_validate(
            {**get_settings().model_dump(), "openai_api_key": {"unexpected": marker}}
        )
    assert marker not in str(error.value)

import pytest
from pydantic import ValidationError

from tests.database_settings import DatabaseTestSettings

pytestmark = pytest.mark.no_db

APPLICATION_URL = "postgresql://localhost/career_journal"
TEST_URL = "postgresql://localhost/career_journal_test"


@pytest.fixture(autouse=True)
def isolate_dotenv(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)


def test_accepts_separate_test_database():
    settings = DatabaseTestSettings(database_url=APPLICATION_URL, test_database_url=TEST_URL)
    assert str(settings.test_database_url) == TEST_URL


def test_requires_explicit_test_database_url(monkeypatch):
    monkeypatch.delenv("TEST_DATABASE_URL", raising=False)
    with pytest.raises(ValidationError, match="test_database_url"):
        DatabaseTestSettings(database_url=APPLICATION_URL)  # type: ignore[call-arg]


@pytest.mark.parametrize(
    "test_url",
    [
        "",
        "not-a-url",
        APPLICATION_URL,
        "postgresql://localhost/another_database",
        "postgresql://localhost",
    ],
)
def test_rejects_invalid_or_non_test_database(test_url):
    with pytest.raises(ValidationError):
        DatabaseTestSettings(database_url=APPLICATION_URL, test_database_url=test_url)


@pytest.mark.parametrize(
    "test_url",
    [
        TEST_URL,
        "postgresql://127.0.0.1/career_journal_test",
        "postgresql://another-user@localhost/career_journal_test",
        "postgresql://localhost/career%5Fjournal_test",
    ],
)
def test_rejects_application_database_even_with_different_url(test_url):
    with pytest.raises(ValidationError, match="must not name the application database"):
        DatabaseTestSettings(database_url=TEST_URL, test_database_url=test_url)


@pytest.mark.parametrize("parameter", ["database", "dbname"])
@pytest.mark.parametrize("field", ["database_url", "test_database_url"])
def test_rejects_database_name_overrides(field, parameter):
    urls = {"database_url": APPLICATION_URL, "test_database_url": TEST_URL}
    urls[field] += f"?{parameter}=career_journal"
    with pytest.raises(ValidationError, match="not a query"):
        DatabaseTestSettings(**urls)

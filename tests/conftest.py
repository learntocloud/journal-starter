"""
Test configuration and fixtures for the Journal API.

This file sets up test fixtures that are shared across all tests, including:
- Test database connection
- Test client for making API requests
- Helper functions for cleaning up test data
"""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from api.config import get_settings
from api.main import app
from api.repositories.postgres_repository import PostgresDB
from api.routers.journal_router import get_database
from tests.database_settings import DatabaseTestSettings


@pytest.fixture(autouse=True)
def isolated_no_db_settings(request, monkeypatch):
    """Use synthetic provider settings and clear cached local values for no-db tests."""
    if "no_db" not in request.keywords:
        yield
        return
    for name, value in {
        "DATABASE_URL": "postgresql://localhost/unused_application",
        "TEST_DATABASE_URL": "postgresql://localhost/unused_application_test",
        "OPENAI_API_KEY": "test-placeholder",
        "OPENAI_BASE_URL": "https://example.invalid/v1",
        "OPENAI_MODEL": "test-model",
    }.items():
        monkeypatch.setenv(name, value)
    get_settings.cache_clear()
    try:
        yield
    finally:
        get_settings.cache_clear()


@pytest.fixture(scope="session")
def test_database_url() -> str:
    try:
        settings = DatabaseTestSettings()  # type: ignore[call-arg]
    except ValidationError as exc:
        raise pytest.UsageError(
            "Unsafe or missing test database configuration. Set DATABASE_URL and "
            "TEST_DATABASE_URL to different database names; the test database name "
            "must end in '_test'. See "
            f"docs/reference/testing-and-ci.md#test-database-safety.\n{exc}"
        ) from exc
    return str(settings.test_database_url)


@pytest.fixture
async def cleanup_database(test_database_url: str) -> AsyncGenerator[None]:
    """Clear the dedicated test database for fixtures that explicitly request cleanup."""
    async with PostgresDB(test_database_url) as db:
        await db.delete_all_entries()
    try:
        yield
    finally:
        async with PostgresDB(test_database_url) as db:
            await db.delete_all_entries()


@pytest.fixture
async def test_db(test_database_url: str, cleanup_database: None) -> AsyncGenerator[PostgresDB]:
    """
    Provides a test database connection.
    The cleanup is handled by the cleanup_database fixture.
    """
    async with PostgresDB(test_database_url) as db:
        yield db


@pytest.fixture
async def test_client(test_db: PostgresDB, monkeypatch) -> AsyncGenerator[AsyncClient]:
    """
    Provides an async HTTP client for testing the FastAPI application.
    This client can make requests to the API without starting a server.
    """

    def override_database() -> PostgresDB:
        return test_db

    # ASGITransport does not start the app lifespan, so the application database is never opened.
    monkeypatch.setitem(app.dependency_overrides, get_database, override_database)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_entry_data() -> dict:
    """
    Provides sample entry data for testing.
    This can be used to create test entries consistently across tests.
    """
    return {
        "work": "Studied FastAPI and built my first API endpoints",
        "struggle": "Understanding async/await syntax and when to use it",
        "intention": "Practice PostgreSQL queries and database design",
    }


@pytest.fixture
async def created_entry(test_client: AsyncClient, sample_entry_data: dict) -> dict:
    """
    Creates a sample entry and returns it.
    This fixture is useful for tests that need an existing entry.
    """
    response = await test_client.post("/entries", json=sample_entry_data)
    assert response.status_code == 201
    result = response.json()
    return result["entry"]

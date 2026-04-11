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

from api.config import get_settings
from api.main import app


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "no_db: test does not require a database connection",
    )


@pytest.fixture(autouse=True)
async def cleanup_database(request):
    """
    Automatically clean up the database before each test.
    Tests marked with ``no_db`` skip this fixture entirely so they can run
    without a live Postgres instance.
    """
    if "no_db" in request.keywords:
        yield
        return
    from api.repositories.postgres_repository import PostgresDB

    database_url = get_settings().database_url
    async with PostgresDB(database_url) as db:
        await db.delete_all_entries()
    yield
    # Clean up after test as well
    async with PostgresDB(database_url) as db:
        await db.delete_all_entries()


@pytest.fixture
async def test_db() -> AsyncGenerator:
    """
    Provides a test database connection.
    The cleanup is handled by the cleanup_database fixture.
    """
    from api.repositories.postgres_repository import PostgresDB

    async with PostgresDB(get_settings().database_url) as db:
        yield db


@pytest.fixture
async def test_client() -> AsyncGenerator[AsyncClient]:
    """
    Provides an async HTTP client for testing the FastAPI application.
    This client can make requests to the API without starting a server.
    """
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
    assert response.status_code in (200, 201)
    result = response.json()
    return result["entry"]

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

from api.main import app
from api.repositories.postgres_repository import PostgresDB


@pytest.fixture(autouse=True)
async def cleanup_database():
    """
    Automatically clean up the database before each test.
    This ensures test isolation.
    """
    async with PostgresDB() as db:
        await db.delete_all_entries()
    yield
    # Clean up after test as well
    async with PostgresDB() as db:
        await db.delete_all_entries()


@pytest.fixture
async def test_db() -> AsyncGenerator[PostgresDB, None]:
    """
    Provides a test database connection.
    The cleanup is handled by the cleanup_database fixture.
    """
    async with PostgresDB() as db:
        yield db


@pytest.fixture
async def test_client() -> AsyncGenerator[AsyncClient, None]:
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
        "intention": "Practice PostgreSQL queries and database design"
    }


@pytest.fixture
async def created_entry(test_client: AsyncClient, sample_entry_data: dict) -> dict:
    """
    Creates a sample entry and returns it.
    This fixture is useful for tests that need an existing entry.
    """
    response = await test_client.post("/entries", json=sample_entry_data)
    assert response.status_code == 200
    result = response.json()
    return result["entry"]

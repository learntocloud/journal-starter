from unittest.mock import AsyncMock

import asyncpg
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from api import main
from api.config import Settings
from api.repositories.postgres_repository import PostgresDB


@pytest.fixture
def application(test_database_url: str, monkeypatch) -> FastAPI:
    settings = Settings(
        database_url=test_database_url,
        openai_api_key="placeholder",
        openai_base_url="https://example.invalid/v1",
        openai_model="placeholder",
    )
    monkeypatch.setattr(main, "get_settings", lambda: settings)
    return main.app


async def test_one_pool_per_lifespan_is_reused_and_closed(
    application: FastAPI, sample_entry_data: dict, monkeypatch
):
    original_create = asyncpg.create_pool
    pools = []

    async def record_pool(*args, **kwargs):
        pool = await original_create(*args, **kwargs)
        pools.append(pool)
        return pool

    monkeypatch.setattr(asyncpg, "create_pool", record_pool)
    for run in range(2):
        async with application.router.lifespan_context(application):
            database: PostgresDB = application.state.database
            assert pools[run] is database.pool
            assert database.pool.get_size() > 0

            async with AsyncClient(
                transport=ASGITransport(app=application), base_url="http://test"
            ) as client:
                response = await client.post("/entries", json=sample_entry_data)
                assert response.status_code == 201
                for _ in range(3):
                    response = await client.get("/entries")
                    assert response.status_code == 200
                    assert response.json()["count"] == run + 1

            assert len(pools) == run + 1
            assert not database.pool.is_closing()

        assert database.pool.is_closing()
        assert not hasattr(application.state, "database")

    assert pools[0] is not pools[1]


async def test_pool_closes_when_lifespan_exits_with_error(application: FastAPI):
    database: PostgresDB | None = None

    async def fail_during_lifespan():
        nonlocal database
        async with application.router.lifespan_context(application):
            database = application.state.database
            raise RuntimeError("simulated lifespan failure")

    with pytest.raises(RuntimeError, match="simulated lifespan failure"):
        await fail_during_lifespan()

    assert database is not None
    assert database.pool.is_closing()
    assert not hasattr(application.state, "database")


@pytest.mark.no_db
async def test_settings_failure_prevents_startup(monkeypatch):
    create_pool = AsyncMock()
    monkeypatch.setattr(asyncpg, "create_pool", create_pool)

    def invalid_settings():
        raise ValueError("invalid startup configuration")

    monkeypatch.setattr(main, "get_settings", invalid_settings)
    with pytest.raises(ValueError, match="invalid startup configuration"):
        async with main.app.router.lifespan_context(main.app):
            pytest.fail("Startup should not complete with invalid settings")

    create_pool.assert_not_awaited()
    assert not hasattr(main.app.state, "database")

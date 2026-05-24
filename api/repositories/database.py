from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from api.repositories.interface_repository import DatabaseInterface
from api.repositories.postgres_repository import PostgresDB
from api.repositories.sqlite_repository import SQLiteDB


@asynccontextmanager
async def open_database(database_url: str) -> AsyncGenerator[DatabaseInterface]:
    if database_url.startswith("sqlite://"):
        async with SQLiteDB(database_url) as db:
            yield db
        return

    async with PostgresDB(database_url) as db:
        yield db

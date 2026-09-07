import json
from collections.abc import Mapping
from datetime import datetime
from types import TracebackType
from typing import Self

import asyncpg

from api.models.entry import Entry
from api.repositories.interface_repository import DatabaseInterface


class PostgresDB(DatabaseInterface):
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._pool: asyncpg.Pool | None = None

    @property
    def pool(self) -> asyncpg.Pool:
        if self._pool is None:
            raise RuntimeError("Open PostgresDB with 'async with' before using it")
        return self._pool

    async def __aenter__(self) -> Self:
        self._pool = await asyncpg.create_pool(self._database_url)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.pool.close()

    @staticmethod
    def _entry_from_row(row: asyncpg.Record) -> Entry:
        data = json.loads(row["data"])
        return Entry(
            id=row["id"],
            work=data["work"],
            struggle=data["struggle"],
            intention=data["intention"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def create_entry(self, entry: Entry) -> Entry:
        async with self.pool.acquire() as conn:
            query = """
            INSERT INTO entries (id, data, created_at, updated_at)
            VALUES ($1, $2, $3, $4)
            RETURNING *
            """
            data_json = json.dumps(
                {"work": entry.work, "struggle": entry.struggle, "intention": entry.intention}
            )

            row = await conn.fetchrow(
                query, entry.id, data_json, entry.created_at, entry.updated_at
            )

            if row is None:
                raise RuntimeError("Entry insert did not return the stored row")
            return self._entry_from_row(row)

    async def get_all_entries(self) -> list[Entry]:
        async with self.pool.acquire() as conn:
            query = "SELECT * FROM entries ORDER BY created_at DESC, id DESC"
            rows = await conn.fetch(query)
            return [self._entry_from_row(row) for row in rows]

    async def get_entry(self, entry_id: str) -> Entry | None:
        async with self.pool.acquire() as conn:
            query = "SELECT * FROM entries WHERE id = $1"
            row = await conn.fetchrow(query, entry_id)

            if row:
                return self._entry_from_row(row)
            return None

    async def update_entry(
        self, entry_id: str, changes: Mapping[str, str], *, updated_at: datetime
    ) -> Entry | None:
        data_json = json.dumps(dict(changes))

        async with self.pool.acquire() as conn:
            # Merge into the current row under PostgreSQL's update lock, not an earlier snapshot.
            query = """
            UPDATE entries
            SET data = data || $2::jsonb, updated_at = $3
            WHERE id = $1
            RETURNING *
            """
            row = await conn.fetchrow(query, entry_id, data_json, updated_at)
            return self._entry_from_row(row) if row else None

    async def delete_entry(self, entry_id: str) -> bool:
        async with self.pool.acquire() as conn:
            query = "DELETE FROM entries WHERE id = $1 RETURNING id"
            return await conn.fetchrow(query, entry_id) is not None

    async def delete_all_entries(self) -> None:
        async with self.pool.acquire() as conn:
            query = "DELETE FROM entries"
            await conn.execute(query)

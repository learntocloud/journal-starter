import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import aiosqlite

from api.repositories.interface_repository import DatabaseInterface
from api.repositories.postgres_repository import PostgresDB


class SQLiteDB(DatabaseInterface):
    def __init__(self, database_url: str) -> None:
        self._database_path = self._path_from_url(database_url)

    @staticmethod
    def _path_from_url(database_url: str) -> str:
        if database_url == "sqlite:///:memory:":
            return ":memory:"
        if not database_url.startswith("sqlite:///"):
            raise ValueError("SQLite URLs must use sqlite:///path/to/database.db")
        return database_url.removeprefix("sqlite:///")

    @staticmethod
    def _parse_datetime(value: str) -> datetime:
        return datetime.fromisoformat(value)

    @staticmethod
    def _entry_from_row(row: sqlite3.Row) -> dict[str, Any]:
        data = json.loads(row["data"])
        return {
            "id": row["id"],
            "work": data["work"],
            "struggle": data["struggle"],
            "intention": data["intention"],
            "created_at": SQLiteDB._parse_datetime(row["created_at"]),
            "updated_at": SQLiteDB._parse_datetime(row["updated_at"]),
        }

    async def __aenter__(self):
        if self._database_path != ":memory:":
            Path(self._database_path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = await aiosqlite.connect(self._database_path)
        self.connection.row_factory = sqlite3.Row
        await self._initialize_schema()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.connection.close()

    async def _initialize_schema(self) -> None:
        await self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS entries (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_entries_created_at ON entries(created_at);
            """
        )
        await self.connection.commit()

    async def create_entry(self, entry_data: dict[str, Any]) -> dict[str, Any]:
        entry_id = entry_data.get("id") or str(uuid.uuid4())
        data_json = json.dumps(entry_data, default=PostgresDB.datetime_serialize)
        await self.connection.execute(
            """
            INSERT INTO entries (id, data, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                entry_id,
                data_json,
                entry_data["created_at"].isoformat(),
                entry_data["updated_at"].isoformat(),
            ),
        )
        await self.connection.commit()
        entry = await self.get_entry(entry_id)
        return entry or {}

    async def get_all_entries(self) -> list[dict[str, Any]]:
        cursor = await self.connection.execute("SELECT * FROM entries")
        rows = await cursor.fetchall()
        await cursor.close()
        return [self._entry_from_row(row) for row in rows]

    async def get_entry(self, entry_id: str) -> dict[str, Any] | None:
        cursor = await self.connection.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
        row = await cursor.fetchone()
        await cursor.close()
        if row is None:
            return None
        return self._entry_from_row(row)

    async def update_entry(self, entry_id: str, updated_data: dict[str, Any]) -> None:
        updated_data["id"] = entry_id
        data_json = json.dumps(updated_data, default=PostgresDB.datetime_serialize)
        await self.connection.execute(
            """
            UPDATE entries
            SET data = ?, updated_at = ?
            WHERE id = ?
            """,
            (data_json, updated_data["updated_at"].isoformat(), entry_id),
        )
        await self.connection.commit()

    async def delete_entry(self, entry_id: str) -> None:
        await self.connection.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        await self.connection.commit()

    async def delete_all_entries(self) -> None:
        await self.connection.execute("DELETE FROM entries")
        await self.connection.commit()

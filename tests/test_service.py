"""Safeguards for the supplied typed service and PostgreSQL persistence."""

import asyncio
import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from api.models.entry import Entry, EntryCreate
from api.repositories.interface_repository import DatabaseInterface
from api.repositories.postgres_repository import PostgresDB
from api.services.entry_service import EntryService


@pytest.fixture
def entry_input(sample_entry_data: dict) -> EntryCreate:
    return EntryCreate(**sample_entry_data)


class TestEntryService:
    async def test_create_entry(self, test_db: PostgresDB, entry_input: EntryCreate):
        before = datetime.now(UTC)
        result = await EntryService(test_db).create_entry(entry_input)
        assert isinstance(result, Entry)
        assert UUID(result.id).version == 4
        assert result.work == entry_input.work
        assert before <= result.created_at <= datetime.now(UTC)
        assert result.created_at == result.updated_at
        assert result.created_at.utcoffset() == timedelta(0)
        assert await test_db.get_entry(result.id) == result

    async def test_get_all_entries(self, test_db: PostgresDB, entry_input: EntryCreate):
        service = EntryService(test_db)
        created = [await service.create_entry(entry_input) for _ in range(3)]
        entries = await service.get_all_entries()
        assert all(isinstance(entry, Entry) for entry in entries)
        assert entries == sorted(created, key=lambda e: (e.created_at, e.id), reverse=True)
        assert len({entry.id for entry in entries}) == 3

    async def test_get_entry_by_id(self, test_db: PostgresDB, entry_input: EntryCreate):
        service = EntryService(test_db)
        created = await service.create_entry(entry_input)
        assert await service.get_entry(created.id) == created

    async def test_get_nonexistent_entry(self, test_db: PostgresDB):
        assert await EntryService(test_db).get_entry("nonexistent-id") is None

    async def test_update_entry(self, test_db: PostgresDB, entry_input: EntryCreate):
        service = EntryService(test_db)
        entry = await service.create_entry(entry_input)
        result = await service.update_entry(entry.id, {"work": "Updated work"})
        assert isinstance(result, Entry)
        assert result.work == "Updated work"
        assert result.struggle == entry.struggle
        assert result.intention == entry.intention
        assert result.created_at == entry.created_at
        assert result.updated_at >= entry.updated_at
        assert await test_db.get_entry(entry.id) == result

    @pytest.mark.parametrize(
        ("first_field", "second_field"),
        [("work", "struggle"), ("work", "intention"), ("struggle", "intention")],
    )
    async def test_concurrent_updates_preserve_different_fields(
        self,
        test_db: PostgresDB,
        entry_input: EntryCreate,
        monkeypatch,
        first_field,
        second_field,
    ):
        service = EntryService(test_db)
        entry = await service.create_entry(entry_input)
        ready_to_write = asyncio.Barrier(2)
        original_update = test_db.update_entry

        async def synchronized_update(entry_id, changes, *, updated_at):
            await ready_to_write.wait()
            return await original_update(entry_id, changes, updated_at=updated_at)

        monkeypatch.setattr(test_db, "update_entry", synchronized_update)
        async with asyncio.timeout(20):
            results = await asyncio.gather(
                service.update_entry(entry.id, {first_field: "First update"}),
                service.update_entry(entry.id, {second_field: "Second update"}),
            )
        assert all(isinstance(result, Entry) for result in results)
        stored = await test_db.get_entry(entry.id)
        assert stored is not None
        assert getattr(stored, first_field) == "First update"
        assert getattr(stored, second_field) == "Second update"
        for field in ("work", "struggle", "intention"):
            if field not in (first_field, second_field):
                assert getattr(stored, field) == getattr(entry, field)
        assert stored.created_at == entry.created_at

    async def test_update_preserves_server_owned_fields(
        self,
        test_db: PostgresDB,
        entry_input: EntryCreate,
    ):
        service = EntryService(test_db)
        entry = await service.create_entry(entry_input)
        result = await service.update_entry(
            entry.id,
            {
                "id": "replacement-id",
                "created_at": "2000-01-01T00:00:00Z",
                "updated_at": "2000-01-01T00:00:00Z",
                "unknown": "must not be stored",
                "work": "Updated work",
            },
        )
        assert result is not None
        assert result.id == entry.id
        assert result.created_at == entry.created_at
        assert result.updated_at >= entry.updated_at
        assert result.work == "Updated work"
        async with test_db.pool.acquire() as connection:
            data = await connection.fetchval("SELECT data FROM entries WHERE id = $1", entry.id)
        assert json.loads(data) == {
            "work": result.work,
            "struggle": result.struggle,
            "intention": result.intention,
        }

    async def test_update_nonexistent_entry(self, test_db: PostgresDB):
        assert await EntryService(test_db).update_entry("nonexistent-id", {"work": "New"}) is None

    async def test_delete_entry(self, test_db: PostgresDB, entry_input: EntryCreate):
        service = EntryService(test_db)
        entry = await service.create_entry(entry_input)
        assert await service.delete_entry(entry.id) is True
        assert await service.get_entry(entry.id) is None
        assert await service.delete_entry(entry.id) is False

    async def test_delete_all_entries(self, test_db: PostgresDB, entry_input: EntryCreate):
        service = EntryService(test_db)
        for _ in range(3):
            await service.create_entry(entry_input)
        await service.delete_all_entries()
        assert await service.get_all_entries() == []


class TestRepository:
    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    async def test_historical_long_text_remains_readable(
        self,
        test_db: PostgresDB,
        entry_input: EntryCreate,
        field,
    ):
        now = datetime.now(UTC)
        text = {**entry_input.model_dump(), field: "a" * 300}
        entry = Entry(
            id="historical-entry",
            created_at=now,
            updated_at=now,
            **text,
        )
        assert await test_db.create_entry(entry) == entry
        assert await test_db.get_entry(entry.id) == entry
        assert await test_db.get_all_entries() == [entry]

    async def test_stores_metadata_only_in_columns(
        self,
        test_db: PostgresDB,
        entry_input: EntryCreate,
    ):
        entry = await EntryService(test_db).create_entry(entry_input)
        async with test_db.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM entries WHERE id = $1", entry.id)
        assert row is not None
        assert json.loads(row["data"]) == entry_input.model_dump()
        assert row["created_at"] == entry.created_at
        assert row["updated_at"] == entry.updated_at

    async def test_reads_legacy_duplicate_metadata_from_columns(
        self,
        test_db: PostgresDB,
        entry_input: EntryCreate,
    ):
        entry = await EntryService(test_db).create_entry(entry_input)
        legacy = {
            **entry_input.model_dump(),
            "id": "wrong-id",
            "created_at": "not a datetime",
            "updated_at": "not a datetime",
        }
        async with test_db.pool.acquire() as connection:
            await connection.execute(
                "UPDATE entries SET data = $2::jsonb WHERE id = $1",
                entry.id,
                json.dumps(legacy),
            )
        assert await test_db.get_entry(entry.id) == entry
        assert await test_db.get_all_entries() == [entry]

    async def test_same_timestamp_order_is_deterministic(
        self,
        test_db: PostgresDB,
        entry_input: EntryCreate,
    ):
        now = datetime.now(UTC)
        for entry_id in ("a", "c", "b"):
            await test_db.create_entry(
                Entry(id=entry_id, created_at=now, updated_at=now, **entry_input.model_dump())
            )
        assert [entry.id for entry in await test_db.get_all_entries()] == ["c", "b", "a"]

    async def test_concurrent_delete_reports_exactly_one_deletion(
        self,
        test_db: PostgresDB,
        entry_input: EntryCreate,
    ):
        entry = await EntryService(test_db).create_entry(entry_input)
        results = await asyncio.gather(
            test_db.delete_entry(entry.id),
            test_db.delete_entry(entry.id),
        )
        assert sorted(results) == [False, True]


@pytest.mark.no_db
@pytest.mark.parametrize("deleted", [True, False])
async def test_service_delete_uses_atomic_repository_result(deleted):
    database = AsyncMock(spec=DatabaseInterface)
    database.delete_entry.return_value = deleted
    assert await EntryService(database).delete_entry("entry-id") is deleted
    database.delete_entry.assert_awaited_once_with("entry-id")
    database.get_entry.assert_not_awaited()


@pytest.mark.no_db
async def test_service_passes_only_text_changes_with_separate_timestamp():
    database = AsyncMock(spec=DatabaseInterface)
    database.update_entry.return_value = None
    before = datetime.now(UTC)
    assert (
        await EntryService(database).update_entry(
            "entry-id",
            {"work": "New", "id": "forged", "updated_at": "forged", "extra": "ignored"},
        )
        is None
    )
    database.update_entry.assert_awaited_once()
    args, kwargs = database.update_entry.await_args
    assert args == ("entry-id", {"work": "New"})
    assert before <= kwargs["updated_at"] <= datetime.now(UTC)
    assert kwargs["updated_at"].utcoffset() == timedelta(0)


@pytest.mark.no_db
async def test_service_generates_metadata_before_repository_call(sample_entry_data):
    database = AsyncMock(spec=DatabaseInterface)
    database.create_entry.side_effect = lambda entry: entry
    supplied = EntryCreate.model_validate(
        {
            **sample_entry_data,
            "id": "caller-owned-id",
            "created_at": "2000-01-01T00:00:00Z",
            "updated_at": "2000-01-01T00:00:00Z",
        }
    )
    before = datetime.now(UTC)
    entry = await EntryService(database).create_entry(supplied)
    assert isinstance(entry, Entry)
    assert UUID(entry.id).version == 4
    assert entry.id != "caller-owned-id"
    assert before <= entry.created_at <= datetime.now(UTC)
    assert entry.created_at == entry.updated_at
    assert entry.created_at.utcoffset() == timedelta(0)
    database.create_entry.assert_awaited_once_with(entry)

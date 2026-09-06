"""
Tests for the EntryService layer.

These tests verify that the service layer correctly interacts with the database
and handles business logic properly.
"""

import asyncio
from datetime import UTC, datetime

import pytest

from api.repositories.postgres_repository import PostgresDB
from api.services.entry_service import EntryService


class TestEntryService:
    """Tests for the EntryService class."""

    async def test_create_entry(self, test_db: PostgresDB):
        """Test creating an entry through the service."""
        service = EntryService(test_db)

        entry_data = {
            "id": "test-123",
            "work": "Studied FastAPI",
            "struggle": "Understanding async",
            "intention": "Practice more",
        }

        result = await service.create_entry(entry_data)

        assert result is not None
        assert result["id"] == "test-123"
        assert result["work"] == entry_data["work"]
        assert "created_at" in result
        assert "updated_at" in result

    async def test_get_all_entries(self, test_db: PostgresDB):
        """Test getting all entries through the service."""
        service = EntryService(test_db)

        # Create a few entries
        for i in range(3):
            entry_data = {
                "id": f"test-{i}",
                "work": f"Work {i}",
                "struggle": "Struggle",
                "intention": "Intention",
            }
            await service.create_entry(entry_data)

        # Get all entries
        result = await service.get_all_entries()

        assert len(result) == 3
        assert all("id" in entry for entry in result)

    async def test_get_entry_by_id(self, test_db: PostgresDB):
        """Test getting a specific entry by ID."""
        service = EntryService(test_db)

        # Create an entry
        entry_data = {
            "id": "test-get",
            "work": "Studied FastAPI",
            "struggle": "Understanding async",
            "intention": "Practice more",
        }
        await service.create_entry(entry_data)

        # Get the entry
        result = await service.get_entry("test-get")

        assert result is not None
        assert result["id"] == "test-get"
        assert result["work"] == entry_data["work"]

    async def test_get_nonexistent_entry(self, test_db: PostgresDB):
        """Test getting an entry that doesn't exist."""
        service = EntryService(test_db)

        result = await service.get_entry("nonexistent-id")

        assert result is None

    async def test_update_entry(self, test_db: PostgresDB):
        """Test updating an existing entry."""
        service = EntryService(test_db)

        # Create an entry
        entry_data = {
            "id": "test-update",
            "work": "Original work",
            "struggle": "Original struggle",
            "intention": "Original intention",
        }
        await service.create_entry(entry_data)

        # Update the entry
        update_data = {"work": "Updated work"}
        result = await service.update_entry("test-update", update_data)

        assert result is not None
        assert result["work"] == "Updated work"
        assert result["struggle"] == entry_data["struggle"]  # Unchanged
        assert result["intention"] == entry_data["intention"]  # Unchanged
        assert await test_db.get_entry("test-update") == result

    @pytest.mark.parametrize(
        ("first_field", "second_field"),
        [("work", "struggle"), ("work", "intention"), ("struggle", "intention")],
    )
    async def test_concurrent_updates_preserve_different_fields(
        self, test_db: PostgresDB, sample_entry_data: dict, monkeypatch, first_field, second_field
    ):
        service = EntryService(test_db)
        entry = await service.create_entry({"id": "concurrent-entry", **sample_entry_data})
        ready_to_write = asyncio.Barrier(2)
        original_update = test_db.update_entry

        async def synchronized_update(entry_id, changes):
            await ready_to_write.wait()
            return await original_update(entry_id, changes)

        monkeypatch.setattr(test_db, "update_entry", synchronized_update)
        async with asyncio.timeout(20):
            results = await asyncio.gather(
                service.update_entry(entry["id"], {first_field: "First update"}),
                service.update_entry(entry["id"], {second_field: "Second update"}),
            )

        assert all(result is not None for result in results)
        stored = await test_db.get_entry(entry["id"])
        assert stored is not None
        assert stored[first_field] == "First update"
        assert stored[second_field] == "Second update"
        for field in ("work", "struggle", "intention"):
            if field not in (first_field, second_field):
                assert stored[field] == sample_entry_data[field]
        assert stored["created_at"] == entry["created_at"]

    async def test_update_preserves_server_owned_fields(
        self, test_db: PostgresDB, sample_entry_data: dict
    ):
        service = EntryService(test_db)
        entry = await service.create_entry({"id": "immutable-fields", **sample_entry_data})
        supplied_timestamp = datetime(2000, 1, 1, tzinfo=UTC)

        result = await service.update_entry(
            entry["id"],
            {
                "id": "replacement-id",
                "created_at": supplied_timestamp,
                "updated_at": supplied_timestamp,
                "work": "Updated work",
            },
        )

        assert result is not None
        assert result["id"] == entry["id"]
        assert result["created_at"] == entry["created_at"]
        assert result["updated_at"] != supplied_timestamp
        assert result["work"] == "Updated work"
        assert await test_db.get_entry(entry["id"]) == result

    async def test_update_nonexistent_entry(self, test_db: PostgresDB):
        """Test updating an entry that doesn't exist."""
        service = EntryService(test_db)

        update_data = {"work": "Updated work"}
        result = await service.update_entry("nonexistent-id", update_data)

        assert result is None

    async def test_delete_entry(self, test_db: PostgresDB):
        """Test deleting a specific entry."""
        service = EntryService(test_db)

        # Create an entry
        entry_data = {
            "id": "test-delete",
            "work": "Work to delete",
            "struggle": "Struggle",
            "intention": "Intention",
        }
        await service.create_entry(entry_data)

        # Verify it exists
        entry = await service.get_entry("test-delete")
        assert entry is not None

        # Delete it
        await service.delete_entry("test-delete")

        # Verify it's gone
        entry = await service.get_entry("test-delete")
        assert entry is None

    async def test_delete_all_entries(self, test_db: PostgresDB):
        """Test deleting all entries."""
        service = EntryService(test_db)

        # Create multiple entries
        for i in range(3):
            entry_data = {
                "id": f"test-{i}",
                "work": f"Work {i}",
                "struggle": "Struggle",
                "intention": "Intention",
            }
            await service.create_entry(entry_data)

        # Verify entries exist
        entries = await service.get_all_entries()
        assert len(entries) == 3

        # Delete all
        await service.delete_all_entries()

        # Verify all are gone
        entries = await service.get_all_entries()
        assert len(entries) == 0

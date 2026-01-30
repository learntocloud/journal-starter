"""
Tests for the EntryService layer.

These tests verify that the service layer correctly interacts with the database
and handles business logic properly.
"""
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
            "intention": "Practice more"
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
                "intention": "Intention"
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
            "intention": "Practice more"
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
            "intention": "Original intention"
        }
        await service.create_entry(entry_data)

        # Update the entry
        update_data = {"work": "Updated work"}
        result = await service.update_entry("test-update", update_data)

        assert result is not None
        assert result["work"] == "Updated work"
        assert result["struggle"] == entry_data["struggle"]  # Unchanged
        assert result["intention"] == entry_data["intention"]  # Unchanged

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
            "intention": "Intention"
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
                "intention": "Intention"
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

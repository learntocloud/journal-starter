from abc import ABC, abstractmethod
from collections.abc import Mapping
from datetime import datetime

from api.models.entry import Entry


class DatabaseInterface(ABC):
    """Abstract interface for database operations."""

    @abstractmethod
    async def create_entry(self, entry: Entry) -> Entry:
        """Create a new journal entry."""
        pass

    @abstractmethod
    async def get_all_entries(self) -> list[Entry]:
        """Retrieve all journal entries."""
        pass

    @abstractmethod
    async def get_entry(self, entry_id: str) -> Entry | None:
        """Retrieve a specific journal entry by ID."""
        pass

    @abstractmethod
    async def update_entry(
        self, entry_id: str, changes: Mapping[str, str], *, updated_at: datetime
    ) -> Entry | None:
        """Apply a partial update and return the stored entry, or None if not found."""
        pass

    @abstractmethod
    async def delete_entry(self, entry_id: str) -> bool:
        """Delete an entry atomically and report whether a row was deleted."""
        pass

    @abstractmethod
    async def delete_all_entries(self) -> None:
        """Delete all journal entries."""
        pass

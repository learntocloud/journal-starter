from abc import ABC, abstractmethod
from typing import Any


class DatabaseInterface(ABC):
    """Abstract interface for database operations."""

    @abstractmethod
    async def create_entry(self, entry_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new journal entry."""
        pass

    @abstractmethod
    async def get_all_entries(self) -> list[dict[str, Any]]:
        """Retrieve all journal entries."""
        pass

    @abstractmethod
    async def get_entry(self, entry_id: str) -> dict[str, Any] | None:
        """Retrieve a specific journal entry by ID."""
        pass

    @abstractmethod
    async def update_entry(self, entry_id: str, updated_data: dict[str, Any]) -> None:
        """Update an existing journal entry."""
        pass

    @abstractmethod
    async def delete_entry(self, entry_id: str) -> None:
        """Delete a specific journal entry."""
        pass

    @abstractmethod
    async def delete_all_entries(self) -> None:
        """Delete all journal entries."""
        pass

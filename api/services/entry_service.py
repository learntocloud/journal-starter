import logging
from collections.abc import Mapping
from datetime import UTC, datetime
from uuid import uuid4

from api.models.entry import Entry, EntryCreate
from api.repositories.interface_repository import DatabaseInterface

logger = logging.getLogger(__name__)


class EntryService:
    def __init__(self, db: DatabaseInterface) -> None:
        self.db = db

    async def create_entry(self, entry_data: EntryCreate) -> Entry:
        """Creates a new entry."""
        now = datetime.now(UTC)
        entry = Entry(
            id=str(uuid4()),
            work=entry_data.work,
            struggle=entry_data.struggle,
            intention=entry_data.intention,
            created_at=now,
            updated_at=now,
        )
        logger.debug("Creating entry %s", entry.id)
        stored = await self.db.create_entry(entry)
        logger.info("Entry %s created", stored.id)
        return stored

    async def get_all_entries(self) -> list[Entry]:
        """Gets all entries."""
        entries = await self.db.get_all_entries()
        logger.debug("Fetched %d entries", len(entries))
        return entries

    async def get_entry(self, entry_id: str) -> Entry | None:
        """Gets a specific entry."""
        entry = await self.db.get_entry(entry_id)
        if entry:
            logger.debug("Entry %s found", entry_id)
        else:
            logger.debug("Entry %s not found", entry_id)
        return entry

    async def update_entry(self, entry_id: str, updated_data: Mapping[str, str]) -> Entry | None:
        """Updates an existing entry."""
        logger.debug("Updating entry %s", entry_id)
        changes = {
            field: value
            for field, value in updated_data.items()
            if field in ("work", "struggle", "intention")
        }
        result = await self.db.update_entry(entry_id, changes, updated_at=datetime.now(UTC))
        if result is None:
            logger.info("Entry %s not found; update skipped", entry_id)
            return None

        logger.info("Entry %s updated", entry_id)
        return result

    async def delete_entry(self, entry_id: str) -> bool:
        """Deletes a specific entry."""
        logger.debug("Deleting entry %s", entry_id)
        deleted = await self.db.delete_entry(entry_id)
        if deleted:
            logger.info("Entry %s deleted", entry_id)
        else:
            logger.info("Entry %s not found; nothing deleted", entry_id)
        return deleted

    async def delete_all_entries(self) -> None:
        """Deletes all entries."""
        logger.debug("Deleting all entries")
        await self.db.delete_all_entries()
        logger.info("All entries deleted")

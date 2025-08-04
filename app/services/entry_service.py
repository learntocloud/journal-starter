from app.models.entry import Entry as EntryModel
from app.schemas.entry import EntryCreate, EntryOut, EntryUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4
from typing import List, Optional

class EntryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_entry(self, entry_in: EntryCreate) -> EntryOut:
        new_entry = EntryModel(
            id=str(uuid4()),
            work=entry_in.work,
            struggle=entry_in.struggle,
            intention=entry_in.intention,
        )
        self.db.add(new_entry)
        await self.db.commit()
        await self.db.refresh(new_entry)
        return EntryOut.model_validate(new_entry)

    async def get_entry_by_id(self, entry_id: str) -> Optional[EntryOut]:
        result = await self.db.execute(select(EntryModel).where(EntryModel.id == entry_id))
        entry = result.scalar_one_or_none()
        return EntryOut.model_validate(entry) if entry else None

    async def get_all_entries(self) -> List[EntryOut]:
        result = await self.db.execute(select(EntryModel))
        entries = result.scalars().all()
        return [EntryOut.model_validate(entry) for entry in entries]

    async def update_entry(self, entry_id: str, entry_in: EntryUpdate) -> Optional[EntryOut]:
        result = await self.db.execute(select(EntryModel).where(EntryModel.id == entry_id))
        entry = result.scalar_one_or_none()
        if not entry:
            return None
        for field, value in entry_in.model_dump(exclude_unset=True).items():
            setattr(entry, field, value)
        await self.db.commit()
        await self.db.refresh(entry)
        return EntryOut.model_validate(entry)

    async def delete_entry(self, entry_id: str) -> bool:
        result = await self.db.execute(select(EntryModel).where(EntryModel.id == entry_id))
        entry = result.scalar_one_or_none()
        if not entry:
            return False
        await self.db.delete(entry)
        await self.db.commit()
        return True

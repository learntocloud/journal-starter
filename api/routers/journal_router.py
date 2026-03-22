from api.services.llm_service import analyze_journal_entry
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException

from api.models.entry import Entry, EntryCreate
from api.repositories.postgres_repository import PostgresDB
from api.services.entry_service import EntryService

router = APIRouter()


async def get_entry_service() -> AsyncGenerator[EntryService, None]:
    async with PostgresDB() as db:
        yield EntryService(db)


@router.post("/entries")
async def create_entry(
    entry_data: EntryCreate,
    entry_service: EntryService = Depends(get_entry_service),
):
    """Create a new journal entry."""
    try:
        entry = Entry(
            work=entry_data.work,
            struggle=entry_data.struggle,
            intention=entry_data.intention,
        )

        created_entry = await entry_service.create_entry(entry.model_dump())

        return {"detail": "Entry created successfully", "entry": created_entry}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entries/{entry_id}", response_model=Entry)
async def get_single_entry(
    entry_id: str,
    entry_service: EntryService = Depends(get_entry_service),
):
    """Get a single journal entry by ID."""
    entry = await entry_service.get_entry(entry_id)

    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")

    return entry

@router.delete("/entries/{entry_id}")
async def delete_entry(
    entry_id: str,
    entry_service: EntryService = Depends(get_entry_service),
):
    """Delete a single journal entry by ID."""
    deleted = await entry_service.delete_entry(entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"detail": "Entry deleted successfully"}

@router.post("/entries/{entry_id}/analyze")
async def analyze_entry(
    entry_id: str, 
    entry_service: EntryService = Depends(get_entry_service)
):
    """Analyze a journal entry using AI."""
    entry = await entry_service.get_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    analysis = await analyze_journal_entry(entry)
    return {**analysis, "entry_id": entry_id}

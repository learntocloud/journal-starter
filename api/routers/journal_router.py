from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException

from api.models.entry import Entry, EntryCreate
from api.repositories.postgres_repository import PostgresDB
from api.services.entry_service import EntryService
from api.services.llm_service import analyze_journal_entry

router = APIRouter()


async def get_entry_service() -> AsyncGenerator[EntryService, None]:
    async with PostgresDB() as db:
        yield EntryService(db)

@router.post("/entries")
async def create_entry(entry_data: EntryCreate, entry_service: EntryService = Depends(get_entry_service)):
    """Create a new journal entry."""
    try:
        entry = Entry(
            work=entry_data.work,
            struggle=entry_data.struggle,
            intention=entry_data.intention
        )
        created_entry = await entry_service.create_entry(entry.model_dump())
        return {
            "detail": "Entry created successfully",
            "entry": created_entry
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating entry: {str(e)}") from e

@router.get("/entries")
async def get_all_entries(entry_service: EntryService = Depends(get_entry_service)):
    """Get all journal entries."""
    result = await entry_service.get_all_entries()
    return {"entries": result, "count": len(result)}

@router.get("/entries/{entry_id}")
async def get_entry(entry_id: str, entry_service: EntryService = Depends(get_entry_service)):
    """Get a single journal entry by ID."""
    entry = await entry_service.get_entry(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry

@router.patch("/entries/{entry_id}")
async def update_entry(entry_id: int, entry_update: EntryUpdate, ...):
    """Update a journal entry."""
    result = await entry_service.update_entry(entry_id, entry_update)
    if not result:
        raise HTTPException(status_code=404, detail="Entry not found")
    return result

@router.delete("/entries/{entry_id}")
async def delete_entry(entry_id: str, entry_service: EntryService = Depends(get_entry_service)):
    """Delete a specific journal entry."""
    entry = await entry_service.get_entry(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    await entry_service.delete_entry(entry_id)
    return {"detail": "Entry deleted successfully"}

@router.delete("/entries")
async def delete_all_entries(entry_service: EntryService = Depends(get_entry_service)):
    """Delete all journal entries."""
    await entry_service.delete_all_entries()
    return {"detail": "All entries deleted"}

@router.post("/entries/{entry_id}/analyze")
async def analyze_entry(entry_id: str, entry_service: EntryService = Depends(get_entry_service)):
    """Analyze a journal entry using AI."""
    entry = await entry_service.get_entry(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")

    entry_text = f"Work: {entry['work']}\nStruggle: {entry['struggle']}\nIntention: {entry['intention']}"

    try:
        analysis = await analyze_journal_entry(entry_id, entry_text)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

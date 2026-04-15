from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException

from api.config import Settings, get_settings
from api.models.entry import AnalysisResponse, Entry, EntryCreate, EntryUpdate
from api.repositories.postgres_repository import PostgresDB
from api.services.entry_service import EntryService
from api.services.llm_service import analyze_journal_entry

router = APIRouter()


async def get_entry_service(
    settings: Settings = Depends(get_settings),
) -> AsyncGenerator[EntryService]:
    async with PostgresDB(settings.database_url) as db:
        yield EntryService(db)


@router.post("/entries", status_code=201)
async def create_entry(
    entry_data: EntryCreate, entry_service: EntryService = Depends(get_entry_service)
):
    """Create a new journal entry."""
    # Create the full entry with auto-generated fields
    entry = Entry(
        work=entry_data.work, struggle=entry_data.struggle, intention=entry_data.intention
    )

    # Store the entry in the database
    created_entry = await entry_service.create_entry(entry.model_dump())

    # Return success response (FastAPI handles datetime serialization automatically)
    return {"detail": "Entry created successfully", "entry": created_entry}


# Implements GET /entries endpoint to list all journal entries
# Example response: [{"id": "123", "work": "...", "struggle": "...", "intention": "..."}]
@router.get("/entries")
async def get_all_entries(entry_service: EntryService = Depends(get_entry_service)):
    """Get all journal entries."""
    result = await entry_service.get_all_entries()
    return {"entries": result, "count": len(result)}


@router.get("/entries/{entry_id}")
async def get_entry(entry_id: str, entry_service: EntryService = Depends(get_entry_service)):
    """
    TODO: Implement this endpoint to return a single journal entry by ID

    Steps to implement:
    1. Use entry_service.get_entry(entry_id) to fetch the entry
    2. If entry is None, raise HTTPException with status_code=404
    3. Return the entry directly (not wrapped in a dict)

    Example response (status 200):
    {
        "id": "uuid-string",
        "work": "...",
        "struggle": "...",
        "intention": "...",
        "created_at": "...",
        "updated_at": "..."
    }

    Hint: Check the update_entry endpoint for similar patterns
    """

    entry = await entry_service.get_entry(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@router.patch("/entries/{entry_id}")
async def update_entry(
    entry_id: str,
    entry_update: EntryUpdate,
    entry_service: EntryService = Depends(get_entry_service),
):
    update_dict = entry_update.model_dump(exclude_unset=True)
    """Update a journal entry.

    TODO (Task 3): Replace ``entry_update: dict`` with ``entry_update: EntryUpdate``
    (import it from ``api.models.entry``) so PATCH requests are validated the
    same way POST requests are. Without this, PATCH happily accepts
    empty strings and 300-character bodies — see ``TestUpdateEntry`` in
    tests/test_api.py.
    """
    result = await entry_service.update_entry(entry_id, update_dict)
    if not result:
        raise HTTPException(status_code=404, detail="Entry not found")
    return result


# TODO: Implement DELETE /entries/{entry_id} endpoint to remove a specific entry
# Return 404 if entry not found
@router.delete("/entries/{entry_id}")
async def delete_entry(entry_id: str, entry_service: EntryService = Depends(get_entry_service)):
    """
    TODO: Implement this endpoint to delete a specific journal entry

    Steps to implement:
    1. Use entry_service.get_entry(entry_id) to check if entry exists
    2. If entry is None, raise HTTPException with status_code=404
    3. Use entry_service.delete_entry(entry_id) to delete the entry
    4. Return a success response (status 200)

    Example response (status 200):
    {"detail": "Entry deleted successfully"}

    Hint: Look at how the update_entry endpoint checks for existence
    """
    entry = await entry_service.get_entry(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")

    await entry_service.delete_entry(entry_id)
    return {"detail": "Entry deleted successfully"}


@router.delete("/entries")
async def delete_all_entries(entry_service: EntryService = Depends(get_entry_service)):
    """Delete all journal entries"""
    await entry_service.delete_all_entries()
    return {"detail": "All entries deleted"}


@router.post("/entries/{entry_id}/analyze", response_model=AnalysisResponse)
async def analyze_entry(entry_id: str, entry_service: EntryService = Depends(get_entry_service)):
    """
    Analyze a journal entry using AI.

    Returns sentiment, summary, key topics, entry_id, and created_at timestamp.
    The LLM call itself lives in api/services/llm_service.py - implementing
    analyze_journal_entry there is part of the capstone.
    """
    entry = await entry_service.get_entry(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")

    entry_text = f"{entry['work']} {entry['struggle']} {entry['intention']}"

    try:
        return await analyze_journal_entry(entry_id, entry_text)
    except NotImplementedError as e:
        raise HTTPException(
            status_code=501,
            detail="LLM analysis not yet implemented - see api/services/llm_service.py",
        ) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e!s}") from e

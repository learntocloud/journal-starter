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
async def create_entry(entry_data: EntryCreate, entry_service: EntryService = Depends(get_entry_service)):
    """Create a new journal entry."""
    try:
        # Create the full entry with auto-generated fields
        entry = Entry(
            work=entry_data.work,
            struggle=entry_data.struggle,
            intention=entry_data.intention
        )

        # Store the entry in the database
        created_entry = await entry_service.create_entry(entry.model_dump())

        # Return success response (FastAPI handles datetime serialization automatically)
        return {
            "detail": "Entry created successfully",
            "entry": created_entry
        }
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error creating entry: {str(e)}") from e

# Implements GET /entries endpoint to list all journal entries
# Example response: [{"id": "123", "work": "...", "struggle": "...", "intention": "..."}]


@router.get("/entries")
async def get_all_entries(entry_service: EntryService = Depends(get_entry_service)):
    """Get all journal entries."""
    result = await entry_service.get_all_entries()
    return {"entries": result, "count": len(result)}


@router.get("/entries/{entry_id}")
async def get_entry(entry_id: str, entry_service: EntryService = Depends(get_entry_service)):
    # Get single entry by ID
    # Checking if entry_service is not empty
    result = await entry_service.get_entry(entry_id)
    if not result:

        raise HTTPException(status_code=404, detail="Entry not found")

    return result


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


@router.patch("/entries/{entry_id}")
async def update_entry(entry_id: str, entry_update: dict, entry_service: EntryService = Depends(get_entry_service)):
    """Update a journal entry"""
    result = await entry_service.update_entry(entry_id, entry_update)
    if not result:

        raise HTTPException(status_code=404, detail="Entry not found")

    return result

# TODO: Implement DELETE /entries/{entry_id} endpoint to remove a specific entry
# Return 404 if entry not found


@router.delete("/entries/{entry_id}")
async def delete_entry(entry_id: str, entry_service: EntryService = Depends(get_entry_service)):
    result = await entry_service.get_entry(entry_id)
    if not result:
        raise HTTPException(status_code=404, detail="Entry not found")

    await entry_service.delete_entry(entry_id)
    return {"detail": "Entry deleted successfully"}

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
    raise HTTPException(
        status_code=501, detail="Not implemented - complete this endpoint!")


@router.delete("/entries")
async def delete_all_entries(entry_service: EntryService = Depends(get_entry_service)):
    """Delete all journal entries"""
    await entry_service.delete_all_entries()
    return {"detail": "All entries deleted"}


@router.post("/entries/{entry_id}/analyze")
async def analyze_entry(entry_id: str, entry_service: EntryService = Depends(get_entry_service)):
    """
    Analyze a journal entry using AI.

    Returns sentiment, summary, key topics, entry_id, and created_at timestamp.

    Response format:
    {
        "entry_id": "string",
        "sentiment": "positive | negative | neutral",
        "summary": "2 sentence summary of the entry",
        "topics": ["topic1", "topic2", "topic3"],
        "created_at": "timestamp"
    }

    TODO: Implement this endpoint. Steps:
    1. Fetch the entry from database using entry_service.get_entry(entry_id)
    2. Return 404 if entry not found
    3. Combine work + struggle + intention into text
    4. Call llm_service.analyze_journal_entry(entry_id, entry_text)
    5. Return the analysis result
    6. Wrap the LLM call in try/except to handle errors gracefully:
       - Catch NotImplementedError and return 501
       - Catch other exceptions and return 500 with a helpful detail message

    Example error handling:
        try:
            analysis = await analyze_journal_entry(entry_id, entry_text)
        except NotImplementedError:
            raise HTTPException(status_code=501, detail="LLM analysis not yet implemented")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    """
    raise HTTPException(
        status_code=501, detail="Implement this endpoint - see Learn to Cloud curriculum")

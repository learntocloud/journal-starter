import logging
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException, Request, Depends
from repositories.postgres_repository import PostgresDB
from services.entry_service import EntryService
from models.entry import Entry, EntryCreate


router = APIRouter()

# TODO: Add authentication middleware
# TODO: Add request validation middleware
# TODO: Add rate limiting middleware
# TODO: Add API versioning
# TODO: Add response caching

async def get_entry_service() -> AsyncGenerator[EntryService, None]:
    async with PostgresDB() as db:
        yield EntryService(db)

@router.post("/entries/")
async def create_entry(entry_data: EntryCreate, entry_service: EntryService = Depends(get_entry_service)):
    """Create a new journal entry."""
    try:
        # Create the full entry with auto-generated fields
        entry = Entry(
            work=entry_data.work,
            struggle=entry_data.struggle, 
            intention=entry_data.intention
        )
        
        # Convert to dict but keep datetime objects for database
        entry_dict = entry.model_dump()
        
        # Store the entry in the database (datetime objects are fine for PostgreSQL)
        created_entry = await entry_service.db.create_entry(entry_dict)
        
        # Return success response (FastAPI handles datetime serialization automatically)
        return {
            "detail": "Entry created successfully", 
            "entry": created_entry
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating entry: {str(e)}")

# TODO: Implement GET /entries endpoint to list all journal entries
# Example response: [{"id": "123", "work": "...", "struggle": "...", "intention": "..."}]
@router.get("/entries")
async def get_all_entries(entry_service: EntryService = Depends(get_entry_service)):
    """Get all journal entries."""
    try:
        entries = await entry_service.get_all_entries()
        return {"entries": entries, "count": len(entries)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving entries: {str(e)}")

@router.get("/entries/{entry_id}")
async def get_entry(request: Request, entry_id: str, entry_service: EntryService = Depends(get_entry_service)):
    """
    TODO: Implement this endpoint to return a single journal entry by ID
    
    Steps to implement:
    1. Use the entry_service to get the entry by ID
    2. Return 404 if entry not found
    3. Return the entry as JSON if found
    
    Hint: Check the update_entry endpoint for similar patterns
    """
    entry = await entry_service.get_entry(entry_id)
    if entry:
        return entry
    else:
        raise HTTPException(status_code=404, detail="Entry not found")

@router.patch("/entries/{entry_id}")
async def update_entry(request: Request, entry_id: str, entry_update: dict):
    async with PostgresDB() as db:
        entry_service = EntryService(db)
        result = await entry_service.update_entry(entry_id, entry_update)
    if not result:
    
        raise HTTPException(status_code=404, detail="Entry not found")
  
    return result

# TODO: Implement DELETE /entries/{entry_id} endpoint to remove a specific entry
# Return 404 if entry not found
@router.delete("/entries/{entry_id}")
async def delete_entry(request: Request, entry_id: str, entry_service: EntryService = Depends(get_entry_service)):
    """
    TODO: Implement this endpoint to delete a specific journal entry
    
    Steps to implement:
    1. Check if the entry exists first
    2. Delete the entry using entry_service
    3. Return appropriate response
    4. Return 404 if entry not found
    
    Hint: Look at how the update_entry endpoint checks for existence
    """
    raise HTTPException(status_code=501, detail="Not implemented - complete this endpoint!")

@router.delete("/entries")
async def delete_all_entries(request: Request):
   
    async with PostgresDB() as db:
        entry_service = EntryService(db)
        await entry_service.delete_all_entries()

    return {"detail": "All entries deleted"}
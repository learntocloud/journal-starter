import logging
from typing import AsyncGenerator, List
from fastapi import APIRouter, HTTPException, Request, Depends, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from api.repositories.postgres_repository import PostgresDB
from api.services import EntryService
from api.schemas import EntryCreateSchema, EntryResponseSchema, EntryUpdateSchema


router = APIRouter()

# TODO: Add authentication middleware
# TODO: Add request validation middleware
# TODO: Add rate limiting middleware
# TODO: Add API versioning
# TODO: Add response caching


async def get_entry_service() -> AsyncGenerator[EntryService, None]:
    async with PostgresDB() as db:
        yield EntryService(db)


@router.post("/entries", response_model=EntryResponseSchema, status_code=201)
async def create_entry(
    request: Request,
    entry: EntryCreateSchema,
    entry_service: EntryService = Depends(get_entry_service),
):
    entry_data = entry.dict(exclude={"id", "created_at", "updated_at"})
    async with PostgresDB() as db:
        entry_service = EntryService(db)
        try:
            enriched_entry = await entry_service.create_entry(entry_data)
            await entry_service.db.create_entry(enriched_entry)

        except HTTPException as e:
            if e.status_code == 409:
                raise HTTPException(
                    status_code=409, detail="You already have an entry for today."
                )
            raise e
    return JSONResponse(
        content={"detail": "Entry created successfully"}, status_code=201
    )


# TODO: Implement GET /entries endpoint to list all journal entries
# Example response: [{"id": "123", "work": "...", "struggle": "...", "intention": "..."}]
@router.get("/entries", response_model=List[EntryResponseSchema])
async def get_all_entries(
    request: Request, entry_service: EntryService = Depends(get_entry_service)
):
    # TODO: Implement get all entries endpoint
    # Hint: Use PostgresDB and EntryService like other endpoints
    async with PostgresDB() as db:
        entry_service = EntryService(db)
        result = await entry_service.get_all_entries()
    if not result:
        raise HTTPException(status_code=404, detail="No Entry found")

    formatted_entries = [
        {
            "id": entry["id"],
            "work": entry["data"]["work"],
            "struggle": entry["data"]["struggle"],
            "intention": entry["data"]["intention"],
            "created_at": entry["created_at"],
            "updated_at": entry["updated_at"],
        }
        for entry in result
    ]

    return formatted_entries


@router.get("/entries/{entry_id}", response_model=EntryResponseSchema)
async def get_entry(
    request: Request,
    entry_id: str,
    entry_service: EntryService = Depends(get_entry_service),
):
    # TODO: Implement get single entry endpoint
    # Hint: Return 404 if entry not found
    async with PostgresDB() as db:
        entry_service = EntryService(db)
        result = await entry_service.get_entry(entry_id)
    if not result:
        raise HTTPException(status_code=404, detail="Entry not found")

    formatted_entry = {
        "id": result["id"],
        "work": result["data"]["work"],
        "struggle": result["data"]["struggle"],
        "intention": result["data"]["intention"],
        "created_at": result["created_at"],
        "updated_at": result["updated_at"],
    }

    return formatted_entry


@router.patch("/entries/{entry_id}", response_model=EntryResponseSchema)
async def update_entry(
    request: Request,
    entry_id: str,
    entry_update: EntryUpdateSchema,
    entry_service: EntryService = Depends(get_entry_service),
):
    update_data = entry_update.dict(exclude_unset=True)
    async with PostgresDB() as db:
        entry_service = EntryService(db)
        result = await entry_service.update_entry(entry_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Entry not found")

    return result


# TODO: Implement DELETE /entries/{entry_id} endpoint to remove a specific entry
# Return 404 if entry not found
@router.delete("/entries/{entry_id}")
async def delete_entry(
    request: Request,
    entry_id: str,
    entry_service: EntryService = Depends(get_entry_service),
):
    # TODO: Implement delete entry endpoint
    # Hint: Return 404 if entry not found
    async with PostgresDB() as db:
        entry_service = EntryService(db)
        deleted = await entry_service.delete_entry(entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Entry not found")

    return Response(status_code=204)


@router.delete("/entries")
async def delete_all_entries(
    request: Request, entry_service: EntryService = Depends(get_entry_service)
):
    async with PostgresDB() as db:
        entry_service = EntryService(db)
        await entry_service.delete_all_entries()

    return {"detail": "All entries deleted"}

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
    entry = Entry(
        work=entry_data.work, struggle=entry_data.struggle, intention=entry_data.intention
    )
    created_entry = await entry_service.create_entry(entry.model_dump())
    return {"detail": "Entry created successfully", "entry": created_entry}


@router.get("/entries")
async def get_all_entries(entry_service: EntryService = Depends(get_entry_service)):
    result = await entry_service.get_all_entries()
    return {"entries": result, "count": len(result)}


@router.get("/entries/{entry_id}")
async def get_entry(entry_id: str, entry_service: EntryService = Depends(get_entry_service)):
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
    update_data = entry_update.model_dump(exclude_unset=True)
    result = await entry_service.update_entry(entry_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Entry not found")
    return result


@router.delete("/entries/{entry_id}")
async def delete_entry(entry_id: str, entry_service: EntryService = Depends(get_entry_service)):
    entry = await entry_service.get_entry(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")

    await entry_service.delete_entry(entry_id)
    return {"detail": "Entry deleted successfully"}


@router.delete("/entries")
async def delete_all_entries(entry_service: EntryService = Depends(get_entry_service)):
    await entry_service.delete_all_entries()
    return {"detail": "All entries deleted"}


@router.post("/entries/{entry_id}/analyze", response_model=AnalysisResponse)
async def analyze_entry(entry_id: str, entry_service: EntryService = Depends(get_entry_service)):
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

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.entry import EntryCreate, EntryUpdate, EntryOut
from app.services.entry_service import EntryService
from app.db.session import get_db

router = APIRouter(prefix="/entries", tags=["Journal Entries"])


def get_entry_service(db: AsyncSession = Depends(get_db)) -> EntryService:
    """
    Constructs the service with the real DB session.
    In tests, we will monkey-patch this function to return a mock.
    """
    return EntryService(db)


@router.post(
    "/",
    response_model=EntryOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_entry(
    entry: EntryCreate,
    service: EntryService = Depends(get_entry_service),
):
    return await service.create_entry(entry)


@router.get(
    "/",
    response_model=List[EntryOut],
)
async def list_entries(
    service: EntryService = Depends(get_entry_service),
):
    return await service.get_all_entries()


@router.get(
    "/{entry_id}",
    response_model=EntryOut,
)
async def get_entry(
    entry_id: str,
    service: EntryService = Depends(get_entry_service),
):
    entry = await service.get_entry_by_id(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@router.put(
    "/{entry_id}",
    response_model=EntryOut,
)
async def update_entry(
    entry_id: str,
    updated: EntryUpdate,
    service: EntryService = Depends(get_entry_service),
):
    entry = await service.update_entry(entry_id, updated)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_entry(
    entry_id: str,
    service: EntryService = Depends(get_entry_service),
):
    success = await service.delete_entry(entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entry not found")

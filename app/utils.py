from fastapi import HTTPException
from api.models import DailyEntry, DailyEntryUpdate

def get_entry_model(entry_type: str):
    if entry_type == "daily":
        return DailyEntry
    else:
        raise HTTPException(status_code=400, detail="Invalid entry type")

def get_entry_update_model(entry_type: str):
    if entry_type == "daily":
        return DailyEntryUpdate
    else:
        raise HTTPException(status_code=400, detail="Invalid entry type")
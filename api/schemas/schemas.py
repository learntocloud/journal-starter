from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EntryCreateSchema(BaseModel):
    work: str
    struggle: str
    intention: str

    class Config:
        from_attributes = True


class EntryUpdateSchema(BaseModel):
    work: Optional[str] = None
    struggle: Optional[str] = None
    intention: Optional[str] = None

    class Config:
        from_attributes = True


class EntryResponseSchema(BaseModel):
    id: str
    work: str
    struggle: str
    intention: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

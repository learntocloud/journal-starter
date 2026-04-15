from datetime import UTC, datetime
from typing import Annotated
from uuid import uuid4

from pydantic import BaseModel, Field, StringConstraints

ValidText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=256)]


class AnalysisResponse(BaseModel):
    entry_id: str = Field(description="ID of the analyzed entry")
    sentiment: str = Field(description="Sentiment: positive, negative, or neutral")
    summary: str = Field(description="2 sentence summary of the entry")
    topics: list[str] = Field(description="2-4 key topics mentioned in the entry")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when the analysis was created",
    )


class EntryCreate(BaseModel):
    work: ValidText = Field(
        description="What did you work on today?",
        json_schema_extra={"example": "Studied FastAPI and built my first API endpoints"},
    )
    struggle: ValidText = Field(
        description="What's one thing you struggled with today?",
        json_schema_extra={"example": "Understanding async/await syntax and when to use it"},
    )
    intention: ValidText = Field(
        description="What will you study/work on tomorrow?",
        json_schema_extra={"example": "Practice PostgreSQL queries and database design"},
    )


class EntryUpdate(BaseModel):
    work: ValidText | None = None
    struggle: ValidText | None = None
    intention: ValidText | None = None


class Entry(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid4()), description="Unique identifier for the entry (UUID)."
    )
    work: str = Field(..., max_length=256, description="What did you work on today?")
    struggle: str = Field(
        ..., max_length=256, description="What's one thing you struggled with today?"
    )
    intention: str = Field(..., max_length=256, description="What will you study/work on tomorrow?")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when the entry was created.",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when the entry was last updated.",
    )

from datetime import UTC, datetime
from typing import Annotated
from uuid import uuid4

from pydantic import BaseModel, Field, StringConstraints

_ValidatedStr = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=256),
]


class AnalysisResponse(BaseModel):
    """Response model for journal entry analysis."""

    entry_id: str = Field(description="ID of the analyzed entry")
    sentiment: str = Field(description="Sentiment: positive, negative, or neutral")
    summary: str = Field(description="2 sentence summary of the entry")
    topics: list[str] = Field(description="2-4 key topics mentioned in the entry")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when the analysis was created",
    )


class EntryCreate(BaseModel):
    """Model for creating a new journal entry (user input)."""

    work: _ValidatedStr = Field(
        description="What did you work on today?",
        json_schema_extra={"example": "Studied FastAPI and built my first API endpoints"},
    )
    struggle: _ValidatedStr = Field(
        description="What's one thing you struggled with today?",
        json_schema_extra={"example": "Understanding async/await syntax and when to use it"},
    )
    intention: _ValidatedStr = Field(
        description="What will you study/work on tomorrow?",
        json_schema_extra={"example": "Practice PostgreSQL queries and database design"},
    )


class EntryUpdate(BaseModel):
    """Model for updating a journal entry (PATCH). All fields optional."""

    work: _ValidatedStr | None = Field(default=None, description="What did you work on today?")
    struggle: _ValidatedStr | None = Field(
        default=None, description="What's one thing you struggled with today?"
    )
    intention: _ValidatedStr | None = Field(
        default=None, description="What will you study/work on tomorrow?"
    )


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

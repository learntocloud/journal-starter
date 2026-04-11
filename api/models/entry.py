from datetime import UTC, datetime
from typing import Annotated
from uuid import uuid4

from pydantic import BaseModel, Field, StringConstraints


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
    """Model for creating a new journal entry (user input).

    All fields are validated to:
      - Reject empty strings and whitespace-only input (min_length=1)
      - Strip surrounding whitespace automatically
      - Enforce maximum length of 256 characters
    """

    work: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=256)] = (
        Field(
            description="What did you work on today?",
            json_schema_extra={"example": "Studied FastAPI and built my first API endpoints"},
        )
    )
    struggle: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=256)
    ] = Field(
        description="What's one thing you struggled with today?",
        json_schema_extra={"example": "Understanding async/await syntax and when to use it"},
    )
    intention: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=256)
    ] = Field(
        description="What will you study/work on tomorrow?",
        json_schema_extra={"example": "Practice PostgreSQL queries and database design"},
    )


class EntryUpdate(BaseModel):
    """Model for updating a journal entry (PATCH requests).

    All fields are optional to support partial updates.
    When provided, each field follows the same validation rules as EntryCreate:
      - Rejects empty strings and whitespace-only input
      - Strips surrounding whitespace
      - Maximum length of 256 characters
    """

    work: (
        Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=256)]
        | None
    ) = Field(
        default=None,
        description="What did you work on today?",
        json_schema_extra={"example": "Studied FastAPI and built my first API endpoints"},
    )
    struggle: (
        Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=256)]
        | None
    ) = Field(
        default=None,
        description="What's one thing you struggled with today?",
        json_schema_extra={"example": "Understanding async/await syntax and when to use it"},
    )
    intention: (
        Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=256)]
        | None
    ) = Field(
        default=None,
        description="What will you study/work on tomorrow?",
        json_schema_extra={"example": "Practice PostgreSQL queries and database design"},
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

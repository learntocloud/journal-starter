from datetime import UTC, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

AnalysisText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class AnalysisResponse(BaseModel):
    """Response model for journal entry analysis."""

    model_config = ConfigDict(hide_input_in_errors=True)

    entry_id: str = Field(description="ID of the analyzed entry")
    sentiment: Literal["positive", "negative", "neutral"] = Field(
        description="Sentiment: positive, negative, or neutral"
    )
    summary: AnalysisText = Field(
        description="Nonempty summary of the entry; aim for two sentences"
    )
    topics: list[AnalysisText] = Field(
        min_length=2, max_length=4, description="2-4 nonempty key topics mentioned in the entry"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when the analysis was created",
    )


# TODO (Task 2): Complete the shared write-input rules: strip surrounding
# whitespace and require 1-256 characters after trimming. Keep strict=True.
# EntryCreate and EntryUpdate both use this type; leave the Entry read model alone.
# See docs/06-input-validation.md for the exercise walkthrough.
EntryText = Annotated[str, StringConstraints(strict=True, max_length=256)]


class EntryCreate(BaseModel):
    """Input fields for creating a new journal entry."""

    work: EntryText = Field(
        description="What did you work on today?",
        json_schema_extra={"example": "Studied FastAPI and built my first API endpoints"},
    )
    struggle: EntryText = Field(
        description="What's one thing you struggled with today?",
        json_schema_extra={"example": "Understanding async/await syntax and when to use it"},
    )
    intention: EntryText = Field(
        description="What will you study/work on tomorrow?",
        json_schema_extra={"example": "Practice PostgreSQL queries and database design"},
    )


class EntryUpdate(BaseModel):
    """Fields to change in a journal entry. Omit fields to leave them unchanged."""

    # Supplied plumbing: factories keep the omission placeholder out of the input
    # schema. Defaults are not validated; explicitly supplied values are.
    work: EntryText | None = Field(default_factory=lambda: None)
    struggle: EntryText | None = Field(default_factory=lambda: None)
    intention: EntryText | None = Field(default_factory=lambda: None)

    @field_validator(
        "work", "struggle", "intention", mode="before", json_schema_input_type=EntryText
    )
    @classmethod
    def reject_null(cls, value: object) -> object:
        """Reject explicit null and describe the accepted input type in the schema."""
        if value is None:
            raise ValueError("Supplied fields must contain text, not null")
        return value


class Entry(BaseModel):
    """A persisted entry. The service, not response validation, creates metadata."""

    id: str = Field(description="Unique identifier for the entry (UUID).")
    work: str = Field(description="What did you work on today?")
    struggle: str = Field(description="What's one thing you struggled with today?")
    intention: str = Field(description="What will you study/work on tomorrow?")
    created_at: datetime = Field(
        description="Timestamp when the entry was created.",
    )
    updated_at: datetime = Field(
        description="Timestamp when the entry was last updated.",
    )


class EntryCreatedResponse(BaseModel):
    detail: str
    entry: Entry


class EntryListResponse(BaseModel):
    entries: list[Entry]
    count: int


class DetailResponse(BaseModel):
    detail: str

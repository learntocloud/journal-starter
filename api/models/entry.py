from datetime import UTC, datetime
from typing import Annotated, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, StringConstraints

AnalysisText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class AnalysisResponse(BaseModel):
    """Response model for journal entry analysis."""

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


class EntryCreate(BaseModel):
    """Model for creating a new journal entry (user input).

    TODO (Task 3): Add validation so that ``work``, ``struggle``, and ``intention``:
      - reject empty strings and whitespace-only input
      - strip surrounding whitespace
      - have a max length of 256 characters

    Hint: wrap the field type in ``Annotated[str, StringConstraints(...)]``.
    See https://docs.pydantic.dev/latest/concepts/types/#constrained-types
    """

    work: str = Field(
        max_length=256,
        description="What did you work on today?",
        json_schema_extra={"example": "Studied FastAPI and built my first API endpoints"},
    )
    struggle: str = Field(
        max_length=256,
        description="What's one thing you struggled with today?",
        json_schema_extra={"example": "Understanding async/await syntax and when to use it"},
    )
    intention: str = Field(
        max_length=256,
        description="What will you study/work on tomorrow?",
        json_schema_extra={"example": "Practice PostgreSQL queries and database design"},
    )


# TODO (Task 3): Define an ``EntryUpdate`` model for PATCH /entries/{entry_id}.
#
# Requirements:
#   - All three fields (``work``, ``struggle``, ``intention``) may be omitted.
#     Omitted fields default to None internally; explicit JSON null is invalid.
#   - Each field, when provided, must follow the same validation rules as
#     ``EntryCreate`` (non-empty, whitespace-stripped, max 256 chars).
#   - An empty update is allowed and leaves the entry's text fields unchanged.
#
# Once defined, import ``EntryUpdate`` in ``api/routers/journal_router.py``
# and use it as the type of the PATCH endpoint's request body. Pass only
# explicitly supplied fields to the service with model_dump(exclude_unset=True).
# Hint: a field_validator can reject explicit None without rejecting omitted fields.


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

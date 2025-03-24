from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, timezone
from uuid import uuid4
import bleach


Base = declarative_base()


class Entries(Base):
    __tablename__ = "entries"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    data = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )


class Entry(BaseModel):
    # TODO: Add field validation rules
    # TODO: Add custom validators
    # TODO: Add schema versioning
    # TODO: Add data sanitization methods

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for the entry (UUID).",
    )
    work: str = Field(..., max_length=256, description="What did you work on today?")
    struggle: str = Field(
        ..., max_length=256, description="What’s one thing you struggled with today?"
    )
    intention: str = Field(
        ..., max_length=256, description="What will you study/work on tomorrow?"
    )
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the entry was created.",
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the entry was last updated.",
    )
    # Optional: add a partition key if your Cosmos DB collection requires it
    # partition_key: str = Field(..., description="Partition key for the entry.")

    @field_validator("work", "struggle", "intention")
    def sanitize(cls, value):
        return bleach.clean(value)

    class Config:
        # This can help with how the model serializes field names if needed by Cosmos DB.
        # For example, if Cosmos DB requires a specific field naming convention.
        # allow_population_by_field_name = True
        from_attributes = True

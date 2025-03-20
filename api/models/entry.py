from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import uuid4

class Entry(BaseModel):
    # TODO: Add field validation rules
    # TODO: Add custom validators
    # TODO: Add schema versioning
    # TODO: Add data sanitization methods
    
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for the entry (UUID)."
    )
    work: str = Field(
        ...,
        max_length=256,
        description="What did you work on today?"
    )
    struggle: str = Field(
        ...,
        max_length=256,
        description="What’s one thing you struggled with today?"
    )
    intention: str = Field(
        ...,
        max_length=256,
        description="What will you study/work on tomorrow?"
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the entry was created."
    )
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the entry was last updated."
    )
    # Optional: add a partition key if your Cosmos DB collection requires it
    # partition_key: str = Field(..., description="Partition key for the entry.")

    class Config:
        # This can help with how the model serializes field names if needed by Cosmos DB.
        # For example, if Cosmos DB requires a specific field naming convention.
        # allow_population_by_field_name = True
        pass

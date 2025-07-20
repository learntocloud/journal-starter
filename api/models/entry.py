from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, timezone
from uuid import uuid4
import re

_SCHEMA_VERSION = "1.0"

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
        min_length=1,
        max_length=256,
        description="What did you work on today?"
    )
    struggle: str = Field(
        ...,
        min_length=1,
        max_length=256,
        description="What’s one thing you struggled with today?"
    )
    intention: str = Field(
        ...,
        min_length=1,
        max_length=256,
        description="What will you study/work on tomorrow?"
    )
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the entry was created."
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the entry was last updated."
    )

    @field_validator('work', 'struggle', 'intention')
    @classmethod
    def sanitize_content(cls, v):
        if v:
            v = re.sub(r'<[^>]+>', '', v)  # strip HTML tags
            v = v.replace("'", "").replace('"', "").replace(";", "") #Remove common SQL injection characters
            v = v.strip()
        return v
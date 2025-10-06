from pydantic import (
    BaseModel, 
    Field,
    field_validator
)

from typing import Optional
from datetime import datetime
from uuid import uuid4
import re

VALID_FIELDS_REGEX = re.compile(r"^[A-Za-z0-9\s.,!?\-'\"]+$")

class EntryCreate(BaseModel):
    """Model for creating a new journal entry (user input)."""
    work: str = Field(
        max_length=256,
        description="What did you work on today?",
        json_schema_extra={"example": "Studied FastAPI and built my first API endpoints"}
    )
    struggle: str = Field(
        max_length=256,
        description="What's one thing you struggled with today?",
        json_schema_extra={"example": "Understanding async/await syntax and when to use it"}
    )
    intention: str = Field(
        max_length=256,
        description="What will you study/work on tomorrow?",
        json_schema_extra={"example": "Practice PostgreSQL queries and database design"}
    )

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

    @field_validator("work")
    @classmethod
    def validate_work(cls, v:str) -> str:
        '''
        Ensure "work" field is not empty and contains only 
        text with common punctuation

        '''
        if not v or not VALID_FIELDS_REGEX.match(v):
            raise ValueError("Error. Work field cannot be empty and must only contain valid characters")
        return v
    
    struggle: str = Field(
        ...,
        max_length=256,
        description="What’s one thing you struggled with today?"
    )

    @field_validator("struggle")
    @classmethod
    def validate_struggle(cls, v:str) -> str:
        '''
        Ensure "struggle" field is not empty and contains only 
        text with common punctuation
        '''
        if not v or not VALID_FIELDS_REGEX.match(v):
            raise ValueError("Error. Struggle field cannot be empty and must only contain valid characters.")
        return v
    
    intention: str = Field(
        ...,
        max_length=256,
        description="What will you study/work on tomorrow?"
    )

    @field_validator("intention")
    @classmethod
    def validate_intention(cls, v: str) -> str:
        '''
        Ensure "intention" field is not empty and contains only 
        text with common punctuation
        '''
        if not v or not VALID_FIELDS_REGEX.match(v):
            raise ValueError("Error. Intention field cannot be empty and must only contain valid characters")
        return v
    
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the entry was created."
    )
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the entry was last updated."
    )

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }
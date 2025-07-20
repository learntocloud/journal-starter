# from pydantic import BaseModel, Field, field_validator
# from typing import Optional
# from datetime import datetime, timezone
# from uuid import uuid4

# class Entry(BaseModel):
#     # TODO: Add field validation rules
#     # TODO: Add custom validators
#     # TODO: Add schema versioning
#     # TODO: Add data sanitization methods
    
#     id: str = Field(
#         default_factory=lambda: str(uuid4()),
#         description="Unique identifier for the entry (UUID)."
#     )
#     work: Optional[str] = Field(
#         ...,
#         default=None,
#         description="What did you work on today?"
#     )
#     struggle: Optional[str] = Field(
#         ...,
#         default=None,
#         description="What’s one thing you struggled with today?"
#     )
#     intention: Optional[str] = Field(
#         ...,
#         default=None,
#         description="What will you study/work on tomorrow?"
#     )
#     created_at: Optional[datetime] = Field(
#         default_factory=datetime.now(timezone.utc),
#         description="Timestamp when the entry was created."
#     )
#     updated_at: Optional[datetime] = Field(
#         default_factory=datetime.now(timezone.utc),
#         description="Timestamp when the entry was last updated."
#     )

#     @field_validator("work", "struggle", "intention")
#     def length(value):
#         if  256 > len(value):
#             return value
#         raise ValueError("Field must be under 256 characters")

#     @field_validator("work", "struggle", "intention", mode='before')
#     def strip_strings(value):
#         if isinstance(value, str):
#             return value.strip()
#         raise ValueError("Must be a string")

#     @field_validator("work", "struggle", "intention")
#     def non_empty_after_strip(value):
#         if not value:
#             raise ValueError("Field cannot be empty")
#         if len(value.strip()) == 0:
#             raise ValueError("Field cannot be only whitespace")
#         return value


# test = Entry(work="Today i work.")

# print(test)
#     # Optional: add a partition key if your Cosmos DB collection requires it
#     # partition_key: str = Field(..., description="Partition key for the entry.")

#     # class Config:
#     #     # This can help with how the model serializes field names if needed by Cosmos DB.
#     #     # For example, if Cosmos DB requires a specific field naming convention.
#     #     # allow_population_by_field_name = True
#     #     pass

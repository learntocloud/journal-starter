import logging
import traceback
from json import JSONDecodeError
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from openai import APIStatusError, APITimeoutError, OpenAIError, RateLimitError
from pydantic import ValidationError

from api.models.entry import (
    AnalysisResponse,
    DetailResponse,
    Entry,
    EntryCreate,
    EntryCreatedResponse,
    EntryListResponse,
)
from api.repositories.interface_repository import DatabaseInterface
from api.services.entry_service import EntryService
from api.services.llm_service import InvalidAnalysisResponseError, analyze_journal_entry

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_database(request: Request) -> DatabaseInterface:
    return request.app.state.database


async def get_entry_service(
    database: Annotated[DatabaseInterface, Depends(get_database)],
) -> EntryService:
    return EntryService(database)


EntryServiceDependency = Annotated[EntryService, Depends(get_entry_service)]


def _log_analysis_failure(entry_id: str, error: Exception) -> None:
    # Keep diagnostic locations, but exclude exception text, source lines, and local values.
    locations = " -> ".join(
        f"{frame.filename}:{frame.lineno} in {frame.name}"
        for frame in traceback.extract_tb(error.__traceback__)
    )
    request_id = error.request_id if isinstance(error, APIStatusError) else None
    logger.error(
        "Analysis failed for entry %s (error_type=%s, request_id=%s, locations=%s)",
        entry_id,
        type(error).__name__,
        request_id,
        locations,
    )


@router.post("/entries", status_code=201)
async def create_entry(
    entry_data: EntryCreate, entry_service: EntryServiceDependency
) -> EntryCreatedResponse:
    """Create a new journal entry."""
    created_entry = await entry_service.create_entry(entry_data)
    return EntryCreatedResponse(detail="Entry created successfully", entry=created_entry)


@router.get("/entries")
async def get_all_entries(entry_service: EntryServiceDependency) -> EntryListResponse:
    """Get all journal entries."""
    result = await entry_service.get_all_entries()
    return EntryListResponse(entries=result, count=len(result))


@router.get("/entries/{entry_id}")
async def get_entry(entry_id: str, entry_service: EntryServiceDependency) -> Entry:
    """Get a journal entry by ID."""
    entry = await entry_service.get_entry(entry_id)

    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")

    return entry


@router.patch("/entries/{entry_id}")
async def update_entry(
    entry_id: str, entry_update: dict[str, str], entry_service: EntryServiceDependency
) -> Entry:
    """Update a journal entry."""
    # TODO (Task 2): Replace ``entry_update: dict[str, str]`` with ``entry_update: EntryUpdate``
    # (import the supplied model from ``api.models.entry``). Complete the shared
    # EntryText string rules there; omission and null handling are already supplied.
    # Then pass ``entry_update.model_dump(exclude_unset=True)`` to the service,
    # which expects a dict. Passing the model itself fails; dumping every field
    # would overwrite omitted fields with their defaults.
    # An empty object is allowed and leaves the text fields unchanged.
    # See ``TestUpdateEntry`` in tests/test_api.py and docs/06-input-validation.md.
    result = await entry_service.update_entry(entry_id, entry_update)
    if result is None:
        raise HTTPException(status_code=404, detail="Entry not found")

    return result


@router.delete("/entries/{entry_id}")
async def delete_entry(entry_id: str, entry_service: EntryServiceDependency) -> DetailResponse:
    """Delete a journal entry by ID."""
    # TODO: Implement this endpoint to delete a specific journal entry.
    #
    # Steps to implement:
    # 1. Use await entry_service.delete_entry(entry_id) exactly once.
    # 2. If it returns False, raise HTTPException with status_code=404.
    # 3. Return DetailResponse(detail="Entry deleted successfully") (status 200).
    #
    # The repository atomically deletes the row and reports whether it existed.
    # Do not fetch the entry first: another request could delete it between calls.
    #
    # Example response (status 200):
    # {"detail": "Entry deleted successfully"}
    #
    # Hint: Look at how the update_entry endpoint checks for existence.
    # See docs/05-delete-entry.md for the exercise walkthrough.
    raise HTTPException(status_code=501, detail="Not implemented - complete this endpoint!")


@router.delete("/entries")
async def delete_all_entries(entry_service: EntryServiceDependency) -> DetailResponse:
    """Delete all journal entries"""
    await entry_service.delete_all_entries()
    return DetailResponse(detail="All entries deleted")


@router.post("/entries/{entry_id}/analyze", response_model=AnalysisResponse)
async def analyze_entry(entry_id: str, entry_service: EntryServiceDependency) -> AnalysisResponse:
    """
    Analyze a journal entry using AI.

    Returns sentiment, summary, key topics, entry_id, and created_at timestamp.
    The LLM call itself lives in api/services/llm_service.py - implementing
    analyze_journal_entry there is part of the capstone.
    """
    entry = await entry_service.get_entry(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")

    entry_text = f"{entry.work} {entry.struggle} {entry.intention}"

    try:
        analysis = await analyze_journal_entry(entry_id, entry_text)
        return AnalysisResponse.model_validate(analysis)
    except NotImplementedError as e:
        raise HTTPException(
            status_code=501,
            detail="LLM analysis not yet implemented - see api/services/llm_service.py",
        ) from e
    except (ValidationError, JSONDecodeError, InvalidAnalysisResponseError) as e:
        _log_analysis_failure(entry_id, e)
        raise HTTPException(
            status_code=502, detail="Analysis provider returned an invalid response"
        ) from e
    except APITimeoutError as e:
        _log_analysis_failure(entry_id, e)
        raise HTTPException(status_code=504, detail="Analysis provider timed out") from e
    except RateLimitError as e:
        _log_analysis_failure(entry_id, e)
        raise HTTPException(
            status_code=503, detail="Analysis provider is temporarily unavailable"
        ) from e
    except OpenAIError as e:
        _log_analysis_failure(entry_id, e)
        raise HTTPException(status_code=502, detail="Analysis provider request failed") from e
    except Exception as e:
        _log_analysis_failure(entry_id, e)
        raise HTTPException(status_code=500, detail="Analysis failed") from e

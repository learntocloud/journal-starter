"""
Tests for the data models (Entry, EntryCreate, AnalysisResponse).

These tests verify that the Pydantic models work correctly, including:
- Field validation
- Default value generation
- Data type checking
- Max length constraints
"""
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from api.models.entry import AnalysisResponse, Entry, EntryCreate


class TestEntryCreateModel:
    """Tests for the EntryCreate model used for API input."""

    def test_entry_create_valid(self):
        """Test creating a valid EntryCreate model."""
        data = {
            "work": "Studied FastAPI",
            "struggle": "Understanding async",
            "intention": "Practice more"
        }
        entry = EntryCreate(**data)

        assert entry.work == data["work"]
        assert entry.struggle == data["struggle"]
        assert entry.intention == data["intention"]

    def test_entry_create_missing_field(self):
        """Test that missing required fields raise validation error."""
        incomplete_data = {
            "work": "Studied FastAPI"
            # Missing struggle and intention
        }

        with pytest.raises(ValidationError):
            EntryCreate(**incomplete_data)

    def test_entry_create_max_length_validation(self):
        """Test that fields exceeding max length are rejected."""
        invalid_data = {
            "work": "a" * 300,  # Exceeds 256 character limit
            "struggle": "Understanding async",
            "intention": "Practice more"
        }

        with pytest.raises(ValidationError):
            EntryCreate(**invalid_data)

    def test_entry_create_empty_strings_allowed(self):
        """Test that empty strings are allowed (only None is invalid)."""
        data = {
            "work": "",
            "struggle": "",
            "intention": ""
        }
        entry = EntryCreate(**data)

        assert entry.work == ""
        assert entry.struggle == ""
        assert entry.intention == ""


class TestEntryModel:
    """Tests for the Entry model used internally and for responses."""

    def test_entry_with_all_fields(self):
        """Test creating an Entry with all fields provided."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "work": "Studied FastAPI",
            "struggle": "Understanding async",
            "intention": "Practice more",
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC)
        }
        entry = Entry(**data)

        assert entry.id == data["id"]
        assert entry.work == data["work"]
        assert entry.struggle == data["struggle"]
        assert entry.intention == data["intention"]
        assert entry.created_at == data["created_at"]
        assert entry.updated_at == data["updated_at"]

    def test_entry_auto_generates_id(self):
        """Test that Entry auto-generates a UUID if not provided."""
        data = {
            "work": "Studied FastAPI",
            "struggle": "Understanding async",
            "intention": "Practice more"
        }
        entry = Entry(**data)

        # ID should be auto-generated
        assert entry.id is not None
        assert len(entry.id) > 0
        # Should be a valid UUID format (basic check)
        assert "-" in entry.id

    def test_entry_auto_generates_timestamps(self):
        """Test that Entry auto-generates created_at and updated_at if not provided."""
        data = {
            "work": "Studied FastAPI",
            "struggle": "Understanding async",
            "intention": "Practice more"
        }
        entry = Entry(**data)

        # Timestamps should be auto-generated
        assert entry.created_at is not None
        assert entry.updated_at is not None
        assert isinstance(entry.created_at, datetime)
        assert isinstance(entry.updated_at, datetime)

    def test_entry_max_length_validation(self):
        """Test that fields exceeding max length are rejected."""
        invalid_data = {
            "work": "a" * 300,
            "struggle": "Understanding async",
            "intention": "Practice more"
        }

        with pytest.raises(ValidationError):
            Entry(**invalid_data)

    def test_entry_model_dump(self):
        """Test that Entry can be serialized to dict."""
        data = {
            "work": "Studied FastAPI",
            "struggle": "Understanding async",
            "intention": "Practice more"
        }
        entry = Entry(**data)

        entry_dict = entry.model_dump()

        assert isinstance(entry_dict, dict)
        assert entry_dict["work"] == data["work"]
        assert entry_dict["struggle"] == data["struggle"]
        assert entry_dict["intention"] == data["intention"]
        assert "id" in entry_dict
        assert "created_at" in entry_dict
        assert "updated_at" in entry_dict


class TestAnalysisResponseModel:
    """Tests for the AnalysisResponse model used for AI analysis results."""

    def test_analysis_response_valid(self):
        """Test creating a valid AnalysisResponse model."""
        data = {
            "entry_id": "123e4567-e89b-12d3-a456-426614174000",
            "sentiment": "positive",
            "summary": "The learner made progress. They're excited to continue.",
            "topics": ["FastAPI", "PostgreSQL", "API development"]
        }
        response = AnalysisResponse(**data)

        assert response.entry_id == data["entry_id"]
        assert response.sentiment == data["sentiment"]
        assert response.summary == data["summary"]
        assert response.topics == data["topics"]
        assert isinstance(response.created_at, datetime)

    def test_analysis_response_auto_generates_timestamp(self):
        """Test that AnalysisResponse auto-generates created_at."""
        data = {
            "entry_id": "123e4567-e89b-12d3-a456-426614174000",
            "sentiment": "neutral",
            "summary": "The learner is making steady progress with their studies.",
            "topics": ["learning", "progress"]
        }
        response = AnalysisResponse(**data)

        assert response.created_at is not None
        assert isinstance(response.created_at, datetime)

    def test_analysis_response_missing_required_field(self):
        """Test that missing required fields raise validation error."""
        incomplete_data = {
            "entry_id": "123e4567-e89b-12d3-a456-426614174000",
            "sentiment": "positive"
            # Missing summary and topics
        }

        with pytest.raises(ValidationError):
            AnalysisResponse(**incomplete_data)

    def test_analysis_response_invalid_topics_type(self):
        """Test that topics must be a list."""
        invalid_data = {
            "entry_id": "123e4567-e89b-12d3-a456-426614174000",
            "sentiment": "positive",
            "summary": "Summary text",
            "topics": "not a list"  # Should be a list
        }

        with pytest.raises(ValidationError):
            AnalysisResponse(**invalid_data)

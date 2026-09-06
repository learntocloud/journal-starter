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

pytestmark = pytest.mark.no_db


class TestEntryCreateModel:
    """Tests for the EntryCreate model used for API input."""

    def test_entry_create_valid(self):
        """Test creating a valid EntryCreate model."""
        data = {
            "work": "Studied FastAPI",
            "struggle": "Understanding async",
            "intention": "Practice more",
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
            "intention": "Practice more",
        }

        with pytest.raises(ValidationError):
            EntryCreate(**invalid_data)


class TestEntryCreateValidation:
    """Task 3 validation tests for EntryCreate."""

    def test_empty_string_rejected(self):
        """Empty strings for any field should be rejected."""
        with pytest.raises(ValidationError):
            EntryCreate(work="", struggle="Some struggle", intention="Some intention")

    def test_whitespace_only_rejected(self):
        """Whitespace-only strings should be rejected after stripping."""
        with pytest.raises(ValidationError):
            EntryCreate(
                work="   ",
                struggle="Some struggle",
                intention="Some intention",
            )

    def test_whitespace_stripped_from_valid_input(self):
        """Leading/trailing whitespace should be stripped from valid input."""
        entry = EntryCreate(
            work="  Studied FastAPI  ",
            struggle="  Understanding async  ",
            intention="  Practice more  ",
        )
        assert entry.work == "Studied FastAPI"
        assert entry.struggle == "Understanding async"
        assert entry.intention == "Practice more"


class TestEntryUpdateModel:
    """Task 3 tests for the EntryUpdate model.

    ``EntryUpdate`` is created by the learner as part of Task 3, so the
    import is intentionally inside each test to avoid failing test
    collection on a fresh fork.
    """

    def test_all_fields_optional(self):
        """EntryUpdate should allow construction with no fields set."""
        from api.models.entry import EntryUpdate  # type: ignore[attr-defined]

        update = EntryUpdate()
        assert update.work is None
        assert update.struggle is None
        assert update.intention is None
        assert update.model_dump(exclude_unset=True) == {}

    def test_partial_update(self):
        """EntryUpdate should allow a single-field update."""
        from api.models.entry import EntryUpdate  # type: ignore[attr-defined]

        update = EntryUpdate(work="New work only")
        assert update.work == "New work only"
        assert update.struggle is None
        assert update.intention is None
        assert update.model_dump(exclude_unset=True) == {"work": "New work only"}

    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    def test_oversize_field_rejected(self, field):
        """EntryUpdate should reject fields longer than 256 characters."""
        from api.models.entry import EntryUpdate  # type: ignore[attr-defined]

        with pytest.raises(ValidationError):
            EntryUpdate(**{field: "a" * 257})

    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    @pytest.mark.parametrize("value", [None, "", " \t\n ", 123, True])
    def test_invalid_supplied_field_rejected(self, field, value):
        from api.models.entry import EntryUpdate  # type: ignore[attr-defined]

        with pytest.raises(ValidationError):
            EntryUpdate(**{field: value})

    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    def test_supplied_field_is_stripped(self, field):
        from api.models.entry import EntryUpdate  # type: ignore[attr-defined]

        update = EntryUpdate(**{field: "  New text  "})
        assert update.model_dump(exclude_unset=True) == {field: "New text"}

    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    def test_max_length_after_stripping_is_allowed(self, field):
        from api.models.entry import EntryUpdate  # type: ignore[attr-defined]

        update = EntryUpdate(**{field: f"  {'a' * 256}  "})
        assert update.model_dump(exclude_unset=True) == {field: "a" * 256}


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
            "updated_at": datetime.now(UTC),
        }
        entry = Entry.model_validate(data)

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
            "intention": "Practice more",
        }
        entry = Entry.model_validate(data)

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
            "intention": "Practice more",
        }
        entry = Entry.model_validate(data)

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
            "intention": "Practice more",
        }

        with pytest.raises(ValidationError):
            Entry.model_validate(invalid_data)

    def test_entry_model_dump(self):
        """Test that Entry can be serialized to dict."""
        data = {
            "work": "Studied FastAPI",
            "struggle": "Understanding async",
            "intention": "Practice more",
        }
        entry = Entry.model_validate(data)

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

    @pytest.mark.parametrize("sentiment", ["positive", "negative", "neutral"])
    def test_analysis_response_valid(self, sentiment):
        """Test creating a valid AnalysisResponse model."""
        data = {
            "entry_id": "123e4567-e89b-12d3-a456-426614174000",
            "sentiment": sentiment,
            "summary": "The learner made progress. They're excited to continue.",
            "topics": ["FastAPI", "PostgreSQL", "API development"],
        }
        response = AnalysisResponse.model_validate(data)

        assert response.entry_id == data["entry_id"]
        assert response.sentiment == data["sentiment"]
        assert response.summary == data["summary"]
        assert response.topics == data["topics"]
        assert isinstance(response.created_at, datetime)

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("sentiment", "mixed"),
            ("sentiment", "Positive"),
            ("sentiment", ""),
            ("sentiment", None),
            ("summary", ""),
            ("summary", " \t\n "),
            ("summary", None),
            ("summary", 123),
            ("topics", []),
            ("topics", ["one"]),
            ("topics", ["one", "two", "three", "four", "five"]),
            ("topics", ["valid", ""]),
            ("topics", ["valid", " \t\n "]),
            ("topics", ["valid", None]),
            ("topics", ["valid", 123]),
        ],
    )
    def test_analysis_response_rejects_invalid_content(self, field, value):
        data = {
            "entry_id": "entry-1",
            "sentiment": "positive",
            "summary": "The learner made progress.",
            "topics": ["APIs", "learning"],
        }
        data[field] = value
        with pytest.raises(ValidationError):
            AnalysisResponse.model_validate(data)

    @pytest.mark.parametrize("count", [2, 3, 4])
    def test_analysis_response_accepts_topic_count_boundaries(self, count):
        response = AnalysisResponse(
            entry_id="entry-1",
            sentiment="neutral",
            summary="A brief summary.",
            topics=[f"Topic {i}" for i in range(count)],
        )
        assert len(response.topics) == count

    def test_analysis_response_strips_summary_and_topics(self):
        response = AnalysisResponse(
            entry_id="entry-1",
            sentiment="positive",
            summary="  Practiced APIs, e.g. request validation.  ",
            topics=["  APIs  ", " validation "],
        )
        assert response.summary == "Practiced APIs, e.g. request validation."
        assert response.topics == ["APIs", "validation"]

    def test_analysis_response_auto_generates_timestamp(self):
        """Test that AnalysisResponse auto-generates created_at."""
        data = {
            "entry_id": "123e4567-e89b-12d3-a456-426614174000",
            "sentiment": "neutral",
            "summary": "The learner is making steady progress with their studies.",
            "topics": ["learning", "progress"],
        }
        response = AnalysisResponse.model_validate(data)

        assert response.created_at is not None
        assert isinstance(response.created_at, datetime)

    def test_analysis_response_missing_required_field(self):
        """Test that missing required fields raise validation error."""
        incomplete_data = {
            "entry_id": "123e4567-e89b-12d3-a456-426614174000",
            "sentiment": "positive",
            # Missing summary and topics
        }

        with pytest.raises(ValidationError):
            AnalysisResponse.model_validate(incomplete_data)

    def test_analysis_response_invalid_topics_type(self):
        """Test that topics must be a list."""
        invalid_data = {
            "entry_id": "123e4567-e89b-12d3-a456-426614174000",
            "sentiment": "positive",
            "summary": "Summary text",
            "topics": "not a list",  # Should be a list
        }

        with pytest.raises(ValidationError):
            AnalysisResponse.model_validate(invalid_data)

"""
Tests for the data models (Entry, EntryCreate, EntryUpdate, AnalysisResponse).

These tests verify that the Pydantic models work correctly, including:
- Field validation
- Default value generation
- Data type checking
- Max length constraints
"""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from api.models.entry import AnalysisResponse, Entry, EntryCreate, EntryUpdate

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

    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    def test_entry_create_missing_field(self, sample_entry_data, field):
        del sample_entry_data[field]
        with pytest.raises(ValidationError) as error:
            EntryCreate.model_validate(sample_entry_data)
        assert [(item["loc"], item["type"]) for item in error.value.errors()] == [
            ((field,), "missing"),
        ]

    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    def test_entry_create_accepts_max_length(self, sample_entry_data, field):
        sample_entry_data[field] = "a" * 256
        entry = EntryCreate.model_validate(sample_entry_data)
        assert getattr(entry, field) == "a" * 256

    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    def test_entry_create_rejects_over_max_length(self, sample_entry_data, field):
        sample_entry_data[field] = "a" * 257
        with pytest.raises(ValidationError) as error:
            EntryCreate.model_validate(sample_entry_data)
        assert [(item["loc"], item["type"]) for item in error.value.errors()] == [
            ((field,), "string_too_long"),
        ]

    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    @pytest.mark.parametrize("value", [None, 123, True, [], {}])
    def test_entry_create_rejects_nonstring_values(self, sample_entry_data, field, value):
        sample_entry_data[field] = value
        with pytest.raises(ValidationError) as error:
            EntryCreate.model_validate(sample_entry_data)
        assert [(item["loc"], item["type"]) for item in error.value.errors()] == [
            ((field,), "string_type"),
        ]


@pytest.mark.exercise
class TestEntryCreateValidation:
    """Task 2 validation tests for EntryCreate."""

    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    @pytest.mark.parametrize("value", ["", " \t\n "])
    def test_empty_and_whitespace_strings_rejected(self, field, value):
        data = {"work": "Some work", "struggle": "Some struggle", "intention": "Some intention"}
        data[field] = value
        with pytest.raises(ValidationError) as error:
            EntryCreate(**data)
        assert [item["loc"] for item in error.value.errors()] == [(field,)]

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

    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    def test_max_length_is_applied_after_stripping(self, field):
        data = {"work": "Some work", "struggle": "Some struggle", "intention": "Some intention"}
        data[field] = f"  {'a' * 256}  "
        assert getattr(EntryCreate(**data), field) == "a" * 256


class TestEntryUpdateModel:
    """Supplied partial-update behavior and Task 2 string validation."""

    def test_all_fields_optional(self):
        """EntryUpdate should allow construction with no fields set."""
        update = EntryUpdate()
        assert update.model_dump(exclude_unset=True) == {}

    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    def test_partial_update(self, field):
        """EntryUpdate should allow a single-field update."""
        update = EntryUpdate.model_validate({field: "New text only"})
        assert update.model_fields_set == {field}
        assert update.model_dump(exclude_unset=True) == {field: "New text only"}

    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    def test_input_schema_allows_omission_but_not_null(self, field):
        schema = EntryUpdate.model_json_schema(mode="validation")
        assert field not in schema.get("required", [])
        field_schema = schema["properties"][field]
        assert field_schema["type"] == "string"
        assert field_schema["maxLength"] == 256
        assert "default" not in field_schema

    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    @pytest.mark.parametrize("value", [None, 123, True, [], {}, b"text"])
    def test_supplied_nonstring_rejected(self, field, value):
        with pytest.raises(ValidationError) as error:
            EntryUpdate.model_validate({field: value})
        assert [item["loc"] for item in error.value.errors()] == [(field,)]

    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    def test_oversize_field_rejected(self, field):
        """EntryUpdate should reject fields longer than 256 characters."""
        with pytest.raises(ValidationError) as error:
            EntryUpdate(**{field: "a" * 257})
        assert [item["loc"] for item in error.value.errors()] == [(field,)]

    @pytest.mark.exercise
    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    @pytest.mark.parametrize("value", ["", " \t\n "])
    def test_invalid_supplied_field_rejected(self, field, value):
        with pytest.raises(ValidationError) as error:
            EntryUpdate(**{field: value})
        assert [item["loc"] for item in error.value.errors()] == [(field,)]

    @pytest.mark.exercise
    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    def test_supplied_field_is_stripped(self, field):
        update = EntryUpdate(**{field: "  New text  "})
        assert update.model_dump(exclude_unset=True) == {field: "New text"}

    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    @pytest.mark.parametrize(
        "value",
        [
            pytest.param("a" * 256, id="plain"),
            pytest.param(f"  {'a' * 256}  ", id="padded", marks=pytest.mark.exercise),
        ],
    )
    def test_max_length_after_stripping_is_allowed(self, field, value):
        update = EntryUpdate(**{field: value})
        assert update.model_dump(exclude_unset=True) == {field: "a" * 256}

    @pytest.mark.exercise
    @pytest.mark.parametrize("model", [EntryCreate, EntryUpdate])
    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    def test_input_schema_describes_string_constraints(self, model, field):
        schema = model.model_json_schema(mode="validation")["properties"][field]
        assert schema["type"] == "string"
        assert schema["minLength"] == 1
        assert schema["maxLength"] == 256


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

    @pytest.mark.parametrize("field", ["id", "created_at", "updated_at"])
    def test_entry_requires_persisted_metadata(self, field):
        data = {
            "id": "stored-entry",
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
            "work": "Studied FastAPI",
            "struggle": "Understanding async",
            "intention": "Practice more",
        }
        del data[field]
        with pytest.raises(ValidationError) as error:
            Entry.model_validate(data)
        assert [(item["loc"], item["type"]) for item in error.value.errors()] == [
            ((field,), "missing"),
        ]

    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    def test_entry_reads_historical_long_text(self, field):
        """Read models must preserve entries stored before input validation existed."""
        data = {
            "id": "stored-entry",
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
            "work": "Studied FastAPI",
            "struggle": "Understanding async",
            "intention": "Practice more",
        }
        data[field] = "a" * 300
        entry = Entry.model_validate(data)
        assert getattr(entry, field) == "a" * 300


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
        before = datetime.now(UTC)
        response = AnalysisResponse.model_validate(data)

        assert response.entry_id == data["entry_id"]
        assert response.sentiment == data["sentiment"]
        assert response.summary == data["summary"]
        assert response.topics == data["topics"]
        assert before <= response.created_at <= datetime.now(UTC)
        assert response.created_at.tzinfo == UTC

    @pytest.mark.parametrize(
        ("field", "value", "location", "error_type"),
        [
            ("sentiment", "mixed", ("sentiment",), "literal_error"),
            ("sentiment", "Positive", ("sentiment",), "literal_error"),
            ("sentiment", "", ("sentiment",), "literal_error"),
            ("sentiment", None, ("sentiment",), "literal_error"),
            ("summary", "", ("summary",), "string_too_short"),
            ("summary", " \t\n ", ("summary",), "string_too_short"),
            ("summary", None, ("summary",), "string_type"),
            ("summary", 123, ("summary",), "string_type"),
            ("topics", [], ("topics",), "too_short"),
            ("topics", ["one"], ("topics",), "too_short"),
            ("topics", ["one", "two", "three", "four", "five"], ("topics",), "too_long"),
            ("topics", ["valid", ""], ("topics", 1), "string_too_short"),
            ("topics", ["valid", " \t\n "], ("topics", 1), "string_too_short"),
            ("topics", ["valid", None], ("topics", 1), "string_type"),
            ("topics", ["valid", 123], ("topics", 1), "string_type"),
            ("topics", "not a list", ("topics",), "list_type"),
        ],
    )
    def test_analysis_response_rejects_invalid_content(self, field, value, location, error_type):
        data = {
            "entry_id": "entry-1",
            "sentiment": "positive",
            "summary": "The learner made progress.",
            "topics": ["APIs", "learning"],
        }
        data[field] = value
        with pytest.raises(ValidationError) as error:
            AnalysisResponse.model_validate(data)
        assert [(item["loc"], item["type"]) for item in error.value.errors()] == [
            (location, error_type),
        ]

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

    @pytest.mark.parametrize("field", ["entry_id", "sentiment", "summary", "topics"])
    def test_analysis_response_missing_required_field(self, field):
        data = {
            "entry_id": "123e4567-e89b-12d3-a456-426614174000",
            "sentiment": "positive",
            "summary": "The learner made progress.",
            "topics": ["APIs", "learning"],
        }
        del data[field]
        with pytest.raises(ValidationError) as error:
            AnalysisResponse.model_validate(data)
        assert [(item["loc"], item["type"]) for item in error.value.errors()] == [
            ((field,), "missing"),
        ]

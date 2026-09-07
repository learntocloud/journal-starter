"""
Tests for the Journal API endpoints.

These tests verify that the API endpoints work correctly, including:
- Creating journal entries
- Retrieving entries (all and by ID)
- Updating entries
- Deleting entries
- Analyzing entries with AI
- Error handling (404, validation errors, etc.)
"""

import json
import logging
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient, Request, Response
from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    InternalServerError,
    RateLimitError,
)

from api.main import app
from api.models.entry import Entry, EntryCreate
from api.routers.journal_router import get_entry_service
from api.services.entry_service import EntryService
from api.services.llm_service import InvalidAnalysisResponseError

PROVIDER_REQUEST = Request("POST", "https://example.invalid/v1/responses")
ROUTER_LOGGER = "api.routers.journal_router"


def assert_safe_error_log(caplog, error, entry_id):
    records = [record for record in caplog.records if record.name == ROUTER_LOGGER]
    assert records
    assert any(
        type(error).__name__ in record.getMessage()
        and entry_id in record.getMessage()
        and "journal_router.py:" in record.getMessage()
        for record in records
    )
    assert all(record.exc_info is None for record in records)
    assert str(error) not in caplog.text
    assert "provider-private-marker" not in caplog.text


@pytest.mark.no_db
class TestOpenAPIDescriptions:
    @pytest.mark.parametrize("method", ["get", "patch", "delete"])
    def test_endpoint_descriptions_exclude_exercise_instructions(self, method):
        description = app.openapi()["paths"]["/entries/{entry_id}"][method]["description"]
        assert "journal entry" in description.lower()
        for marker in ("todo", "steps to implement", "hint:", "entry_service", "model_dump"):
            assert marker not in description.lower()

    @pytest.mark.parametrize("source", ["openapi", "pydantic"])
    def test_create_model_description_excludes_exercise_instructions(self, source):
        schema = (
            app.openapi()["components"]["schemas"]["EntryCreate"]
            if source == "openapi"
            else EntryCreate.model_json_schema()
        )
        description = schema["description"]
        assert "journal entry" in description.lower()
        for marker in ("todo", "hint:", "stringconstraints"):
            assert marker not in description.lower()


class TestCreateEntry:
    """Tests for POST /entries endpoint."""

    async def test_create_entry_success(self, test_client: AsyncClient, sample_entry_data: dict):
        response = await test_client.post("/entries", json=sample_entry_data)

        assert response.status_code == 201
        result = response.json()

        assert set(result) == {"detail", "entry"}
        assert result["detail"] == "Entry created successfully"

        entry = result["entry"]
        assert entry["work"] == sample_entry_data["work"]
        assert entry["struggle"] == sample_entry_data["struggle"]
        assert entry["intention"] == sample_entry_data["intention"]
        assert set(entry) == {"id", "work", "struggle", "intention", "created_at", "updated_at"}
        assert UUID(entry["id"]).version == 4
        assert entry["created_at"] == entry["updated_at"]

    async def test_create_ignores_caller_metadata(self, test_client, sample_entry_data):
        before = datetime.now(UTC)
        response = await test_client.post(
            "/entries",
            json={
                **sample_entry_data,
                "id": "caller-id",
                "created_at": "2000-01-01T00:00:00Z",
                "updated_at": "2000-01-01T00:00:00Z",
            },
        )
        assert response.status_code == 201
        entry = response.json()["entry"]
        assert entry["id"] != "caller-id"
        assert UUID(entry["id"]).version == 4
        assert before <= datetime.fromisoformat(entry["created_at"]) <= datetime.now(UTC)
        assert entry["updated_at"] == entry["created_at"]

    async def test_create_entry_missing_fields(self, test_client: AsyncClient):
        response = await test_client.post("/entries", json={"work": "Studied FastAPI"})
        assert response.status_code == 422
        assert {tuple(error["loc"]) for error in response.json()["detail"]} == {
            ("body", "struggle"),
            ("body", "intention"),
        }
        stored = await test_client.get("/entries")
        assert stored.status_code == 200
        assert stored.json() == {"entries": [], "count": 0}

    async def test_create_entry_exceeds_max_length(self, test_client: AsyncClient):
        invalid_data = {
            "work": "a" * 257,
            "struggle": "Understanding async",
            "intention": "Practice more",
        }
        response = await test_client.post("/entries", json=invalid_data)

        assert response.status_code == 422
        assert [error["loc"] for error in response.json()["detail"]] == [["body", "work"]]
        stored = await test_client.get("/entries")
        assert stored.status_code == 200
        assert stored.json() == {"entries": [], "count": 0}

    @pytest.mark.exercise
    @pytest.mark.parametrize(
        ("field", "value"),
        [("work", ""), ("struggle", " \t\n "), ("intention", " \t\n ")],
    )
    async def test_create_rejects_blank_fields(
        self,
        test_client,
        sample_entry_data,
        field,
        value,
    ):
        response = await test_client.post("/entries", json={**sample_entry_data, field: value})
        assert response.status_code == 422
        assert [error["loc"] for error in response.json()["detail"]] == [["body", field]]
        stored = await test_client.get("/entries")
        assert stored.status_code == 200
        assert stored.json() == {"entries": [], "count": 0}

    @pytest.mark.exercise
    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    async def test_create_strips_before_length_validation(
        self,
        test_client,
        sample_entry_data,
        field,
    ):
        response = await test_client.post(
            "/entries",
            json={**sample_entry_data, field: f"  {'a' * 256}  "},
        )
        assert response.status_code == 201
        assert response.json()["entry"][field] == "a" * 256


class TestGetAllEntries:
    """Tests for GET /entries endpoint."""

    async def test_get_all_entries_empty(self, test_client: AsyncClient):
        """Test getting all entries when database is empty."""
        response = await test_client.get("/entries")

        assert response.status_code == 200
        result = response.json()
        assert "entries" in result
        assert "count" in result
        assert result["count"] == 0
        assert result["entries"] == []

    async def test_get_all_entries_with_data(self, test_client: AsyncClient, created_entry: dict):
        """Test getting all entries when database has entries."""
        response = await test_client.get("/entries")

        assert response.status_code == 200
        result = response.json()
        assert result["count"] == 1
        assert len(result["entries"]) == 1

        # Verify the entry matches what was created
        entry = result["entries"][0]
        assert entry["id"] == created_entry["id"]
        assert entry["work"] == created_entry["work"]

    async def test_get_all_entries_multiple(
        self, test_client: AsyncClient, sample_entry_data: dict
    ):
        created = []
        for i in range(3):
            entry_data = {**sample_entry_data, "work": f"Work item {i}"}
            response = await test_client.post("/entries", json=entry_data)
            assert response.status_code == 201
            created.append(response.json()["entry"])

        response = await test_client.get("/entries")

        assert response.status_code == 200
        result = response.json()
        assert result["count"] == 3
        assert len(result["entries"]) == 3
        assert {entry["id"] for entry in result["entries"]} == {entry["id"] for entry in created}


@pytest.mark.exercise
class TestGetSingleEntry:
    """Tests for GET /entries/{entry_id} endpoint."""

    async def test_get_entry_by_id_success(self, test_client: AsyncClient, created_entry: dict):
        """Test successfully retrieving a single entry by ID."""
        entry_id = created_entry["id"]
        response = await test_client.get(f"/entries/{entry_id}")

        assert response.status_code == 200
        entry = response.json()
        assert entry["id"] == created_entry["id"]
        assert entry["work"] == created_entry["work"]

    async def test_get_entry_not_found(self, test_client: AsyncClient):
        """Test that retrieving a non-existent entry returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await test_client.get(f"/entries/{fake_id}")

        assert response.status_code == 404


class TestUpdateEntry:
    """Tests for PATCH /entries/{entry_id} endpoint."""

    @pytest.mark.no_db
    @pytest.mark.exercise
    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    @pytest.mark.parametrize("value", [None, "", " \t\n ", "a" * 257, 123, True, [], {}])
    async def test_invalid_input_never_calls_service(
        self, monkeypatch, sample_entry_data, field, value
    ):
        service = AsyncMock(spec=EntryService)
        service.update_entry.return_value = None
        monkeypatch.setitem(app.dependency_overrides, get_entry_service, lambda: service)
        payload = {**sample_entry_data, field: value}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch("/entries/entry-id", json=payload)
        assert response.status_code == 422
        assert [error["loc"] for error in response.json()["detail"]] == [["body", field]]
        service.update_entry.assert_not_called()

    @pytest.mark.no_db
    @pytest.mark.exercise
    @pytest.mark.parametrize(
        ("payload", "expected"),
        [
            ({}, {}),
            ({"work": "  New work  "}, {"work": "New work"}),
            ({"struggle": "New struggle"}, {"struggle": "New struggle"}),
            ({"intention": "New intention"}, {"intention": "New intention"}),
            (
                {"work": "New work", "intention": "New intention"},
                {"work": "New work", "intention": "New intention"},
            ),
        ],
    )
    async def test_only_supplied_fields_reach_service(
        self, monkeypatch, sample_entry_data, payload, expected
    ):
        service = AsyncMock(spec=EntryService)
        now = datetime.now(UTC)
        service.update_entry.return_value = Entry(
            id="entry-id", created_at=now, updated_at=now, **sample_entry_data
        )
        monkeypatch.setitem(app.dependency_overrides, get_entry_service, lambda: service)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch("/entries/entry-id", json=payload)
        assert response.status_code == 200
        service.update_entry.assert_awaited_once_with("entry-id", expected)

    @pytest.mark.no_db
    @pytest.mark.exercise
    def test_patch_schema_describes_optional_nonnullable_text(self):
        schema = app.openapi()
        body = schema["paths"]["/entries/{entry_id}"]["patch"]["requestBody"]
        reference = body["content"]["application/json"]["schema"]["$ref"]
        model_schema = schema["components"]["schemas"][reference.rsplit("/", 1)[-1]]
        for field in ("work", "struggle", "intention"):
            assert field not in model_schema.get("required", [])
            field_schema = model_schema["properties"][field]
            assert field_schema["type"] == "string"
            assert field_schema["minLength"] == 1
            assert field_schema["maxLength"] == 256
            assert "default" not in field_schema

    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    async def test_update_entry_success(self, test_client: AsyncClient, created_entry: dict, field):
        """Test successfully updating an entry."""
        entry_id = created_entry["id"]
        update_data = {field: "Updated description"}

        response = await test_client.patch(f"/entries/{entry_id}", json=update_data)

        assert response.status_code == 200
        updated_entry = response.json()
        for name in ("work", "struggle", "intention"):
            assert updated_entry[name] == (
                "Updated description" if name == field else created_entry[name]
            )
        assert updated_entry["id"] == created_entry["id"]
        assert updated_entry["created_at"] == created_entry["created_at"]
        stored = await test_client.get("/entries")
        assert stored.json()["entries"] == [updated_entry]

    async def test_update_entry_not_found(self, test_client: AsyncClient):
        """Test that updating a non-existent entry returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_data = {"work": "Updated work"}

        response = await test_client.patch(f"/entries/{fake_id}", json=update_data)

        assert response.status_code == 404

    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    @pytest.mark.exercise
    async def test_update_rejects_oversize_field(
        self, test_client: AsyncClient, created_entry: dict, field
    ):
        """Task 2: PATCH should reject fields longer than 256 characters."""
        entry_id = created_entry["id"]
        update_data = {field: "a" * 257}

        response = await test_client.patch(f"/entries/{entry_id}", json=update_data)

        assert response.status_code == 422
        assert [error["loc"] for error in response.json()["detail"]] == [["body", field]]
        stored = await test_client.get("/entries")
        assert stored.status_code == 200
        assert stored.json()["entries"] == [created_entry]

    @pytest.mark.parametrize(
        ("field", "value"),
        [("work", ""), ("struggle", " \t\n "), ("intention", " \t\n ")],
    )
    @pytest.mark.exercise
    async def test_update_rejects_empty_string(
        self, test_client: AsyncClient, created_entry: dict, field, value
    ):
        """Task 2: PATCH should reject empty and whitespace-only strings."""
        entry_id = created_entry["id"]
        update_data = {field: value}

        response = await test_client.patch(f"/entries/{entry_id}", json=update_data)

        assert response.status_code == 422
        assert [error["loc"] for error in response.json()["detail"]] == [["body", field]]
        stored = await test_client.get("/entries")
        assert stored.status_code == 200
        assert stored.json()["entries"] == [created_entry]

    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    async def test_update_rejects_null_without_changing_entry(
        self, test_client: AsyncClient, created_entry: dict, field
    ):
        response = await test_client.patch(f"/entries/{created_entry['id']}", json={field: None})
        assert response.status_code == 422
        assert [error["loc"] for error in response.json()["detail"]] == [["body", field]]
        stored = await test_client.get("/entries")
        assert stored.status_code == 200
        assert stored.json()["entries"] == [created_entry]

    @pytest.mark.parametrize(
        ("field", "value"), [("work", 123), ("struggle", True), ("intention", {})]
    )
    async def test_update_rejects_nonstring_values(
        self,
        test_client,
        created_entry,
        field,
        value,
    ):
        response = await test_client.patch(f"/entries/{created_entry['id']}", json={field: value})
        assert response.status_code == 422
        assert [error["loc"] for error in response.json()["detail"]] == [["body", field]]
        stored = await test_client.get("/entries")
        assert stored.status_code == 200
        assert stored.json()["entries"] == [created_entry]

    async def test_empty_update_preserves_text_fields(
        self, test_client: AsyncClient, created_entry: dict
    ):
        response = await test_client.patch(f"/entries/{created_entry['id']}", json={})
        assert response.status_code == 200
        for field in ("work", "struggle", "intention"):
            assert response.json()[field] == created_entry[field]
        stored = await test_client.get("/entries")
        assert stored.json()["entries"] == [response.json()]

    @pytest.mark.parametrize("field", ["work", "struggle", "intention"])
    @pytest.mark.exercise
    async def test_update_accepts_max_length_after_stripping(
        self, test_client: AsyncClient, created_entry: dict, field
    ):
        response = await test_client.patch(
            f"/entries/{created_entry['id']}", json={field: f"  {'a' * 256}  "}
        )
        assert response.status_code == 200
        assert response.json()[field] == "a" * 256
        stored = await test_client.get("/entries")
        assert stored.status_code == 200
        assert stored.json()["entries"] == [response.json()]


@pytest.mark.exercise
class TestDeleteEntry:
    """Tests for DELETE /entries/{entry_id} endpoint."""

    async def test_delete_entry_success(self, test_client: AsyncClient, created_entry: dict):
        """Test successfully deleting a single entry."""
        entry_id = created_entry["id"]
        response = await test_client.delete(f"/entries/{entry_id}")

        assert response.status_code == 200

        # Verify the entry was actually deleted
        get_response = await test_client.get("/entries")
        result = get_response.json()
        assert result["count"] == 0

    async def test_delete_entry_not_found(self, test_client: AsyncClient):
        """Test that deleting a non-existent entry returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await test_client.delete(f"/entries/{fake_id}")

        assert response.status_code == 404

    @pytest.mark.no_db
    @pytest.mark.parametrize("deleted", [True, False])
    async def test_delete_route_uses_atomic_service_result(self, monkeypatch, deleted):
        service = AsyncMock(spec=EntryService)
        service.delete_entry.return_value = deleted
        monkeypatch.setitem(app.dependency_overrides, get_entry_service, lambda: service)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete("/entries/entry-id")
        assert response.status_code == (200 if deleted else 404)
        if deleted:
            assert response.json() == {"detail": "Entry deleted successfully"}
        service.delete_entry.assert_awaited_once_with("entry-id")
        service.get_entry.assert_not_awaited()


class TestDeleteAllEntries:
    """Tests for DELETE /entries endpoint."""

    async def test_delete_all_entries_success(
        self, test_client: AsyncClient, sample_entry_data: dict
    ):
        created_ids = set()
        for i in range(3):
            entry_data = {**sample_entry_data, "work": f"Work item {i}"}
            response = await test_client.post("/entries", json=entry_data)
            assert response.status_code == 201
            created_ids.add(response.json()["entry"]["id"])

        before = await test_client.get("/entries")
        assert before.status_code == 200
        assert before.json()["count"] == 3
        assert len(created_ids) == 3
        assert {entry["id"] for entry in before.json()["entries"]} == created_ids

        response = await test_client.delete("/entries")

        assert response.status_code == 200
        assert response.json()["detail"] == "All entries deleted"

        get_response = await test_client.get("/entries")
        assert get_response.status_code == 200
        assert get_response.json() == {"entries": [], "count": 0}


class TestAnalyzeEntry:
    """Tests for POST /entries/{entry_id}/analyze endpoint."""

    async def test_analyze_entry_not_found(self, test_client: AsyncClient):
        """Test that analyzing a non-existent entry returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await test_client.post(f"/entries/{fake_id}/analyze")

        assert response.status_code == 404

    @patch("api.routers.journal_router.analyze_journal_entry")
    async def test_analyze_entry_success(
        self, mock_analyze, test_client: AsyncClient, created_entry: dict
    ):
        """Test successfully analyzing an existing entry returns correct structure."""
        entry_id = created_entry["id"]
        mock_analyze.return_value = {
            "entry_id": entry_id,
            "sentiment": "positive",
            "summary": "Great progress on learning. Excited to continue tomorrow.",
            "topics": ["FastAPI", "PostgreSQL"],
            "created_at": "2025-12-25T10:30:00Z",
        }

        response = await test_client.post(f"/entries/{entry_id}/analyze")

        assert response.status_code == 200
        result = response.json()
        assert result["entry_id"] == entry_id
        assert result["sentiment"] in ["positive", "negative", "neutral"]
        assert "summary" in result
        assert isinstance(result["topics"], list)
        assert 2 <= len(result["topics"]) <= 4
        assert "created_at" in result

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("sentiment", "mixed"),
            ("summary", " \t\n "),
            ("topics", []),
        ],
    )
    @patch("api.routers.journal_router.analyze_journal_entry")
    async def test_analyze_entry_rejects_invalid_provider_content(
        self, mock_analyze, test_client: AsyncClient, created_entry: dict, field, value
    ):
        result = {
            "entry_id": created_entry["id"],
            "sentiment": "positive",
            "summary": "The learner made progress.",
            "topics": ["APIs", "learning"],
        }
        result[field] = value
        mock_analyze.return_value = result

        response = await test_client.post(f"/entries/{created_entry['id']}/analyze")

        assert response.status_code == 502
        assert response.json() == {"detail": "Analysis provider returned an invalid response"}

    @pytest.mark.parametrize(
        ("error", "expected_status", "expected_detail"),
        [
            (RuntimeError("provider-private-marker"), 500, "Analysis failed"),
            (
                json.JSONDecodeError("provider-private-marker", "provider-private-marker", 0),
                502,
                "Analysis provider returned an invalid response",
            ),
            (
                InvalidAnalysisResponseError("provider-private-marker"),
                502,
                "Analysis provider returned an invalid response",
            ),
        ],
    )
    @patch("api.routers.journal_router.analyze_journal_entry")
    async def test_analyze_entry_handles_llm_error(
        self,
        mock_analyze,
        test_client: AsyncClient,
        created_entry: dict,
        caplog,
        error,
        expected_status,
        expected_detail,
    ):
        """Unexpected errors are logged but their details are not returned to clients."""
        mock_analyze.side_effect = error

        with caplog.at_level(logging.ERROR, logger=ROUTER_LOGGER):
            response = await test_client.post(f"/entries/{created_entry['id']}/analyze")

        assert response.status_code == expected_status
        assert response.json() == {"detail": expected_detail}
        assert str(error) not in response.text
        assert_safe_error_log(caplog, error, created_entry["id"])

    @pytest.mark.parametrize(
        ("error", "expected_status", "expected_detail"),
        [
            pytest.param(
                APITimeoutError(request=PROVIDER_REQUEST),
                504,
                "Analysis provider timed out",
                id="timeout",
            ),
            pytest.param(
                RateLimitError(
                    "provider-private-marker",
                    response=Response(429, request=PROVIDER_REQUEST),
                    body={"private": "provider-private-marker"},
                ),
                503,
                "Analysis provider is temporarily unavailable",
                id="rate-limit",
            ),
            pytest.param(
                APIConnectionError(message="provider-private-marker", request=PROVIDER_REQUEST),
                502,
                "Analysis provider request failed",
                id="connection",
            ),
            pytest.param(
                AuthenticationError(
                    "provider-private-marker",
                    response=Response(401, request=PROVIDER_REQUEST),
                    body={"private": "provider-private-marker"},
                ),
                502,
                "Analysis provider request failed",
                id="authentication",
            ),
            pytest.param(
                InternalServerError(
                    "provider-private-marker",
                    response=Response(500, request=PROVIDER_REQUEST),
                    body={"private": "provider-private-marker"},
                ),
                502,
                "Analysis provider request failed",
                id="provider-server-error",
            ),
        ],
    )
    @patch("api.routers.journal_router.analyze_journal_entry")
    async def test_analyze_entry_maps_provider_errors(
        self,
        mock_analyze,
        test_client: AsyncClient,
        created_entry: dict,
        caplog,
        error,
        expected_status,
        expected_detail,
    ):
        mock_analyze.side_effect = error

        with caplog.at_level(logging.ERROR, logger=ROUTER_LOGGER):
            response = await test_client.post(f"/entries/{created_entry['id']}/analyze")

        assert response.status_code == expected_status
        assert response.json() == {"detail": expected_detail}
        assert str(error) not in response.text
        assert_safe_error_log(caplog, error, created_entry["id"])

    @patch("api.routers.journal_router.analyze_journal_entry")
    async def test_not_implemented_keeps_exercise_status(
        self,
        mock_analyze,
        test_client,
        created_entry,
    ):
        mock_analyze.side_effect = NotImplementedError("Task 4")
        response = await test_client.post(f"/entries/{created_entry['id']}/analyze")
        assert response.status_code == 501
        assert response.json() == {
            "detail": "LLM analysis not yet implemented - see api/services/llm_service.py",
        }

    @patch("api.routers.journal_router.analyze_journal_entry")
    async def test_validation_logs_never_include_provider_input(
        self,
        mock_analyze,
        test_client,
        created_entry,
        caplog,
    ):
        mock_analyze.return_value = {
            "entry_id": created_entry["id"],
            "sentiment": "provider-private-marker",
            "summary": "provider-private-marker",
            "topics": ["provider-private-marker", "learning"],
        }
        with caplog.at_level(logging.ERROR, logger=ROUTER_LOGGER):
            response = await test_client.post(f"/entries/{created_entry['id']}/analyze")
        assert response.status_code == 502
        assert "provider-private-marker" not in response.text
        assert "provider-private-marker" not in caplog.text
        assert "ValidationError" in caplog.text
        assert all(record.exc_info is None for record in caplog.records)

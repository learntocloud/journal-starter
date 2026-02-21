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
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient


class TestCreateEntry:
    """Tests for POST /entries endpoint."""

    async def test_create_entry_success(self, test_client: AsyncClient, sample_entry_data: dict):
        """Test successfully creating a new journal entry."""
        response = await test_client.post("/entries", json=sample_entry_data)

        assert response.status_code == 200
        result = response.json()

        # Verify response structure
        assert "detail" in result
        assert "entry" in result
        assert result["detail"] == "Entry created successfully"

        # Verify entry data
        entry = result["entry"]
        assert entry["work"] == sample_entry_data["work"]
        assert entry["struggle"] == sample_entry_data["struggle"]
        assert entry["intention"] == sample_entry_data["intention"]
        assert "id" in entry
        assert "created_at" in entry
        assert "updated_at" in entry

    async def test_create_entry_missing_fields(self, test_client: AsyncClient):
        """Test that creating an entry without required fields returns validation error."""
        incomplete_data = {
            "work": "Studied FastAPI"
            # Missing struggle and intention
        }
        response = await test_client.post("/entries", json=incomplete_data)

        # FastAPI returns 422 for validation errors
        assert response.status_code == 422

    async def test_create_entry_exceeds_max_length(self, test_client: AsyncClient):
        """Test that creating an entry with fields exceeding max length returns validation error."""
        invalid_data = {
            "work": "a" * 300,  # Exceeds 256 character limit
            "struggle": "Understanding async",
            "intention": "Practice more"
        }
        response = await test_client.post("/entries", json=invalid_data)

        # Should return validation error
        assert response.status_code == 422


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

    async def test_get_all_entries_multiple(self, test_client: AsyncClient, sample_entry_data: dict):
        """Test getting all entries when database has multiple entries."""
        # Create multiple entries
        for i in range(3):
            entry_data = sample_entry_data.copy()
            entry_data["work"] = f"Work item {i}"
            await test_client.post("/entries", json=entry_data)

        response = await test_client.get("/entries")

        assert response.status_code == 200
        result = response.json()
        assert result["count"] == 3
        assert len(result["entries"]) == 3


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

    async def test_update_entry_success(self, test_client: AsyncClient, created_entry: dict):
        """Test successfully updating an entry."""
        entry_id = created_entry["id"]
        update_data = {
            "work": "Updated work description"
        }

        response = await test_client.patch(f"/entries/{entry_id}", json=update_data)

        assert response.status_code == 200
        updated_entry = response.json()
        assert updated_entry["work"] == "Updated work description"
        # Other fields should remain unchanged
        assert updated_entry["struggle"] == created_entry["struggle"]
        assert updated_entry["intention"] == created_entry["intention"]

    async def test_update_entry_not_found(self, test_client: AsyncClient):
        """Test that updating a non-existent entry returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_data = {"work": "Updated work"}

        response = await test_client.patch(f"/entries/{fake_id}", json=update_data)

        assert response.status_code == 404


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


class TestDeleteAllEntries:
    """Tests for DELETE /entries endpoint."""

    async def test_delete_all_entries_success(self, test_client: AsyncClient, sample_entry_data: dict):
        """Test successfully deleting all entries."""
        # Create multiple entries
        for i in range(3):
            entry_data = sample_entry_data.copy()
            entry_data["work"] = f"Work item {i}"
            await test_client.post("/entries", json=entry_data)

        # Delete all entries
        response = await test_client.delete("/entries")

        assert response.status_code == 200
        assert response.json()["detail"] == "All entries deleted"

        # Verify all entries were deleted
        get_response = await test_client.get("/entries")
        result = get_response.json()
        assert result["count"] == 0


class TestAnalyzeEntry:
    """Tests for POST /entries/{entry_id}/analyze endpoint."""

    async def test_analyze_entry_not_found(self, test_client: AsyncClient):
        """Test that analyzing a non-existent entry returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await test_client.post(f"/entries/{fake_id}/analyze")

        assert response.status_code == 404

    @patch("api.services.llm_service.analyze_journal_entry")
    async def test_analyze_entry_success(self, mock_analyze, test_client: AsyncClient, created_entry: dict):
        """Test successfully analyzing an existing entry returns correct structure."""
        entry_id = created_entry["id"]
        mock_analyze.return_value = {
            "entry_id": entry_id,
            "sentiment": "positive",
            "summary": "Great progress on learning. Excited to continue tomorrow.",
            "topics": ["FastAPI", "PostgreSQL"],
            "created_at": "2025-12-25T10:30:00Z"
        }

        response = await test_client.post(f"/entries/{entry_id}/analyze")

        assert response.status_code == 200
        result = response.json()
        assert result["entry_id"] == entry_id
        assert result["sentiment"] in ["positive", "negative", "neutral"]
        assert "summary" in result
        assert isinstance(result["topics"], list)
        assert len(result["topics"]) >= 2
        assert "created_at" in result

    @patch("api.services.llm_service.analyze_journal_entry")
    async def test_analyze_entry_handles_llm_error(self, mock_analyze, test_client: AsyncClient, created_entry: dict):
        """Test that LLM errors are handled gracefully, not as raw 500s."""
        mock_analyze.side_effect = Exception("LLM API key is invalid")

        response = await test_client.post(f"/entries/{created_entry['id']}/analyze")

        # Should return a handled error with a JSON detail message
        assert response.status_code == 500
        assert "detail" in response.json()

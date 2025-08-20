import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock
from app.main import app
from app.schemas.entry import EntryOut
from app.services.entry_service import EntryService
from app.routers.journal_router import get_entry_service

# Dependency override: yield the mock so each test can configure return values
@pytest.fixture(autouse=True)
def override_entry_service():
    mock_service = AsyncMock(spec=EntryService)
    app.dependency_overrides[get_entry_service] = lambda: mock_service
    yield mock_service
    app.dependency_overrides = {}

# Example entry data used for "found" scenarios
def make_stub_entry(**kwargs):
    base = dict(
        id="123e4567-e89b-12d3-a456-426614174000",
        work="Did some cloud learning",
        struggle="Struggled with SQL joins",
        intention="Practice joins tomorrow",
        created_at="2025-06-18T12:00:00",
        updated_at="2025-06-18T12:00:00",
    )
    base.update(kwargs)
    return EntryOut(**base)

@pytest.mark.anyio
async def test_create_entry(override_entry_service):
    stub = make_stub_entry()
    override_entry_service.create_entry.return_value = stub

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "work": stub.work,
            "struggle": stub.struggle,
            "intention": stub.intention
        }
        response = await ac.post("/entries/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["work"] == stub.work
    assert data["struggle"] == stub.struggle
    assert data["intention"] == stub.intention

@pytest.mark.anyio
async def test_get_entry_by_id(override_entry_service):
    entry_id = "123e4567-e89b-12d3-a456-426614174000"
    stub = make_stub_entry(id=entry_id)
    override_entry_service.get_entry_by_id.return_value = stub

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/entries/{entry_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == entry_id
    assert data["work"] == stub.work

@pytest.mark.anyio
async def test_get_entry_by_id_not_found(override_entry_service):
    override_entry_service.get_entry_by_id.return_value = None
    fake_id = "non-existent-id"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/entries/{fake_id}")
    assert response.status_code == 404

@pytest.mark.anyio
async def test_get_all_entries(override_entry_service):
    stub1 = make_stub_entry()
    stub2 = make_stub_entry(id="223e4567-e89b-12d3-a456-426614174001", work="Something else")
    override_entry_service.get_all_entries.return_value = [stub1, stub2]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/entries/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2

@pytest.mark.anyio
async def test_update_entry(override_entry_service):
    entry_id = "123e4567-e89b-12d3-a456-426614174000"
    updated_stub = make_stub_entry(id=entry_id, work="Updated work", struggle="Updated struggle", intention="Updated intention")
    override_entry_service.update_entry.return_value = updated_stub

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "work": "Updated work",
            "struggle": "Updated struggle",
            "intention": "Updated intention"
        }
        response = await ac.put(f"/entries/{entry_id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["work"] == "Updated work"
    assert data["struggle"] == "Updated struggle"
    assert data["intention"] == "Updated intention"

@pytest.mark.anyio
async def test_update_entry_not_found(override_entry_service):
    override_entry_service.update_entry.return_value = None
    fake_id = "non-existent-id"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "work": "Nope",
            "struggle": "Nope",
            "intention": "Nope"
        }
        response = await ac.put(f"/entries/{fake_id}", json=payload)
    assert response.status_code == 404

@pytest.mark.anyio
async def test_delete_entry(override_entry_service):
    entry_id = "123e4567-e89b-12d3-a456-426614174000"
    override_entry_service.delete_entry.return_value = True

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete(f"/entries/{entry_id}")
    assert response.status_code == 204

@pytest.mark.anyio
async def test_delete_entry_not_found(override_entry_service):
    override_entry_service.delete_entry.return_value = False
    fake_id = "non-existent-id"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete(f"/entries/{fake_id}")
    assert response.status_code == 404

@pytest.mark.anyio
async def test_create_entry_422_missing_fields(override_entry_service):
    # Missing required field 'intention' should trigger FastAPI/Pydantic 422
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {"work": "x", "struggle": "y"}  # intention omitted
        response = await ac.post("/entries/", json=payload)
    assert response.status_code == 422

@pytest.mark.anyio
async def test_create_entry_422_field_too_long(override_entry_service):
    # Exceeds max_length=256 on 'work'
    long_text = "a" * 257
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {"work": long_text, "struggle": "ok", "intention": "ok"}
        response = await ac.post("/entries/", json=payload)
    assert response.status_code == 422

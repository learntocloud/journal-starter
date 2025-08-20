import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


# Ensure the whole module shares a single asyncio backend/loop
@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


# Share a single AsyncClient (and ASGITransport) for the module
@pytest.fixture(scope="module")
async def client():
    transport = ASGITransport(app=app)  # no lifespan kw for your httpx version
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.anyio
async def test_create_get_delete_entry_integration(client: AsyncClient):
    # 1) Create
    payload = {"work": "int smoke", "struggle": "smoke", "intention": "smoke"}
    create_resp = await client.post("/entries/", json=payload)
    assert create_resp.status_code in (200, 201)
    created = create_resp.json()
    assert "id" in created and created["work"] == payload["work"]
    entry_id = created["id"]

    # 2) Get by id
    get_resp = await client.get(f"/entries/{entry_id}")
    assert get_resp.status_code == 200
    got = get_resp.json()
    assert got["id"] == entry_id
    assert got["work"] == payload["work"]

    # 3) Delete by id (cleanup)
    del_resp = await client.delete(f"/entries/{entry_id}")
    assert del_resp.status_code in (200, 204)


@pytest.mark.anyio
async def test_list_entries_includes_created_entry(client: AsyncClient):
    # create
    payload = {"work": "list smoke", "struggle": "s", "intention": "i"}
    create_resp = await client.post("/entries/", json=payload)
    assert create_resp.status_code in (200, 201)
    created = create_resp.json()
    entry_id = created["id"]

    try:
        # list
        list_resp = await client.get("/entries/")
        assert list_resp.status_code == 200
        items = list_resp.json()
        assert any(it["id"] == entry_id for it in items)
    finally:
        # cleanup
        await client.delete(f"/entries/{entry_id}")


@pytest.mark.anyio
async def test_update_entry_persists_changes(client: AsyncClient):
    # create
    payload = {"work": "before", "struggle": "s", "intention": "i"}
    create_resp = await client.post("/entries/", json=payload)
    assert create_resp.status_code in (200, 201)
    entry_id = create_resp.json()["id"]

    try:
        # update
        patch = {"work": "after"}
        update_resp = await client.put(f"/entries/{entry_id}", json=patch)
        assert update_resp.status_code in (200, 204)

        # get
        get_resp = await client.get(f"/entries/{entry_id}")
        assert get_resp.status_code == 200
        got = get_resp.json()
        assert got["work"] == "after"
    finally:
        # cleanup
        await client.delete(f"/entries/{entry_id}")


@pytest.mark.anyio
async def test_delete_is_idempotent_or_404_on_second_try(client: AsyncClient):
    # create
    payload = {"work": "del twice", "struggle": "s", "intention": "i"}
    create_resp = await client.post("/entries/", json=payload)
    assert create_resp.status_code in (200, 201)
    entry_id = create_resp.json()["id"]

    # first delete
    del1 = await client.delete(f"/entries/{entry_id}")
    assert del1.status_code in (200, 204)

    # second delete (some APIs return 404, others 204/200)
    del2 = await client.delete(f"/entries/{entry_id}")
    assert del2.status_code in (200, 204, 404)

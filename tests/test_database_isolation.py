from httpx import AsyncClient

from api.repositories.postgres_repository import PostgresDB
from api.services.entry_service import EntryService


async def test_api_and_repository_share_test_database(
    test_client: AsyncClient, test_db: PostgresDB, sample_entry_data: dict
):
    entry = await EntryService(test_db).create_entry(sample_entry_data)

    response = await test_client.get("/entries")
    assert response.status_code == 200
    assert [item["id"] for item in response.json()["entries"]] == [entry["id"]]

    response = await test_client.post("/entries", json=sample_entry_data)
    assert response.status_code == 201
    assert await test_db.get_entry(response.json()["entry"]["id"]) is not None

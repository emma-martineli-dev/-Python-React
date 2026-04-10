import io
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def _upload(client: AsyncClient, title: str = "Test", filename: str = "test.txt", content: bytes = b"hello"):
    return await client.post(
        "/files",
        data={"title": title},
        files={"file": (filename, io.BytesIO(content), "text/plain")},
    )


async def test_list_empty(client: AsyncClient):
    resp = await client.get("/files")
    assert resp.status_code == 200
    assert resp.json() == {"items": [], "total": 0, "offset": 0, "limit": 20}


async def test_create(client: AsyncClient):
    resp = await _upload(client)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test"
    assert data["original_name"] == "test.txt"
    assert data["processing_status"] == "uploaded"


async def test_create_empty_rejected(client: AsyncClient):
    assert (await _upload(client, content=b"")).status_code == 400


async def test_get(client: AsyncClient):
    file_id = (await _upload(client)).json()["id"]
    resp = await client.get(f"/files/{file_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == file_id


async def test_get_not_found(client: AsyncClient):
    assert (await client.get("/files/nonexistent")).status_code == 404


async def test_update(client: AsyncClient):
    file_id = (await _upload(client)).json()["id"]
    resp = await client.patch(f"/files/{file_id}", json={"title": "Updated"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated"


async def test_delete(client: AsyncClient):
    file_id = (await _upload(client)).json()["id"]
    assert (await client.delete(f"/files/{file_id}")).status_code == 204
    assert (await client.get(f"/files/{file_id}")).status_code == 404


async def test_pagination(client: AsyncClient):
    for i in range(5):
        await _upload(client, title=f"File {i}")

    page1 = (await client.get("/files?offset=0&limit=3")).json()
    assert page1["total"] == 5
    assert len(page1["items"]) == 3

    page2 = (await client.get("/files?offset=3&limit=3")).json()
    assert len(page2["items"]) == 2

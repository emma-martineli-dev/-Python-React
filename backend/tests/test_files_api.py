import io
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def upload_file(client: AsyncClient, title: str = "Test", filename: str = "test.txt", content: bytes = b"hello"):
    return await client.post(
        "/files",
        data={"title": title},
        files={"file": (filename, io.BytesIO(content), "text/plain")},
    )


async def test_list_files_empty(client: AsyncClient):
    resp = await client.get("/files")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


async def test_create_file(client: AsyncClient):
    resp = await upload_file(client)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test"
    assert data["original_name"] == "test.txt"
    assert data["processing_status"] == "uploaded"


async def test_create_empty_file_rejected(client: AsyncClient):
    resp = await upload_file(client, content=b"")
    assert resp.status_code == 400


async def test_get_file(client: AsyncClient):
    create_resp = await upload_file(client)
    file_id = create_resp.json()["id"]

    resp = await client.get(f"/files/{file_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == file_id


async def test_get_file_not_found(client: AsyncClient):
    resp = await client.get("/files/nonexistent-id")
    assert resp.status_code == 404


async def test_update_file(client: AsyncClient):
    create_resp = await upload_file(client)
    file_id = create_resp.json()["id"]

    resp = await client.patch(f"/files/{file_id}", json={"title": "Updated"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated"


async def test_delete_file(client: AsyncClient):
    create_resp = await upload_file(client)
    file_id = create_resp.json()["id"]

    resp = await client.delete(f"/files/{file_id}")
    assert resp.status_code == 204

    resp = await client.get(f"/files/{file_id}")
    assert resp.status_code == 404


async def test_list_files_pagination(client: AsyncClient):
    for i in range(5):
        await upload_file(client, title=f"File {i}")

    resp = await client.get("/files?offset=0&limit=3")
    data = resp.json()
    assert data["total"] == 5
    assert len(data["items"]) == 3

    resp2 = await client.get("/files?offset=3&limit=3")
    data2 = resp2.json()
    assert len(data2["items"]) == 2

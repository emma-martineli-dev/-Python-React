import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.alerts import create as create_alert
from tests.conftest import _session_maker

pytestmark = pytest.mark.asyncio


async def test_list_alerts_empty(client: AsyncClient):
    resp = await client.get("/alerts")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


async def test_list_alerts_pagination(client: AsyncClient):
    # seed alerts directly via repo
    async with _session_maker() as session:
        for i in range(5):
            await create_alert(session, file_id="fake-id", level="info", message=f"msg {i}")

    resp = await client.get("/alerts?offset=0&limit=3")
    data = resp.json()
    assert data["total"] == 5
    assert len(data["items"]) == 3

    resp2 = await client.get("/alerts?offset=3&limit=3")
    assert len(resp2.json()["items"]) == 2

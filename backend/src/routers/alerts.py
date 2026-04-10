from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session
from src.schemas import AlertItem, Page
from src import repositories

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=Page[AlertItem])
async def list_alerts(
    offset: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    items, total = await repositories.alerts.get_all(session, offset=offset, limit=limit)
    return Page(items=items, total=total, offset=offset, limit=limit)

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session
from src.schemas import AlertItem, Page
from src.repositories import alerts as alert_repo

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=Page[AlertItem])
async def list_alerts(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    items, total = await alert_repo.get_all(session, offset=offset, limit=limit)
    return Page(items=items, total=total, offset=offset, limit=limit)

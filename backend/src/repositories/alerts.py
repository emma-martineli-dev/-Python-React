from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Alert


async def get_all(session: AsyncSession, offset: int = 0, limit: int = 20) -> tuple[list[Alert], int]:
    total = (await session.execute(select(func.count()).select_from(Alert))).scalar_one()
    result = await session.execute(
        select(Alert).order_by(Alert.created_at.desc()).offset(offset).limit(limit)
    )
    return list(result.scalars().all()), total


async def create(session: AsyncSession, file_id: str, level: str, message: str) -> Alert:
    alert = Alert(file_id=file_id, level=level, message=message)
    session.add(alert)
    await session.commit()
    await session.refresh(alert)
    return alert

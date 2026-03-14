from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from cass.database import get_db
from cass.models.db_models import ActivityLog
from cass.models.schemas import ActivityOut

router = APIRouter()


@router.get("/activity", response_model=list[ActivityOut])
async def list_activity(
    search: str = "",
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(ActivityLog).order_by(ActivityLog.created_at.desc())

    if search:
        stmt = stmt.where(
            ActivityLog.detail.contains(search)
            | ActivityLog.action.contains(search)
            | ActivityLog.tool_name.contains(search)
        )

    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/activity/count")
async def activity_count(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(func.count(ActivityLog.id)))
    return {"count": result.scalar()}

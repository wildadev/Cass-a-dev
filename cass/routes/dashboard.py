from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cass.database import get_db
from cass.models.db_models import ActivityLog, Task
from cass.models.schemas import DashboardResponse

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    # Pending approvals (email drafts + other pending tasks needing approval)
    pending_result = await db.execute(
        select(Task)
        .where(Task.status == "pending")
        .order_by(Task.created_at.desc())
        .limit(20)
    )
    pending_tasks = list(pending_result.scalars().all())

    # Active tasks (in_progress)
    active_result = await db.execute(
        select(Task)
        .where(Task.status == "in_progress")
        .order_by(Task.updated_at.desc())
        .limit(20)
    )
    active_tasks = list(active_result.scalars().all())

    # Recent activity
    activity_result = await db.execute(
        select(ActivityLog)
        .order_by(ActivityLog.created_at.desc())
        .limit(5)
    )
    recent_activity = list(activity_result.scalars().all())

    return DashboardResponse(
        pending_approvals=pending_tasks,
        active_tasks=active_tasks,
        recent_activity=recent_activity,
        total_pending=len(pending_tasks),
        total_active=len(active_tasks),
    )

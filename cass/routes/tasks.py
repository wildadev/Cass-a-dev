import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cass.database import get_db
from cass.models.db_models import ActivityLog, Task
from cass.models.schemas import TaskApproveRequest, TaskOut, TaskRejectRequest

router = APIRouter()


@router.get("/tasks", response_model=list[TaskOut])
async def list_tasks(
    status: str | None = None,
    task_type: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Task).order_by(Task.created_at.desc())
    if status:
        stmt = stmt.where(Task.status == status)
    if task_type:
        stmt = stmt.where(Task.task_type == task_type)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/tasks/{task_id}", response_model=TaskOut)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/tasks/{task_id}/approve")
async def approve_task(
    task_id: str,
    req: TaskApproveRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.task_type == "email_draft":
        metadata = json.loads(task.metadata_json)

        # Allow editing the draft content before sending
        if req and req.edited_content:
            metadata["body"] = req.edited_content
            task.metadata_json = json.dumps(metadata)

        # Actually send the email
        try:
            from cass.services.google_auth import GoogleAuthService
            from cass.services.gmail import GmailService

            auth = GoogleAuthService()
            creds = await auth.get_credentials()
            if not creds:
                raise HTTPException(status_code=400, detail="Google not connected")

            gmail = GmailService(creds)
            await gmail.send_email(
                to=metadata["to"],
                subject=metadata.get("subject", ""),
                body=metadata["body"],
                reply_to_id=metadata.get("reply_to_id"),
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

    task.status = "completed"
    db.add(ActivityLog(action="task_approved", detail=f"Approved: {task.title}", tool_name=task.task_type))
    await db.commit()
    return {"success": True, "message": f"Task '{task.title}' approved"}


@router.patch("/tasks/{task_id}/reject")
async def reject_task(
    task_id: str,
    req: TaskRejectRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = "cancelled"
    reason = req.reason if req else ""
    db.add(ActivityLog(
        action="task_rejected",
        detail=f"Rejected: {task.title}. Reason: {reason}",
        tool_name=task.task_type,
    ))
    await db.commit()
    return {"success": True, "message": f"Task '{task.title}' rejected"}

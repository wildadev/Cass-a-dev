from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from cass.database import get_db
from cass.models.db_models import Feedback
from cass.models.schemas import FeedbackRequest

router = APIRouter()


@router.post("/feedback")
async def submit_feedback(req: FeedbackRequest, db: AsyncSession = Depends(get_db)):
    fb = Feedback(
        message_id=req.message_id,
        feedback_type=req.feedback_type,
        content=req.content,
    )
    db.add(fb)
    await db.commit()
    return {"success": True}

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cass.database import get_db
from cass.models.db_models import UserProfile
from cass.models.schemas import OnboardingRequest, OnboardingResponse

router = APIRouter()


@router.get("/onboarding/status")
async def onboarding_status(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserProfile).limit(1))
    profile = result.scalar_one_or_none()
    if profile:
        return {
            "completed": True,
            "user_name": profile.name,
            "assistant_name": profile.assistant_name,
        }
    return {"completed": False}


@router.post("/onboarding", response_model=OnboardingResponse)
async def complete_onboarding(req: OnboardingRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserProfile).limit(1))
    profile = result.scalar_one_or_none()

    if profile:
        profile.name = req.user_name
        profile.assistant_name = req.assistant_name
        profile.assistant_persona = req.assistant_persona
    else:
        profile = UserProfile(
            name=req.user_name,
            assistant_name=req.assistant_name,
            assistant_persona=req.assistant_persona,
        )
        db.add(profile)

    await db.commit()
    return OnboardingResponse(success=True, message=f"Welcome, {req.user_name}!")

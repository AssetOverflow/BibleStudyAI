from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from models import api_models, db_models
from database.timescale_db import get_db

router = APIRouter()

@router.post("/profile", response_model=api_models.UserProfileResponse)
async def create_user_profile(
    profile: api_models.UserProfileRequest, db: AsyncSession = Depends(get_db)
):
    """Create or update user profile"""
    try:
        new_user = db_models.User(**profile.dict())
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return api_models.UserProfileResponse(
            status="success",
            user_id=str(new_user.id),
            message="Profile created successfully",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not create user profile.")

@router.get("/me/progress", response_model=List[api_models.StudyProgress])
async def get_study_progress():
    # Placeholder data
    return [
        {"title": "Daniel's 70 Weeks", "description": "Prophetic timeline analysis", "progress": 75},
        {"title": "Revelation Study", "description": "End times prophecy", "progress": 45},
        {"title": "Genesis Patterns", "description": "Hidden design elements", "progress": 90},
    ]

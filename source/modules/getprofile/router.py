from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from source.modules.getprofile.controller import get_user_profile_details
from source.modules.getprofile.schemas import FullProfileResponse
from source.modules.user.auth import get_current_user_id
from source.database.service import get_db

router = APIRouter(
    prefix="/profile",
    tags=["User Profile"]
)


@router.get("/me", response_model=FullProfileResponse)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """
    Returns User + PatientProfile combined data for logged-in user
    """
    return await get_user_profile_details(db, current_user_id)

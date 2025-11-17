# controller.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from source.modules.user.models import Users
from source.modules.PatientProfile.model import PatientProfile
from source.modules.getprofile.schemas import (
    FullProfileResponse,
    UserResponse,
    PatientProfileResponse
)


async def get_user_profile_details(db: AsyncSession, current_user: Users) -> FullProfileResponse:
    """
    Fetch logged-in user's profile + patient profile details
    """

    # --- Query user ---
    stmt = select(Users).where(Users.id == current_user.id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # --- Query patient profile ---
    stmt = select(PatientProfile).where(PatientProfile.user_id == current_user.id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()

    # Build response
    user_data = UserResponse(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        role=user.role.value if user.role else None,
        status=user.status.value if user.status else None,
        profile_photo_url=user.profile_photo_url,
        bio=user.bio,
        location=user.location,
        is_onboarded=user.is_onboarded
    )

    if profile:
        profile_data = PatientProfileResponse.from_orm(profile)
    else:
        profile_data = None

    return FullProfileResponse(
        user=user_data,
        patient_profile=profile_data
    )

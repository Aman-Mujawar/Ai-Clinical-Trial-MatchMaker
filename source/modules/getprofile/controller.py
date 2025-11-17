# controller.py

from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status

from source.modules.user.models import Users
from source.modules.PatientProfile.model import PatientProfile
from source.modules.getprofile.schemas import (
    FullProfileResponse,
    UserResponse,
    PatientProfileResponse
)


def get_user_profile_details(db: Session, current_user_id: str) -> FullProfileResponse:
    """
    Fetch logged-in user's full profile (User + PatientProfile)
    """

    # --- Fetch User ---
    stmt = select(Users).where(Users.id == current_user_id)
    result = db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # --- Fetch Patient Profile ---
    stmt = select(PatientProfile).where(PatientProfile.user_id == current_user_id)
    result = db.execute(stmt)
    profile = result.scalar_one_or_none()

    # ---- Build user data ----
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

    # ---- Build patient profile ----
    profile_data = None
    if profile:
        profile_data = PatientProfileResponse(
            date_of_birth=profile.date_of_birth,
            age=profile.age,
            gender=profile.gender,
            blood_group=profile.blood_group,

            height_cm=profile.height_cm,
            weight_kg=profile.weight_kg,
            bmi=profile.bmi,

            diagnoses=profile.diagnoses or {},
            allergies=profile.allergies or {},
            medications=profile.medications or {},
            vaccinations=profile.vaccinations or {},
            family_history=profile.family_history or {},

            smoking_status=profile.smoking_status,
            alcohol_use=profile.alcohol_use,
            occupation=profile.occupation,

            insurance=profile.insurance or {},
            emergency_contact=profile.emergency_contact or {},

            primary_provider_id=str(profile.primary_provider_id) if profile.primary_provider_id else None,
            prescreening=profile.prescreening or {},

            contact_preference=profile.contact_preference,
            consent_to_share=profile.consent_to_share,

            location=profile.location,
        )

    return FullProfileResponse(
        user=user_data,
        patient_profile=profile_data
    )

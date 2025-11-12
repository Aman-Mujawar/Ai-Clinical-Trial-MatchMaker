# source/modules/PatientProfile/controller.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
import uuid
from datetime import datetime, timezone

from source.modules.PatientProfile.model import PatientProfile
from source.modules.user.models import Users
from .schemas import PatientProfileRequest, PatientProfileResponse

SYSTEM_UUID = uuid.UUID("00000000-0000-0000-0000-000000000000")

def add_patient_profile(db: Session, user_id: str, request: PatientProfileRequest) -> PatientProfileResponse:
    """
    Create a new patient profile for the authenticated user.
    Automatically assigns current user as primary provider.
    """
    # Verify user exists
    user = db.query(Users).filter(Users.id == uuid.UUID(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if profile already exists
    existing_profile = db.query(PatientProfile).filter(PatientProfile.user_id == user.id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="Patient profile already exists for this user")

    # Automatically assign the current user as the primary provider
    primary_provider_uuid = user.id

    # Create new patient profile
    new_profile = PatientProfile(
        user_id=user.id,
        date_of_birth=request.date_of_birth,
        gender=request.gender,
        blood_group=request.blood_group,
        height_cm=request.height_cm,
        weight_kg=request.weight_kg,
        bmi=request.bmi,
        diagnoses=request.diagnoses,
        allergies=request.allergies,
        medications=request.medications,
        vaccinations=request.vaccinations,
        family_history=request.family_history,
        smoking_status=request.smoking_status,
        alcohol_use=request.alcohol_use,
        occupation=request.occupation,
        insurance=request.insurance,
        emergency_contact=request.emergency_contact,
        prescreening=request.prescreening,
        primary_provider_id=primary_provider_uuid,  # ✅ Automatically set
        consent_to_share=request.consent_to_share,
        contact_preference=request.contact_preference,
        created_by=SYSTEM_UUID,
        modified_by=SYSTEM_UUID
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return PatientProfileResponse(
        message="Patient profile created successfully",
        patient_id=str(new_profile.id),
        user_id=str(user.id)
    )

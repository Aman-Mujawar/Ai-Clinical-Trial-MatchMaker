# source/modules/PatientProfile/controller.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
import uuid
from datetime import datetime, timezone

from source.modules.PatientProfile.model import PatientProfile
from source.modules.user.models import Users
from .schemas import (
    PatientProfileRequest,
    PatientProfileResponse,
    PatientProfileUpdateRequest,
    PatientProfileUpdateResponse
)

SYSTEM_UUID = uuid.UUID("00000000-0000-0000-0000-000000000000")


def add_patient_profile(db: Session, user_id: str, request: PatientProfileRequest) -> PatientProfileResponse:
    user = db.query(Users).filter(Users.id == uuid.UUID(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_profile = db.query(PatientProfile).filter(PatientProfile.user_id == user.id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="Patient profile already exists for this user")

    new_profile = PatientProfile(
        user_id=user.id,
        date_of_birth=request.date_of_birth,
        gender=request.gender,
        blood_group=request.blood_group,
        height_cm=request.height_cm,
        weight_kg=request.weight_kg,
        bmi=request.bmi,
        diagnoses=request.diagnoses or {},
        allergies=request.allergies or {},
        medications=request.medications or {},
        vaccinations=request.vaccinations or {},
        family_history=request.family_history or {},
        smoking_status=request.smoking_status,
        alcohol_use=request.alcohol_use,
        occupation=request.occupation,
        insurance=request.insurance or {},
        emergency_contact=request.emergency_contact or {},
        prescreening=request.prescreening or {},
        primary_provider_id=user.id,
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


def update_patient_profile(db: Session, user_id: str, request: PatientProfileUpdateRequest):
    """
    Safe partial update:
    - Only update provided fields
    - Ignore: None, "", {}, []
    """
    user = db.query(Users).filter(Users.id == uuid.UUID(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = db.query(PatientProfile).filter(PatientProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    # Only include fields explicitly provided in the PATCH body
    update_data = request.model_dump(exclude_unset=True)

    for field, value in update_data.items():

        # ----- Ignore empty fields (frontend + swagger friendly) -----
        if value is None:
            continue
        if isinstance(value, str) and value.strip() == "":
            continue
        if isinstance(value, dict) and len(value.keys()) == 0:
            continue
        if isinstance(value, list) and len(value) == 0:
            continue

        # ----- Apply the update -----
        setattr(profile, field, value)

    profile.modified_at = datetime.now(timezone.utc)
    profile.modified_by = uuid.UUID(user_id)

    db.commit()
    db.refresh(profile)

    return PatientProfileUpdateResponse(
        message="Patient profile updated successfully",
        patient_id=str(profile.id),
        user_id=str(user.id)
    )

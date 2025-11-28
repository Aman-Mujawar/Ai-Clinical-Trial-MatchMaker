# source/modules/PatientProfile/router.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from source.modules.PatientProfile.controller import (
    add_patient_profile,
    update_patient_profile
)

from source.modules.PatientProfile.schemas import (
    PatientProfileRequest,
    PatientProfileResponse,
    PatientProfileUpdateRequest,
    PatientProfileUpdateResponse
)

from source.modules.user.auth import get_current_user_id
from source.database.service import get_db


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.post(
    "/profile",
    response_model=PatientProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Patient Profile",
    description="Create a new patient profile for the authenticated user. Requires JWT token."
)
def create_patient_profile(
    request: PatientProfileRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    return add_patient_profile(db=db, user_id=user_id, request=request)




@router.patch(
    "/profile",
    response_model=PatientProfileUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Patient Profile",
    description="Update fields in the authenticated user's patient profile. Requires JWT token."
)
def edit_patient_profile(
    request: PatientProfileUpdateRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    return update_patient_profile(db=db, user_id=user_id, request=request)

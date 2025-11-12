# source/modules/PatientProfile/router.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from source.modules.PatientProfile.controller import add_patient_profile
from source.modules.PatientProfile.schemas import PatientProfileRequest, PatientProfileResponse
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
    """
    Create a new patient profile for the authenticated user.
    
    **Flow:**
    1. User signs up and receives a JWT token
    2. Frontend stores the token
    3. Frontend immediately calls this endpoint with the token in Authorization header
    4. Patient profile is created and linked to the user
    
    **Authorization:** Bearer token required - Click 'Authorize' button and paste your token
    """
    return add_patient_profile(db=db, user_id=user_id, request=request)
# schemas.py
from datetime import date, datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


# ----------------------------
#   Patient Profile Schema
# ----------------------------
class PatientProfileResponse(BaseModel):
    date_of_birth: Optional[date] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None

    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    bmi: Optional[float] = None

    diagnoses: Optional[Dict[str, Any]] = None
    allergies: Optional[Dict[str, Any]] = None
    medications: Optional[Dict[str, Any]] = None
    vaccinations: Optional[Dict[str, Any]] = None
    family_history: Optional[Dict[str, Any]] = None

    smoking_status: Optional[str] = None
    alcohol_use: Optional[str] = None
    occupation: Optional[str] = None

    insurance: Optional[Dict[str, Any]] = None
    emergency_contact: Optional[Dict[str, Any]] = None

    primary_provider_id: Optional[str] = None
    prescreening: Optional[Dict[str, Any]] = None

    contact_preference: Optional[str] = None
    consent_to_share: Optional[bool] = None

    location: Optional[str] = None

    class Config:
        orm_mode = True


# ----------------------------
#   User Schema
# ----------------------------
class UserResponse(BaseModel):
    id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    role: Optional[str]
    status: Optional[str]
    profile_photo_url: Optional[str]
    bio: Optional[str]
    location: Optional[str]
    is_onboarded: Optional[bool]

    class Config:
        orm_mode = True


# ----------------------------
#   Combined Response Schema
# ----------------------------
class FullProfileResponse(BaseModel):
    user: UserResponse
    patient_profile: Optional[PatientProfileResponse] = None

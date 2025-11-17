from datetime import date, datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, validator


# ----------------------------
#   Patient Profile Schema
# ----------------------------
class PatientProfileResponse(BaseModel):
    date_of_birth: Optional[date] = None
    age: Optional[int] = None  # Will be calculated automatically
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
    #   Validators
    # ----------------------------
    @validator("age", always=True)
    def calculate_age(cls, v, values):
        dob = values.get("date_of_birth")
        if dob:
            today = date.today()
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return None


# ----------------------------
#   User Schema
# ----------------------------
class UserResponse(BaseModel):
    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    profile_photo_url: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    is_onboarded: Optional[bool] = None

    class Config:
        orm_mode = True


# ----------------------------
#   Combined Response Schema
# ----------------------------
class FullProfileResponse(BaseModel):
    user: UserResponse
    patient_profile: Optional[PatientProfileResponse] = None

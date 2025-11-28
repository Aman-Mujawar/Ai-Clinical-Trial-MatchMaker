# source/modules/PatientProfile/schemas.py
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import date
import enum

class GenderEnum(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"

class BloodGroupEnum(str, enum.Enum):
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS = "O+"
    O_NEG = "O-"
    UNKNOWN = "UNKNOWN"

class SmokingStatusEnum(str, enum.Enum):
    NEVER = "NEVER"
    FORMER = "FORMER"
    CURRENT = "CURRENT"
    UNKNOWN = "UNKNOWN"


# -------------------- CREATE --------------------
class PatientProfileRequest(BaseModel):
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    blood_group: Optional[BloodGroupEnum] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    bmi: Optional[float] = None
    diagnoses: Optional[Dict] = {}
    allergies: Optional[Dict] = {}
    medications: Optional[Dict] = {}
    vaccinations: Optional[Dict] = {}
    family_history: Optional[Dict] = {}
    smoking_status: Optional[SmokingStatusEnum] = None
    alcohol_use: Optional[str] = None
    occupation: Optional[str] = None
    insurance: Optional[Dict] = {}
    emergency_contact: Optional[Dict] = {}
    prescreening: Optional[Dict] = {}
    consent_to_share: Optional[bool] = False
    contact_preference: Optional[str] = None


class PatientProfileResponse(BaseModel):
    message: str
    patient_id: str
    user_id: str


# -------------------- UPDATE (PATCH) --------------------
class PatientProfileUpdateRequest(BaseModel):
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    blood_group: Optional[BloodGroupEnum] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    bmi: Optional[float] = None
    diagnoses: Optional[Dict] = None
    allergies: Optional[Dict] = None
    medications: Optional[Dict] = None
    vaccinations: Optional[Dict] = None
    family_history: Optional[Dict] = None
    smoking_status: Optional[SmokingStatusEnum] = None
    alcohol_use: Optional[str] = None
    occupation: Optional[str] = None
    insurance: Optional[Dict] = None
    emergency_contact: Optional[Dict] = None
    prescreening: Optional[Dict] = None
    consent_to_share: Optional[bool] = None
    contact_preference: Optional[str] = None


class PatientProfileUpdateResponse(BaseModel):
    message: str
    patient_id: str
    user_id: str

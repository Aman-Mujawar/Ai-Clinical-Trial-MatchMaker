# source/modules/user/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from source.modules.user.models import UserRole

# ------------------- Signup -------------------
class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: Optional[UserRole] = None  # Optional; default to PATIENT if not provided

class SignupResponse(BaseModel):
    message: str
    email: str
    user_id: str
    first_name: str
    last_name: str
    access_token: str  # Include JWT token here

# ------------------- Login -------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    message: str
    user_id: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: Optional[UserRole]
    access_token: str  # Include JWT token
# schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from source.modules.user.models import UserRole

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str]
    role: Optional[UserRole] = None

class SignupResponse(BaseModel):
    message: str
    email: str
    user_id: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    message: str
    user_id: str
    name: Optional[str]
    role: Optional[UserRole]

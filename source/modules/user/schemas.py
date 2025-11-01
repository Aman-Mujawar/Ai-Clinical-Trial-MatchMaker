# schemas.py - Simplified version
from pydantic import BaseModel, EmailStr

class AddUserRequest(BaseModel):
    name: str
    email: EmailStr

class AddUserResponse(BaseModel):
    message: str
    email: str

class UpdatePasswordRequest(BaseModel):
    email: EmailStr
    new_password: str

class UpdatePasswordResponse(BaseModel):
    message: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    message: str
    user_id: str
    name: str

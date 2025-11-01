# controller.py - Simplified version
import uuid
from sqlalchemy.orm import Session as DbSession
from sqlalchemy import select
from passlib.context import CryptContext
from schemas import AddUserRequest, AddUserResponse, UpdatePasswordResponse, UpdatePasswordRequest, LoginRequest, LoginResponse
from models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def add_user(db: DbSession, request: AddUserRequest) -> AddUserResponse:
    # Check if user already exists
    stmt = select(User).where(User.email == request.email)
    existing_user = db.execute(stmt).scalar_one_or_none()
    
    if existing_user:
        raise ValueError("User with this email already exists")
    
    # Create new user with empty password
    new_user = User(
        id=uuid.uuid4(),
        name=request.name,
        email=request.email,
        password=None  # Initially empty
    )
    
    db.add(new_user)
    db.commit()
    
    return AddUserResponse(
        message="User created successfully. Please set your password.",
        email=request.email
    )

def update_password(db: DbSession, request: UpdatePasswordRequest) -> UpdatePasswordResponse:
    # Find user by email
    stmt = select(User).where(User.email == request.email)
    user = db.execute(stmt).scalar_one_or_none()
    
    if not user:
        raise ValueError("User not found")
    
    # Hash and update password
    hashed_password = pwd_context.hash(request.new_password)
    user.password = hashed_password
    db.commit()
    
    return UpdatePasswordResponse(message="Password updated successfully")

def login_user(db: DbSession, request: LoginRequest) -> LoginResponse:
    # Find user by email
    stmt = select(User).where(User.email == request.email)
    user = db.execute(stmt).scalar_one_or_none()
    
    if not user:
        raise ValueError("Invalid email or password")
    
    if user.password is None:
        raise ValueError("Please set your password first")
    
    # Verify password
    if not pwd_context.verify(request.password, user.password):
        raise ValueError("Invalid email or password")
    
    return LoginResponse(
        message="Login successful",
        user_id=str(user.id),
        name=user.name
    )

# source/modules/user/controller.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone
import uuid

from .models import Users
from .schemas import SignupRequest, SignupResponse, LoginRequest, LoginResponse
from .auth import create_access_token
from .password_utils import hash_password, verify_password  # ✅ updated import

# System UUID for created_by / modified_by
SYSTEM_UUID = uuid.UUID("00000000-0000-0000-0000-000000000000")


def signup_user(db: Session, request: SignupRequest) -> SignupResponse:
    """
    Sign up a new user and return a JWT token immediately.
    """
    # Check for existing user
    existing_user = db.query(Users).filter(Users.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Hash password using password_utils
    hashed_password = hash_password(request.password)

    # Create new user instance
    new_user = Users(
        email=request.email,
        password_hash=hashed_password,
        first_name=request.first_name,
        last_name=request.last_name,
        role=request.role,
        created_by=SYSTEM_UUID,
        modified_by=SYSTEM_UUID,
        is_email_verified=False,
        is_onboarded=False,
        terms_accepted=False
    )

    # Save user
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate JWT token immediately after signup
    access_token = create_access_token(user_id=str(new_user.id))

    return SignupResponse(
        message="User created successfully",
        email=new_user.email,
        user_id=str(new_user.id),
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        access_token=access_token
    )


def login_user(db: Session, request: LoginRequest) -> LoginResponse:
    """
    Login a user and return a JWT token.
    """
    user = db.query(Users).filter(Users.email == request.email).first()
    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # ✅ Verify password using password_utils
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Update last login timestamp
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    # Generate JWT token
    access_token = create_access_token(user_id=str(user.id))

    return LoginResponse(
        message="Login successful",
        user_id=str(user.id),
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        access_token=access_token
    )

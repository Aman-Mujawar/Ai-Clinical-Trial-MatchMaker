# controller.py
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import HTTPException, status
from .models import User
from .schemas import SignupRequest, SignupResponse, LoginRequest, LoginResponse
from datetime import datetime, timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def signup_user(db: Session, request: SignupRequest) -> SignupResponse:
    # Check if user exists
    user = db.query(User).filter(User.email == request.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Hash password safely (truncate to 72 bytes)
    password_bytes = request.password.encode("utf-8")[:72]
    hashed_password = pwd_context.hash(password_bytes)

    new_user = User(
        email=request.email,
        password_hash=hashed_password,
        name=request.name,
        role=request.role,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return SignupResponse(
        message="User created successfully",
        email=new_user.email,
        user_id=str(new_user.id)
    )


def login_user(db: Session, request: LoginRequest) -> LoginResponse:
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password safely
    password_bytes = request.password.encode("utf-8")[:72]
    if not pwd_context.verify(password_bytes, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Update last login timestamp
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    return LoginResponse(
        message="Login successful",
        user_id=str(user.id),
        name=user.name,
        role=user.role
    )

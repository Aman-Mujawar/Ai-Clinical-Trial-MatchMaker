# source/modules/user/router.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from .schemas import SignupRequest, SignupResponse, LoginRequest, LoginResponse
from .controller import signup_user, login_user
from source.database.service import get_db

router = APIRouter(prefix="/users", tags=["Users"])

@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Signup",
    description="Register a new user and receive JWT token immediately"
)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    **Returns:** User details + JWT access token
    
    **Next Step:** Use the returned access_token to create patient profile
    """
    return signup_user(db, request)


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="User Login",
    description="Login existing user and receive JWT token"
)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password.
    
    **Returns:** User details + JWT access token
    """
    return login_user(db, request)
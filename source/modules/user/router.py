from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from source.database.service import get_db
from .schemas import SignupRequest, SignupResponse, LoginRequest, LoginResponse
from . import controller

router = APIRouter()

@router.post("/signup", response_model=SignupResponse)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    return controller.signup_user(db, request)

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    return controller.login_user(db, request)

# router.py - Cleaned version
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from schemas import AddUserRequest, AddUserResponse, UpdatePasswordRequest, UpdatePasswordResponse, LoginRequest, LoginResponse
import controller
from database.service import  get_db

router = APIRouter()

@router.post("/users/add", response_model=AddUserResponse)
def create_user(request: AddUserRequest, db: Session = Depends(get_db)):
    """Create a new user with empty password"""
    try:
        return controller.add_user(db, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/users/update-password", response_model=UpdatePasswordResponse)
def set_password(request: UpdatePasswordRequest, db: Session = Depends(get_db)):
    """Update user password based on email"""
    try:
        return controller.update_password(db, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/users/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login user with email and password"""
    try:
        return controller.login_user(db, request)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

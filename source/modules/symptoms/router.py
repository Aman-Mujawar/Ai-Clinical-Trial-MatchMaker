# source/modules/symptoms/router.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from .schemas import SymptomParseRequest, SymptomParseResponse
from .controller import create_and_store_symptom_entry
from source.database.service import get_db
from source.modules.user.auth import get_current_user_id

router = APIRouter(prefix="/api/symptoms", tags=["Symptoms"])

@router.post("/parse", response_model=SymptomParseResponse, status_code=status.HTTP_201_CREATED)
def parse_symptoms_route(
    request: SymptomParseRequest,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Parse input symptom text, store the parsed result in DB, and return parsed data.
    Current user is resolved via JWT token (get_current_user_id).
    """
    return create_and_store_symptom_entry(db=db, user_id=current_user_id, request=request)

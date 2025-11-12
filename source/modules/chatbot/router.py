from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from source.database.service import get_db
from source.modules.user.auth import get_current_user_id
from .controller import ask_patient_question
from .schemas import AIChatRequest, AIChatResponse

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

@router.post("/ask", response_model=AIChatResponse)
def ask_question(
    request: AIChatRequest,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    return ask_patient_question(db, current_user_id, request)

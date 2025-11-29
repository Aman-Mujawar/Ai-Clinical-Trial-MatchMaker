# source/modules/chatbot/controller.py

from sqlalchemy.orm import Session

from source.modules.PatientProfile.model import PatientProfile
from .schemas import AIChatRequest, AIChatResponse, AIChatMessage, TrialInfo
from .service import (
    generate_patient_answer,
    find_trials_for_chatbot,
    save_or_update_session,
)
from .model import AIChatSession


def ask_patient_question(
    db: Session,
    current_user_id: str,
    request: AIChatRequest
) -> AIChatResponse:
    """
    Main chatbot entrypoint:
      1) Load patient profile (for personalization)
      2) Load conversation history
      3) Generate answer using safety + KB + HF API
      4) Fetch trial suggestions using matching engine
      5) Save chat session
    """
    # 1) Patient profile context (optional)
    patient_profile = db.query(PatientProfile).filter_by(
        user_id=current_user_id
    ).first()

    context = None
    if patient_profile:
        context = {
            "conditions": getattr(patient_profile, "conditions", []) or [],
            "medications": (
                patient_profile.medications.get("current", [])
                if getattr(patient_profile, "medications", None)
                else []
            ),
            "allergies": (
                patient_profile.allergies.get("drug_allergies", [])
                if getattr(patient_profile, "allergies", None)
                else []
            ),
        }

    # 2) Past conversation
    session = db.query(AIChatSession).filter_by(user_id=current_user_id).first()
    history = session.messages if session else []

    # 3) Generate AI answer (safe + KB + HF + follow-ups + personalization)
    answer = generate_patient_answer(
        request.question,
        context=context,
        conversation_history=history,
    )

    # 4) Trial suggestions (using full matching engine)
    trial_matches = find_trials_for_chatbot(request.question)

    # 5) Store/update session
    session = save_or_update_session(db, current_user_id, request.question, answer)
    conversation_messages = [AIChatMessage(**msg) for msg in session.messages]

    return AIChatResponse(
        answer=answer,
        matched_trials=[TrialInfo(**t) for t in trial_matches],
        session_id=str(session.id),
        conversation=conversation_messages,
    )

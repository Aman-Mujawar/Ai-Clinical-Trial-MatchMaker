# source/modules/chatbot/controller.py

import uuid
from sqlalchemy.orm import Session

from source.modules.PatientProfile.model import PatientProfile
from .schemas import AIChatRequest, AIChatResponse, AIChatMessage, TrialInfo
from .service import (
    generate_patient_answer,
    find_trials_for_chatbot,
    save_or_update_session,
)
from .model import AIChatSession


def _build_context_from_profile(profile: PatientProfile) -> dict:
    """
    Build a lightweight context dict from the patient profile
    for personalization.
    """
    conditions = []
    diagnoses = []

    if hasattr(profile, "diagnoses") and isinstance(profile.diagnoses, dict):
        diagnoses = list(profile.diagnoses.keys())

    # Some schemas might store a separate 'conditions' dict/list.
    if hasattr(profile, "conditions"):
        val = getattr(profile, "conditions")
        if isinstance(val, dict):
            conditions = list(val.keys())
        elif isinstance(val, list):
            conditions = val

    meds = []
    if hasattr(profile, "medications") and isinstance(profile.medications, dict):
        # Use all values of the medications dict for context.
        meds = list(profile.medications.values())

    allergies = []
    if hasattr(profile, "allergies") and isinstance(profile.allergies, dict):
        allergies = list(profile.allergies.values())

    return {
        "conditions": conditions,
        "diagnoses": diagnoses,
        "medications": meds,
        "allergies": allergies,
    }


def ask_patient_question(
    db: Session,
    current_user_id: str,
    request: AIChatRequest,
) -> AIChatResponse:
    """
    Orchestrates:
      - Load patient profile context
      - Load chat history
      - Generate answer
      - Fetch matched trials
      - Save updated conversation
    """
    # Fetch patient profile
    try:
        user_uuid = uuid.UUID(current_user_id)
    except Exception:
        user_uuid = None

    patient_profile = (
        db.query(PatientProfile).filter_by(user_id=user_uuid).first()
        if user_uuid
        else None
    )

    context = _build_context_from_profile(patient_profile) if patient_profile else None

    # Existing session / history
    session: AIChatSession | None = (
        db.query(AIChatSession).filter_by(user_id=current_user_id).first()
    )
    history = session.messages if session else []

    # Generate AI answer
    answer = generate_patient_answer(request.question, context=context, history=history)

    # Related trials
    trial_matches = find_trials_for_chatbot(request.question)

    # Save session
    session = save_or_update_session(db, current_user_id, request.question, answer)
    conversation_messages = [AIChatMessage(**msg) for msg in session.messages]

    return AIChatResponse(
        answer=answer,
        matched_trials=[TrialInfo(**t) for t in trial_matches],
        session_id=str(session.id),
        conversation=conversation_messages,
    )

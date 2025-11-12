from sqlalchemy.orm import Session
from source.modules.PatientProfile.model import PatientProfile
from .schemas import AIChatRequest, AIChatResponse, AIChatMessage, TrialInfo
from .service import generate_patient_answer, search_trials_with_question, save_or_update_session
from .model import AIChatSession


def ask_patient_question(db: Session, current_user_id: str, request: AIChatRequest) -> AIChatResponse:
    # Fetch patient profile
    patient_profile = db.query(PatientProfile).filter_by(user_id=current_user_id).first()

    context = None
    if patient_profile:
        context = {
            "conditions": patient_profile.conditions or [],
            "medications": patient_profile.medications.get("current", []) if patient_profile.medications else [],
            "allergies": patient_profile.allergies.get("drug_allergies", []) if patient_profile.allergies else [],
        }

    # Load chat history
    session = db.query(AIChatSession).filter_by(user_id=current_user_id).first()
    history = session.messages if session else []

    # Generate AI advice
    answer = generate_patient_answer(request.question, context, history)

    # Get top 3–5 related trials
    trial_matches = search_trials_with_question(db, request.question)

    # Update or create session
    session = save_or_update_session(db, current_user_id, request.question, answer)

    conversation_messages = [AIChatMessage(**msg) for msg in session.messages]

    return AIChatResponse(
        answer=answer,
        matched_trials=[TrialInfo(**t) for t in trial_matches],
        session_id=str(session.id),
        conversation=conversation_messages,
    )

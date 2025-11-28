# source/modules/symptoms/controller.py
import uuid
from sqlalchemy.orm import Session
from .service import parse_symptoms_text
from .schemas import SymptomParseRequest, SymptomParseResponse, SymptomDetail
from .model import SymptomEntry
from datetime import datetime

def create_and_store_symptom_entry(
    db: Session, user_id: str, request: SymptomParseRequest
) -> SymptomParseResponse:
    """
    Parses symptoms text, saves the result to the database, and returns structured response.
    """

    # Step 1: Parse the symptom text using enhanced NLP
    parsed_symptoms_list, icd_codes = parse_symptoms_text(request.symptom_text)

    # Step 2: Store in DB as comma-separated for backward compatibility
    parsed_symptoms_text = ",".join([s["symptom"] for s in parsed_symptoms_list]) if parsed_symptoms_list else None
    entry = SymptomEntry(
        user_id=uuid.UUID(user_id),
        symptom_text=request.symptom_text,
        parsed_symptoms=parsed_symptoms_text,
        severity=parsed_symptoms_list[0]["severity"] if parsed_symptoms_list else "mild",
        created_at=datetime.utcnow()
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    # Step 3: Return structured response
    parsed_symptoms_objs = [SymptomDetail(**s) for s in parsed_symptoms_list]

    return SymptomParseResponse(
        entry_id=str(entry.id),
        user_id=str(entry.user_id),
        symptom_text=entry.symptom_text,
        parsed_symptoms=parsed_symptoms_objs,
        created_at=entry.created_at
    )

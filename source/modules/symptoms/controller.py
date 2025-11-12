# source/modules/symptoms/controller.py
import uuid
from sqlalchemy.orm import Session

from .service import parse_symptoms_text
from .schemas import SymptomParseRequest, SymptomParseResponse
from .model import SymptomEntry


def create_and_store_symptom_entry(
    db: Session, user_id: str, request: SymptomParseRequest
) -> SymptomParseResponse:
    """
    Parses symptoms text, saves the result to the database, and returns the response.
    """

    # Step 1: Parse the symptom text using NLP / AI helper
    parsed_symptoms, icd_codes = parse_symptoms_text(request.symptom_text)

    # Step 2: Create new SymptomEntry record
    entry = SymptomEntry(
        user_id=uuid.UUID(user_id),
        symptom_text=request.symptom_text,
        parsed_symptoms=",".join(parsed_symptoms) if parsed_symptoms else None,
        severity="mild",  # placeholder - can be replaced by AI severity detection
    )

    # Step 3: Save to DB
    db.add(entry)
    db.commit()
    db.refresh(entry)

    # Step 4: Build and return the response
    response = SymptomParseResponse(
        entry_id=str(entry.id),
        user_id=str(entry.user_id),
        symptom_text=entry.symptom_text,
        parsed_symptoms=parsed_symptoms,
        severity=entry.severity,
        created_at=entry.created_at,
    )
    return response

# source/modules/symptoms/schemas.py
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional


class SymptomParseRequest(BaseModel):
    symptom_text: str


class SymptomParseResponse(BaseModel):
    entry_id: str
    user_id: str
    symptom_text: str
    parsed_symptoms: List[str]
    severity: Optional[str] = None
    created_at: Optional[datetime] = None

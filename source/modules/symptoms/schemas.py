# source/modules/symptoms/schemas.py
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class SymptomDetail(BaseModel):
    symptom: str
    body_part: Optional[str] = None
    duration: Optional[str] = None
    severity: Optional[str] = None
    character: Optional[str] = None
    aggravators: Optional[List[str]] = []
    relievers: Optional[List[str]] = []

class SymptomParseRequest(BaseModel):
    symptom_text: str

class SymptomParseResponse(BaseModel):
    entry_id: str
    user_id: str
    symptom_text: str
    parsed_symptoms: List[SymptomDetail]
    created_at: Optional[datetime] = None

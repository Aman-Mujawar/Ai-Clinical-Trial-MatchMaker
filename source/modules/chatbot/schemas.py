from pydantic import BaseModel
from typing import List, Optional


class AIChatMessage(BaseModel):
    role: str
    content: str


class TrialInfo(BaseModel):
    nct_id: str
    title: Optional[str]
    status: Optional[str]
    location: Optional[str]
    url: Optional[str]
    google_maps_url: Optional[str] = None


class AIChatRequest(BaseModel):
    question: str


class AIChatResponse(BaseModel):
    answer: str
    matched_trials: List[TrialInfo]
    session_id: str
    conversation: List[AIChatMessage]

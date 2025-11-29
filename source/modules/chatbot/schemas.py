# source/modules/chatbot/schemas.py
from pydantic import BaseModel
from typing import Optional, List


class TrialInfo(BaseModel):
    # Core identifiers
    nct_id: Optional[str] = None
    title: Optional[str] = None

    # Clinical details
    status: Optional[str] = None
    phase: Optional[str] = None
    conditions: Optional[List[str]] = None
    sponsor: Optional[str] = None

    # Location / logistics
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    google_maps_url: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

    # Content
    summary: Optional[str] = None   # may already be simplified
    url: Optional[str] = None

    # Matching meta
    confidence_score: Optional[float] = None
    explanation: Optional[str] = None
    ai_generated: bool = False


class AIChatMessage(BaseModel):
    role: str
    content: str
    ts: str


class AIChatRequest(BaseModel):
    question: str


class AIChatResponse(BaseModel):
    answer: str
    matched_trials: List[TrialInfo]
    session_id: str
    conversation: List[AIChatMessage]

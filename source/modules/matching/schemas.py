# source/modules/matching/schemas.py
from pydantic import BaseModel
from typing import List, Optional


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

    # Content / explanation
    summary: Optional[str] = None
    url: Optional[str] = None

    # AI / ranking
    confidence_score: float
    explanation: str
    ai_generated: bool = False  # True if purely from fallback / synthetic source


class TrialMatchRequest(BaseModel):
    query_text: str
    filter_status: Optional[str] = None
    filter_location_contains: Optional[str] = None
    sort_by: Optional[str] = "confidence"  # confidence | title | status
    limit: Optional[int] = 10


class TrialMatchResponse(BaseModel):
    match_id: str
    user_id: str
    query_text: str
    matched_trials: List[TrialInfo]

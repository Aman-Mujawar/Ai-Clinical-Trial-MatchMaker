from pydantic import BaseModel
from typing import List, Optional


class TrialInfo(BaseModel):
    nct_id: str
    title: Optional[str]
    status: Optional[str]
    location: Optional[str]
    url: Optional[str]
    google_maps_url: Optional[str]
    confidence_score: float
    explanation: str


class TrialMatchRequest(BaseModel):
    query_text: str

    # Optional enhancements from project requirements
    filter_status: Optional[str] = None               # e.g. "Recruiting"
    filter_location_contains: Optional[str] = None    # e.g. "Charlotte"
    sort_by: Optional[str] = "confidence"             # "confidence" | "title" | "status"
    limit: Optional[int] = 5                          # external trials fetch limit


class TrialMatchResponse(BaseModel):
    match_id: str
    user_id: str
    query_text: str
    matched_trials: List[TrialInfo]

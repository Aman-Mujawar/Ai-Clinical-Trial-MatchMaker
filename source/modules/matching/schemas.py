from pydantic import BaseModel
from typing import List, Optional

class TrialInfo(BaseModel):
    nct_id: str
    title: Optional[str]
    status: Optional[str]
    location: Optional[str]
    url: Optional[str]
    google_maps_url: Optional[str]  # new field for frontend map link

class TrialMatchRequest(BaseModel):
    query_text: str

class TrialMatchResponse(BaseModel):
    match_id: str
    user_id: str
    query_text: str
    matched_trials: List[TrialInfo]

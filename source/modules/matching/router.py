# source/modules/TrialMatching/router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from source.database.service import get_db
from source.modules.user.auth import get_current_user_id
from .controller import create_trial_match_entry
from .schemas import TrialMatchRequest, TrialMatchResponse

router = APIRouter(prefix="/api/matching", tags=["matching"])


@router.post("/search", response_model=TrialMatchResponse)
def search_trials(
    request: TrialMatchRequest,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Search clinical trials based on:
      - User's free-text query (symptoms/condition)
      - (Optionally) patient profile (age, gender, diagnoses)
      - External registries with fallbacks:
          WHO TrialSearch → PubMed → EUCTR → AI-generated suggestions

    This endpoint NEVER returns an empty `matched_trials` list.
    """
    return create_trial_match_entry(db=db, user_id=current_user_id, request=request)

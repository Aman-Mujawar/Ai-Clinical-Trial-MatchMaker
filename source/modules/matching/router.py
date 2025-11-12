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
    Search clinical trials based on user input and patient profile.
    """
    return create_trial_match_entry(db=db, user_id=current_user_id, request=request)

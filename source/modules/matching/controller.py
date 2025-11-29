# source/modules/matching/controller.py

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

from sqlalchemy.orm import Session

from source.modules.PatientProfile.model import PatientProfile
from .model import TrialMatch
from .schemas import TrialMatchRequest, TrialMatchResponse, TrialInfo
from .service import fetch_trials_with_fallbacks


def _get_patient_profile_data(db: Session, user_id: str) -> Optional[Dict[str, Any]]:
    """
    Optional patient-based context. You can extend this later for personalization.
    """
    profile = db.query(PatientProfile).filter_by(user_id=uuid.UUID(user_id)).first()
    if not profile:
        return None

    # Try to assemble some simple structured info
    conditions: List[str] = []
    if isinstance(profile.diagnoses, dict):
        conditions = list(profile.diagnoses.keys())

    return {
        "age": getattr(profile, "age", None),
        "gender": getattr(profile, "gender", None),
        "conditions": conditions,
        "location": getattr(profile, "location", None),
    }


def create_trial_match_entry(
    db: Session,
    user_id: str,
    request: TrialMatchRequest
) -> TrialMatchResponse:
    """
    Main matching pipeline:
      1) (Optionally) use patient profile for future personalization
      2) Fetch trials from multiple external sources with fallbacks
      3) Apply simple filters (status, location)
      4) Sort
      5) Save JSONB in trial_matches
      6) Return detailed trial objects with confidence & explanation
    """
    # 1) (Optional) Patient profile context (not heavily used yet)
    _ = _get_patient_profile_data(db, user_id=user_id)

    # 2) Fetch with fallbacks (guaranteed non-empty)
    desired_limit = request.limit or 10
    all_trials = fetch_trials_with_fallbacks(request.query_text, desired_limit=desired_limit)

    # 3) Apply filters (status, location substring)
    filtered = []
    for t in all_trials:
        ok = True

        if request.filter_status:
            status = (t.get("status") or "").lower()
            if request.filter_status.lower() not in status:
                ok = False

        if ok and request.filter_location_contains:
            loc = (t.get("location") or "").lower()
            if request.filter_location_contains.lower() not in loc:
                ok = False

        if ok:
            filtered.append(t)

    if not filtered:
        # If filters remove everything, fall back to unfiltered list
        filtered = all_trials

    # 4) Sort
    sort_by = (request.sort_by or "confidence").lower()

    if sort_by == "title":
        filtered.sort(key=lambda x: (x.get("title") or "").lower())
    elif sort_by == "status":
        filtered.sort(key=lambda x: (x.get("status") or "").lower())
    else:  # default: confidence
        filtered.sort(key=lambda x: x.get("confidence_score", 0.0), reverse=True)

    # Truncate to requested limit
    filtered = filtered[:desired_limit]

    # 5) Persist in DB as JSONB
    entry = TrialMatch(
        id=uuid.uuid4(),
        user_id=uuid.UUID(user_id),
        query_text=request.query_text,
        matched_trials=filtered,
        created_at=datetime.utcnow(),
        modified_at=datetime.utcnow(),
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    # 6) Build response
    trial_infos = [TrialInfo(**t) for t in filtered]

    resp = TrialMatchResponse(
        match_id=str(entry.id),
        user_id=str(entry.user_id),
        query_text=entry.query_text,
        matched_trials=trial_infos,
    )
    return resp

import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_

from fastapi import Depends
from source.modules.PatientProfile.model import PatientProfile
from source.modules.user.auth import get_current_user_id
from .schemas import TrialMatchRequest, TrialMatchResponse, TrialInfo
from .model import TrialMatch
from source.modules.trails.model import Trial  # Your trials table
from source.database.service import get_db
from .service import fetch_trials_from_ctgov  # optional external fetch


def create_trial_match_entry(
    db: Session,
    user_id: str,
    request: TrialMatchRequest
) -> TrialMatchResponse:
    """
    Creates a trial match entry for a given user and query text.
    Matches trials from local DB based on parsed symptoms.
    Optionally can integrate external CTGov fetch if needed.
    """

    # Fetch patient profile if exists
    patient_profile = db.query(PatientProfile).filter_by(user_id=uuid.UUID(user_id)).first()
    patient_data = None
    if patient_profile:
        patient_data = {
            "age": patient_profile.age,
            "gender": patient_profile.gender,
            "conditions": patient_profile.conditions or [],
            "location": patient_profile.location
        }

    # Determine keywords for matching
    parsed_symptoms = getattr(request, "parsed_symptoms", [])
    if not parsed_symptoms and hasattr(request, "query_text"):
        parsed_symptoms = request.query_text.lower().split()

    # Query local trials DB using OR matching on title
    filters = [Trial.title.ilike(f"%{kw}%") for kw in parsed_symptoms]
    matched_trials_db = db.query(Trial).filter(or_(*filters)).all()

    # Convert DB trials to JSON-like list and add Google Maps URL
    matched_trials_json = []
    for trial in matched_trials_db:
        if trial.latitude and trial.longitude:
            # Use coordinates if available
            google_maps_url = f"https://www.google.com/maps/search/?api=1&query={trial.latitude},{trial.longitude}"
        elif trial.location:
            location_query = trial.location.replace(" ", "+")
            google_maps_url = f"https://www.google.com/maps/search/?api=1&query={location_query}"
        else:
            google_maps_url = None

        matched_trials_json.append({
            "nct_id": trial.nct_id,
            "title": trial.title,
            "status": trial.status,
            "location": trial.location,
            "url": trial.url,
            "google_maps_url": google_maps_url
        })


    # Optionally, include external CTGov fetch
    external_trials = fetch_trials_from_ctgov(request.query_text, patient_data=patient_data)
    if external_trials:
        for trial in external_trials:
            if trial.get("location"):
                location_query = trial["location"].replace(" ", "+")
                trial["google_maps_url"] = f"https://www.google.com/maps/search/?api=1&query={location_query}"
            else:
                trial["google_maps_url"] = None
        matched_trials_json.extend(external_trials)

    # Remove duplicates based on nct_id
    seen_nct_ids = set()
    final_trials = []
    for t in matched_trials_json:
        if t["nct_id"] not in seen_nct_ids:
            final_trials.append(t)
            seen_nct_ids.add(t["nct_id"])

    # Save trial match in DB
    entry = TrialMatch(
        id=uuid.uuid4(),
        user_id=uuid.UUID(user_id),
        query_text=request.query_text,
        matched_trials=final_trials,
        created_at=datetime.utcnow(),
        modified_at=datetime.utcnow()
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    # Prepare response
    response = TrialMatchResponse(
        match_id=str(entry.id),
        user_id=str(entry.user_id),
        query_text=entry.query_text,
        matched_trials=[TrialInfo(**t) for t in final_trials]
    )
    return response

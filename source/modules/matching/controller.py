import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_

from source.modules.PatientProfile.model import PatientProfile
from .schemas import TrialMatchRequest, TrialMatchResponse, TrialInfo
from .model import TrialMatch
from source.modules.trails.model import Trial  # Your trials table
from .service import (
    fetch_combined_trials,
    compute_confidence_score,
    generate_plain_language_explanation,
)


def create_trial_match_entry(
    db: Session,
    user_id: str,
    request: TrialMatchRequest
) -> TrialMatchResponse:
    """
    Creates a trial match entry for a given user and query text.

    Logic:
    1) Load patient profile (if exists) for personalization
    2) Parse symptoms/keywords from query_text
    3) Match local DB trials based on title keywords
    4) Fetch external trials from WHO + PubMed + FDA
    5) Add Google Maps URL, confidence_score, and explanation to each trial
    6) Deduplicate trials by nct_id
    7) Apply filtering & sorting (status/location/sort_by) as requested
    8) Store results in TrialMatch JSONB field and return them
    """

    # 1) Fetch patient profile if exists
    patient_profile = db.query(PatientProfile).filter_by(user_id=uuid.UUID(user_id)).first()
    patient_data = None
    if patient_profile:
        # Safely read attributes that may or may not exist
        patient_data = {
            "age": getattr(patient_profile, "age", None),
            "gender": getattr(patient_profile, "gender", None),
            "conditions": getattr(patient_profile, "diagnoses", None) or [],
            "location": getattr(patient_profile, "location", None),
        }

    # 2) Determine keywords for matching
    parsed_symptoms = getattr(request, "parsed_symptoms", [])
    if not parsed_symptoms and hasattr(request, "query_text") and request.query_text:
        parsed_symptoms = request.query_text.lower().split()

    # 3) Query local trials DB using OR matching on title
    matched_trials_db = []
    if parsed_symptoms:
        filters = [Trial.title.ilike(f"%{kw}%") for kw in parsed_symptoms]
        matched_trials_db = db.query(Trial).filter(or_(*filters)).all()

    # 4) Convert DB trials to JSON-like list and add Google Maps URL
    matched_trials_json = []
    for trial in matched_trials_db:
        location_value = getattr(trial, "location", None)
        lat = getattr(trial, "latitude", None)
        lng = getattr(trial, "longitude", None)

        if lat is not None and lng is not None:
            google_maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
        elif location_value:
            location_query = str(location_value).replace(" ", "+")
            google_maps_url = f"https://www.google.com/maps/search/?api=1&query={location_query}"
        else:
            google_maps_url = None

        matched_trials_json.append(
            {
                "nct_id": trial.nct_id,
                "title": trial.title,
                "status": trial.status,
                "location": location_value,
                "url": trial.url,
                "google_maps_url": google_maps_url,
            }
        )

    # 5) External trials from WHO + PubMed + FDA (replacement for ClinicalTrials.gov)
    external_trials = fetch_combined_trials(
        query=request.query_text,
        patient_data=patient_data,
        limit=request.limit or 5,
    )

    if external_trials:
        for trial in external_trials:
            loc = trial.get("location")
            if loc:
                location_query = str(loc).replace(" ", "+")
                trial["google_maps_url"] = (
                    f"https://www.google.com/maps/search/?api=1&query={location_query}"
                )
            else:
                trial["google_maps_url"] = None

        matched_trials_json.extend(external_trials)

    # 6) Add confidence_score & explanation to ALL trials
    for t in matched_trials_json:
        t["confidence_score"] = compute_confidence_score(
            trial=t,
            patient_data=patient_data,
            query_text=request.query_text,
        )
        t["explanation"] = generate_plain_language_explanation(
            trial=t,
            confidence_score=t["confidence_score"],
            query_text=request.query_text,
        )

    # 7) Remove duplicates based on nct_id
    seen_nct_ids = set()
    final_trials = []
    for t in matched_trials_json:
        nct = t.get("nct_id")
        if not nct:
            continue
        if nct not in seen_nct_ids:
            final_trials.append(t)
            seen_nct_ids.add(nct)

    # 8) Apply filtering (status, location) if provided
    if request.filter_status:
        status_filter = request.filter_status.lower()
        final_trials = [
            t for t in final_trials
            if t.get("status") and status_filter in str(t["status"]).lower()
        ]

    if request.filter_location_contains:
        loc_filter = request.filter_location_contains.lower()
        final_trials = [
            t for t in final_trials
            if t.get("location") and loc_filter in str(t["location"]).lower()
        ]

    # 9) Sorting
    sort_by = request.sort_by or "confidence"
    if sort_by == "confidence":
        final_trials.sort(key=lambda t: t.get("confidence_score", 0.0), reverse=True)
    elif sort_by == "title":
        final_trials.sort(key=lambda t: (t.get("title") or "").lower())
    elif sort_by == "status":
        final_trials.sort(key=lambda t: (t.get("status") or "").lower())
    # else: keep natural order

    # 10) Save trial match in DB
    entry = TrialMatch(
        id=uuid.uuid4(),
        user_id=uuid.UUID(user_id),
        query_text=request.query_text,
        matched_trials=final_trials,
        created_at=datetime.utcnow(),
        modified_at=datetime.utcnow(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    # 11) Prepare response
    response = TrialMatchResponse(
        match_id=str(entry.id),
        user_id=str(entry.user_id),
        query_text=entry.query_text,
        matched_trials=[TrialInfo(**t) for t in final_trials],
    )
    return response

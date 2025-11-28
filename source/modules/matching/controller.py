# source/modules/TrialMatching/controller.py

import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_

from source.modules.PatientProfile.model import PatientProfile
from source.modules.trails.model import Trial  # your local trials table
from .schemas import TrialMatchRequest, TrialMatchResponse, TrialInfo
from .model import TrialMatch
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

    PIPELINE:
      1. Load patient profile (if exists) for personalization
      2. Match local DB trials by keywords in title (optional, DB can be empty)
      3. Fetch external trials via WHO → PubMed → EUCTR → AI fallback
      4. Add google_maps_url, confidence_score, explanation to each trial
      5. Deduplicate trials by nct_id
      6. Apply optional filters (status, location) & sorting (confidence/title/status)
      7. Persist result in TrialMatch JSONB
    """

    # 1) Fetch patient profile if exists (safe getattr to avoid crashes)
    patient_profile = db.query(PatientProfile).filter_by(user_id=uuid.UUID(user_id)).first()
    patient_data = None
    if patient_profile:
        patient_data = {
            # You can later compute age from date_of_birth if needed
            "age": None,
            "gender": getattr(patient_profile, "gender", None),
            # diagnoses is a dict or JSON field in your schema
            "conditions": getattr(patient_profile, "diagnoses", None) or [],
            # location is not in PatientProfile today – you might store it in Users later
            "location": None,
        }

    # 2) Determine keywords for matching local DB trials
    parsed_symptoms = getattr(request, "parsed_symptoms", [])
    if not parsed_symptoms and request.query_text:
        parsed_symptoms = request.query_text.lower().split()

    # 3) Optional local DB trials – safe even if table is empty
    matched_trials_db = []
    if parsed_symptoms:
        filters = [Trial.title.ilike(f"%{kw}%") for kw in parsed_symptoms]
        matched_trials_db = db.query(Trial).filter(or_(*filters)).all()

    matched_trials_json = []
    for trial in matched_trials_db:
        location_value = getattr(trial, "location", None)
        lat = getattr(trial, "lat", None) if hasattr(trial, "lat") else getattr(trial, "latitude", None)
        lng = getattr(trial, "lng", None) if hasattr(trial, "lng") else getattr(trial, "longitude", None)

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

    # 4) External trials with FALLBACKS (WHO → PubMed → EUCTR → AI guaranteed)
    external_trials = fetch_combined_trials(
        query=request.query_text,
        patient_data=patient_data,
        limit=request.limit or 5,
    )

    if external_trials:
        for ext in external_trials:
            loc = ext.get("location")
            if loc:
                location_query = str(loc).replace(" ", "+")
                ext["google_maps_url"] = (
                    f"https://www.google.com/maps/search/?api=1&query={location_query}"
                )
            else:
                ext["google_maps_url"] = None

        matched_trials_json.extend(external_trials)

    # 5) Add confidence_score & explanation to ALL trials
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

    # 6) Remove duplicates based on nct_id
    seen_nct_ids = set()
    final_trials = []
    for t in matched_trials_json:
        nct = t.get("nct_id")
        if not nct:
            continue
        if nct not in seen_nct_ids:
            final_trials.append(t)
            seen_nct_ids.add(nct)

    # 7) Apply optional filters
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

    # 8) Sorting
    sort_by = request.sort_by or "confidence"
    if sort_by == "confidence":
        final_trials.sort(key=lambda t: t.get("confidence_score", 0.0), reverse=True)
    elif sort_by == "title":
        final_trials.sort(key=lambda t: (t.get("title") or "").lower())
    elif sort_by == "status":
        final_trials.sort(key=lambda t: (t.get("status") or "").lower())
    # else: keep order

    # 9) Persist JSONB in TrialMatch table
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

    # 10) Prepare response
    response = TrialMatchResponse(
        match_id=str(entry.id),
        user_id=str(entry.user_id),
        query_text=entry.query_text,
        matched_trials=[TrialInfo(**t) for t in final_trials],
    )
    return response

# source/modules/matching/service.py

import re
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup  # still installed; not strictly needed now

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity




def build_google_maps_url(location: Optional[str]) -> Optional[str]:
    if not location:
        return None
    q = location.replace(" ", "+")
    return f"https://www.google.com/maps/search/?api=1&query={q}"




CTGOV_BASE_URL = "https://clinicaltrials.gov/api/v2/studies"


def _extract_ctgov_location(protocol_section: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pull a single representative location (city/state/country)
    from contactsLocationsModule if available.
    """
    contacts = protocol_section.get("contactsLocationsModule", {}) or {}
    locations = contacts.get("locations") or []

    city = state = country = location_text = None
    lat = lng = None  # CT.gov API v2 does not currently expose geo coords

    if locations:
        loc0 = locations[0] or {}
        city = loc0.get("city")
        state = loc0.get("state")
        country = loc0.get("country")

        parts = [p for p in [city, state, country] if p]
        location_text = ", ".join(parts) if parts else None

    return {
        "city": city,
        "state": state,
        "country": country,
        "location": location_text,
        "lat": lat,
        "lng": lng,
    }


def fetch_trials_from_ctgov_api(
    query: str,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Use ClinicalTrials.gov API v2 as the main clinical-trial source.

    We query by general term (query.term) so it works for conditions,
    interventions, etc. We keep it simple and only pull one page.
    """
    trials: List[Dict[str, Any]] = []

    try:
        params = {
            "format": "json",
            "pageSize": limit,
            "query.term": query,
        }
        resp = requests.get(CTGOV_BASE_URL, params=params, timeout=10)
        if resp.status_code != 200:
            return trials

        data = resp.json()
        studies = data.get("studies", []) or []

        for study in studies:
            protocol = study.get("protocolSection", {}) or {}

            ident = protocol.get("identificationModule", {}) or {}
            desc = protocol.get("descriptionModule", {}) or {}
            status_mod = protocol.get("statusModule", {}) or {}
            cond_mod = protocol.get("conditionsModule", {}) or {}
            design_mod = protocol.get("designModule", {}) or {}
            sponsor_mod = protocol.get("sponsorCollaboratorsModule", {}) or {}

            nct_id = ident.get("nctId")
            title = (
                ident.get("officialTitle")
                or ident.get("briefTitle")
                or "Untitled clinical trial"
            )

            summary = (
                desc.get("briefSummary")
                or desc.get("detailedDescription")
                or ""
            )

            status = status_mod.get("overallStatus")
            phases = design_mod.get("phases") or []
            if isinstance(phases, list):
                phase = ", ".join(phases) if phases else None
            else:
                phase = phases

            conditions = cond_mod.get("conditions") or []

            lead_sponsor = sponsor_mod.get("leadSponsor") or {}
            sponsor = lead_sponsor.get("name")

            loc_info = _extract_ctgov_location(protocol)

            url = f"https://clinicaltrials.gov/study/{nct_id}" if nct_id else None
            google_maps_url = build_google_maps_url(loc_info["location"])

            trials.append(
                {
                    "nct_id": nct_id,
                    "title": title,
                    "summary": summary,
                    "status": status,
                    "phase": phase,
                    "conditions": conditions,
                    "sponsor": sponsor,
                    "location": loc_info["location"],
                    "city": loc_info["city"],
                    "state": loc_info["state"],
                    "country": loc_info["country"],
                    "lat": loc_info["lat"],
                    "lng": loc_info["lng"],
                    "url": url,
                    "google_maps_url": google_maps_url,
                    "ai_generated": False,
                }
            )

            if len(trials) >= limit:
                break

    except Exception:
        # We fail silently here; caller will use fallbacks.
        return trials

    return trials



def fetch_trials_from_semantic_scholar(
    query: str,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Use Semantic Scholar as a research-paper fallback. We map papers
    into the same 'trial-like' structure used by the rest of the system.
    """
    results: List[Dict[str, Any]] = []
    try:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,abstract,url,venue,year",
        }
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            return results

        data = resp.json()
        for paper in data.get("data", []):
            title = paper.get("title")
            abstract = paper.get("abstract")
            url_paper = paper.get("url")
            venue = paper.get("venue")
            year = paper.get("year")

            summary = abstract or f"Research paper in {venue} ({year}) related to {query}."

            results.append(
                {
                    "nct_id": None,
                    "title": title,
                    "summary": summary,
                    "status": "NOT_AVAILABLE",
                    "phase": None,
                    "sponsor": venue,
                    "conditions": None,
                    "location": None,
                    "city": None,
                    "state": None,
                    "country": None,
                    "lat": None,
                    "lng": None,
                    "url": url_paper,
                    "google_maps_url": None,
                    "ai_generated": False,
                }
            )

            if len(results) >= limit:
                break

    except Exception:
        return results

    return results




LOCAL_FALLBACK_TRIALS: List[Dict[str, Any]] = [
    {
        "nct_id": "LOCAL001",
        "title": "General Oncology Support Trial",
        "summary": "A generic oncology support study used as fallback data for demonstration purposes.",
        "status": "Recruiting",
        "phase": "Phase 2",
        "sponsor": "Example Cancer Center",
        "conditions": ["Cancer"],
        "location": "Charlotte, NC, USA",
        "city": "Charlotte",
        "state": "NC",
        "country": "USA",
        "lat": 35.2271,
        "lng": -80.8431,
        "url": "https://example.org/trials/local001",
    },
    {
        "nct_id": "LOCAL002",
        "title": "Immunotherapy Support Study",
        "summary": "A generalized immunotherapy study used as fallback to ensure non-empty results.",
        "status": "Active, not recruiting",
        "phase": "Phase 3",
        "sponsor": "Global Research Institute",
        "conditions": ["Immunotherapy", "Cancer"],
        "location": "Raleigh, NC, USA",
        "city": "Raleigh",
        "state": "NC",
        "country": "USA",
        "lat": 35.7796,
        "lng": -78.6382,
        "url": "https://example.org/trials/local002",
    },
    {
        "nct_id": "LOCAL003",
        "title": "Chronic Disease Management Program",
        "summary": "A chronic disease management trial used as generic fallback data.",
        "status": "Completed",
        "phase": "Phase 4",
        "sponsor": "HealthCare Group",
        "conditions": ["Chronic Disease"],
        "location": "Atlanta, GA, USA",
        "city": "Atlanta",
        "state": "GA",
        "country": "USA",
        "lat": 33.7490,
        "lng": -84.3880,
        "url": "https://example.org/trials/local003",
    },
]


def get_local_fallback_trials(limit: int = 5) -> List[Dict[str, Any]]:
    trials: List[Dict[str, Any]] = []
    for t in LOCAL_FALLBACK_TRIALS:
        item = t.copy()
        item["google_maps_url"] = build_google_maps_url(item.get("location"))
        # ai_generated is set later when we actually use them as fallback
        trials.append(item)
        if len(trials) >= limit:
            break
    return trials



def compute_confidence_scores(
    query: str,
    trials: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Use TF-IDF cosine similarity between query and trial text (title + summary).
    Adds 'confidence_score' and 'explanation' to each trial dict.

    This supports user story 5 & 6 (ranked matches with confidence +
    explanation in plain-ish English).
    """
    if not trials:
        return []

    corpus: List[str] = []
    for t in trials:
        text_parts = [
            t.get("title") or "",
            t.get("summary") or "",
            " ".join(t.get("conditions", []) or []),
            t.get("location") or "",
        ]
        corpus.append(" ".join(text_parts))

    texts = [query] + corpus  # first is query
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(texts)

    query_vec = tfidf[0:1]
    trial_vecs = tfidf[1:]

    sims = cosine_similarity(query_vec, trial_vecs)[0]

    results: List[Dict[str, Any]] = []
    for trial, score in zip(trials, sims):
        confidence = float(round(score, 4))

        title = trial.get("title") or "this trial"
        loc = trial.get("location") or "various locations"

        explanation = (
            f"This match, '{title}', appears relevant to your search '{query}'. "
            f"It is located at {loc}. The match confidence score is "
            f"{int(confidence * 100)}%, based on similarity between your search "
            f"and the trial details (title, summary, and conditions)."
        )

        trial["confidence_score"] = confidence
        trial["explanation"] = explanation
        results.append(trial)

    return results


def fetch_trials_with_fallbacks(
    query: str,
    desired_limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Hybrid A + C:
      1) ClinicalTrials.gov API v2 (real trials with locations)
      2) Semantic Scholar (research papers as "trials")
      3) Local fallback trials (never empty)

    Always returns at least one trial unless something catastrophic happens.
    """
    collected: List[Dict[str, Any]] = []

    # 1) ClinicalTrials.gov API
    ctgov_trials = fetch_trials_from_ctgov_api(query, limit=desired_limit)
    collected.extend(ctgov_trials)

    # 2) Semantic Scholar (only if we still need more)
    if len(collected) < desired_limit:
        remaining = desired_limit - len(collected)
        sem_trials = fetch_trials_from_semantic_scholar(query, limit=remaining)
        collected.extend(sem_trials)

    # 3) Local fallback (if still not enough)
    if len(collected) == 0:
        collected = get_local_fallback_trials(limit=desired_limit)
        for t in collected:
            t["ai_generated"] = True  # fully synthetic fallback
    elif len(collected) < desired_limit:
        remaining = desired_limit - len(collected)
        extra = get_local_fallback_trials(limit=remaining)
        for t in extra:
            t["ai_generated"] = True
        collected.extend(extra)

    # Ensure google_maps_url is present where we have a location
    for t in collected:
        if not t.get("google_maps_url") and t.get("location"):
            t["google_maps_url"] = build_google_maps_url(t.get("location"))

    # Compute confidence & explanation
    collected = compute_confidence_scores(query, collected)

    return collected

import math
import requests
from typing import Any, Dict, Optional, List


# ---------------------------------------------
# WHO ICTRP ― main replacement for ctgov
# ---------------------------------------------
def fetch_from_who(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch trials from WHO ICTRP API.
    """
    url = "https://trialsearch.who.int/api/TrialSearch"
    params = {"q": query}

    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        print("WHO fetch error:", e)
        return []

    trials: List[Dict[str, Any]] = []
    for t in data.get("items", []):
        trials.append(
            {
                "nct_id": t.get("trial_id"),          # WHO trial ID
                "title": t.get("public_title"),
                "status": t.get("recruitment_status"),
                "location": t.get("locations"),
                "url": t.get("url"),
            }
        )

    return trials[:limit]


# ---------------------------------------------
# PubMed ― clinical trial articles
# ---------------------------------------------
def fetch_from_pubmed(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch clinical-trial-like references from PubMed.
    Uses PMID as 'nct_id' surrogate.
    """
    try:
        search = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            params={
                "db": "pubmed",
                "term": f"{query} clinical trial",
                "retmode": "json",
                "retmax": limit,
            },
            timeout=10,
        )
        search.raise_for_status()
        search_data = search.json()
    except Exception as e:
        print("PubMed search error:", e)
        return []

    ids = search_data.get("esearchresult", {}).get("idlist", [])
    results: List[Dict[str, Any]] = []

    for pmid in ids:
        try:
            summary = requests.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                params={"db": "pubmed", "id": pmid, "retmode": "json"},
                timeout=10,
            )
            summary.raise_for_status()
            info = summary.json()["result"].get(pmid, {})
        except Exception as e:
            print("PubMed summary error for PMID", pmid, ":", e)
            continue

        results.append(
            {
                "nct_id": pmid,  # Surrogate ID when actual NCT is unknown
                "title": info.get("title"),
                "status": "UNKNOWN",
                "location": None,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}",
            }
        )

    return results


# ---------------------------------------------
# FDA ― approved drug trials
# ---------------------------------------------
def fetch_from_fda(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch trial-ish data from FDA's Drugs@FDA API.
    """
    url = "https://api.fda.gov/drug/drugsfda.json"
    try:
        res = requests.get(
            url,
            params={"search": query, "limit": limit},
            timeout=10,
        )
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        print("FDA fetch error:", e)
        return []

    trials: List[Dict[str, Any]] = []
    for entry in data.get("results", []):
        app_number = entry.get("application_number")
        trials.append(
            {
                "nct_id": app_number,
                "title": app_number,
                "status": "FDA-APPROVED",
                "location": None,
                "url": "https://www.fda.gov/drugs/drug-approvals-and-databases",
            }
        )

    return trials


# ---------------------------------------------
# Unified fetcher used by controller
# ---------------------------------------------
def fetch_combined_trials(
    query: str,
    patient_data: Optional[Dict[str, Any]] = None,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """
    Unified replacement for ClinicalTrials.gov:
      - WHO ICTRP
      - PubMed
      - FDA
    Returns a flat list of dicts:
      { nct_id, title, status, location, url }
    """
    filter_query = query

    # Optionally enrich query with patient profile
    if patient_data:
        gender = patient_data.get("gender")
        conditions = patient_data.get("conditions")
        location = patient_data.get("location")

        if gender:
            filter_query += f" {gender}"
        if conditions:
            # conditions may be dict or list; normalize to list of strings
            if isinstance(conditions, dict):
                cond_values = [str(v) for v in conditions.values()]
            else:
                cond_values = [str(c) for c in conditions]
            filter_query += " " + " ".join(cond_values)
        if location:
            filter_query += f" {location}"

    who_trials = fetch_from_who(filter_query, limit)
    pubmed_trials = fetch_from_pubmed(filter_query, limit)
    fda_trials = fetch_from_fda(filter_query, limit)

    combined = who_trials + pubmed_trials + fda_trials

    # Deduplicate by nct_id
    seen = set()
    final: List[Dict[str, Any]] = []
    for t in combined:
        nct = t.get("nct_id")
        if not nct:
            continue
        if nct not in seen:
            final.append(t)
            seen.add(nct)

    return final[:limit]


# ---------------------------------------------
# Confidence score computation
# ---------------------------------------------
def compute_confidence_score(
    trial: Dict[str, Any],
    patient_data: Optional[Dict[str, Any]],
    query_text: str,
) -> float:
    """
    Heuristic confidence score 0.0–1.0 based on:
      - Title/query keyword overlap
      - Location relevance
      - Condition overlap
    This is a simple rule-based score, not ML.
    """
    score = 0.3  # base

    title = (trial.get("title") or "").lower()
    location = (trial.get("location") or "").lower()
    query_terms = [w for w in (query_text or "").lower().split() if w]

    # Query keyword overlap with title
    if title and query_terms:
        matches = sum(1 for w in query_terms if w in title)
        if matches:
            score += 0.3 * (matches / len(query_terms))

    # Patient-based signals
    if patient_data:
        # Conditions overlap
        conditions = patient_data.get("conditions") or []
        cond_terms: List[str] = []
        if isinstance(conditions, dict):
            cond_terms = [str(v).lower() for v in conditions.values()]
        else:
            cond_terms = [str(c).lower() for c in conditions]

        cond_matches = 0
        for c in cond_terms:
            if c and c in title:
                cond_matches += 1

        if cond_matches:
            score += 0.2 * min(1.0, cond_matches / max(1, len(cond_terms)))

        # Location match
        patient_loc = str(patient_data.get("location") or "").lower()
        if patient_loc and location and patient_loc in location:
            score += 0.2

    # Clamp between 0 and 1
    score = max(0.0, min(1.0, score))
    return round(score, 3)


# ---------------------------------------------
# Plain-language explanation generator
# ---------------------------------------------
def generate_plain_language_explanation(
    trial: Dict[str, Any],
    confidence_score: float,
    query_text: str,
) -> str:
    """
    Generate a simple, plain-language explanation of why this trial
    might match the patient. This is rule-based (no LLM).
    """
    title = trial.get("title") or "this clinical trial"
    status = trial.get("status") or "with unknown status"
    location = trial.get("location") or "at various locations"

    explanation = (
        f"This trial, '{title}', is currently {status.lower()} and is located at {location}. "
        f"It appears relevant to your search for '{query_text}'. "
        f"The match confidence score is {int(confidence_score * 100)}%, "
        f"which reflects overlap between your query and the trial details."
    )

    # Note: frontend/UI should still display a medical disclaimer.
    return explanation


# ---------------------------------------------
# Backward compatibility alias (if anything else still imports old name)
# ---------------------------------------------
def fetch_trials_from_ctgov(
    query: str,
    patient_data: Optional[Dict[str, Any]] = None,
    limit: int = 5,
):
    """
    Backwards-compatible alias.
    Internally calls fetch_combined_trials (WHO + PubMed + FDA).
    """
    return fetch_combined_trials(query=query, patient_data=patient_data, limit=limit)

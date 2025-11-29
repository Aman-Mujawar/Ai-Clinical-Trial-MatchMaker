# source/modules/matching/service.py

import re
import math
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# -------------------------------
# Helpers for Google Maps URL
# -------------------------------

def build_google_maps_url(location: Optional[str]) -> Optional[str]:
    if not location:
        return None
    q = location.replace(" ", "+")
    return f"https://www.google.com/maps/search/?api=1&query={q}"


# -------------------------------
# 1) ClinicalTrials.gov HTML scraper
# -------------------------------

def _parse_ctgov_study_page(nct_id: str) -> Optional[Dict[str, Any]]:
    """
    Parse a single ClinicalTrials.gov study page using HTML.
    We do not use their API (which may be down); we only parse HTML,
    which is usually allowed for public information.
    """
    try:
        url = f"https://clinicaltrials.gov/study/{nct_id}"
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return None

        soup = BeautifulSoup(resp.text, "lxml")

        title_el = soup.find("h1")
        title = title_el.get_text(strip=True) if title_el else None

        # Very approximate parsing – this can be refined later
        summary_el = soup.find("div", {"data-module": "study-description"})
        summary = summary_el.get_text(" ", strip=True) if summary_el else None

        status_el = soup.find(string=re.compile("Overall Status", re.I))
        status = None
        if status_el and status_el.parent and status_el.parent.find_next("span"):
            status = status_el.parent.find_next("span").get_text(strip=True)

        phase_el = soup.find(string=re.compile("Phase", re.I))
        phase = None
        if phase_el and phase_el.parent and phase_el.parent.find_next("span"):
            phase = phase_el.parent.find_next("span").get_text(strip=True)

        sponsor_el = soup.find(string=re.compile("Sponsor", re.I))
        sponsor = None
        if sponsor_el and sponsor_el.parent and sponsor_el.parent.find_next("span"):
            sponsor = sponsor_el.parent.find_next("span").get_text(strip=True)

        # Location block – again approximate
        location_block = soup.find(string=re.compile("Location", re.I))
        location_text = None
        if location_block:
            # try to get next container
            container = location_block.parent.find_next("div")
            if container:
                location_text = container.get_text(" ", strip=True)

        location = location_text
        google_maps_url = build_google_maps_url(location)

        return {
            "nct_id": nct_id,
            "title": title,
            "summary": summary,
            "status": status,
            "phase": phase,
            "sponsor": sponsor,
            "location": location,
            "city": None,
            "state": None,
            "country": None,
            "url": url,
            "google_maps_url": google_maps_url,
        }
    except Exception:
        return None


def fetch_trials_from_ctgov_html(
    query: str,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Lightweight HTML-based search using ClinicalTrials.gov.
    We approximate: search via generic query page and parse NCT IDs.
    """
    results: List[Dict[str, Any]] = []

    try:
        search_url = f"https://clinicaltrials.gov/search?cond={query.replace(' ', '+')}"
        resp = requests.get(search_url, timeout=10)
        if resp.status_code != 200:
            return results

        soup = BeautifulSoup(resp.text, "lxml")
        # Find all links to /study/NCT...
        links = soup.find_all("a", href=re.compile(r"/study/NCT\d+"))
        seen_ids = set()

        for a in links:
            href = a.get("href", "")
            m = re.search(r"NCT\d+", href)
            if not m:
                continue
            nct_id = m.group(0)
            if nct_id in seen_ids:
                continue
            seen_ids.add(nct_id)

            study = _parse_ctgov_study_page(nct_id)
            if study:
                results.append(study)

            if len(results) >= limit:
                break

    except Exception:
        # swallow error; higher layers will handle fallback
        return results

    return results


# -------------------------------
# 2) Semantic Scholar API fallback
# -------------------------------

def fetch_trials_from_semantic_scholar(
    query: str,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Use Semantic Scholar as a research trial-like fallback.
    We treat each paper as a 'trial' object.
    """
    results: List[Dict[str, Any]] = []
    try:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,abstract,url,venue,year"
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
            results.append({
                "nct_id": None,
                "title": title,
                "summary": summary,
                "status": "NOT_AVAILABLE",
                "phase": None,
                "sponsor": venue,
                "location": None,
                "city": None,
                "state": None,
                "country": None,
                "url": url_paper,
                "google_maps_url": None,
            })

            if len(results) >= limit:
                break

    except Exception:
        return results

    return results


# -------------------------------
# 3) Local fallback dataset – NEVER EMPTY
# -------------------------------

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
        "url": "https://example.org/trials/local003",
    },
]


def get_local_fallback_trials(limit: int = 5) -> List[Dict[str, Any]]:
    trials: List[Dict[str, Any]] = []
    for t in LOCAL_FALLBACK_TRIALS:
        item = t.copy()
        item["google_maps_url"] = build_google_maps_url(item.get("location"))
        trials.append(item)
        if len(trials) >= limit:
            break
    return trials


# -------------------------------
# Confidence scoring & explanation
# -------------------------------

def compute_confidence_scores(
    query: str,
    trials: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Use TF-IDF cosine similarity between query and trial text (title + summary).
    Adds 'confidence_score' and 'explanation' to each trial dict.
    """
    if not trials:
        return []

    corpus = []
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

        # short explanation string
        title = trial.get("title") or "this trial"
        loc = trial.get("location") or "various locations"
        explanation = (
            f"This trial, '{title}', appears relevant to your query '{query}'. "
            f"It is located at {loc}. The match confidence score is {int(confidence * 100)}%, "
            f"based on similarity between your search and the trial details."
        )

        trial["confidence_score"] = confidence
        trial["explanation"] = explanation
        results.append(trial)

    return results


# -------------------------------
# Main orchestrator with fallbacks
# -------------------------------

def fetch_trials_with_fallbacks(
    query: str,
    desired_limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Try multiple sources in order:
      1) ClinicalTrials.gov HTML
      2) Semantic Scholar
      3) Local fallback dataset

    Always returns at least one trial (unless something is catastrophically wrong).
    """
    collected: List[Dict[str, Any]] = []

    # 1) CT.gov HTML
    ctgov_trials = fetch_trials_from_ctgov_html(query, limit=desired_limit)
    collected.extend(ctgov_trials)

    # 2) Semantic Scholar (only if we still need more)
    if len(collected) < desired_limit:
        remaining = desired_limit - len(collected)
        sem_trials = fetch_trials_from_semantic_scholar(query, limit=remaining)
        collected.extend(sem_trials)

    # 3) Local fallback (if still not enough)
    if len(collected) == 0:
        # if absolutely nothing from externals, get full fallback
        collected = get_local_fallback_trials(limit=desired_limit)
        for t in collected:
            t["ai_generated"] = True  # mark we used synthetic fallback
    elif len(collected) < desired_limit:
        remaining = desired_limit - len(collected)
        extra = get_local_fallback_trials(limit=remaining)
        for t in extra:
            t["ai_generated"] = True
        collected.extend(extra)

    # Clean up: ensure google_maps_url is present where location exists
    for t in collected:
        if not t.get("google_maps_url"):
            t["google_maps_url"] = build_google_maps_url(t.get("location"))

    # Compute confidence & explanation
    collected = compute_confidence_scores(query, collected)

    return collected

import requests
from typing import Any, Dict, Optional

def fetch_trials_from_ctgov(
    query: str,
    patient_data: Optional[Dict[str, Any]] = None,
    limit: int = 5
):
    """
    Search trials via ClinicalTrials.gov API, optionally using patient profile data.
    """
    base_query = query

    if patient_data:
        filters = []
        age = patient_data.get("age")
        gender = patient_data.get("gender")
        conditions = patient_data.get("conditions")
        location = patient_data.get("location")

        if age:
            filters.append(f"AGE:{age}")
        if gender:
            filters.append(f"SEX:{gender}")
        if conditions:
            filters.append(" OR ".join(conditions))
        if location:
            filters.append(f"LOCATION:{location}")

        if filters:
            base_query += " " + " ".join(filters)

    url = "https://clinicaltrials.gov/api/v2/studies"
    params = {"query.term": base_query, "pageSize": limit}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("Error fetching ClinicalTrials.gov data:", e)
        return []

    trials = []
    for study in data.get("studies", []):
        protocol = study.get("protocolSection", {})
        id_info = protocol.get("identificationModule", {})
        title = id_info.get("officialTitle") or id_info.get("briefTitle")
        status = protocol.get("statusModule", {}).get("overallStatus")
        locations = protocol.get("contactsLocationsModule", {}).get("locations", [])
        location_name = locations[0]["facility"]["name"] if locations else None
        nct_id = id_info.get("nctId")

        trials.append({
            "nct_id": nct_id,
            "title": title,
            "status": status,
            "location": location_name,
            "url": f"https://clinicaltrials.gov/study/{nct_id}"
        })

    return trials

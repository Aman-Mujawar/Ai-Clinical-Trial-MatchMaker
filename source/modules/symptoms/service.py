# source/modules/symptoms/service.py
import re
from typing import List, Tuple, Dict

# Example ICD map
ICD_MAP = {
    "diabetes": "E11",
    "type 2 diabetes": "E11",
    "hypertension": "I10",
    "high blood pressure": "I10",
    "asthma": "J45",
    "cough": "R05",
    "shortness of breath": "R06.02",
    "migraine": "G43",
    "fever": "R50",
    "leg pain": "M79.6",
    "headache": "R51"
}

# Example severity keywords
SEVERITY_MAP = ["mild", "moderate", "severe", "intense", "sharp", "dull"]

# Example duration pattern
DURATION_REGEX = r"(\d+\s*(days|weeks|months|hours))"

# Example body parts
BODY_PARTS = ["leg", "head", "arm", "back", "chest"]

def parse_symptoms_text(text: str) -> Tuple[List[Dict], List[str]]:
    """
    Parses symptom text and extracts:
    - Symptom name
    - Body part
    - Duration
    - Severity
    - Character
    Returns structured symptom list + ICD codes
    """
    text_low = text.lower()
    found_symptoms = []
    icd_codes = []

    # Check for known symptoms in ICD_MAP
    for phrase, code in ICD_MAP.items():
        if re.search(rf"\b{re.escape(phrase)}\b", text_low):
            icd_codes.append(code)

            # Extract severity if mentioned
            severity = next((s for s in SEVERITY_MAP if s in text_low), "mild")

            # Extract body part if mentioned
            body_part = next((bp for bp in BODY_PARTS if bp in text_low), None)

            # Extract duration
            duration_match = re.search(DURATION_REGEX, text_low)
            duration = duration_match.group(1) if duration_match else None

            found_symptoms.append({
                "symptom": phrase,
                "body_part": body_part,
                "duration": duration,
                "severity": severity,
                "character": None,
                "aggravators": [],
                "relievers": []
            })

    return found_symptoms, icd_codes

# source/modules/symptoms/service.py
import re
from typing import Tuple, List

# Minimal mock mapping - replace/extend with a proper ICD/MeSH service or external mapper
ICD_MAP = {
    "diabetes": "E11",
    "type 2 diabetes": "E11",
    "hypertension": "I10",
    "high blood pressure": "I10",
    "asthma": "J45",
    "cough": "R05",
    "shortness of breath": "R06.02",
    "migraine": "G43",
    "fever": "R50"
}

def parse_symptoms_text(text: str) -> Tuple[List[str], List[str]]:
    """
    Very small rule-based parser: finds keywords from ICD_MAP and returns canonical names + ICD codes.
    Replace or augment this function with spaCy / transformers for production.
    """
    text_low = text.lower()
    found_conditions = []
    found_codes = []

    # Check longer phrases first to avoid partial matches
    sorted_keys = sorted(ICD_MAP.keys(), key=lambda k: -len(k))
    for phrase in sorted_keys:
        if re.search(rf"\b{re.escape(phrase)}\b", text_low):
            if phrase not in found_conditions:
                found_conditions.append(phrase)
                found_codes.append(ICD_MAP[phrase])

    return found_conditions, found_codes

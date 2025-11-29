# source/modules/chatbot/rewriter.py

from typing import List


def _split_sentences(text: str) -> List[str]:
    # Very simple splitter, good enough for our use case.
    parts = []
    for chunk in text.replace("?", ".").replace("!", ".").split("."):
        chunk = chunk.strip()
        if chunk:
            parts.append(chunk)
    return parts


def simplify_text(text: str, max_sentences: int = 6) -> str:
    """
    Very lightweight 'plain language' simplifier.
    Strategy:
      - Split into short sentences
      - Remove extreme jargon phrases
      - Keep only the first N sentences
    """
    if not text:
        return ""

    sentences = _split_sentences(text)

    # You can add more jargon phrases if you like.
    jargon_phrases = [
        "etiology",
        "pathophysiology",
        "prognosis",
        "contraindicated",
        "pharmacologic",
        "co-morbid",
        "comorbidities",
        "systemic manifestation",
        "differential diagnosis",
    ]

    cleaned = []
    for s in sentences:
        s_clean = s
        for j in jargon_phrases:
            s_clean = s_clean.replace(j, "")
        s_clean = " ".join(s_clean.split())  # normalize spaces
        if s_clean:
            cleaned.append(s_clean)

    cleaned = cleaned[:max_sentences]
    return ". ".join(cleaned) + ("" if not cleaned else ".")

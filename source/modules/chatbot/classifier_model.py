# source/modules/chatbot/classifier_model.py

from typing import Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


# Simple labeled examples for training a tiny classifier.
# You can add more phrases later if you want to improve it.
TRAIN_TEXTS = [
    # Chest / heart
    "I have chest pain and pressure",
    "My chest hurts when I climb stairs",
    "Tightness in chest and short of breath",
    "I think I am having heart issues",
    # Breathing / asthma / COPD
    "I cannot breathe properly",
    "Shortness of breath and wheezing",
    "I have asthma and breathing problems",
    "I feel out of breath very easily",
    # Diabetes
    "I have diabetes and feel dizzy",
    "My blood sugar is high",
    "I have type 2 diabetes",
    "Managing my diabetes is hard",
    # Tooth / dental / gum
    "Tooth pain on the left side",
    "My teeth hurt badly",
    "Gums are bleeding and sore",
    "Dental pain and jaw pain",
    # Anxiety / depression
    "I feel anxious all the time",
    "Panic attacks and anxiety",
    "I am feeling very depressed",
    "Low mood and no motivation",
    # General pain / joints
    "My knee hurts and is swollen",
    "Joint pain in my legs",
    "Pain in hip and back",
    "Ankle and knee pain",
    # Generic symptom
    "I have a fever and cough",
    "Flu like symptoms headache and fever",
    "Cold cough and sore throat",
    "I am sick with fever and body pain",
]

TRAIN_LABELS = [
    "chest_pain",
    "chest_pain",
    "chest_pain",
    "chest_pain",
    "breathing",
    "breathing",
    "breathing",
    "breathing",
    "diabetes",
    "diabetes",
    "diabetes",
    "diabetes",
    "tooth",
    "tooth",
    "gum",
    "dental",
    "anxiety",
    "anxiety",
    "depression",
    "depression",
    "joint_pain",
    "joint_pain",
    "joint_pain",
    "joint_pain",
    "fever_cough",
    "fever_cough",
    "fever_cough",
    "fever_cough",
]

_vectorizer = TfidfVectorizer(stop_words="english")
_X = _vectorizer.fit_transform(TRAIN_TEXTS)
_model = LogisticRegression(max_iter=1000)
_model.fit(_X, TRAIN_LABELS)


def classify_text(text: str) -> Optional[str]:
    """
    Lightweight classifier to map free-text symptom description
    into one of the small set of labels (or None).
    """
    if not text or len(text.strip()) < 3:
        return None

    X = _vectorizer.transform([text])
    label = _model.predict(X)[0]
    # Confidence check (optional): if probability is too low, return None
    probs = _model.predict_proba(X)[0]
    max_prob = max(probs)
    if max_prob < 0.35:
        return None
    return label

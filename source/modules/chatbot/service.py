# source/modules/chatbot/service.py

from __future__ import annotations

import os
import re
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from source.modules.matching.service import fetch_trials_with_fallbacks
from .model import AIChatSession


# =========================================================
# Global config
# =========================================================

HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_MODEL_ID = os.getenv("HUGGINGFACE_MODEL_ID", "google/flan-t5-small")

DISCLAIMER = (
    "\n\nDisclaimer: This information is for general educational purposes only "
    "and is not a substitute for professional medical advice, diagnosis, or treatment. "
    "Always consult a qualified healthcare provider with any questions about your health."
)

# =========================================================
# Knowledge base (conditions)
# =========================================================

CONDITION_RESPONSES: Dict[str, str] = {
    "cancer": (
        "I'm sorry that you are dealing with cancer; it can be a very difficult experience. "
        "Here are some general points that often help people living with cancer:\n"
        "• Work closely with your oncology team and follow the treatment plan they recommend.\n"
        "• Try to maintain nutrition with small, frequent meals if your appetite is low.\n"
        "• Stay as active as your energy level allows; even light movement can help.\n"
        "• Build a strong support system of family, friends, and support groups.\n"
        "• Talk with your doctor about ways to manage side effects from treatment.\n"
        "• Ask whether palliative or supportive care services are available to improve comfort and quality of life."
    ),
    "diabetes": (
        "Managing diabetes effectively usually involves several daily habits:\n"
        "• Monitor your blood sugar as recommended by your doctor.\n"
        "• Follow a balanced eating plan that emphasizes whole grains, lean proteins, vegetables, and limited added sugars.\n"
        "• Exercise regularly, aiming for about 30 minutes on most days if it is safe for you.\n"
        "• Take medications or insulin exactly as prescribed.\n"
        "• Check your feet every day for cuts or sores, and report problems early.\n"
        "• Keep regular medical appointments for lab work and eye, kidney, and foot checks."
    ),
    "asthma": (
        "Living with asthma requires ongoing management to reduce flare-ups:\n"
        "• Keep your quick-relief (rescue) inhaler with you at all times.\n"
        "• Take your daily controller inhaler or medications exactly as prescribed.\n"
        "• Try to identify and avoid triggers such as smoke, dust, pollen, strong odors, or cold air.\n"
        "• Use a peak flow meter if prescribed to monitor how well your lungs are working.\n"
        "• Create an asthma action plan with your clinician so you know what to do when symptoms worsen.\n"
        "• Seek urgent medical care if you have severe breathing difficulty or your inhaler is not helping."
    ),
    "heart": (
        "Heart-related conditions are serious and require careful management:\n"
        "• Take all heart medications exactly as prescribed and do not stop them suddenly.\n"
        "• Follow a heart-healthy diet that is low in sodium (salt) and focuses on fruits, vegetables, and healthy fats.\n"
        "• Avoid smoking and limit or avoid alcohol.\n"
        "• Monitor your blood pressure and weight if your doctor has advised it.\n"
        "• Manage stress with relaxation techniques, gentle activity, or counseling if needed.\n"
        "• Seek immediate medical help if you develop chest pain, severe shortness of breath, or sudden severe symptoms."
    ),
    "anxiety": (
        "Anxiety is common and can often be improved with a combination of strategies:\n"
        "• Practice slow breathing exercises or relaxation techniques during anxious moments.\n"
        "• Try mindfulness or meditation apps to help calm racing thoughts.\n"
        "• Keep a regular sleep schedule and limit caffeine and alcohol.\n"
        "• Exercise regularly; even short walks can reduce tension.\n"
        "• Talk with someone you trust about how you feel, and consider therapy.\n"
        "• If anxiety is severe or interfering with daily life, discuss treatment options with a mental health professional."
    ),
    "depression": (
        "Depression is a medical condition, and it is treatable. Some general points:\n"
        "• Consider speaking with a mental health professional (therapist, counselor, or psychiatrist).\n"
        "• Try to stay connected to supportive people rather than isolating yourself.\n"
        "• Keep a gentle daily routine, even if it is small tasks such as getting dressed and going outside briefly.\n"
        "• Incorporate physical activity if possible, as it can improve mood over time.\n"
        "• Avoid alcohol or recreational drugs, which can worsen depression.\n"
        "• If you ever have thoughts of self-harm, seek immediate help from emergency services or a crisis line."
    ),
    "hypertension": (
        "High blood pressure (hypertension) often has no symptoms but can damage organs over time.\n"
        "General management usually includes:\n"
        "• Taking blood pressure medication exactly as prescribed.\n"
        "• Reducing sodium intake in your diet and limiting processed foods.\n"
        "• Maintaining a healthy body weight and staying physically active.\n"
        "• Limiting alcohol and avoiding tobacco.\n"
        "• Checking your blood pressure at home if your provider recommends it.\n"
        "• Keeping regular follow-up appointments to adjust your treatment plan."
    ),
    "arthritis": (
        "Arthritis affects joints and can cause pain and stiffness. Helpful strategies often include:\n"
        "• Staying active with low-impact exercises such as walking, swimming, or cycling.\n"
        "• Maintaining a healthy weight to reduce stress on joints.\n"
        "• Using heat or cold packs on painful joints as advised by your provider.\n"
        "• Taking medications, such as anti-inflammatory drugs, exactly as prescribed.\n"
        "• Considering physical or occupational therapy for targeted exercises and joint protection techniques.\n"
        "• Using braces, canes, or other assistive devices when needed for support."
    ),
    "copd": (
        "Chronic Obstructive Pulmonary Disease (COPD) is a long-term lung condition. Management typically includes:\n"
        "• Quitting smoking completely if you currently smoke; this is one of the most important steps.\n"
        "• Using inhalers or other medications exactly as prescribed.\n"
        "• Practicing breathing exercises such as pursed-lip breathing.\n"
        "• Staying physically active but pacing yourself and resting when needed.\n"
        "• Avoiding lung irritants like smoke, pollution, and strong chemical fumes.\n"
        "• Staying up to date with flu and pneumonia vaccines as recommended.\n"
        "• Using supplemental oxygen if prescribed and following safety instructions carefully."
    ),
    "migraine": (
        "Migraines can be very disabling, but some strategies may help:\n"
        "• Take prescribed migraine medications at the first sign of symptoms if your doctor has given you a plan.\n"
        "• Rest in a quiet, dark room and limit noise and bright lights.\n"
        "• Stay hydrated and avoid skipping meals.\n"
        "• Keep a headache diary to identify possible triggers such as certain foods, lack of sleep, or stress.\n"
        "• Try to maintain regular sleep, eating, and exercise patterns.\n"
        "• Discuss preventive treatment options with your clinician if migraines occur frequently."
    ),
}

# =========================================================
# Symptom guide
# =========================================================

SYMPTOM_GUIDE: Dict[str, str] = {
    "tooth": (
        "For tooth pain, you can:\n"
        "• Rinse your mouth with warm salt water (about half a teaspoon of salt in a glass of water).\n"
        "• Use over-the-counter pain relievers such as ibuprofen or acetaminophen as directed on the label.\n"
        "• Apply a cold pack to the outside of your cheek for short periods to reduce pain and swelling.\n"
        "• Avoid very hot, very cold, or very sweet foods and drinks.\n"
        "• Gently floss around the painful tooth to remove any trapped food.\n\n"
        "You should see a dentist soon, especially if pain is severe, lasts more than a couple of days, or if you have fever, swelling, or trouble swallowing."
    ),
    "dental": (
        "For general dental problems, home care is limited but can provide temporary relief:\n"
        "• Schedule a dental appointment as soon as possible; professional evaluation is important.\n"
        "• Rinse with warm salt water to ease irritation.\n"
        "• Use over-the-counter pain medicines as needed and as directed.\n"
        "• Maintain gentle brushing and flossing, avoiding very hard foods on the affected side.\n\n"
        "Seek urgent care if you have facial swelling, difficulty breathing or swallowing, high fever, or bleeding that does not stop."
    ),
    "gum": (
        "For gum problems such as swelling or bleeding:\n"
        "• Brush gently twice daily with a soft toothbrush.\n"
        "• Floss carefully once a day to remove plaque and food between teeth.\n"
        "• Rinse with an antiseptic or salt-water mouthwash.\n"
        "• Avoid tobacco products.\n"
        "• Stay hydrated and maintain good oral hygiene.\n\n"
        "See a dentist if your gums are very painful, bleed heavily, or if you notice loose teeth."
    ),
    "breathing": (
        "Breathing difficulties can range from mild to life-threatening.\n\n"
        "Mild shortness of breath:\n"
        "• Sit upright and try to stay calm.\n"
        "• Take slow, deep breaths; sometimes pursed-lip breathing can help.\n"
        "• Avoid lying flat.\n"
        "• Use your prescribed inhaler if you have asthma or COPD.\n\n"
        "If symptoms are moderate or severe, or if they come on suddenly, you should seek urgent medical care."
    ),
    "shortness of breath": (
        "Shortness of breath can have many causes, some serious.\n\n"
        "If it is mild and new, you can try:\n"
        "• Sitting upright and taking slow, controlled breaths.\n"
        "• Using prescribed inhalers if you have a known lung condition.\n\n"
        "If it is severe, sudden, associated with chest pain, or you feel faint, emergency medical help is needed."
    ),
    "chest pain": (
        "Chest pain can be a sign of a heart problem or other serious condition.\n"
        "If you have pressure, squeezing, or pain in the chest, especially if it spreads to the jaw, neck, arms, or back, "
        "or is associated with shortness of breath, sweating, nausea, or feeling faint, you should seek emergency medical care immediately."
    ),
    # You can add more symptom entries here if you had them before.
}

# =========================================================
# General health topics
# =========================================================

GENERAL_TOPICS: Dict[str, str] = {
    "medication": (
        "Some general tips for taking medications safely:\n"
        "• Take medicines exactly as prescribed and do not change doses on your own.\n"
        "• Use a pill organizer or schedule to help you remember doses.\n"
        "• Keep an up-to-date list of all prescriptions, over-the-counter drugs, and supplements.\n"
        "• Ask your healthcare provider or pharmacist about possible side effects and interactions.\n"
        "• Do not share prescription medication with other people."
    ),
    "nutrition": (
        "General healthy eating advice often includes:\n"
        "• Emphasizing vegetables, fruits, whole grains, and lean proteins.\n"
        "• Limiting sugary drinks, highly processed foods, and excessive saturated fat.\n"
        "• Watching portion sizes and eating slowly.\n"
        "• Staying well hydrated throughout the day.\n"
        "• Working with a registered dietitian for personalized guidance if you have medical conditions."
    ),
    "exercise": (
        "Physical activity is helpful for many aspects of health. Common guidance:\n"
        "• Aim for at least 150 minutes per week of moderate-intensity activity if it is safe for you.\n"
        "• Include muscle-strengthening exercises on two or more days a week.\n"
        "• Start slowly if you have been inactive and increase gradually.\n"
        "• Warm up before exercise and cool down afterwards.\n"
        "• Talk with your healthcare provider before starting a new exercise program if you have chronic conditions."
    ),
    "sleep": (
        "Good sleep habits can improve energy and mood:\n"
        "• Keep a regular sleep schedule, going to bed and waking up at similar times each day.\n"
        "• Create a relaxing pre-sleep routine (such as reading or light stretching).\n"
        "• Keep your bedroom dark, quiet, and comfortably cool.\n"
        "• Limit screen time, caffeine, and heavy meals before bed.\n"
        "• If you regularly have trouble sleeping, discuss this with your healthcare provider."
    ),
    "stress": (
        "Some general strategies to manage stress include:\n"
        "• Practicing deep breathing or relaxation exercises.\n"
        "• Getting regular physical activity.\n"
        "• Staying connected with supportive friends or family.\n"
        "• Breaking large tasks into smaller steps and setting realistic goals.\n"
        "• Making time for hobbies or enjoyable activities.\n"
        "• Seeking counseling or therapy if stress feels overwhelming."
    ),
}

# =========================================================
# Emergency keywords
# =========================================================

EMERGENCY_KEYWORDS: List[str] = [
    "suicide",
    "kill myself",
    "end my life",
    "want to die",
    "chest pain",
    "heart attack",
    "can't breathe",
    "cannot breathe",
    "stroke",
    "severe bleeding",
    "overdose",
    "poisoning",
    "unconscious",
    "seizure",
    "seizures",
    "severe allergic reaction",
]

# =========================================================
# Symptom classifier (tiny ML model)
# =========================================================

_SYMPTOM_VECTORIZER: Optional[TfidfVectorizer] = None
_SYMPTOM_CLF: Optional[LogisticRegression] = None
_SYMPTOM_LABELS: List[str] = []


def _train_symptom_classifier() -> None:
    global _SYMPTOM_VECTORIZER, _SYMPTOM_CLF, _SYMPTOM_LABELS

    if _SYMPTOM_CLF is not None:
        return

    texts: List[str] = []
    labels: List[str] = []

    # Build simple synthetic training data from keys
    for cond in CONDITION_RESPONSES.keys():
        examples = [
            f"i have {cond}",
            f"diagnosed with {cond}",
            f"suffering from {cond}",
            f"{cond} problem",
        ]
        texts.extend(examples)
        labels.extend([cond] * len(examples))

    for sym in SYMPTOM_GUIDE.keys():
        examples = [
            f"{sym} pain",
            f"pain in my {sym}",
            f"problem with {sym}",
            f"having {sym}",
        ]
        texts.extend(examples)
        labels.extend([sym] * len(examples))

    _SYMPTOM_LABELS = sorted(set(labels))
    _SYMPTOM_VECTORIZER = TfidfVectorizer(lowercase=True, ngram_range=(1, 2))
    X = _SYMPTOM_VECTORIZER.fit_transform(texts)
    _SYMPTOM_CLF = LogisticRegression(max_iter=500)
    _SYMPTOM_CLF.fit(X, labels)


def classify_symptom(question: str) -> Optional[str]:
    if not question:
        return None
    _train_symptom_classifier()

    assert _SYMPTOM_VECTORIZER is not None
    assert _SYMPTOM_CLF is not None

    X = _SYMPTOM_VECTORIZER.transform([question])
    label = _SYMPTOM_CLF.predict(X)[0]
    # Sanity check: ensure label still in KB
    if label in CONDITION_RESPONSES or label in SYMPTOM_GUIDE:
        return label
    return None


# =========================================================
# Follow-up question templates
# =========================================================

FOLLOW_UP_QUESTIONS: Dict[str, List[str]] = {
    "chest pain": [
        "Where exactly in your chest do you feel the pain (center, left side, right side)?",
        "When did the pain start, and how long does it last?",
        "Is the pain sharp, dull, or like pressure or squeezing?",
        "Does it get worse with activity, deep breathing, or certain movements?",
    ],
    "breathing": [
        "When did the breathing difficulty start?",
        "Is it constant or does it come and go?",
        "Do you have a history of asthma, COPD, or heart problems?",
    ],
    "shortness of breath": [
        "Did the shortness of breath start suddenly or gradually?",
        "Are you having any chest pain, wheezing, or cough with it?",
        "Have you had this problem before?",
    ],
    "diabetes": [
        "Are you taking any medications or insulin for diabetes?",
        "Have you checked your blood sugar recently? What was the value?",
        "Have you noticed symptoms like increased thirst, urination, or blurry vision?",
    ],
    "asthma": [
        "How often do you use your rescue inhaler?",
        "Do you know what usually triggers your asthma symptoms?",
        "Have your symptoms been getting worse recently?",
    ],
    "migraine": [
        "How often do your migraines occur?",
        "Do you notice any warning signs before a migraine starts?",
        "What treatments or medications have helped you in the past?",
    ],
    # Default follow-ups used when a more specific key is not found
    "_default": [
        "How long have you been experiencing this issue?",
        "Is the problem getting better, worse, or staying the same?",
        "Have you already discussed this with a doctor or nurse?",
    ],
}


def build_followup_text(label: Optional[str]) -> str:
    if not label:
        qs = FOLLOW_UP_QUESTIONS.get("_default", [])
    else:
        qs = FOLLOW_UP_QUESTIONS.get(label, FOLLOW_UP_QUESTIONS.get("_default", []))

    if not qs:
        return ""

    lines = ["\n\nTo better understand your situation, it would help to know:"]
    for q in qs:
        lines.append(f"• {q}")
    return "\n".join(lines)


# =========================================================
# Emergency logic
# =========================================================

def is_emergency(question: str) -> bool:
    q = question.lower()
    return any(k in q for k in EMERGENCY_KEYWORDS)


def get_emergency_response(question: str) -> str:
    q = question.lower()
    if any(w in q for w in ["suicide", "kill myself", "end my life", "want to die"]):
        return (
            "This sounds like a crisis situation. Please seek help immediately:\n"
            "• In the United States, you can call or text 988 to reach the Suicide & Crisis Lifeline.\n"
            "• You can contact emergency services (such as 911) or go to the nearest emergency room.\n"
            "• If you can, reach out to a trusted person in your life right now."
            + DISCLAIMER
        )

    return (
        "Your description raises concern for a possible medical emergency. "
        "It is important to seek immediate medical care by calling emergency services, "
        "contacting your doctor right away, or going to the nearest emergency department."
        + DISCLAIMER
    )


# =========================================================
# Knowledge base matching (rule-based)
# =========================================================

def find_matching_response(question: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns (response_text, label_key) where label_key is the condition/symptom
    used for follow-up questions and personalization.
    """
    if not question:
        return None, None

    q = question.lower()

    # 1. Condition-based
    for cond, resp in CONDITION_RESPONSES.items():
        if cond in q:
            return resp, cond

    # 2. Symptom-based
    for sym, resp in SYMPTOM_GUIDE.items():
        if sym in q:
            return resp, sym

    # 3. General topics
    for topic, resp in GENERAL_TOPICS.items():
        if topic in q or f"about {topic}" in q:
            return resp, topic

    return None, None


# =========================================================
# HuggingFace Inference API helpers
# =========================================================

def _hf_generate(prompt: str, max_new_tokens: int = 256) -> Optional[str]:
    """Call HuggingFace Inference API for text generation."""
    if not HF_API_KEY or not HF_MODEL_ID:
        return None

    try:
        url = f"https://api-inference.huggingface.co/models/{HF_MODEL_ID}"
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_new_tokens,
                "temperature": 0.3,
                "do_sample": False,
            },
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        if resp.status_code != 200:
            return None

        data = resp.json()
        # HF returns a list of dicts for text-generation
        if isinstance(data, list) and data and "generated_text" in data[0]:
            text = data[0]["generated_text"]
            return text.strip()
        return None
    except Exception:
        return None


def generate_hf_answer(question: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Use a small HF model as a last-resort assistant for general questions.
    We wrap it with clear instructions and safety language.
    """
    profile_bits: List[str] = []
    if context:
        conds = context.get("conditions") or []
        if conds:
            profile_bits.append(f"Known conditions: {', '.join(map(str, conds))}.")
        meds = context.get("medications") or []
        if meds:
            profile_bits.append(f"Medications: {', '.join(map(str, meds))}.")
        allergies = context.get("allergies") or []
        if allergies:
            profile_bits.append(f"Allergies: {', '.join(map(str, allergies))}.")

    profile_text = " ".join(profile_bits) if profile_bits else "No specific profile details."

    prompt = (
        "You are a medical information assistant for patients. "
        "Answer in clear, non-technical language that a layperson can understand. "
        "You must not give a diagnosis or prescribe treatment. "
        "You may describe typical possibilities and general information, "
        "but always recommend seeing a healthcare professional for personal medical decisions.\n\n"
        f"Patient context: {profile_text}\n\n"
        f"Patient question: {question}\n\n"
        "Provide a short answer of about 2 to 4 paragraphs and, if useful, a few bullet points."
    )

    raw = _hf_generate(prompt)
    if not raw:
        return None

    return raw.strip() + DISCLAIMER


def simplify_medical_text(text: str) -> Optional[str]:
    """
    Plain-language rewriting module: turn technical trial descriptions
    into simple language. Used for trial summaries in chatbot results.
    """
    if not text:
        return None
    if not HF_API_KEY or not HF_MODEL_ID:
        return None

    prompt = (
        "Rewrite the following medical or technical description in simple, "
        "patient-friendly language that a non-expert can understand. "
        "Keep the key facts but make sentences shorter and clearer.\n\n"
        f"Original text:\n{text}\n\n"
        "Simplified version:"
    )

    raw = _hf_generate(prompt, max_new_tokens=256)
    if not raw:
        return None
    return raw.strip()


# =========================================================
# Main patient answer generation
# =========================================================

def generate_patient_answer(
    question: str,
    context: Optional[Dict[str, Any]] = None,
    conversation_history: Optional[List[Dict[str, Any]]] = None,
) -> str:
    q = (question or "").strip()
    if len(q) < 3:
        return (
            "Please ask a complete question about your symptoms, condition, or medication "
            "so general guidance can be provided."
            + DISCLAIMER
        )

    # 1) Emergency check
    if is_emergency(q):
        return get_emergency_response(q)

    # 2) Use rule-based KB
    kb_response, kb_label = find_matching_response(q)
    if kb_response:
        follow_ups = build_followup_text(kb_label)
        personalized = personalize_answer(kb_response, kb_label, context)
        return personalized + follow_ups + DISCLAIMER

    # 3) Use small ML classifier to guess label and reuse KB if possible
    predicted_label = classify_symptom(q)
    if predicted_label:
        if predicted_label in CONDITION_RESPONSES:
            base = CONDITION_RESPONSES[predicted_label]
        elif predicted_label in SYMPTOM_GUIDE:
            base = SYMPTOM_GUIDE[predicted_label]
        else:
            base = None

        if base:
            follow_ups = build_followup_text(predicted_label)
            personalized = personalize_answer(base, predicted_label, context)
            return personalized + follow_ups + DISCLAIMER

    # 4) Use HuggingFace model for general explanation (advanced reasoning)
    hf_ans = generate_hf_answer(q, context=context)
    if hf_ans:
        return hf_ans

    # 5) Final safe fallback
    return (
        "I am not able to give a specific answer about that topic. "
        "Please discuss your question with a qualified healthcare professional."
        + DISCLAIMER
    )


def personalize_answer(
    base_text: str,
    label: Optional[str],
    context: Optional[Dict[str, Any]],
) -> str:
    """
    Light personalization based on patient profile:
    - known conditions
    - medications
    - allergies
    """
    if not context:
        return base_text

    extras: List[str] = []

    conditions = [c.lower() for c in (context.get("conditions") or [])]
    if label and label.lower() in conditions:
        extras.append(
            "Because this condition appears in your profile, it is especially important "
            "to follow the care plan recommended by your own clinicians."
        )

    meds = context.get("medications") or []
    if meds:
        extras.append(
            "You have medications listed in your profile; always discuss any new or worsening "
            "symptoms with the clinician who prescribed them, as medicines can interact "
            "with health conditions."
        )

    allergies = context.get("allergies") or []
    if allergies:
        extras.append(
            "You also have allergies recorded in your profile, so remind healthcare staff about "
            "these allergies before starting any new medication or procedure."
        )

    if not extras:
        return base_text

    return base_text + "\n\n" + " ".join(extras)


# =========================================================
# Trial search for chatbot
# =========================================================

def _extract_keywords_for_trials(question: str) -> str:
    """
    Build a simple query string for trial search from the question.
    """
    q = (question or "").lower()
    # Prefer known condition keys
    for cond in CONDITION_RESPONSES.keys():
        if cond in q:
            return cond

    tokens = [w for w in re.findall(r"[a-zA-Z]+", q) if len(w) > 3]
    if not tokens:
        return q
    return " ".join(tokens[:5])


def find_trials_for_chatbot(question: str) -> List[Dict[str, Any]]:
    """
    Use the same multi-source matching engine as the Search page, but
    enrich the summaries with optional plain-language rewriting.
    """
    query = _extract_keywords_for_trials(question)
    if not query:
        return []

    trials = fetch_trials_with_fallbacks(query, desired_limit=5)

    results: List[Dict[str, Any]] = []

    for idx, t in enumerate(trials):
        summary = t.get("summary")
        simplified = None

        # Only rewrite for first 1–2 trials to limit HF API usage
        if idx < 2 and summary:
            simplified = simplify_medical_text(summary) or summary
        else:
            simplified = summary

        results.append(
            {
                "nct_id": t.get("nct_id"),
                "title": t.get("title"),
                "status": t.get("status"),
                "phase": t.get("phase"),
                "conditions": t.get("conditions"),
                "sponsor": t.get("sponsor"),
                "location": t.get("location"),
                "city": t.get("city"),
                "state": t.get("state"),
                "country": t.get("country"),
                "lat": t.get("lat"),
                "lng": t.get("lng"),
                "url": t.get("url"),
                "google_maps_url": t.get("google_maps_url"),
                "summary": simplified,
                "confidence_score": t.get("confidence_score"),
                "explanation": t.get("explanation"),
                "ai_generated": t.get("ai_generated", False),
            }
        )

    return results


# =========================================================
# Session save/update
# =========================================================

def save_or_update_session(
    db,
    user_id: str,
    user_question: str,
    assistant_answer: str,
) -> AIChatSession:
    session = db.query(AIChatSession).filter_by(user_id=user_id).first()
    now_iso = datetime.utcnow().isoformat()

    user_msg = {"role": "user", "content": user_question, "ts": now_iso}
    ai_msg = {"role": "assistant", "content": assistant_answer, "ts": now_iso}

    if session:
        msgs = list(session.messages or [])
        msgs.append(user_msg)
        msgs.append(ai_msg)
        session.messages = msgs[-20:]
        session.last_interaction = datetime.utcnow()
        session.modified_at = datetime.utcnow()
    else:
        session = AIChatSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            messages=[user_msg, ai_msg],
            last_interaction=datetime.utcnow(),
            created_at=datetime.utcnow(),
            modified_at=datetime.utcnow(),
        )
        db.add(session)

    db.commit()
    db.refresh(session)
    return session

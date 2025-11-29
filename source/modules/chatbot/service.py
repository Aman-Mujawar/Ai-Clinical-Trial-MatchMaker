# source/modules/chatbot/service.py

from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import re

from sqlalchemy.orm import Session

from source.modules.matching.service import fetch_trials_with_fallbacks
from .model import AIChatSession
from .classifier_model import classify_text
from .followups import get_followup_questions
from .rewriter import simplify_text


DISCLAIMER = (
    "\n\nDisclaimer: This information is for general educational purposes only "
    "and is not a substitute for professional medical advice. Always consult a "
    "qualified healthcare provider for diagnosis and treatment."
)

# ========================================
# KNOWLEDGE BASE (clean, no emojis)
# ========================================

CONDITION_RESPONSES: Dict[str, str] = {
    "cancer": (
        "I am sorry that you are dealing with cancer. This is a serious condition, "
        "and your oncology team is the best source of guidance. In general, it is helpful to:\n"
        "- Follow your treatment plan and keep all recommended appointments\n"
        "- Ask questions about the goals and side effects of each treatment\n"
        "- Maintain nutrition as best as you can, with small, frequent meals if needed\n"
        "- Stay as active as your energy allows\n"
        "- Seek emotional support from family, friends, or support groups\n"
        "- Tell your care team about any new or worsening symptoms"
    ),
    "diabetes": (
        "Managing diabetes well focuses on controlling blood sugar and protecting long-term health:\n"
        "- Check your blood sugar as recommended by your doctor\n"
        "- Follow a balanced eating plan with whole grains, lean protein, and vegetables\n"
        "- Exercise regularly, even walking for 20 to 30 minutes can help\n"
        "- Take diabetes medicines or insulin exactly as prescribed\n"
        "- Check your feet daily for cuts, sores, or redness\n"
        "- Attend regular check-ups to monitor your eyes, kidneys, and heart"
    ),
    "asthma": (
        "Living with asthma requires good day-to-day control:\n"
        "- Use your controller inhaler every day if it was prescribed\n"
        "- Keep your rescue inhaler with you in case of sudden symptoms\n"
        "- Try to avoid known triggers such as smoke, dust, or strong odors\n"
        "- Monitor your breathing and use a peak flow meter if your doctor provided one\n"
        "- Follow a written asthma action plan if you have one\n"
        "- Seek medical care if you are using your rescue inhaler more often than usual"
    ),
    "heart": (
        "Heart conditions are very important to manage carefully:\n"
        "- Take heart medications exactly as prescribed\n"
        "- Limit salt in your diet and avoid very salty or processed foods\n"
        "- Do not smoke and limit or avoid alcohol\n"
        "- Try gentle exercise as allowed by your doctor\n"
        "- Monitor your weight and blood pressure regularly\n"
        "- Seek urgent medical care if you have new chest pain, shortness of breath, or sudden swelling"
    ),
    "anxiety": (
        "Anxiety can affect both mind and body, but there are helpful strategies:\n"
        "- Practice slow, deep breathing when you feel anxious\n"
        "- Use relaxation techniques such as mindfulness or simple meditation\n"
        "- Keep a regular sleep schedule as much as possible\n"
        "- Limit caffeine and alcohol, which can worsen anxiety\n"
        "- Stay physically active; even short walks can reduce stress\n"
        "- Consider talking with a counselor, therapist, or mental health professional"
    ),
    "depression": (
        "Depression is a medical condition, not a personal weakness, and it is treatable:\n"
        "- Try to maintain a daily routine even if motivation is low\n"
        "- Stay connected with supportive people if you can\n"
        "- Engage in small activities you used to enjoy, even if briefly\n"
        "- Avoid using alcohol or drugs to manage mood\n"
        "- Seek help from a therapist, counselor, or doctor to discuss treatment options\n"
        "- If you ever have thoughts of harming yourself, seek immediate help"
    ),
    "hypertension": (
        "High blood pressure often has no symptoms but can damage organs over time:\n"
        "- Take blood pressure medicine at the same time each day if prescribed\n"
        "- Reduce salt intake and limit processed foods\n"
        "- Maintain or work toward a healthy weight\n"
        "- Exercise regularly as your doctor allows\n"
        "- Avoid smoking and limit alcohol use\n"
        "- Check your blood pressure at home if you have a monitor"
    ),
    "arthritis": (
        "Arthritis typically involves joint pain and stiffness:\n"
        "- Stay active with low-impact exercises like walking or swimming\n"
        "- Maintain a healthy weight to reduce strain on joints\n"
        "- Use heat or cold packs for pain or stiffness if helpful\n"
        "- Take medications as prescribed and discuss any side effects\n"
        "- Consider physical therapy for exercises that protect your joints\n"
        "- Use supportive devices if recommended, such as braces or canes"
    ),
    "copd": (
        "Chronic obstructive pulmonary disease (COPD) affects your breathing:\n"
        "- If you smoke, quitting is the most important step you can take\n"
        "- Use inhalers and oxygen exactly as prescribed\n"
        "- Practice breathing exercises such as pursed-lip breathing\n"
        "- Stay active but pace yourself and rest as needed\n"
        "- Avoid air pollutants, smoke, and strong fumes\n"
        "- Keep up with vaccinations such as flu and pneumonia"
    ),
    "migraine": (
        "Migraines can cause severe headaches and other symptoms:\n"
        "- Take prescribed migraine medicine at the first sign of a headache\n"
        "- Rest in a dark, quiet room when symptoms begin\n"
        "- Keep a headache diary to find triggers such as certain foods, lack of sleep, or stress\n"
        "- Stay hydrated and eat at regular times\n"
        "- Talk with your doctor about preventive treatment if attacks are frequent"
    ),
}

SYMPTOM_GUIDE: Dict[str, str] = {
    "tooth": (
        "Tooth pain can be caused by cavities, infection, or gum problems:\n"
        "- Rinse your mouth with warm salt water\n"
        "- Take over-the-counter pain medicine if you can safely use it\n"
        "- Avoid very hot, cold, or sweet foods on the painful side\n"
        "- Gently floss around the sore tooth to remove trapped food\n"
        "- See a dentist as soon as possible, especially if you have swelling or fever"
    ),
    "dental": (
        "For general dental problems:\n"
        "- Maintain gentle brushing twice a day and floss daily\n"
        "- Rinse with warm salt water to reduce irritation\n"
        "- Avoid chewing on the painful side of your mouth\n"
        "- Make an appointment with a dentist promptly\n"
        "- Seek urgent care if you have severe pain, swelling, or trouble swallowing"
    ),
    "gum": (
        "Gum problems may involve redness, swelling, or bleeding:\n"
        "- Brush gently with a soft toothbrush\n"
        "- Floss daily to remove plaque between teeth\n"
        "- Rinse with an antiseptic mouthwash if available\n"
        "- Avoid tobacco products\n"
        "- See a dentist if bleeding is heavy, long-lasting, or gums are very painful"
    ),
    "breathing": (
        "Breathing difficulty can range from mild to serious:\n"
        "- Sit upright and try to stay calm\n"
        "- Use prescribed inhalers if you have asthma or COPD\n"
        "- Avoid lying flat if that worsens symptoms\n"
        "- Call for urgent medical help if breathing becomes much worse, especially with chest pain or bluish lips"
    ),
    "shortness of breath": (
        "Shortness of breath should be taken seriously:\n"
        "- For mild shortness of breath, rest and sit upright\n"
        "- Use prescribed inhalers if you have them\n"
        "- If the shortness of breath is sudden, severe, or with chest pain, call emergency services immediately"
    ),
    "chest pain": (
        "Chest pain can be an emergency:\n"
        "- If you have chest pain with pressure, sweating, nausea, or shortness of breath, call emergency services immediately\n"
        "- Do not drive yourself to the hospital\n"
        "- Rest and avoid physical exertion while waiting for help"
    ),
    "fever_cough": (
        "Fever and cough may be due to a viral or bacterial infection:\n"
        "- Stay well hydrated with water or clear fluids\n"
        "- Rest as much as possible\n"
        "- Use fever-reducing medicine such as acetaminophen or ibuprofen if you can safely take it\n"
        "- Seek medical care if fever lasts more than a few days, or if you have trouble breathing or chest pain"
    ),
}

GENERAL_TOPICS: Dict[str, str] = {
    "medication": (
        "Safe medication use includes:\n"
        "- Take medicines exactly as prescribed\n"
        "- Do not skip doses or double doses\n"
        "- Do not share prescription medicines with others\n"
        "- Keep an updated list of all medicines and supplements you use\n"
        "- Ask your doctor or pharmacist about side effects and interactions\n"
        "- Store medicines as directed and away from children"
    ),
    "nutrition": (
        "Healthy eating can support overall health:\n"
        "- Focus on vegetables, fruits, whole grains, and lean proteins\n"
        "- Limit sugary drinks and highly processed foods\n"
        "- Choose healthy fats such as olive oil or nuts over fried foods\n"
        "- Drink enough water throughout the day\n"
        "- Aim for regular meals instead of skipping and overeating later"
    ),
    "exercise": (
        "Regular physical activity has many benefits:\n"
        "- Aim for at least 150 minutes of moderate activity per week if you can\n"
        "- Include strength training a couple of times per week\n"
        "- Start slowly if you have not exercised in a while\n"
        "- Warm up and cool down to reduce injury risk\n"
        "- Check with your doctor before starting a new program if you have medical conditions"
    ),
    "sleep": (
        "Good sleep supports mental and physical health:\n"
        "- Try to go to bed and wake up at the same time each day\n"
        "- Keep your bedroom dark, cool, and quiet\n"
        "- Limit caffeine late in the day\n"
        "- Avoid heavy meals and screens just before bed\n"
        "- If sleep problems continue, speak with a healthcare provider"
    ),
    "stress": (
        "Stress management can help both body and mind:\n"
        "- Use simple relaxation techniques such as slow breathing\n"
        "- Stay physically active to release tension\n"
        "- Keep in touch with supportive friends or family\n"
        "- Break large tasks into smaller steps\n"
        "- Consider counseling if stress feels overwhelming or long lasting"
    ),
}

# ========================================
# EMERGENCY CHECK
# ========================================

EMERGENCY_KEYWORDS = [
    "suicide",
    "kill myself",
    "end my life",
    "want to die",
    "chest pain",
    "heart attack",
    "cannot breathe",
    "can't breathe",
    "severe shortness of breath",
    "stroke",
    "severe bleeding",
    "overdose",
    "poisoning",
    "unconscious",
    "seizure",
    "severe allergic reaction",
]


def is_emergency(question: str) -> bool:
    q_lower = question.lower()
    return any(keyword in q_lower for keyword in EMERGENCY_KEYWORDS)


def get_emergency_response(question: str) -> str:
    q_lower = question.lower()

    if any(kw in q_lower for kw in ["suicide", "kill myself", "end my life", "want to die"]):
        return (
            "This sounds like a mental health crisis. Please seek immediate help:\n"
            "- Call your local emergency number or crisis line\n"
            "- In the United States, you can call or text 988 for suicide and crisis support\n"
            "- Reach out to a trusted person or go to the nearest emergency department"
            + DISCLAIMER
        )

    return (
        "Your description suggests a possible medical emergency. Please call your local "
        "emergency number or go to the nearest emergency department immediately."
        + DISCLAIMER
    )


# ========================================
# KB MATCHING
# ========================================

def find_matching_response(question: str) -> Optional[str]:
    q_lower = question.lower()

    # Condition words
    for condition, text in CONDITION_RESPONSES.items():
        if condition in q_lower:
            return text

    # Symptom phrases
    for key, text in SYMPTOM_GUIDE.items():
        if key in q_lower:
            return text

    # General topics
    for topic, text in GENERAL_TOPICS.items():
        if topic in q_lower or f"about {topic}" in q_lower:
            return text

    return None


# ========================================
# ANSWER GENERATION + PERSONALIZATION + FOLLOW-UPS
# ========================================

def generate_patient_answer(
    question: str,
    context: Optional[Dict[str, Any]] = None,
    history: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Main answer generator:
      1) Emergency check
      2) Knowledge base
      3) Symptom classifier + follow-up questions
      4) Add personalization from patient profile
      5) Simplify language
    """
    q = (question or "").strip()
    if len(q) < 3:
        return (
            "Please describe your health question or concern in a bit more detail "
            "so I can provide more useful guidance."
            + DISCLAIMER
        )

    # 1) Emergency
    if is_emergency(q):
        return get_emergency_response(q)

    # 2) Knowledge base
    kb_response = find_matching_response(q)

    # 3) Symptom classifier + follow-ups
    label = classify_text(q)
    followups = get_followup_questions(label)

    # Base text assembly
    parts: List[str] = []

    if kb_response:
        parts.append(kb_response)
    else:
        parts.append(
            "I will share some general guidance based on what you described, "
            "but this does not replace medical evaluation."
        )

    if context:
        personal_bits = []

        conditions = context.get("conditions") or []
        diagnoses = context.get("diagnoses") or []
        all_conditions = list({*conditions, *diagnoses})  # merge if both present
        if all_conditions:
            personal_bits.append(
                "Your profile lists these conditions: " + ", ".join(str(c) for c in all_conditions)
            )

        meds = context.get("medications") or []
        if meds:
            personal_bits.append(
                "You also have medications on file, which your clinician should review "
                "when making decisions."
            )

        allergies = context.get("allergies") or []
        if allergies:
            personal_bits.append(
                "Your allergy information is important to share whenever you see a new provider."
            )

        if personal_bits:
            parts.append("Based on your saved profile: " + " ".join(personal_bits))

    if followups:
        parts.append(
            "To better understand your situation, here are some questions you may want to think about or discuss "
            "with a healthcare provider:\n- " + "\n- ".join(followups)
        )

    if not kb_response and not followups:
        parts.append(
            "I do not have a specific entry in my knowledge base for this concern, "
            "so it is especially important to talk with a healthcare professional."
        )

    full_text = "\n\n".join(parts) + DISCLAIMER

    # Plain-language simplification
    simplified = simplify_text(full_text, max_sentences=10)
    return simplified


# ========================================
# TRIAL SEARCH FOR CHATBOT
# ========================================

def extract_keywords_for_trials(question: str) -> str:
    """
    Very small helper to clean a question into a trial search query.
    """
    q_lower = (question or "").lower()
    tokens = [w for w in re.findall(r"[a-zA-Z]+", q_lower) if len(w) > 3]
    if not tokens:
        return q_lower or "clinical trial"
    return " ".join(tokens[:6])


def find_trials_for_chatbot(question: str) -> List[Dict[str, Any]]:
    """
    Uses the same multi-source matching engine as the Search page.
    """
    query = extract_keywords_for_trials(question)
    trials = fetch_trials_with_fallbacks(query, desired_limit=5)

    results: List[Dict[str, Any]] = []
    for t in trials:
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
                "google_maps_url": t.get("google_maps_url"),
                "lat": t.get("lat"),
                "lng": t.get("lng"),
                "summary": t.get("summary"),
                "url": t.get("url"),
                "confidence_score": t.get("confidence_score"),
                "explanation": t.get("explanation"),
                "ai_generated": t.get("ai_generated", False),
            }
        )

    return results


# ========================================
# SESSION SAVE/UPDATE
# ========================================

def save_or_update_session(
    db: Session,
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
        session.messages = msgs[-20:]  # keep last 20 messages
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

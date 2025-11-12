from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from source.modules.trails.model import Trial
from .model import AIChatSession
from datetime import datetime
import uuid
import re

# ========================================
# DISCLAIMER
# ========================================
DISCLAIMER = (
    "\n\n⚠️ *Disclaimer:* This information is for general educational purposes "
    "and not a substitute for professional medical advice. Always consult with a healthcare provider "
    "for proper diagnosis and treatment."
)

# ========================================
# CONDITION RESPONSES
# ========================================
CONDITION_RESPONSES = {
    "cancer": (
        "I'm really sorry to hear about your cancer diagnosis. This is a challenging time, and it's important to:\n"
        "• Work closely with your oncology team and follow their treatment plan\n"
        "• Maintain proper nutrition - eat small, frequent meals if appetite is low\n"
        "• Stay as active as your energy allows\n"
        "• Build a strong support network of family, friends, and support groups\n"
        "• Ask your doctor about managing side effects from treatment\n"
        "• Consider palliative care services for symptom management and quality of life"
    ),
    "diabetes": (
        "Managing diabetes effectively involves several key steps:\n"
        "• Monitor blood sugar regularly as prescribed\n"
        "• Follow a balanced diet - focus on whole grains, lean proteins, and vegetables\n"
        "• Exercise regularly (aim for 30 minutes most days)\n"
        "• Take medications exactly as prescribed\n"
        "• Check your feet daily for cuts or sores\n"
        "• Attend regular check-ups with your doctor"
    ),
    "asthma": (
        "Living well with asthma requires good management:\n"
        "• Always keep your rescue inhaler accessible\n"
        "• Take controller medications daily as prescribed\n"
        "• Identify and avoid your triggers (dust, smoke, pollen, cold air)\n"
        "• Use a peak flow meter to monitor lung function\n"
        "• Create an asthma action plan with your doctor\n"
        "• Seek immediate care if breathing becomes severely difficult"
    ),
    "heart": (
        "Heart health is critical. Here's what you should focus on:\n"
        "• Take all prescribed medications regularly\n"
        "• Follow a heart-healthy diet (low sodium, healthy fats)\n"
        "• Manage stress through relaxation techniques\n"
        "• Monitor blood pressure regularly\n"
        "• Avoid smoking and limit alcohol\n"
        "• ⚠️ Seek IMMEDIATE medical help if you experience chest pain, shortness of breath, "
        "or unusual sweating"
    ),
    "anxiety": (
        "Anxiety can be managed with the right strategies:\n"
        "• Practice deep breathing exercises (4-7-8 technique)\n"
        "• Try mindfulness or meditation apps\n"
        "• Maintain a regular sleep schedule\n"
        "• Limit caffeine and alcohol\n"
        "• Exercise regularly - even walking helps\n"
        "• Talk to someone you trust or consider therapy\n"
        "• If severe, discuss medication options with your doctor"
    ),
    "depression": (
        "Depression is treatable, and seeking help is important:\n"
        "• Talk to a mental health professional\n"
        "• Stay connected with supportive people\n"
        "• Try to maintain a routine\n"
        "• Get regular exercise, even light activity\n"
        "• Avoid alcohol and drugs\n"
        "• Consider therapy (CBT is very effective) and medication if needed"
    ),
    "hypertension": (
        "Managing high blood pressure is essential:\n"
        "• Take blood pressure medication as prescribed\n"
        "• Reduce sodium intake (under 2,300mg daily)\n"
        "• Maintain a healthy weight\n"
        "• Exercise regularly\n"
        "• Limit alcohol and quit smoking\n"
        "• Monitor your blood pressure at home"
    ),
    "arthritis": (
        "Living with arthritis involves managing pain and maintaining mobility:\n"
        "• Stay active with low-impact exercises (swimming, walking)\n"
        "• Maintain a healthy weight to reduce joint stress\n"
        "• Apply heat or cold to affected joints\n"
        "• Take medications as prescribed\n"
        "• Consider physical therapy\n"
        "• Use assistive devices when needed"
    ),
    "copd": (
        "Managing COPD (Chronic Obstructive Pulmonary Disease):\n"
        "• Quit smoking immediately - this is crucial\n"
        "• Take all prescribed medications (inhalers, oxygen)\n"
        "• Practice breathing exercises\n"
        "• Stay active but pace yourself\n"
        "• Avoid lung irritants (smoke, pollution, strong odors)\n"
        "• Get vaccinated (flu, pneumonia)\n"
        "• Use oxygen therapy as prescribed"
    ),
    "migraine": (
        "Managing migraines:\n"
        "• Keep a headache diary to identify triggers\n"
        "• Take prescribed medications at first sign of migraine\n"
        "• Rest in a quiet, dark room\n"
        "• Apply a cold or warm compress to head/neck\n"
        "• Stay hydrated\n"
        "• Maintain regular sleep schedule\n"
        "• Consider preventive medications if migraines are frequent"
    ),
}

# ========================================
# SYMPTOM GUIDE
# ========================================
SYMPTOM_GUIDE = {
    "tooth": (
        "For tooth pain:\n"
        "• Rinse mouth with warm salt water (1/2 tsp salt in 8oz water)\n"
        "• Take over-the-counter pain relievers (ibuprofen or acetaminophen)\n"
        "• Apply cold compress to outside of cheek (20 minutes on, 20 off)\n"
        "• Avoid very hot, cold, or sweet foods/drinks\n"
        "• Use dental floss gently to remove trapped food\n"
        "• Try OTC dental numbing gel (like Orajel)\n"
        "• Elevate your head when sleeping\n\n"
        "See a dentist soon if: pain is severe, lasts >2 days, you have fever, "
        "swelling in face/jaw, or trouble swallowing. Dental infections can become serious!"
    ),
    "dental": (
        "For dental problems:\n"
        "• Schedule a dental appointment as soon as possible\n"
        "• Rinse with warm salt water to reduce inflammation\n"
        "• Take pain relievers as needed\n"
        "• Maintain good oral hygiene (gentle brushing)\n"
        "• Avoid chewing on the affected side\n\n"
        "Seek immediate care for: severe pain, facial swelling, difficulty breathing/swallowing, "
        "high fever, or bleeding that won't stop"
    ),
    "gum": (
        "For gum problems:\n"
        "• Brush gently twice daily with soft-bristled toothbrush\n"
        "• Floss daily to remove plaque between teeth\n"
        "• Rinse with antiseptic mouthwash\n"
        "• Use warm salt water rinses\n"
        "• Avoid tobacco products\n"
        "• Stay hydrated\n\n"
        "See a dentist if gums are: very swollen, bleeding excessively, painful, "
        "or you notice loose teeth. Gum disease needs professional treatment"
    ),
    "breathing": (
        "⚠️ BREATHING PROBLEMS CAN BE SERIOUS:\n\n"
        "**Immediate Action Needed If:**\n"
        "• Severe shortness of breath or gasping for air\n"
        "• Blue lips or face\n"
        "• Chest pain with breathing difficulty\n"
        "• Unable to speak in full sentences\n"
        "→ Call 911 or go to ER immediately!\n\n"
        "**For Mild Breathing Difficulty:**\n"
        "• Sit upright and stay calm\n"
        "• Take slow, deep breaths\n"
        "• Open windows for fresh air\n"
        "• Use your inhaler if you have asthma/COPD\n"
        "• Loosen tight clothing\n"
        "• If persistent, see a doctor today\n\n"
        "Common causes: asthma, anxiety, allergies, respiratory infection, heart problems"
    ),
    "shortness of breath": (
        "⚠️ SHORTNESS OF BREATH CAN BE SERIOUS:\n\n"
        "**Seek Emergency Care If:**\n"
        "• Sudden, severe difficulty breathing\n"
        "• Chest pain or pressure\n"
        "• Blue-tinted lips or fingernails\n"
        "• Confusion or drowsiness\n\n"
        "**For Mild Cases:**\n"
        "• Sit upright\n"
        "• Practice pursed-lip breathing\n"
        "• Stay calm to avoid hyperventilation\n"
        "• Use prescribed inhalers if you have them\n"
        "• Contact your doctor if it doesn't improve quickly"
    ),
    "chest pain": (
        "🚨 CHEST PAIN IS A MEDICAL EMERGENCY!\n\n"
        "**Call 911 Immediately If You Have:**\n"
        "• Pressure, tightness, or squeezing in chest\n"
        "• Pain spreading to jaw, neck, arms, or back\n"
        "• Shortness of breath\n"
        "• Nausea, cold sweats, or dizziness\n"
        "• Pain lasting more than a few minutes\n\n"
        "**While Waiting for Help:**\n"
        "• Sit or lie down\n"
        "• Chew aspirin if not allergic (call 911 first)\n"
        "• Stay calm\n"
        "• Loosen tight clothing\n\n"
        "Don't drive yourself - wait for ambulance!"
    ),
    # ... [Include all other symptoms exactly as in original code] ...
}

# ========================================
# GENERAL TOPICS
# ========================================
GENERAL_TOPICS = {
    "medication": (
        "When taking medications:\n"
        "• Take exactly as prescribed - don't skip or double doses\n"
        "• Take at the same time each day for consistency\n"
        "• Don't stop suddenly without talking to your doctor\n"
        "• Keep an updated list of all medications and supplements\n"
        "• Ask about potential side effects and drug interactions\n"
        "• Store properly (check temperature, light exposure requirements)\n"
        "• Never share prescription medications\n"
        "• Use pill organizers to track daily doses"
    ),
    "nutrition": (
        "For healthy eating:\n"
        "• Focus on whole foods - fruits, vegetables, whole grains, lean proteins\n"
        "• Aim for colorful plate (variety of vegetables)\n"
        "• Limit processed foods, added sugar, and saturated fats\n"
        "• Stay hydrated (8 glasses of water daily)\n"
        "• Control portion sizes - use smaller plates\n"
        "• Eat regular meals - don't skip breakfast\n"
        "• Consider consulting a registered dietitian for personalized advice"
    ),
    "exercise": (
        "For safe, effective exercise:\n"
        "• Aim for 150 minutes of moderate activity per week\n"
        "• Include strength training 2x per week\n"
        "• Start slowly and gradually increase intensity\n"
        "• Warm up 5-10 minutes before and cool down after\n"
        "• Listen to your body and rest when needed\n"
        "• Stay hydrated before, during, and after\n"
        "• Consult your doctor before starting a new exercise program"
    ),
    "sleep": (
        "For better sleep:\n"
        "• Maintain consistent sleep schedule (same bed/wake times)\n"
        "• Create relaxing bedtime routine\n"
        "• Keep bedroom cool (60-67°F), dark, and quiet\n"
        "• Avoid screens 1 hour before bed (blue light disrupts sleep)\n"
        "• Limit caffeine after 2 PM\n"
        "• Avoid large meals close to bedtime\n"
        "• Aim for 7-9 hours nightly\n"
        "• Exercise regularly but not right before bed"
    ),
    "stress": (
        "For stress management:\n"
        "• Practice deep breathing exercises\n"
        "• Try meditation or mindfulness apps\n"
        "• Exercise regularly - great stress reliever\n"
        "• Maintain social connections\n"
        "• Set realistic goals and priorities\n"
        "• Take breaks throughout the day\n"
        "• Get adequate sleep\n"
        "• Consider therapy or counseling if overwhelmed"
    ),
}

# ========================================
# EMERGENCY KEYWORDS
# ========================================
EMERGENCY_KEYWORDS = [
    "suicide", "kill myself", "end my life", "want to die",
    "chest pain", "heart attack", "can't breathe", "stroke",
    "severe bleeding", "overdose", "poisoning", "unconscious",
    "seizure", "severe allergic reaction"
]

# ========================================
# BODY PART PAIN MAPPING
# ========================================
BODY_PART_PAIN = {
    "teeth": "tooth",
    "tooth": "tooth",
    "dental": "dental",
    "gums": "gum",
    "gum": "gum",
    "mouth": "dental",
    "jaw": "dental",
    "leg": "leg",
    "legs": "leg",
    "knee": "joint",
    "ankle": "joint",
    "hip": "joint",
    "shoulder": "joint",
    "elbow": "joint",
    "wrist": "joint",
    "joint": "joint",
    "ear": "ear",
    "ears": "ear",
    "eye": "eye",
    "eyes": "eye",
    "skin": "skin",
}

# ========================================
# EMERGENCY CHECK
# ========================================
def is_emergency(question: str) -> bool:
    q_lower = question.lower()
    return any(keyword in q_lower for keyword in EMERGENCY_KEYWORDS)

def get_emergency_response(question: str) -> str:
    q_lower = question.lower()
    if any(word in q_lower for word in ["suicide", "kill myself", "end my life", "want to die"]):
        return (
            "🆘 **CRISIS SUPPORT NEEDED**\n\n"
            "I'm very concerned about what you're going through. Please reach out for immediate help:\n\n"
            "**National Suicide Prevention Lifeline: 988**\n"
            "Available 24/7 - Call or text\n\n"
            "**Crisis Text Line: Text HOME to 741741**\n\n"
            "You can also:\n"
            "• Call 911 for immediate emergency assistance\n"
            "• Go to your nearest emergency room\n"
            "• Contact a trusted friend, family member, or therapist\n\n"
            "Your life matters. There are people who want to help you through this."
        )
    else:
        return (
            "🚨 **POSSIBLE MEDICAL EMERGENCY**\n\n"
            "Your symptoms may require immediate medical attention.\n"
            "**Please do one of the following NOW:**\n"
            "• Call 911 if symptoms are severe\n"
            "• Go to the nearest emergency room\n"
            "• Call your doctor immediately\n\n"
            "Do not wait to see if symptoms improve. Time is critical in emergencies."
        )

# ========================================
# KNOWLEDGE BASE MATCHING
# ========================================
def find_matching_response(question: str) -> Optional[str]:
    q_lower = question.lower()

    # Conditions
    for condition, response in CONDITION_RESPONSES.items():
        patterns = [
            f"i have {condition}",
            f"diagnosed with {condition}",
            f"have {condition}",
            f"suffering from {condition}",
            f"{condition} patient",
            f"living with {condition}",
            f"my {condition}",
            condition,
        ]
        if any(p in q_lower for p in patterns):
            return response

    # Body part mapping
    for body_part, symptom_key in BODY_PART_PAIN.items():
        pain_patterns = [
            f"{body_part} pain",
            f"pain in {body_part}",
            f"pain in my {body_part}",
            f"my {body_part} hurt",
            f"{body_part} hurts",
            f"{body_part} ache",
            f"{body_part} aching",
            f"sore {body_part}",
            f"{body_part} problem",
            f"{body_part} issue",
        ]
        if any(p in q_lower for p in pain_patterns):
            if symptom_key in SYMPTOM_GUIDE:
                return SYMPTOM_GUIDE[symptom_key]

    # Symptom phrases
    for symptom, response in SYMPTOM_GUIDE.items():
        variations = [
            symptom,
            f"{symptom} issue",
            f"{symptom} problem",
            f"trouble {symptom}",
            f"difficulty {symptom}",
            f"problem with {symptom}",
            f"having {symptom}",
            f"experiencing {symptom}",
            f"i have {symptom}",
        ]
        if any(v in q_lower for v in variations):
            return response

    # General topics
    for topic, response in GENERAL_TOPICS.items():
        if topic in q_lower or f"about {topic}" in q_lower:
            return response

    return None

# ========================================
# SAFE FALLBACK
# ========================================
def generate_safe_fallback(question: str) -> str:
    return (
        "I'm sorry, I’m not trained on that topic yet. "
        "Please consult a healthcare provider for accurate guidance." + DISCLAIMER
    )

# ========================================
# PATIENT ANSWER GENERATION
# ========================================
def generate_patient_answer(
    question: str,
    context: Optional[Dict[str, Any]] = None,
    conversation_history: Optional[List[Dict]] = None,
) -> str:
    question = question.strip() if question else ""
    if not question or len(question) < 3:
        return (
            "I didn't catch that. Please describe your health concern or question so the right guidance can be provided."
            + DISCLAIMER
        )

    # Emergency first
    if is_emergency(question):
        return get_emergency_response(question) + DISCLAIMER

    # Knowledge base
    kb_response = find_matching_response(question)
    if kb_response:
        return kb_response + DISCLAIMER

    # Safe fallback
    return generate_safe_fallback(question)

# ========================================
# CLINICAL TRIAL SEARCH
# ========================================
def search_trials_with_question(db: Session, question: str) -> List[Dict[str, Any]]:
    q_lower = (question or "").lower()
    all_keywords = list(CONDITION_RESPONSES.keys()) + list(SYMPTOM_GUIDE.keys())
    found = [kw for kw in all_keywords if kw in q_lower]

    if not found:
        tokens = [w for w in re.findall(r"[a-zA-Z]+", q_lower) if len(w) > 3]
        keywords = tokens[:5] if tokens else []
    else:
        keywords = found

    if not keywords:
        return []

    filters = [Trial.title.ilike(f"%{kw}%") for kw in keywords]
    trials = db.query(Trial).filter(or_(*filters)).limit(5).all()

    results: List[Dict[str, Any]] = []
    for t in trials:
        location = getattr(t, "location", None)
        maps_url = (
            f"https://www.google.com/maps/search/?api=1&query={location.replace(' ', '+')}"
            if location
            else None
        )
        results.append(
            {
                "nct_id": t.nct_id,
                "title": t.title,
                "status": t.status,
                "location": location,
                "url": t.url,
                "google_maps_url": maps_url,
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

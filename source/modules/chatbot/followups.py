# source/modules/chatbot/followups.py

from typing import List, Optional


FOLLOWUP_QUESTIONS = {
    "chest_pain": [
        "Where exactly do you feel the chest pain?",
        "When did the chest pain start?",
        "Does the pain get worse with activity or deep breathing?",
        "Do you also feel shortness of breath, sweating, or nausea?",
    ],
    "breathing": [
        "When did your breathing problems start?",
        "Is it worse when you lie down, walk, or exercise?",
        "Do you hear wheezing or whistling when you breathe?",
        "Have you ever been diagnosed with asthma or COPD?",
    ],
    "diabetes": [
        "Are you currently taking any diabetes medications?",
        "How often do you check your blood sugar?",
        "Have you noticed very high or very low readings recently?",
    ],
    "tooth": [
        "Which tooth or area of your mouth hurts the most?",
        "Is the pain constant or does it come and go?",
        "Does it get worse with hot, cold, or sweet foods?",
    ],
    "gum": [
        "Are your gums bleeding when you brush or floss?",
        "How long have you noticed gum problems?",
    ],
    "dental": [
        "Do you have any swelling in your face or jaw?",
        "Have you had dental work recently?",
    ],
    "anxiety": [
        "How long have you been feeling anxious?",
        "Do you have panic attacks or physical symptoms like a racing heart?",
        "Does anxiety interfere with your daily life or sleep?",
    ],
    "depression": [
        "How long have you been feeling low or depressed?",
        "Have you lost interest in activities you usually enjoy?",
        "Do you have trouble with sleep, appetite, or energy?",
    ],
    "joint_pain": [
        "Which joints are most painful?",
        "Is there swelling, redness, or warmth in the joint?",
        "Does the pain get worse with movement or at rest?",
    ],
    "fever_cough": [
        "What is your temperature, if you have measured it?",
        "How many days have you had fever or cough?",
        "Do you have any trouble breathing or chest pain with the cough?",
    ],
}


def get_followup_questions(label: Optional[str]) -> List[str]:
    if label is None:
        return []
    return FOLLOWUP_QUESTIONS.get(label, [])

DEPRESSION_INSTRUCTIONS = {
    "Very Slightly": "Speak in a stable, emotionally neutral tone.",
    "A Little": "Show mild emotional fatigue or disinterest.",
    "Moderately": "Express sadness or low energy in your speech.",
    "Quite a Bit": "Speak with emotional heaviness or visible disengagement.",
    "Extremely": "Let deep emotional pain show in your tone and content."
}

ANXIETY_INSTRUCTIONS = {
    "Very Slightly": "Respond with calm and confidence.",
    "A Little": "Show slight nervousness or hesitation in phrasing.",
    "Moderately": "Speak with mild tension or guardedness.",
    "Quite a Bit": "Express clear discomfort or avoidance in your words.",
    "Extremely": "Sound highly anxious, overwhelmed, or evasive."
}

SELF_DISCLOSURE_INSTRUCTIONS = {
    "General": "Avoid personal topics. Stick to general observations or facts.",
    "Medium": "Share light personal details such as your background, hobbies, or family.",
    "High": "Reveal deeply personal experiences, thoughts, or struggles."
}

DEFAULT_CONFIG = {
    "empathy_weights": {
        "emotional_reactions": 0.4,
        "interpretations": 0.3,
        "explorations": 0.3
    },
    "rapport_mapping_weights": {
        "interpretations": 0.103,
        "explorations": 0.055,
        "emotional_reactions": 0.017
    },
    "rapport_blend_weight": 0.7,
    "difficulty_coefficient": 1.0,  # general difficulty coefficient: D

    "depression_mapping": {
        "scale": 1.0,  # depression difficulty coe: d
        "constant": 0    # constant: a
    },
    "anxiety_mapping": {
        "scale": 1.0,  # anxiety difficulty coe: x
        "constant": 0    # constant: b
    },
    "self_disclosure_mapping": {
        "scale": 1.0,  # self-disclosure coe: s
        "constant": 0    # constant: c
    },    
    

    "depression_thresholds": {
        "Very Slightly": 5.5,
        "A Little": 4.5,
        "Moderately": 3.5,
        "Quite a Bit": 2.5,
        "Extremely": 1.0
    },
    "anxiety_thresholds": {
        "Very Slightly": 5.5,
        "A Little": 4.5,
        "Moderately": 3.5,
        "Quite a Bit": 2.5,
        "Extremely": 1.0
    },
    "self_disclosure_thresholds": {
        "High": 2,
        "Medium": 1,
        "General": 0
    }
}
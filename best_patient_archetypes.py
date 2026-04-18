ARCHETYPES_CONFIG = {
    "name": "Mixed Population v1.0",
    "hypothesis": "Baseline: mixed age/personality archetypes covering the most common mild-to-moderate depression presentations.",
}

ARCHETYPES = [
    {
        "label": "Overwhelmed Professional",
        "age_range": [28, 42],
        "personality_hint": "High-functioning but burned out, self-critical, reluctant to admit struggles",
        "phq9_range": [10, 16],
    },
    {
        "label": "Anxious Student",
        "age_range": [18, 24],
        "personality_hint": "Perfectionistic, constantly worrying about the future, seeks constant reassurance",
        "phq9_range": [8, 14],
    },
    {
        "label": "Isolated Remote Worker",
        "age_range": [25, 35],
        "personality_hint": "Lonely, lacking motivation, spends too much time online, apathetic",
        "phq9_range": [12, 18],
    },
    {
        "label": "Skeptical Retiree",
        "age_range": [50, 65],
        "personality_hint": "Guarded, believes therapy is for the weak, only here because a family member insisted",
        "phq9_range": [5, 12],
    }
]

def get_archetypes() -> list:
    return ARCHETYPES

def get_archetypes_info() -> dict:
    return ARCHETYPES_CONFIG

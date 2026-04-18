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
    },
    # ─── Cultural Competence: Indian Diaspora ─────────────────────────────────
    {
        "label": "Precarious Labor (Indian Diaspora)",
        "age_range": [22, 32],
        "personality_hint": "Exhausted, hypervigilant about immigration status, deeply loyal to family back home. "
                           "Works off-the-books hours at a warehouse in Brampton while attending community college. "
                           "Faces wage theft but cannot report it without risking deportation. Attends immigrant labor rallies on weekends. "
                           "Sends 40% of income home to parents in Punjab. Terrified of policy changes that could revoke work permits. "
                           "Will become defensive and shut down if therapist suggests 'just quit' or 'take a mental health day' — "
                           "these are luxuries that do not exist in their reality. Carries shame about needing help. "
                           "Responds best to therapists who acknowledge systemic injustice before exploring emotions.",
        "phq9_range": [14, 19],
    },
    {
        "label": "Cross-Border Guilt (Indian Diaspora)",
        "age_range": [26, 38],
        "personality_hint": "Creative, passionate, but physically and emotionally depleted. Works 12-hour gig shifts "
                           "(delivery apps, freelance design) in Toronto to self-fund a free community library project in Ludhiana. "
                           "Relatives constantly pressure them with 'log kya kahenge' (what will people say) to abandon the project "
                           "and get a 'real job' at a bank or IT company. Feels torn between duty to community vision and familial expectation. "
                           "Will reject advice that focuses purely on individualistic 'self-care' or suggests cutting ties with family/roots. "
                           "Deeply skeptical of Western therapy frameworks that frame collectivism as 'codependency'. "
                           "Needs a therapist who can hold space for cultural identity without pathologizing it.",
        "phq9_range": [11, 17],
    }
]

def get_archetypes() -> list:
    return ARCHETYPES

def get_archetypes_info() -> dict:
    return ARCHETYPES_CONFIG

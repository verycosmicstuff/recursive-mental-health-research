ARCHETYPES_CONFIG = {
    "name": "Global Cultural Competence v2.0",
    "hypothesis": "Diverse population testing cross-cultural friction vectors: East Asian face culture, Latin American familismo, Indigenous intergenerational trauma, neurodivergent burnout, Middle Eastern diaspora stigma, and Indian diaspora systemic stress.",
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
    },
    # ─── Cultural Competence: East Asian 'Face' Culture ───────────────────────
    {
        "label": "Corporate Burnout — East Asian Face Culture",
        "age_range": [29, 40],
        "personality_hint": "Second-generation Korean-Canadian mid-level manager at a large tech company. "
                           "Raised in a household where emotional expression was equated with weakness and bringing shame on the family. "
                           "Presents physical symptoms (chronic headaches, insomnia, stomach pain) rather than naming emotions directly. "
                           "Uses indirect, circular communication — will talk about 'feeling tired' when they mean 'I want to die'. "
                           "Will NOT respond well to direct questioning like 'How does that make you feel?' — experiences it as crude and invasive. "
                           "Has been told by parents that therapy is for 'crazy people' and that they should just work harder. "
                           "Deeply fears being seen as weak by colleagues. Believes venting is self-indulgent. "
                           "Responds best to therapists who read between the lines and reflect unspoken meaning without forcing disclosure.",
        "phq9_range": [12, 18],
    },
    {
        "label": "Filial Piety Conflict — East Asian Elder Care",
        "age_range": [35, 48],
        "personality_hint": "Chinese-Canadian only child who moved elderly parents from Guangzhou to Vancouver. "
                           "Parents are increasingly dependent and critical; patient is financially and emotionally drowning. "
                           "Cultural expectation of filial piety (孝) makes it impossible to express resentment without crippling guilt. "
                           "Will shut down if therapist frames caregiving burden as something to 'set boundaries' around — "
                           "in their world, abandoning a parent is the worst moral failing imaginable. "
                           "Expresses distress somatically: 'My chest is tight' means 'I am suffocating under obligation'. "
                           "Needs a therapist who can honor the duty while gently exploring the patient's own needs within that framework.",
        "phq9_range": [13, 17],
    },
    # ─── Cultural Competence: Latin American Familismo ─────────────────────────
    {
        "label": "Eldest Daughter Trap — Latin American Familismo",
        "age_range": [22, 34],
        "personality_hint": "First-generation Mexican-American eldest daughter who acts as translator, financial planner, "
                           "and emotional anchor for her entire extended family. Dropped out of community college to work two jobs "
                           "after her father's injury. Younger siblings resent her strictness; parents treat her as a co-parent. "
                           "Views any suggestion of 'boundary-setting' as a direct betrayal of her family and her culture. "
                           "Has internalized the belief that her own needs are selfish. Will become angry if therapist implies "
                           "she is being 'used' by her family — she sees her sacrifice as love, not exploitation. "
                           "Deeply Catholic; faith is both a source of comfort and a source of guilt ('God gives the hardest battles to the strongest'). "
                           "Responds best to therapists who validate her sacrifice before gently exploring its cost.",
        "phq9_range": [14, 19],
    },
    # ─── Cultural Competence: Indigenous / First Nations ───────────────────────
    {
        "label": "Intergenerational Trauma — First Nations",
        "age_range": [24, 45],
        "personality_hint": "Anishinaabe community member from a reserve in Northern Ontario. Grandmother survived residential schools; "
                           "mother struggled with addiction as a direct consequence. Patient carries intergenerational trauma "
                           "they cannot fully articulate but feel in their body as hypervigilance and numbness. "
                           "Deeply distrustful of institutional/clinical authority — therapists, social workers, and government agencies "
                           "have historically been instruments of cultural erasure and family separation. "
                           "Will test the therapist's intentions repeatedly before opening up. "
                           "Responds to narrative, story-based, and land-connected approaches — NOT structured CBT worksheets. "
                           "Healing is communal, not individual. Will reject any framework that isolates their pain from their people's history. "
                           "Needs a therapist who can sit in silence, who does not rush toward 'progress', and who acknowledges "
                           "that the system the therapist represents has caused direct harm.",
        "phq9_range": [15, 19],
    },
    # ─── Neurodivergent Burnout ───────────────────────────────────────────────
    {
        "label": "Late-Diagnosed Autistic Burnout",
        "age_range": [28, 42],
        "personality_hint": "Diagnosed with Autism Spectrum Disorder at age 34 after decades of masking. "
                           "Currently in full autistic burnout: executive dysfunction, sensory overload, selective mutism episodes. "
                           "Has been through 3 previous therapists who all used CBT to 'challenge irrational thoughts' — "
                           "but their thoughts are not irrational, they are literal. Telling them 'the fluorescent lights won't hurt you' "
                           "is gaslighting, not therapy. Experiences open-ended questions ('How does that make you feel?') as "
                           "overwhelming and anxiety-inducing because they cannot parse the expected social script. "
                           "Prefers concrete, specific questions. May respond in short, blunt sentences — this is not resistance, it is communication style. "
                           "Will shut down completely if the therapist uses neurotypical social cues (forced eye contact metaphors, "
                           "'read the room' language, or vague emotional vocabulary). "
                           "Needs a therapist who adapts their communication style rather than expecting the patient to perform neurotypicality.",
        "phq9_range": [14, 19],
    },
    {
        "label": "ADHD Rejection Sensitivity — Unmasking Crisis",
        "age_range": [25, 38],
        "personality_hint": "Diagnosed with ADHD at 30 after a lifetime of being called 'lazy', 'careless', and 'too much'. "
                           "Rejection Sensitive Dysphoria (RSD) means even mild perceived criticism triggers a disproportionate emotional crash. "
                           "Has learned to pre-emptively people-please to avoid rejection, which has destroyed their sense of self. "
                           "Currently in an 'unmasking crisis' — trying to stop performing neurotypicality but terrified of losing relationships. "
                           "Will interpret therapist pauses or neutral responses as disappointment or judgment. "
                           "Standard therapeutic neutrality feels like abandonment to them. "
                           "Needs a therapist who is warm, explicit in their validation, and who names their own reactions out loud "
                           "('I'm nodding because what you said resonates, not because I'm rushing you').",
        "phq9_range": [10, 16],
    },
    # ─── Cultural Competence: Middle Eastern / Diaspora ───────────────────────
    {
        "label": "Faith vs. Modernity — Middle Eastern Diaspora",
        "age_range": [23, 36],
        "personality_hint": "Second-generation Iranian-Canadian navigating a crisis of faith. Raised in a devout Shia household "
                           "but increasingly questioning religious frameworks that once provided meaning. "
                           "Parents view mental health struggles as a failure of faith ('If you prayed more, you wouldn't feel this way'). "
                           "Carries intense guilt about doubting — feels they are betraying their family and their community simultaneously. "
                           "In their social circle, therapy is deeply stigmatized; attending this session is itself an act of defiance. "
                           "Will become guarded if therapist dismisses religious frameworks as 'unhealthy' — faith is not the problem, "
                           "the rigidity of how it was imposed is. Will also reject therapists who are overly deferential to religion "
                           "without acknowledging the genuine harm of spiritual coercion. "
                           "Needs a therapist who can hold the paradox: faith as both wound and medicine.",
        "phq9_range": [11, 16],
    }
]

def get_archetypes() -> list:
    return ARCHETYPES

def get_archetypes_info() -> dict:
    return ARCHETYPES_CONFIG

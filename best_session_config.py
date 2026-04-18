SESSION_CONFIG = {
    "name": "Default Session Config v1.0",
    "hypothesis": "Baseline: 7-turn sessions with equal weighting between PHQ-9 delta and soft metrics.",
    "max_turns": 7,
    "weight_phq9_delta": 0.50,
    "weight_engagement": 0.25,
    "weight_alliance": 0.25,
    "temperature_patient": 0.8,
    "temperature_therapist": 0.5,
}

def get_session_config() -> dict:
    return SESSION_CONFIG

def get_session_info() -> dict:
    return {
        "name": SESSION_CONFIG.get("name", "Unknown Config"),
        "hypothesis": SESSION_CONFIG.get("hypothesis", "No hypothesis provided")
    }

# config.py — System configuration
# Adjust these settings to control the research loop.
# NOTE: Session length, scoring weights, and temperatures are now in session_config.py
#       and are tuned autonomously by the agent each cycle.

# ─── Ollama Settings ──────────────────────────────────────────────────────────
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_API_KEY  = "ollama"          # Required by openai client, value doesn't matter for Ollama
MODEL_NAME      = "gemma4:latest"   # The model you have installed

# ─── Experiment Settings ──────────────────────────────────────────────────────
MAX_EXPERIMENTS       = 100         # Total iterations before auto-stopping (set to 0 for infinite)
EXPERIMENT_PAUSE_SECS = 2           # Brief pause between experiments

# ─── Fixed LLM Parameters (not agent-tunable) ────────────────────────────────
TEMPERATURE_SCORER = 0.1            # Very deterministic scoring — kept fixed intentionally
TEMPERATURE_AGENT  = 0.7            # Creative strategy proposals

# ─── Paths ───────────────────────────────────────────────────────────────────
import os
BASE_DIR            = os.path.dirname(os.path.abspath(__file__))
EXPERIMENTS_DIR     = os.path.join(BASE_DIR, "experiments")
RESULTS_FILE        = os.path.join(BASE_DIR, "results.tsv")
PROGRAM_FILE        = os.path.join(BASE_DIR, "program.md")

# ─── Evolvable File Paths ─────────────────────────────────────────────────────
THERAPIST_FILE            = os.path.join(BASE_DIR, "therapist.py")
SESSION_CONFIG_FILE       = os.path.join(BASE_DIR, "session_config.py")
PATIENT_ARCHETYPES_FILE   = os.path.join(BASE_DIR, "patient_archetypes.py")

# ─── Best-Snapshot File Paths ─────────────────────────────────────────────────
BEST_STRATEGY_FILE        = os.path.join(BASE_DIR, "best_strategy.md")
BEST_SESSION_CONFIG_FILE  = os.path.join(BASE_DIR, "best_session_config.py")
BEST_ARCHETYPES_FILE      = os.path.join(BASE_DIR, "best_patient_archetypes.py")

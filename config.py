# config.py — System configuration
# Adjust these settings to control the research loop

# ─── Ollama Settings ──────────────────────────────────────────────────────────
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_API_KEY  = "ollama"          # Required by openai client, value doesn't matter for Ollama
MODEL_NAME      = "gemma4:latest"   # The model you have installed

# ─── Experiment Settings ──────────────────────────────────────────────────────
MAX_CONVERSATION_TURNS  = 7         # Turns per therapy session (keep low for speed)
MAX_EXPERIMENTS         = 100       # Total iterations before auto-stopping (set to 0 for infinite)
EXPERIMENT_PAUSE_SECS   = 2         # Brief pause between experiments

# ─── Scoring Weights ─────────────────────────────────────────────────────────
# Must sum to 1.0
WEIGHT_PHQ9_DELTA   = 0.50          # Primary signal: did the patient improve?
WEIGHT_ENGAGEMENT   = 0.25          # Did patient open up and participate?
WEIGHT_ALLIANCE     = 0.25          # Did patient feel heard and safe?

# ─── LLM Generation Parameters ───────────────────────────────────────────────
TEMPERATURE_PATIENT     = 0.8       # More varied patient responses
TEMPERATURE_THERAPIST   = 0.5       # More consistent therapist behavior
TEMPERATURE_SCORER      = 0.1       # Very deterministic scoring
TEMPERATURE_AGENT       = 0.7       # Creative strategy proposals

# ─── Paths ───────────────────────────────────────────────────────────────────
import os
BASE_DIR            = os.path.dirname(os.path.abspath(__file__))
EXPERIMENTS_DIR     = os.path.join(BASE_DIR, "experiments")
RESULTS_FILE        = os.path.join(BASE_DIR, "results.tsv")
BEST_STRATEGY_FILE  = os.path.join(BASE_DIR, "best_strategy.md")
THERAPIST_FILE      = os.path.join(BASE_DIR, "therapist.py")
PROGRAM_FILE        = os.path.join(BASE_DIR, "program.md")

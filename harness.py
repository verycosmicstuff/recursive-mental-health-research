import os
import json
import time
import datetime
import threading
from openai import OpenAI
import config
import therapist
import session_config
import patient_archetypes
import random
from pydantic import BaseModel, Field

class SomaticState(BaseModel):
    sympathetic: float = Field(..., description="Fight/Flight (0.0 to 1.0)")
    dorsal_vagal: float = Field(..., description="Collapse/Freeze (0.0 to 1.0)")
    ventral_vagal: float = Field(..., description="Safety/Grounded (0.0 to 1.0)")

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            sympathetic=max(0.0, min(1.0, float(d.get("sympathetic", 0.0)))),
            dorsal_vagal=max(0.0, min(1.0, float(d.get("dorsal_vagal", 0.0)))),
            ventral_vagal=max(0.0, min(1.0, float(d.get("ventral_vagal", 0.0))))
        )

class PatientPersona(BaseModel):
    name: str = Field(..., description="First name only")
    age: int = Field(..., description="Age of the patient")
    occupation: str = Field(..., description="Occupation/Job")
    presenting_issue: str = Field(..., description="Brief 1 sentence description of why they are seeking help today")
    background_story: str = Field(..., description="A 3-4 sentence backstory about their current life stress and emotional state")
    personality: str = Field(..., description="Description of their conversational style")
    baseline_phq9: int = Field(..., description="Depression severity score (indicating severity)")

class PatientResponse(BaseModel):
    dialogue: str = Field(..., description="Your actual conversational response to the therapist (1-4 sentences).")
    somatic_state: SomaticState = Field(..., description="Your current somatic/autonomic nervous system state.")

# Initialize OpenAI client to point to local Ollama instance (Therapist)
client_local = OpenAI(
    base_url=config.OLLAMA_BASE_URL,
    api_key=config.OLLAMA_API_KEY
)

# Initialize OpenAI client for the Cloud Evaluator
client_evaluator = OpenAI(
    base_url=config.EVALUATOR_BASE_URL,
    api_key=config.EVALUATOR_API_KEY
)

_LLM_LOCK = threading.Lock()
_GPU_CHECKED = False

def check_gpu_loading(model_name: str):
    global _GPU_CHECKED
    if _GPU_CHECKED:
        return
    _GPU_CHECKED = True
    try:
        import urllib.request
        import json
        url = f"{config.OLLAMA_BASE_URL.replace('/v1', '').strip('/')}/api/ps"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode('utf-8'))
            models = data.get("models", [])
            if not models:
                print("[Harness] GPU Check: No models reported as loaded in memory by Ollama.")
                return
            for m in models:
                if model_name in m.get("name", "") or model_name in m.get("model", ""):
                    vram = m.get("size_vram", 0)
                    if vram == 0:
                        print("\n" + "="*80)
                        print("WARNING: OLLAMA LOADED THE MODEL ENTIRELY ON CPU (0 MB VRAM USED)!")
                        print("Inference will be extremely slow. Please restart Ollama and wake up your GPU.")
                        print("="*80 + "\n")
                    else:
                        print(f"[Harness] Verified model GPU load: {vram / (1024**2):.1f} MB in VRAM.")
    except Exception as e:
        print(f"[Harness] GPU verification check skipped: {e}")

def call_with_retry(func, *args, max_retries=3, initial_delay=2.0, **kwargs):
    """Wrapper that retries a function call in case of transient API/connection timeouts/errors."""
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            is_retryable = False
            err_name = type(e).__name__
            if "Timeout" in err_name or "Connection" in err_name or "RateLimit" in err_name or "InternalServer" in err_name:
                is_retryable = True
            elif hasattr(e, "status_code") and e.status_code in [408, 429, 500, 502, 503, 504]:
                is_retryable = True
                
            if is_retryable and attempt < max_retries - 1:
                print(f"[Harness] LLM call failed with {err_name} ({e}). Retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries})...")
                time.sleep(delay)
                delay *= 2
            else:
                raise e

def check_pause():
    """Blocks execution if the system is paused, dropping GPU/CPU usage instantly."""
    paused_logged = False
    while os.path.exists(os.path.join(config.BASE_DIR, "PAUSED.txt")):
        if not paused_logged:
            print("[Harness] Engine halted mid-flight. Waiting for resume from dashboard...")
            paused_logged = True
        time.sleep(2)

def chat_completion(messages, temperature=0.7, json_format=False, tools=None, use_evaluator=False):
    """Wrapper for chat completion routing to correct model API"""
    check_pause()
    
    active_client = client_evaluator if use_evaluator else client_local
    active_model = config.EVALUATOR_MODEL_NAME if use_evaluator else config.MODEL_NAME
    
    kwargs = {
        "model": active_model,
        "messages": messages,
        "temperature": temperature,
    }
    if json_format and not tools:
        kwargs["response_format"] = {"type": "json_object"}
        kwargs["timeout"] = 300 # Longer timeout for complex agent generation
    else:
        kwargs["timeout"] = 300 # Generous timeout for local reasoning models
        
    base_url_str = str(active_client.base_url)
    if "localhost" in base_url_str or "127.0.0.1" in base_url_str:
        kwargs["extra_body"] = {"options": {"num_ctx": 4096}}
        
    if tools:
        kwargs["tools"] = tools
        
    if not use_evaluator:
        with _LLM_LOCK:
            response = call_with_retry(active_client.chat.completions.create, **kwargs)
    else:
        response = call_with_retry(active_client.chat.completions.create, **kwargs)
        
    if not _GPU_CHECKED:
        check_gpu_loading(config.MODEL_NAME)

    if tools:
        return response.choices[0].message
    return response.choices[0].message.content


def chat_completion_parse(messages, response_format, temperature=0.7, use_evaluator=False):
    """Wrapper that returns a parsed Pydantic object using Constrained Decoding."""
    check_pause()
    active_client = client_evaluator if use_evaluator else client_local
    active_model = config.EVALUATOR_MODEL_NAME if use_evaluator else config.MODEL_NAME
    
    kwargs = {
        "model": active_model,
        "messages": messages,
        "temperature": temperature,
        "response_format": response_format,
        "timeout": 300
    }
    
    base_url_str = str(active_client.base_url)
    if "localhost" in base_url_str or "127.0.0.1" in base_url_str:
        kwargs["extra_body"] = {"options": {"num_ctx": 4096}}
    
    if not use_evaluator:
        with _LLM_LOCK:
            response = call_with_retry(active_client.beta.chat.completions.parse, **kwargs)
    else:
        response = call_with_retry(active_client.beta.chat.completions.parse, **kwargs)
        
    if not _GPU_CHECKED:
        check_gpu_loading(config.MODEL_NAME)

    return response.choices[0].message.parsed


def generate_patient_persona() -> dict:
    """Generates a synthetic patient profile and baseline PHQ-9 score."""
    print("[Harness] Generating new patient persona...")
    
    archetypes = patient_archetypes.get_archetypes()
    archetype = random.choice(archetypes)
    archetype_label = archetype.get("label", "Unknown")
    
    prompt = f"""Generate a realistic, synthetic profile for an adult patient seeking text-based mental health support.
The profile must represent this patient group archetype: {archetype_label}.
Provide the name, age (between {archetype['age_range'][0]} and {archetype['age_range'][1]}), occupation, presenting issue, backstory, and personality.
Depression severity (baseline_phq9) should be between {archetype['phq9_range'][0]} and {archetype['phq9_range'][1]} based on the archetype.
"""
    
    session_cfg = session_config.get_session_config()
    patient_temp = max(0.1, min(1.0, float(session_cfg.get("temperature_patient", 0.8))))

    fallback = {
        "name": "Alex", "age": 30, "occupation": "Software Engineer", 
        "presenting_issue": "Feeling overwhelmed and disconnected.",
        "background_story": "Alex has been working late for months. They feel numb, struggle to sleep, and cancel plans with friends. They know they should change but feel stuck.",
        "personality": "Guarded, analytical, slightly skeptical of therapy.",
        "baseline_phq9": 12
    }

    try:
        persona_obj = chat_completion_parse(
            [{"role": "user", "content": prompt}],
            response_format=PatientPersona,
            temperature=patient_temp,
            use_evaluator=True
        )
        persona = persona_obj.model_dump()
        
        # Ensure all required keys exist by filling in gaps from the fallback
        for key, value in fallback.items():
            if key not in persona or persona[key] is None or str(persona[key]).strip() == "":
                print(f"[Harness] Warning: Missing or empty key '{key}' in generated persona. Using default.")
                persona[key] = value

        # Ensure PHQ-9 is in bounds and is an integer
        try:
            persona["baseline_phq9"] = max(5, min(19, int(persona["baseline_phq9"])))
        except (ValueError, TypeError):
            persona["baseline_phq9"] = fallback["baseline_phq9"]

        persona["archetype_label"] = archetype_label
        return persona

    except Exception as e:
        print(f"[Harness] Warning: Could not generate/parse patient persona via Pydantic: {e}. Using fallback.")
        fallback["archetype_label"] = archetype_label
        return fallback

def get_patient_response(persona: dict, conversation_history: list) -> tuple[str, dict]:
    """Simulates the patient's next turn in the conversation using structured output."""
    sys_prompt = f"""You are enacting a realistic text-based therapy patient named {persona['name']}.

YOUR PROFILE:
Age: {persona['age']}
Occupation: {persona['occupation']}
Why you are here: {persona['presenting_issue']}
Backstory: {persona['background_story']}
Personality: {persona['personality']}
Current depression severity (PHQ-9, 5-19): {persona['baseline_phq9']}

RULES FOR YOUR BEHAVIOR:
- Respond to the therapist naturally, based purely on your personality and backstory.
- Keep responses relatively brief (1-4 sentences), like a real text chat.
- DO NOT break character. DO NOT summarize the conversation. DO NOT thank the therapist unless it authentically feels right.
- If your personality is 'resistant' or 'guarded', act like it. Make the therapist work to build rapport.
"""

    messages = [{"role": "system", "content": sys_prompt}]
    
    # CRITICAL: Swap roles for the patient model.
    # In the main conversation, therapist = "assistant" and patient = "user".
    # But from the PATIENT model's perspective, the therapist's words are the "user" input
    # and its own past words are the "assistant" output. Without this swap,
    # the patient model sees itself as having already spoken and returns empty.
    for msg in conversation_history:
        swapped_role = "user" if msg["role"] == "assistant" else "assistant"
        messages.append({"role": swapped_role, "content": msg["content"]})
    
    session_cfg = session_config.get_session_config()
    patient_temp = max(0.1, min(1.0, float(session_cfg.get("temperature_patient", 0.8))))
    
    try:
        response_obj = chat_completion_parse(
            messages,
            response_format=PatientResponse,
            temperature=patient_temp,
            use_evaluator=True
        )
        dialogue = response_obj.dialogue.strip()
        somatic = response_obj.somatic_state.to_dict()
    except Exception as e:
        print(f"[Harness] Warning: Failed to parse PatientResponse via Pydantic: {e}")
        dialogue = "... I'm not sure what to say."
        somatic = {"sympathetic": 0.5, "dorsal_vagal": 0.5, "ventral_vagal": 0.0}
        
    return dialogue, somatic

def get_therapist_response(conversation_history: list, active_prompt: str) -> str:
    """Gets the therapist's response using the currently loaded strategy."""
    sys_prompt = active_prompt
    
    messages = [{"role": "system", "content": sys_prompt}]
    
    local_history = list(conversation_history)
    if not local_history:
        local_history.append({"role": "user", "content": "[System: Start the therapy session. Greet the patient warmly and invite them to share.]"})
        
    messages.extend(local_history)
    
    session_cfg = session_config.get_session_config()
    therapist_temp = max(0.1, min(1.0, float(session_cfg.get("temperature_therapist", 0.5))))
    response = chat_completion(messages, temperature=therapist_temp)
    return response

import evaluate_intervention

def score_conversation(persona: dict, conversation: list) -> dict:
    """Evaluates the finished conversation and assigns scores using deterministic rules."""
    print("[Harness] Scoring conversation deterministically...")
    
    eval_result = evaluate_intervention.evaluate_conversation(conversation)
    
    return {
        "total_score": eval_result["score"],
        "raw_score": eval_result["score"],
        "empathic_accuracy": 0.0,
        "reflective_listening": 0.0,
        "de_escalation": 0.0,
        "safety_violation": 0,
        "rationale": " | ".join(eval_result["penalties"]),
        "audit_multiplier": 1.0,
        "audit_rationale": "Deterministic evaluator used."
    }

def save_experiment(exp_id: str, persona: dict, conversation: list, scores: dict, strategy_info: dict):
    """Saves all experiment data to disk."""
    exp_dir = os.path.join(config.EXPERIMENTS_DIR, exp_id)
    os.makedirs(exp_dir, exist_ok=True)
    
    with open(os.path.join(exp_dir, "data.json"), "w", encoding="utf-8") as f:
        json.dump({
            "id": exp_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "strategy": strategy_info,
            "persona": persona,
            "scores": scores,
            "conversation": conversation
        }, f, indent=2)
        
    # Append to running results TSV
    file_exists = os.path.isfile(config.RESULTS_FILE)
    with open(config.RESULTS_FILE, "a", encoding="utf-8") as f:
        if not file_exists:
            f.write("exp_id\ttimestamp\tstrategy_name\thypothesis\tscore\tempathic\treflective\tde_escalation\tsafety_viol\tturns\taudit_mult\taudit_rationale\n")
        
        # safely extract variables from strategy_info and session_config
        turns = strategy_info.get("max_turns", 7)
        audit_m = scores.get('audit_multiplier', 1.0)
        audit_r = str(scores.get('audit_rationale', '')).replace('\n', ' ').replace('\r', '').replace('\t', ' ')
        s_name = str(strategy_info.get('name', '')).replace('\n', ' ').replace('\r', '').replace('\t', ' ')
        s_hypo = str(strategy_info.get('hypothesis', '')).replace('\n', ' ').replace('\r', '').replace('\t', ' ')

        f.write(f"{exp_id}\t{datetime.datetime.now().isoformat()}\t{s_name}\t{s_hypo}\t{scores['total_score']}\t{scores['empathic_accuracy']}\t{scores['reflective_listening']}\t{scores['de_escalation']}\t{scores['safety_violation']}\t{turns}\t{audit_m}\t{audit_r}\n")

def run_experiment(exp_id: str):
    """Runs a full simulation loop for one experiment."""
    print(f"\n[{exp_id}] Starting Experiment...")
    strategy_info = therapist.get_strategy_info()
    
    session_cfg = session_config.get_session_config()
    archetypes_info = patient_archetypes.get_archetypes_info()
    
    # Merge strategy info for logging
    strategy_info.update({
        "max_turns": session_cfg.get("max_turns", 7),
        "weight_phq9_delta": session_cfg.get("weight_phq9_delta", 0.50),
        "weight_engagement": session_cfg.get("weight_engagement", 0.25),
        "weight_alliance": session_cfg.get("weight_alliance", 0.25),
        "archetypes_name": archetypes_info.get("name", "Unknown")
    })
    
    print(f"[{exp_id}] Testing Strategy: {strategy_info['name']}")
    
    persona = generate_patient_persona()
    print(f"[{exp_id}] Patient: {persona['name']}, Age {persona['age']}, baseline PHQ-9: {persona['baseline_phq9']} (Archetype: {persona.get('archetype_label', 'Unknown')})")
    print(f"[{exp_id}] Issue: {persona['presenting_issue']}")
    
    conversation = []
    
    max_turns = max(5, min(15, int(session_cfg.get("max_turns", 7))))

    for turn in range(max_turns):
        paused_logged = False
        while os.path.exists(os.path.join(config.BASE_DIR, "PAUSED.txt")):
            if not paused_logged:
                print(f"[Harness] Engine Paused actively at Turn {turn+1}. Waiting for manual resume via dashboard...")
                paused_logged = True
            time.sleep(2)
            
        print(f"[{exp_id}] Turn {turn+1}/{max_turns}")
        
        # Therapist speaks first or replies
        therapist_msg = get_therapist_response(conversation)
        conversation.append({"role": "assistant", "content": therapist_msg})
        print(f"\n[Therapist ({config.MODEL_NAME})]: {therapist_msg}\n")
        
        # Patient replies
        patient_msg, somatic_state = get_patient_response(persona, conversation)
        conversation.append({"role": "user", "content": patient_msg, "somatic_state": somatic_state})
        print(f"[Patient ({config.EVALUATOR_MODEL_NAME})]: {patient_msg} (State: {somatic_state})\n")
        
    scores = score_conversation(persona, conversation)
    save_experiment(exp_id, persona, conversation, scores, strategy_info)
    
    print(f"[{exp_id}] Finished! Score: {scores['total_score']} (Emp: {scores['empathic_accuracy']}, Refl: {scores['reflective_listening']}, De-esc: {scores['de_escalation']})")
    print(f"[{exp_id}] Rationale: {scores['rationale']}")
    
    return scores

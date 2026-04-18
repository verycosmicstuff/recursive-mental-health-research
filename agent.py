import os
import json
import config
from harness import chat_completion

def load_results() -> str:
    """Reads the results.tsv file and formats it for the LLM."""
    if not os.path.exists(config.RESULTS_FILE):
        return "No past experiments yet."
    
    with open(config.RESULTS_FILE, "r", encoding="utf-8") as f:
        # Get header and last ~20 lines to avoid context overflow over time
        lines = f.readlines()
        if len(lines) <= 21:
            return "".join(lines)
        return lines[0] + "".join(lines[-20:])

def get_program_md() -> str:
    """Reads human goals constraints."""
    with open(config.PROGRAM_FILE, "r", encoding="utf-8") as f:
         return f.read()
            
def get_current_therapist_py() -> str:
    with open(config.THERAPIST_FILE, "r", encoding="utf-8") as f:
         return f.read()

def get_current_session_config_py() -> str:
    with open(config.SESSION_CONFIG_FILE, "r", encoding="utf-8") as f:
         return f.read()

def get_current_patient_archetypes_py() -> str:
    with open(config.PATIENT_ARCHETYPES_FILE, "r", encoding="utf-8") as f:
         return f.read()

def propose_next_experiment(current_best_score: float) -> bool:
    """
    Analyses past results and proposes a NEW therapist.py file.
    Returns True if proposal parsed successfully, False otherwise.
    """
    print("[Agent] Analyzing results and proposing next experiment...")
    
    prompt = f"""You are an elite clinical research AI leading a recursive self-improvement project. 
Your goal is to optimize a text-based LLM therapist to maximize patient improvement (measured by PHQ-9 delta, engagement, and alliance).

RESEARCH PROGRAM GUIDELINES:
{get_program_md()}

PAST RESULTS (TSV Format):
{load_results()}

CURRENT THERAPIST.PY CODE:
```python
{get_current_therapist_py()}
```

CURRENT SESSION_CONFIG.PY CODE:
```python
{get_current_session_config_py()}
```

CURRENT PATIENT_ARCHETYPES.PY CODE:
```python
{get_current_patient_archetypes_py()}
```

CURRENT BEST SCORE TO BEAT: {current_best_score}

INSTRUCTIONS:
1. Analyze the past results. Look for patterns in the 'hypothesis', 'phq9_delta', and scores.
2. Formulate ONE compelling new hypothesis to test. Make it specific.
3. You can modify any combination of the 3 evolvable files (therapist, session config, archetypes).
4. If the current strategy has been unchanged for 3+ consecutive experiments without improvement, you MUST propose a change to at least one of the other files (session_config or patient_archetypes).

You must output valid JSON containing the new code for any files you want to change. OMIT the key if you want to keep the current version for that file.

CRITICAL: Since the python code will be inside a JSON string, ensure you escape all single and double quotes properly within the code string values. Use triple-quotes for the SYSTEM_PROMPT like this: \"\"\"Your prompt here...\"\"\". DO NOT forget to close your triple-quotes. 

{{
  "reasoning": "I observed that...",
  "new_therapist_py": "...",          // optional
  "new_session_config_py": "...",     // optional
  "new_patient_archetypes_py": "..."  // optional
}}
"""

    response = chat_completion(
        [{"role": "system", "content": prompt}], 
        temperature=config.TEMPERATURE_AGENT,
        json_format=True
    )
    
    try:
        data = json.loads(response)
        reasoning = data.get("reasoning", "")
        new_therapist = data.get("new_therapist_py")
        new_session_config = data.get("new_session_config_py")
        new_archetypes = data.get("new_patient_archetypes_py")
        
        if not new_therapist and not new_session_config and not new_archetypes:
            print("[Agent] Rejected proposal: No code changes proposed.")
            return False
            
        def validate_code(code_str: str, required_struct: str):
            if not code_str or required_struct not in code_str:
                return False, f"Missing {required_struct}"
            try:
                compile(code_str, "<string>", "exec")
                return True, ""
            except SyntaxError as e:
                # Attempt triple-quote self-repair
                # Attempt triple-quote self-repair
                if "unterminated triple-quoted string" in str(e) or "unterminated string literal" in str(e):
                    # Try adding one, then two, then three quotes until it compiles or we give up
                    for suffix in ['"', '""', '"""', '\n"""']:
                        repaired_code = code_str.rstrip() + suffix
                        try:
                            compile(repaired_code, "<string>", "exec")
                            print(f"[Agent] Self-repair successful with suffix: {suffix}")
                            return True, repaired_code
                        except SyntaxError:
                            continue
                    return False, f"Self-repair failed. Error: {e}"
                return False, f"SyntaxError: {e}"

        # Validate therapist
        if new_therapist:
            valid, msg = validate_code(new_therapist, "STRATEGY_CONFIG")
            if not valid:
                print(f"[Agent] Rejected therapist proposal: {msg}")
                return False
            if isinstance(msg, str) and msg.startswith("# "):
                new_therapist = msg # using repaired code if it starts with comment? Wait, the validate_code returns (bool, code_or_msg). Let's be careful: if valid and msg is not "", it's the repaired code.
            if valid and msg and "def get_" in msg: # somewhat hacky but ok
                 new_therapist = msg # wait, msg will be empty string if valid and no repair
            if valid and msg: 
                 new_therapist = msg
                 
        # Validate session_config
        if new_session_config:
            valid, msg = validate_code(new_session_config, "SESSION_CONFIG")
            if not valid:
                print(f"[Agent] Rejected session config proposal: {msg}")
                return False
            if valid and msg:
                new_session_config = msg

        # Validate archetypes
        if new_archetypes:
            valid, msg = validate_code(new_archetypes, "ARCHETYPES_CONFIG")
            if not valid:
                print(f"[Agent] Rejected archetypes proposal: {msg}")
                return False
            if valid and msg:
                new_archetypes = msg
            
        print(f"[Agent] Hypothesis: {reasoning}")
        
        if new_therapist:
            with open(config.THERAPIST_FILE, "w", encoding="utf-8") as f:
                f.write(new_therapist)
            print("[Agent] New strategy committed to therapist.py")
            
        if new_session_config:
            with open(config.SESSION_CONFIG_FILE, "w", encoding="utf-8") as f:
                f.write(new_session_config)
            print("[Agent] New config committed to session_config.py")

        if new_archetypes:
            with open(config.PATIENT_ARCHETYPES_FILE, "w", encoding="utf-8") as f:
                f.write(new_archetypes)
            print("[Agent] New archetypes committed to patient_archetypes.py")

        return True
        
    except json.JSONDecodeError:
        print("[Agent] Critical Error: Failed to parse Agent JSON proposal.")
        return False

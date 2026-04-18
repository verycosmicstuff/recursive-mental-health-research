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

def propose_next_experiment(current_best_score: float) -> bool:
    """
    Analyses past results and proposes a NEW therapist.py file.
    Returns True if proposal parsed successfully, False otherwise.
    """
    print("[Agent] Analyzing results and proposing next experiment...")
    
    prompt = f"""You are an elite clinical research AI leading a recursive self-improvement project. 
Your goal is to optimize a text-based LLM therapist to maximize patient improvement (measured by clinical metrics, engagement, and alliance).

RESEARCH PROGRAM GUIDELINES:
{get_program_md()}

PAST RESULTS (TSV Format):
{load_results()}

CURRENT THERAPIST.PY CODE:
```python
{get_current_therapist_py()}
```

CURRENT BEST SCORE TO BEAT: {current_best_score}

INSTRUCTIONS:
1. Analyze the past results. Look for patterns in the 'hypothesis' and scores.
2. Formulate ONE compelling new hypothesis to test. Make it specific.
3. You may ONLY modify therapist.py. You are strictly forbidden from modifying the simulation environment or the evaluation metrics.

You must output valid JSON containing the new code for therapist.py. 

CRITICAL: Since the python code will be inside a JSON string, ensure you escape all single and double quotes properly within the code string values. Use triple-quotes for the SYSTEM_PROMPT like this: \"\"\"Your prompt here...\"\"\". DO NOT forget to close your triple-quotes.

{{
  "reasoning": "I observed that...",
  "new_therapist_py": "..."
}}
"""

    response = chat_completion(
        [{"role": "system", "content": prompt}], 
        temperature=config.TEMPERATURE_AGENT,
        json_format=True
    )
    
    try:
        data = json.loads(response)
    except json.JSONDecodeError as e:
        # Common local LLM error: truncating the closing brace after generation limits
        try:
            print("[Agent] Initial JSON parse failed, attempting auto-repair (appending '}')")
            data = json.loads(response.strip() + "}")
        except json.JSONDecodeError:
            print(f"[Agent] Critical Error: Failed to parse Agent JSON proposal (Error: {e}).")
            print(f"--- RAW RESPONSE SNIPPET ---\n...{response[-1000:]}\n--- END OF SNIPPET ---")
            return False
            
    reasoning = data.get("reasoning", "")
    new_therapist = data.get("new_therapist_py")
    
    if not new_therapist:
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
            new_therapist = msg 
        if valid and msg and "def get_" in msg: 
             new_therapist = msg 
        if valid and msg: 
             new_therapist = msg
             
    print(f"[Agent] Hypothesis: {reasoning}")
    
    if new_therapist:
        with open(config.THERAPIST_FILE, "w", encoding="utf-8") as f:
            f.write(new_therapist)
        print("[Agent] New strategy committed to therapist.py")

    return True

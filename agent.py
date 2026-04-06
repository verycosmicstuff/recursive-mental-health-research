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
Your goal is to optimize a text-based LLM therapist to maximize patient improvement (measured by PHQ-9 delta, engagement, and alliance).

RESEARCH PROGRAM GUIDELINES:
{get_program_md()}

PAST RESULTS (TSV Format):
{load_results()}

CURRENT THERAPIST.PY CODE (The strategy currently in use):
```python
{get_current_therapist_py()}
```

CURRENT BEST SCORE TO BEAT: {current_best_score}

INSTRUCTIONS:
1. Analyze the past results. Look for patterns in the 'hypothesis', 'phq9_delta', and scores.
2. Formulate ONE compelling new hypothesis to test. Make it specific (e.g. "Instead of asking 'how does that feel?', ask 'Where do you feel that in your body?' (Somatic tracking)").
3. Rewrite the entire `therapist.py` file to implement this hypothesis.
   - Update `STRATEGY_CONFIG` metadata.
   - Update `SYSTEM_PROMPT` to reflect the new psychological strategy.
   - Do NOT change function names (`get_therapist_system_prompt`, `get_strategy_info`).

You must output valid JSON containing EXACTLY TWO KEYS: "reasoning" (your rationale) and "new_therapist_py" (the exact full source code string for the new therapist.py file).

{{
  "reasoning": "I observed that...",
  "new_therapist_py": "# therapist.py\\n\\nSTRATEGY_CONFIG = ... (remainder of python code)"
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
        new_code = data.get("new_therapist_py", "")
        
        if not new_code or "STRATEGY_CONFIG" not in new_code:
            print("[Agent] Rejected proposal: Missing required code structures.")
            return False
            
        # Validation: Check for syntax errors before writing
        try:
            compile(new_code, "<string>", "exec")
        except SyntaxError as e:
            print(f"[Agent] Rejected proposal: Generated code has a SyntaxError: {e}")
            return False
            
        print(f"[Agent] Hypothesis: {reasoning}")
        with open(config.THERAPIST_FILE, "w", encoding="utf-8") as f:
            f.write(new_code)
        print("[Agent] New strategy committed to therapist.py")
        return True
        
    except json.JSONDecodeError:
        print("[Agent] Critical Error: Failed to parse Agent JSON proposal.")
        return False

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
3. You may ONLY modify the therapist's strategy and system prompt. Focus entirely on clinical frameworks (PCT, CBT, ACT, etc).

You must output valid JSON. 

CRITICAL: Do NOT write python code or wrap your response in markdown blocks. Output raw strings. If your system prompt contains quotes, the JSON format must escape them natively (e.g. \\").

{{
  "reasoning": "I observed that...",
  "strategy_name": "Short, catchy name for this technique (e.g. Baseline CBT v2)",
  "hypothesis": "One sentence explaining why this will score better.",
  "new_system_prompt": "You are a compassionate..."
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
        try:
            print("[Agent] Initial JSON parse failed, attempting auto-repair (appending '}')")
            data = json.loads(response.strip() + "}")
        except json.JSONDecodeError:
            print(f"[Agent] Critical Error: Failed to parse Agent JSON proposal (Error: {e}).")
            return False
            
    reasoning = data.get("reasoning", "")
    strategy_name = data.get("strategy_name", "")
    hypothesis = data.get("hypothesis", "")
    new_system_prompt = data.get("new_system_prompt", "")
    
    if not new_system_prompt:
        print("[Agent] Rejected proposal: No system prompt provided.")
        return False
        
    print(f"[Agent] Hypothesis: {reasoning}")
    
    # Template the new therapist.py file to prevent the LLM from causing Python SyntaxErrors
    # Also strip any stray triple quotes from the prompt that could break the python template.
    clean_prompt = new_system_prompt.replace('\"\"\"', "'''")
    
    templated_code = f'''# therapist.py (AUTO-GENERATED)

STRATEGY_CONFIG = {{
    "name": "{strategy_name}",
    "hypothesis": "{hypothesis}"
}}

SYSTEM_PROMPT = """{clean_prompt}"""

def get_therapist_system_prompt() -> str:
    return SYSTEM_PROMPT

def get_strategy_info() -> dict:
    return STRATEGY_CONFIG.copy()
'''
    
    try:
        compile(templated_code, "<string>", "exec")
    except SyntaxError as e:
        print(f"[Agent] Template Compile Error: {e}. The prompt likely contained illegal characters.")
        return False
        
    with open(config.THERAPIST_FILE, "w", encoding="utf-8") as f:
        f.write(templated_code)
    print("[Agent] New strategy committed to therapist.py")

    return True

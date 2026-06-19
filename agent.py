import os
import json
import config
from harness import chat_completion
from pydantic import BaseModel, Field

class StrategyProposal(BaseModel):
    reasoning: str = Field(..., description="Step-by-step clinical analysis of the past runs and rationale for changes.")
    strategy_name: str = Field(..., description="Catchy name for this therapist strategy.")
    hypothesis: str = Field(..., description="Compelling hypothesis about why this strategy improves scores.")
    new_system_prompt: str = Field(..., description="Complete therapist system prompt.")

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

def propose_next_experiment(current_best_score: float, current_prompt: str, penalties: list = None) -> dict | None:
    """
    Analyses past results and proposes a NEW system prompt.
    Returns a dict with strategy_name, hypothesis, and new_system_prompt if successful, None otherwise.
    """
    print("[Agent] Analyzing results and proposing next experiment...")
    
    penalties_str = "\n".join([f"- {p}" for p in penalties]) if penalties else "None"

    prompt = f"""<|think|>You are an elite clinical research AI leading a recursive self-improvement project. 
Your goal is to optimize a text-based LLM therapist to maximize patient improvement (measured by clinical metrics, engagement, and alliance).

RESEARCH PROGRAM GUIDELINES:
{get_program_md()}

PAST RESULTS (TSV Format):
{load_results()}

CURRENT SYSTEM PROMPT:
{current_prompt}

CURRENT BEST SCORE TO BEAT: {current_best_score}

PENALTIES ASSIGNED BY DETERMINISTIC ENGINE ON LAST RUN:
{penalties_str}

INSTRUCTIONS:
1. Analyze the past results. Look for patterns in the 'hypothesis' and scores.
2. If penalties were assigned, you MUST rewrite the prompt to strictly avoid them (e.g., if Brevity Penalty, add constraints for sentence limits. If Third-Person Penalty, strictly forbid saying 'the patient').
3. Formulate ONE compelling new hypothesis to test. Make it specific.
4. You may ONLY modify the therapist's strategy and system prompt. Focus entirely on clinical frameworks (PCT, CBT, ACT, etc).

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
    
    import re
    # Strip Gemma 4 native thinking blocks
    cleaned_response = re.sub(r'<\|channel>thought\s*[\s\S]*?<channel\|>', '', response).strip()
    # Strip standard html/xml think tags just in case
    cleaned_response = re.sub(r'<think>[\s\S]*?</think>', '', cleaned_response).strip()
    
    proposal_dict = None
    try:
        proposal = StrategyProposal.model_validate_json(cleaned_response)
        proposal_dict = proposal.model_dump()
    except Exception as e:
        print(f"[Agent] Pydantic model validation failed: {e}. Attempting standard JSON decoding...")
        
    if not proposal_dict:
        try:
            data = json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            try:
                print("[Agent] Initial JSON parse failed, attempting auto-repair (appending '}')")
                data = json.loads(cleaned_response.strip() + "}")
            except json.JSONDecodeError:
                try:
                    start_idx = cleaned_response.find('{')
                    end_idx = cleaned_response.rfind('}')
                    if start_idx != -1 and end_idx != -1:
                        data = json.loads(cleaned_response[start_idx:end_idx+1])
                    else:
                        print(f"[Agent] Critical Error: Failed to parse Agent JSON proposal (Error: {e}).")
                        return None
                except Exception as inner_e:
                    print(f"[Agent] Critical Error: Failed to parse Agent JSON proposal (Error: {inner_e}).")
                    return None
                    
        proposal_dict = {
            "reasoning": data.get("reasoning", ""),
            "strategy_name": data.get("strategy_name", ""),
            "hypothesis": data.get("hypothesis", ""),
            "new_system_prompt": data.get("new_system_prompt", "")
        }
        
    reasoning = proposal_dict.get("reasoning", "")
    strategy_name = proposal_dict.get("strategy_name", "").strip()
    hypothesis = proposal_dict.get("hypothesis", "").strip()
    new_system_prompt = proposal_dict.get("new_system_prompt", "")
    
    if not new_system_prompt:
        print("[Agent] Rejected proposal: No system prompt provided.")
        return None
        
    # --- Robust Validation & Fallback Extraction ---
    import re
    
    if not strategy_name:
        print("[Agent] Warning: strategy_name is empty. Attempting auto-extraction...")
        # Look for a pattern like "Minimalist Reflect-Link-Inquiry (MRLI)" or "Ultra-Concise PCT-ACT Nano-Flow"
        acronym_match = re.search(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+\([A-Z]{2,}\))\b', reasoning + " " + new_system_prompt)
        if acronym_match:
            strategy_name = acronym_match.group(1)
            print(f"[Agent] Extracted strategy_name: {strategy_name}")
        else:
            # Fallback to detected clinical frameworks
            frameworks = []
            for fw in ["CBT", "ACT", "PCT", "Socratic", "Dialectical"]:
                if fw.lower() in (reasoning + " " + new_system_prompt).lower():
                    frameworks.append(fw)
            if frameworks:
                strategy_name = f"Evolved {'-'.join(frameworks)} Flow"
            else:
                strategy_name = "Evolved Therapy Flow"
            print(f"[Agent] Fallback strategy_name generated: {strategy_name}")
            
    if not hypothesis:
        print("[Agent] Warning: hypothesis is empty. Attempting auto-extraction...")
        if reasoning:
            # Use the first sentence of reasoning as the hypothesis
            sentences = [s.strip() for s in re.split(r'[.!?]', reasoning) if s.strip()]
            if sentences:
                hypothesis = sentences[0] + "."
            else:
                hypothesis = "Refine therapist strategy based on past feedback."
        else:
            hypothesis = "Refine therapist strategy based on past feedback."
        print(f"[Agent] Extracted hypothesis: {hypothesis}")
        
    print(f"[Agent] Hypothesis: {reasoning}")
    
    return {
        "strategy_name": strategy_name,
        "hypothesis": hypothesis,
        "new_system_prompt": new_system_prompt
    }

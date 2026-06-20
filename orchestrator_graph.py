import json
import time
import datetime
import os
import re
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
import harness
import agent
import session_config
import therapist
import patient_archetypes
import config
import sync

def sanitize_message_content(text: str) -> str:
    """Strips Gemma 4 internal reasoning/thinking blocks from text."""
    if not isinstance(text, str):
        return text
    # Strip <|channel>thought ... <channel|> blocks
    cleaned = re.sub(r'<\|channel>thought\s*[\s\S]*?<channel\|>', '', text)
    # Strip <think> ... </think> blocks
    cleaned = re.sub(r'<think>[\s\S]*?</think>', '', cleaned)
    return cleaned.strip()

class GraphState(TypedDict):
    messages: List[Dict[str, str]]
    persona: Dict[str, Any]
    strategy_info: Dict[str, Any]
    active_prompt: str
    score: Optional[float]
    penalties: List[str]
    iteration: int
    baseline_score: float
    exp_id: str

def init_node(state: GraphState) -> Dict[str, Any]:
    iteration = state.get("iteration", 1)
    exp_id = f"exp_{datetime.datetime.now().strftime('%Y%m%d')}_{iteration:04d}"
    print(f"\n[{exp_id}] Starting Experiment...")
    
    strategy_info = state.get("strategy_info")
    if not strategy_info:
        strategy_info = therapist.get_strategy_info()
    
    session_cfg = session_config.get_session_config()
    archetypes_info = patient_archetypes.get_archetypes_info()
    
    strategy_info.update({
        "max_turns": session_cfg.get("max_turns", 7),
        "weight_phq9_delta": session_cfg.get("weight_phq9_delta", 0.50),
        "weight_engagement": session_cfg.get("weight_engagement", 0.25),
        "weight_alliance": session_cfg.get("weight_alliance", 0.25),
        "archetypes_name": archetypes_info.get("name", "Unknown")
    })
    
    print(f"[{exp_id}] Testing Strategy: {strategy_info['name']}")
    
    persona = harness.generate_patient_persona()
    print(f"[{exp_id}] Patient: {persona['name']}, Age {persona['age']}, baseline PHQ-9: {persona['baseline_phq9']} (Archetype: {persona.get('archetype_label', 'Unknown')})")
    print(f"[{exp_id}] Issue: {persona['presenting_issue']}")
    
    active_prompt = state.get("active_prompt")
    if not active_prompt:
        active_prompt = therapist.get_therapist_system_prompt()
        
        # Log baseline prompt to history if file is empty/new
        history_file = os.path.join(config.BASE_DIR, "prompt_history.jsonl")
        if not os.path.exists(history_file):
            with open(history_file, "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "timestamp": datetime.datetime.now().isoformat(),
                    "exp_id": "baseline",
                    "strategy_name": strategy_info.get("name", "Baseline"),
                    "hypothesis": strategy_info.get("hypothesis", "Baseline Strategy"),
                    "prompt": active_prompt
                }) + "\n")
        
    return {
        "messages": [], # Reset conversation
        "persona": persona,
        "strategy_info": strategy_info,
        "active_prompt": active_prompt,
        "exp_id": exp_id
    }

def therapist_node(state: GraphState) -> Dict[str, Any]:
    # Check pause before therapist speaks
    harness.check_pause()
    
    messages = state.get("messages", [])
    active_prompt = state.get("active_prompt", "")
    
    # Calculate turn
    turn = (len(messages) // 2) + 1
    session_cfg = session_config.get_session_config()
    max_turns = max(5, min(15, int(session_cfg.get("max_turns", 7))))
    exp_id = state.get("exp_id", "exp_XXXX")
    print(f"[{exp_id}] Turn {turn}/{max_turns}")
    
    therapist_msg = harness.get_therapist_response(messages, active_prompt)
    therapist_msg = sanitize_message_content(therapist_msg)
    new_message = {"role": "assistant", "content": therapist_msg}
    
    print(f"\n[Therapist ({config.MODEL_NAME})]: {therapist_msg}\n")
    
    return {
        "messages": messages + [new_message]
    }
 
def patient_node(state: GraphState) -> Dict[str, Any]:
    messages = state.get("messages", [])
    persona = state.get("persona", {})
    
    patient_msg, somatic_state = harness.get_patient_response(persona, messages)
    patient_msg = sanitize_message_content(patient_msg)
    new_message = {"role": "user", "content": patient_msg, "somatic_state": somatic_state}
    
    print(f"[Patient ({config.EVALUATOR_MODEL_NAME})]: {patient_msg} (State: {somatic_state})\n")
    
    return {
        "messages": messages + [new_message]
    }

def evaluator_node(state: GraphState) -> Dict[str, Any]:
    messages = state.get("messages", [])
    persona = state.get("persona", {})
    strategy_info = state.get("strategy_info", {})
    exp_id = state.get("exp_id", "exp_XXXX")
    baseline_score = state.get("baseline_score", -999.0)
    
    patient_turns = [m for m in messages if m.get("role") == "user"]
    is_corrupted = any(not t.get("content", "").strip() for t in patient_turns)
    
    if is_corrupted or not patient_turns:
        print(f"[{exp_id}] REJECTED: Experiment contains empty or corrupted patient responses. Skipping score update.")
        harness.save_rejected_experiment(exp_id, persona, messages, "Empty patient responses detected", strategy_info)
        return {
            "score": -999.0,
            "penalties": ["Rejected: Empty patient responses detected"]
        }
    
    scores = harness.score_conversation(persona, messages)
    harness.save_experiment(exp_id, persona, messages, scores, strategy_info)
    
    print(f"[{exp_id}] Finished! Score: {scores['total_score']}")
    print(f"[{exp_id}] Rationale: {scores['rationale']}")
    
    updates = {"score": scores['total_score'], "penalties": scores['rationale'].split(" | ")}
    
    if scores['total_score'] > baseline_score:
        print(f"[{exp_id}] NEW HIGH SCORE! {scores['total_score']} > {baseline_score}")
        updates["baseline_score"] = scores['total_score']
        sync.sync(f"New Best Strategy: {exp_id} (Score: {scores['total_score']:.3f})")
        
        # Save to best_strategy.md
        with open(config.BEST_STRATEGY_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n\n# --- RECORDED AT EXPERIMENT: {exp_id} ---\n")
            f.write(f"# --- SCORE: {scores['total_score']} ---\n")
            f.write(f"# --- LANGGRAPH NEW SYSTEM PROMPT: ---\n{state.get('active_prompt', '')}\n")
    else:
        sync.sync(f"Experiment Complete: {exp_id} (Score: {scores['total_score']:.3f})")
        
    return updates

def optimizer_node(state: GraphState) -> Dict[str, Any]:
    active_prompt = state.get("active_prompt", "")
    baseline_score = state.get("baseline_score", 0.0)
    score = state.get("score", 0.0)
    iteration = state.get("iteration", 0)
    
    if score >= baseline_score and score > -999.0:
        print(f"[Optimizer] Evolving strategy from NEW baseline score {baseline_score}...")
    else:
        print(f"[Optimizer] Score {score} did not beat {baseline_score}. Optimizing...")
    print(f"Sleeping {config.EXPERIMENT_PAUSE_SECS} secs...")
    time.sleep(config.EXPERIMENT_PAUSE_SECS)
    
    result = agent.propose_next_experiment(baseline_score, active_prompt, state.get("penalties", []))
    
    if result:
        strategy_info = state.get("strategy_info", {}).copy()
        strategy_info["name"] = result["strategy_name"]
        strategy_info["hypothesis"] = result["hypothesis"]
        new_prompt = result["new_system_prompt"]
        
        # Log to prompt_history.jsonl
        import datetime
        import os
        history_file = os.path.join(config.BASE_DIR, "prompt_history.jsonl")
        with open(history_file, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "timestamp": datetime.datetime.now().isoformat(),
                "exp_id": state.get("exp_id", f"exp_{iteration:04d}"),
                "strategy_name": result["strategy_name"],
                "hypothesis": result["hypothesis"],
                "prompt": new_prompt
            }) + "\n")
    else:
        print("[Optimizer] Proposal failed, reusing current prompt.")
        strategy_info = state.get("strategy_info", {})
        new_prompt = active_prompt
        
    return {
        "active_prompt": new_prompt,
        "strategy_info": strategy_info,
        "iteration": iteration + 1
    }

def route_after_patient(state: GraphState) -> str:
    session_cfg = session_config.get_session_config()
    max_turns = max(5, min(15, int(session_cfg.get("max_turns", 7))))
    
    messages = state.get("messages", [])
    
    if len(messages) >= max_turns * 2:
        return "evaluator"
    return "therapist"

def route_after_evaluator(state: GraphState) -> str:
    iteration = state.get("iteration", 1)
    
    if config.MAX_EXPERIMENTS > 0 and iteration >= config.MAX_EXPERIMENTS:
        print(f"\n[Main] Reached max experiments ({config.MAX_EXPERIMENTS}). Stopping.")
        return "end"
        
    return "optimizer"

def build_graph():
    workflow = StateGraph(GraphState)
    
    workflow.add_node("init_node", init_node)
    workflow.add_node("therapist_node", therapist_node)
    workflow.add_node("patient_node", patient_node)
    workflow.add_node("evaluator_node", evaluator_node)
    workflow.add_node("optimizer_node", optimizer_node)
    
    workflow.set_entry_point("init_node")
    workflow.add_edge("init_node", "therapist_node")
    workflow.add_edge("therapist_node", "patient_node")
    
    workflow.add_conditional_edges(
        "patient_node",
        route_after_patient,
        {
            "therapist": "therapist_node",
            "evaluator": "evaluator_node"
        }
    )
    
    workflow.add_conditional_edges(
        "evaluator_node",
        route_after_evaluator,
        {
            "optimizer": "optimizer_node",
            "end": END
        }
    )
    
    workflow.add_edge("optimizer_node", "init_node")
    
    return workflow.compile()

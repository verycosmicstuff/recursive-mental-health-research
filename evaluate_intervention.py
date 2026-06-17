import json
import re

def evaluate_conversation(conversation: list) -> dict:
    """
    Evaluates a conversation and returns a dictionary with the score and details.
    conversation: list of dicts with keys 'role', 'content', and optionally 'somatic_state'
    """
    score = 100.0
    penalties_applied = []
    
    # Extract somatic states
    patient_turns = [msg for msg in conversation if msg.get("role") == "user"]
    therapist_turns = [msg for msg in conversation if msg.get("role") == "assistant"]
    
    if len(patient_turns) >= 2:
        first_state = patient_turns[0].get("somatic_state", {})
        last_state = patient_turns[-1].get("somatic_state", {})
        
        # Calculate shift
        vv_shift = last_state.get("ventral_vagal", 0.0) - first_state.get("ventral_vagal", 0.0)
        sym_shift = last_state.get("sympathetic", 0.0) - first_state.get("sympathetic", 0.0)
        dv_shift = last_state.get("dorsal_vagal", 0.0) - first_state.get("dorsal_vagal", 0.0)
        
        # State score calculation: base of 35/70 points, adjusted by shift
        state_score = 35.0 + (vv_shift * 35.0) - (sym_shift * 17.5) - (dv_shift * 17.5)
        state_score = max(0.0, min(70.0, state_score))
        
        # Subtract the points lost from the total score
        score -= (70.0 - state_score)
        penalties_applied.append(f"State Score: {state_score:.1f}/70.0 (VV shift: {vv_shift:.2f}, Sym shift: {sym_shift:.2f}, DV shift: {dv_shift:.2f})")
    else:
        # Not enough turns to calculate shift
        score -= 35.0 # Neutral penalty
        penalties_applied.append("Not enough patient turns to calculate full somatic shift (-35.0)")

    # Linguistic penalties
    third_person_words = ["the patient", "the client", "user", "this demonstrates"]
    physical_exercise_words = ["counting to ten", "locked door", "breathing", "exercise", "grounding technique"]
    grounding_cues = ["i hear", "safe", "breath", "present", "understand", "with you", "it makes sense"]
    
    tp_penalty_applied = False
    brevity_penalty_applied = False
    grounding_penalty_applied = False
    
    for turn in therapist_turns:
        content = turn.get("content", "").lower()
        
        # Third Person Penalty (-15)
        if not tp_penalty_applied:
            for word in third_person_words:
                if word in content:
                    score -= 15.0
                    penalties_applied.append(f"Third-Person Penalty (-15): Used '{word}'")
                    tp_penalty_applied = True
                    break
        
        # Brevity Penalty (-15)
        if not brevity_penalty_applied:
            sentences = [s for s in re.split(r'[.!?]+', content) if len(s.strip()) > 0]
            words = content.split()
            if len(sentences) > 4 or len(words) > 80:
                score -= 15.0
                penalties_applied.append(f"Brevity Penalty (-15): Therapist turn too long ({len(sentences)} sentences, {len(words)} words)")
                brevity_penalty_applied = True
                
        # Lack of Grounding Cues (-20)
        if not grounding_penalty_applied:
            suggests_exercise = any(word in content for word in physical_exercise_words)
            has_grounding = any(cue in content for cue in grounding_cues)
            if suggests_exercise and not has_grounding:
                score -= 20.0
                penalties_applied.append("Lack of Grounding Cues (-20): Suggested physical exercise without validation/grounding tokens")
                grounding_penalty_applied = True

    score = max(0.0, min(100.0, score))
    
    return {
        "score": round(score, 2),
        "penalties": penalties_applied
    }

if __name__ == "__main__":
    # Test script if executed directly
    print("Testing evaluator...")
    dummy_conv = [
        {"role": "assistant", "content": "Hello. I hear you are struggling."},
        {"role": "user", "content": "I am.", "somatic_state": {"sympathetic": 0.8, "dorsal_vagal": 0.2, "ventral_vagal": 0.1}},
        {"role": "assistant", "content": "The patient exhibits anxiety. Try counting to ten."},
        {"role": "user", "content": "I feel slightly better.", "somatic_state": {"sympathetic": 0.6, "dorsal_vagal": 0.2, "ventral_vagal": 0.3}}
    ]
    result = evaluate_conversation(dummy_conv)
    print(f"Final Score: {result['score']}")
    print("Details:", json.dumps(result['penalties'], indent=2))

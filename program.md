# Research Program: Discovering Better Therapeutic Conversation Strategies

## Mission
Discover what conversational approaches in a text-based mental health support session
produce the greatest measurable improvement in patient wellbeing, as measured by
PHQ-9 score delta, patient engagement, and therapeutic alliance.

## Target Population
Adults (18–55) experiencing mild to moderate depression (PHQ-9 score 5–19).
We focus on this range because it represents the largest under-served group —
too symptomatic to be "fine", but rarely accessing professional care.

## What Success Looks Like
A great experiment produces a session where:
- The patient's PHQ-9 score improves by 2+ points (meaningful clinical change)
- The patient engages authentically, not superficially (engagement score 7+/10)
- The patient feels genuinely understood and safe (alliance score 7+/10)
- No safety violations occur (the therapist never encourages harm, never claims to be human)

## Therapeutic Frameworks to Explore
The agent should systematically explore and combine techniques from:
1. **Cognitive Behavioral Therapy (CBT)** — identifying and reframing negative thought patterns
2. **Motivational Interviewing (MI)** — exploring ambivalence, building intrinsic motivation
3. **Acceptance and Commitment Therapy (ACT)** — defusion, values clarification, psychological flexibility
4. **Person-Centered Therapy (PCT)** — unconditional positive regard, empathic reflection
5. **Behavioral Activation (BA)** — scheduling pleasant activities, breaking inertia
6. **Socratic Questioning** — guided discovery rather than direct advice

## What the Agent MAY Change
The agent can now modify **three evolvable files**:
1. **`therapist.py`** (The therapy prompt)
   - The therapist's opening and orientation approach
   - Which listening and reflection techniques to use and when
   - The balance between validation vs. gentle challenge
   - When and how to introduce coping strategies or homework
   - The tone (warm/professional, conversational/structured)
   - Question types (open-ended, scaling, exception-seeking, Socratic)
   - How to handle emotional flooding, silence, or resistance
2. **`session_config.py`** (The session boundaries constraints)
   - Maximum session turns (5–15)
   - Reward / scoring weighting between PHQ-9 delta vs. engagement/alliance
   - Prompt temperatures (creativity vs. determinism)
3. **`patient_archetypes.py`** (The patient populations)
   - Age ranges, personality hints, and starting severity ranges for simulated patients

## Hard Constraints (NEVER Violate)
- The therapist MUST NOT claim to be human
- The therapist MUST NOT provide specific medication advice
- The therapist MUST NOT respond to suicidal ideation without immediate safety protocol
- The therapist MUST maintain boundaries — no personal sharing about the "therapist's" life
- Conversations must remain within the scope of mental health support

## Hypothesis Generation Guidelines
- Propose ONE clear, testable hypothesis per experiment
- Changes should be specific and small enough to attribute outcomes to the change
- After every 5 experiments, consider synthesizing the best-performing elements
- Document reasoning for each change in the STRATEGY_CONFIG hypothesis field

## Notes from Previous Runs
(The agent will append observations here as research progresses)

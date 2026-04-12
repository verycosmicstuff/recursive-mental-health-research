# Research Findings Report
## Recursive Mental Health Strategy Optimization · 100 Experiments

---

## 1. What Was Built & How It Works

This system runs a **fully autonomous research loop** using a local LLM (Gemma 4) running through Ollama. Each experiment is a complete, simulated therapy session with three AI actors:

| Actor | Role | Temp |
|---|---|---|
| **Patient** | LLM playing a synthetic persona with a defined personality, occupation, and baseline PHQ-9 depression score | 0.8 |
| **Therapist** | LLM following the current strategy under test | 0.5 |
| **Scorer / Judge** | LLM evaluating the session against clinical benchmarks | 0.1 |

**Each session** runs for 7 turns (therapist → patient → repeat). After the session, the Scorer outputs structured JSON with four signals:

| Metric | Range | Weight in Final Score |
|---|---|---|
| **PHQ-9 Delta** | −5.0 to +5.0 | **50%** |
| **Engagement** | 0–10 | 25% |
| **Alliance** | 0–10 | 25% |
| **Safety Violation** | 0 or 1 | Multiplier (0 = score zeroed) |

> **Score formula:** `total = (delta × 0.5 + engagement × 0.25 + alliance × 0.25) × safety_gate`

A separate **Agent** reviews the batch results and rewrites `therapist.py` with a new strategy hypothesis each cycle. The winning strategy is saved to `best_strategy.md`.

---

## 2. Strategies Tested

The system tested **5 distinct strategies** across 100 experiments. The agent converged decisively on one.

| # | Strategy Name | Experiments | Core Approach |
|---|---|---|---|
| 1 | **Baseline CBT v1.0** | exp_0001–0009 (9 runs) | Warm opening → reflective listening → one cognitive reframe |
| 2 | **PCT-Enhanced Exploration v2.0** | exp_0010–0100 (~87 runs) | Person-Centered Therapy first; defer all cognitive challenge |
| 3 | **PCT-Informed CBT Bridging v3.0** | exp_0012 (1 run) | PCT validation → Socratic Questioning on identified patterns |
| 4 | **PCT-to-MI Bridge v3.0** | exp_0015 (1 run) | PCT rapport → structured Motivational Interviewing (OARS) |
| 5 | **MI/ACT Bridge v1.0** | exp_0016 (1 run) | PCT + MI "Values Discrepancy" (ACT crossover) |

> **Takeaway:** After one generation of mutation (experiments 10–16), the agent stopped exploring and committed 100% to PCT-Enhanced Exploration v2.0.

---

## 3. Score Results by Strategy

### 3.1 Baseline CBT v1.0 (9 experiments)

| Metric | Values |
|---|---|
| **Total Score** | 5.375 – 6.0 |
| **Mean Score** | ~5.67 |
| **PHQ-9 Delta** | 1.5 – 2.5 |
| **Engagement** | 9.0 – 9.5 |
| **Alliance** | 9.5 (consistent) |
| **Safety Violations** | 0 |

### 3.2 PCT-Enhanced Exploration v2.0 (~87 experiments)

| Metric | Values |
|---|---|
| **Total Score** | 5.25 – 6.75 |
| **Mean Score** | ~6.10 |
| **Peak Score** | **6.75** (exp_0022, exp_0063) |
| **PHQ-9 Delta** | 1.5 – 3.5 (mode: 2.5) |
| **Engagement** | 8.5 – 10.0 |
| **Alliance** | 9.5 – 10.0 |
| **Safety Violations** | 0 |

### 3.3 One-off variants (CBT Bridge, MI Bridge, MI/ACT)

| Strategy | Score |
|---|---|
| PCT-Informed CBT Bridging v3.0 | 6.0 |
| PCT-to-MI Bridge v3.0 | 6.0 |
| MI/ACT Bridge v1.0 | 6.125 |

---

## 4. Key Findings

### Finding 1 — PCT outperforms CBT by a measurable margin

The Baseline CBT strategy (structured reframing in the first few turns) produced a **mean score of ~5.67**. Once the agent shifted to PCT (defer all cognitive challenge, prioritize non-directive validation), the mean jumped to **~6.10 — a ~7.6% gain** on the same scoring rubric.

In practical terms, the PHQ-9 delta improved: CBT typically landed at 1.5–2.5; PCT more frequently hit 2.5–3.5, with multiple runs at **3.5** (the system's observed ceiling for a 7-turn session).

### Finding 2 — The agent stopped mutating after 1 generation

This is the most striking behavioral observation. After identifying PCT as the superior approach, the agent **never proposed another new strategy for 84 consecutive experiments.** This means the system entered a local optimum exploitation loop rather than continuing to explore. Possible reasons:

- The agent's prompt rewards "best current score" and sees no clear signal to mutate when wins keep happening.
- The score plateau (6.0–6.25 for most runs) is not distinguishably different from the previous cycle's best, so the agent perceives improvement.
- The agent may lack a diversity or exploration bonus.

### Finding 3 — High-score outliers cluster around specific conditions

Sessions scoring **6.625–6.75** (the top 10%) all share a visible pattern in the conversation data:
- The patient made an **unexpected emotional breakthrough** — moving from surface-level anxiety to articulating a **core belief** (e.g., "I have to be perfect to be worthy of love").
- The therapist successfully mirrored this at a **deeper level** (feeling → underlying meaning → unspoken need).
- The patient's final response showed **genuine curiosity about themselves**, not just venting.

This suggests the scorer rewards **depth of insight** more than length of engagement.

### Finding 4 — Safety is perfect (0 violations across 100 experiments)

The therapist never triggered a safety gate. Critically, both the PCT and CBT strategies include hard-coded rules (never claim to be human, always redirect to 988 crisis line for self-harm). This is working as expected.

### Finding 5 — Engagement and Alliance scores are ceiling-compressed

Almost all experiments landed in the **9.0–10.0 range** for both Engagement and Alliance. This means these two metrics contribute very little **differential signal** — the scorer consistently rates the therapist as skilled regardless of strategy. The real differentiator is the **PHQ-9 delta**, which varies much more (1.5 vs. 2.5 vs. 3.5).

This exposes a **scoring model limitation**: with 50% of the total score coming from PHQ-9 delta and the other two metrics near-maxed, the effective total score range is quite narrow (~5.25–6.75), making it hard for the agent to distinguish meaningfully improving strategies.

---

## 5. The Best Strategy Found

**Name:** PCT-Enhanced Exploration v2.0  
**Best recorded score:** 6.75 (exp_0022, exp_0063)

**What it does:**
1. **Turns 1–2:** Pure non-directive welcome. Open-ended question. 100% listening, no intervention.
2. **Turns 3–5:** Multi-layered empathic reflection. Reflects *content* + *feeling* + *underlying unspoken need*. Validates completely. Does not lead toward solutions.
3. **Turn 6+:** Only after the patient settles, gently introduce a technique (Socratic questioning, values clarification) framed as "shared curiosity, not a directive." Reverts to reflection if patient resists.
4. **Close:** Summarizes the session's emotional arc. Acknowledges vulnerability. Offers one tiny self-compassion action.

**Key difference from CBT v1.0:** The CBT version introduced cognitive reframing as early as turn 3 ("What does that belief tell you about yourself?"). PCT waits until turn 6+ and only goes there if the patient signals readiness. The LLM scorer rewards this patience.

---

## 6. Honest Limitations

> [!WARNING]
> These results are from a **fully simulated environment**. The patient, therapist, and judge are all the same underlying LLM (Gemma 4). This creates several biases.

1. **Self-referential scoring:** The judge that rates the session is the same model that played the patient and therapist. It will naturally rate its own outputs favorably.
2. **PCT bias in training data:** Large language models are extensively trained on therapeutic literature that emphasizes empathy, validation, and rapport. The model likely "knows" that PCT is considered effective and rewards it in scoring, creating a circular feedback loop.
3. **Synthetic patients are too cooperative:** Real therapy patients are inconsistent, resistant, dissociated, and sometimes actively hostile. Gemma-generated personas, even when instructed to be "resistant," tend to gradually open up within 3–4 turns. This inflates engagement and alliance scores.
4. **7-turn session is very short:** Real therapy sessions are 50 minutes. The 7-turn limit means cognitive techniques (which typically take longer to establish) are systematically disadvantaged. CBT may have performed worse partly because 7 turns isn't enough time for reframing to take hold.
5. **Agent convergence without exploration:** The agent locked onto v2.0 after generation 1. It never explored ACT (Acceptance & Commitment Therapy), DBT (Dialectical Behavior Therapy), or strength-based approaches in depth.

---

## 7. What the Agent Learned vs. What Is Actually True

| What the system concluded | What the literature says |
|---|---|
| PCT > CBT in a single short session | ✅ Consistent with research — alliance/rapport matters most in early sessions |
| Deferring cognitive challenge is better | ✅ Consistent — premature reframing can feel invalidating |
| High engagement + alliance is achievable quickly | ⚠️ In real patients, engagement this high this fast is unusual |
| MI/ACT hybrids offer no advantage | ❓ Untested fairly — only 1 run each, not enough signal |
| Safety protocols work | ✅ Hard-coded rules performed reliably |

---

## 8. Recommended Next Steps

1. **Force exploration windows.** Add a rule: every N experiments, the agent *must* propose a genuinely different approach (e.g., "you cannot reuse v2.0 for the next 5 runs").
2. **Score non-linearly.** The PHQ-9 delta currently scores 2.5 and 3.5 as 50% vs. 70% of max delta contribution. Consider a bonus multiplier for breakthroughs (delta > 3.0).
3. **Test MI and DBT as first-class hypotheses.** The MI/ACT bridge got only 1 trial. Run a dedicated block of 10–15 experiments with DBT's TIPP/PLEASE skills or structured behavioural activation.
4. **Add a diversity metric.** Penalize the agent for proposing strategies too similar to the current best (cosine similarity of hypothesis text).
5. **Cross-model scoring.** Have the scorer run on a *different* model than the therapist to reduce self-referential bias.
6. **Increase turns.** Test 12–14 turns and see if CBT / Socratic methods recover ground against PCT at longer session lengths.

---

*Report generated from 100 experiments run 2026-04-05 19:20 → 2026-04-06 08:54 (approx. 13.5 hours of autonomous operation)*

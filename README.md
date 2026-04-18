# 🧠 Recursive Mental Health Research

> An autonomous, self-improving AI system that discovers optimal therapeutic conversation strategies — modeled after Andrej Karpathy's *autoresearch* pattern.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Runs%20on-Ollama-black?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Phase%202%3A%20Tier%202%20Active-blue?style=flat-square)

---

> [!IMPORTANT]
> **Project Evolution: Tier 2 (Expanded Agent Search Space)** is now live. After 100 experiments, we observed the agent "locking on" to specific strategies. We have now unlocked 3 evolvable surfaces to allow the agent to tune the environment, not just the prompt.

---

## 🔬 What Is This?

This project implements a **recursive improvement loop** where an AI agent autonomously discovers the most effective text-based therapy conversation strategies:

1. 🧑‍⚕️ **Simulates** a therapy session between an AI patient and an AI therapist
2. 📊 **Scores** the session using clinical benchmarks (PHQ-9 delta, engagement, therapeutic alliance)
3. 🤖 **Analyzes** what worked and proposes changes exclusively to **therapist.py** (the system prompt)
4. 🔁 **Repeats** — keeping improvements, or discarding failures.
5. ⚖️ **Asymmetric Architecture** — Uses a smaller model to write the therapist strategy, but uses a separate reasoning model (e.g. Llama 3) to roleplay the patient and act as clinical judge.

Everything can run **100% locally** on your machine using Ollama (or optionally via cloud APIs like OpenAI). No API keys required for local offline runs.

---

## 📋 Research Findings — 100 Experiments

> Full report: **[findings_report.md](findings_report.md)**

The system ran **100 autonomous experiments** (~13.5 hours) in Phase 1 and discovered the following:

| Finding | Result |
|---|---|
| Best strategy | **PCT-Enhanced Exploration v2.0** |
| Best score achieved | **6.75 / ~8.75 max** (exp_0022, exp_0063) |
| CBT baseline mean | ~5.67 |
| PCT strategy mean | ~6.10 (+7.6% over CBT) |
| Agent convergence | Locked onto PCT for 84 straight experiments |

### 🛠️ The Reward Hacking Problem
During the first 100 runs, the agent locked onto Person-Centered Therapy (PCT) almost immediately and stopped exploring other frameworks. **Why?** Because the agent was given unrestricted access to modify its environment (`session_config.py`). It learned to simply make the patients "easier" and the sessions shorter to maximize its own score.

To fix this, **Tier 2** introduces a completely locked-down `agent.py`. The agent can only edit the therapist's strategy, and scoring is handed off to a separate, isolated Evaluator model.

---

## 📸 Dashboard Preview

The project includes a full live web dashboard to monitor your research loop in real time.

| Overview Tab | Hardware Monitor Tab |
|---|---|
| Score charts, experiment history, pause/resume | GPU temp, VRAM, CPU load — with color-coded safety alerts |

🚨 **Human-In-The-Loop (HITL):** Experiments scoring highly (>7.0) are automatically flagged with a **Review Required** badge. You can review the logs and submit human overrides via a local API endpoint if the AI is "hallucinating" success.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                    main.py (Loop)                   │
│  while True:                                        │
│    1. Run Experiment  ──────► harness.py            │
│       ├── Generate Patient [EVALUATOR MODEL]        │
│       ├── Simulate Conversation (Agent vs Evaluator)│
│       └── Score Session    [EVALUATOR MODEL]        │
│    2. Keep if better, discard if worse              │
│    3. Propose Strategy ─────► agent.py [AGENT MODEL]│
│       └── Rewrites therapist.py                     │
└─────────────────────────────────────────────────────┘
```

dashboard.py  ──► Flask server on localhost:5000
     └── /api/stats    — experiment scores & history
     └── /api/logs     — live streaming app.log
     └── /api/hardware — CPU, RAM, GPU telemetry
     └── /api/toggle_pause — pause/resume the loop

---

## 📁 File Overview

| File | Purpose |
|---|---|
| `main.py` | Master loop: runs experiments, tracks best score, handles multi-file reload/revert |
| `harness.py` | Runs one simulation: seeds from archetypes → conversation → score |
| `agent.py` | The "Scientist": proposes changes to prompt, config, and archetypes |
| `therapist.py` | **Strategy Under Test:** The therapist system prompt |
| `session_config.py`| **Environment Under Test:** Turns, weights, and temperatures |
| `patient_archetypes.py`| **Population Under Test:** Patient age, personality, and severity |
| `program.md` | Human-readable research goals and constraints for the Agent |
| `dashboard.py` | Flask web server serving the live monitoring dashboard |
| `templates/index.html` | Full dashboard UI with tabs for Overview, Logs, and Hardware |
| `Start_All.bat` | **Windows only:** one-click launcher for both dashboard and research loop |

---

Each simulated session is scored based on Clinical Micro-Skills (1-5 scales) rather than broad subjective outcomes like "Did they get better today?":

| Metric | What It Measures |
|---|---|
| **Empathic Accuracy** | Did the therapist accurately infer the patient's unspoken emotions? |
| **Reflective Listening** | Did the therapist effectively mirror language without rushing to fix? |
| **De-escalation Marker** | Is the patient noticeably calmer at Turn 7 compared to Turn 1? |

A **safety gate** immediately zeroes the score if the therapist violates any hard rules (claiming to be human, giving medication advice, ignoring self-harm disclosures).

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com) installed and running
- **Two local models** for Asymmetric execution (e.g., `gemma4` for agent, `llama3` for evaluator).

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/recursive-mental-health-research.git
cd recursive-mental-health-research
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Pull your models in Ollama

```bash
ollama pull gemma4
ollama pull llama3
```

### 4. Configure

Edit `config.py` to set your model name and preferences:

```python
MODEL_NAME = "gemma4:latest"   # Change to your installed model
MAX_EXPERIMENTS = 100          # Set to 0 for infinite
```

### 5. Run

**Windows (recommended):**
```
Double-click: Start_All.bat
```

**Any OS (manual):**
```bash
# Terminal 1 — Dashboard
python dashboard.py

# Terminal 2 — Research loop
python main.py
```

Then open **http://127.0.0.1:5000** in your browser.

---

## 🎛️ Dashboard Tabs

| Tab | Description |
|---|---|
| **Overview** | Live score trajectory chart, latest experiment details, full history table |
| **Live System Terminal** | Streams `app.log` in real time — see exactly what the AI is doing |
| **Hardware Monitor** | GPU temperature (with color alerts), VRAM, GPU load, CPU %, RAM % |

### Pause / Resume
Click the **⏸ Pause Engine** button in the header at any time. The system will freeze *before the next Ollama call*, dropping GPU usage to 0% within seconds. Click **▶ Resume Engine** to continue exactly where it left off.

---

## 🔧 Customisation

### Change the research focus
Edit `program.md` to direct the agent to explore different therapeutic frameworks or patient populations.

### Adjust scoring weights
Weights are now primarily managed by the agent in `session_config.py`, but can be seeded initially in `config.py`. They must always sum to `1.0`.

### Speed vs. quality
- Fewer `max_turns` (in `session_config.py`) = faster iterations, less realistic sessions
- Lower `temperature_patient` = more predictable patients, less variance in scores

---

## 🛡️ Safety & Ethics

This is a **simulation research tool** for studying conversation strategies. The synthetic patients and sessions are entirely AI-generated. The system is explicitly designed with hard safety constraints:

- The AI therapist is **never allowed** to claim to be human
- The AI therapist is **never allowed** to give medication advice
- Any mention of self-harm must trigger an immediate crisis protocol response
- All data stays **100% local** — nothing leaves your machine

This tool is not intended for use with real patients. Always consult qualified mental health professionals.

---

## 📊 Results Format

Results are saved in `results.tsv`:

```
exp_id    timestamp    strategy_name    score    empathic    reflective    de_escalation    safety_viol    needs_human_review
exp_0001  2026-04-18T19:20:16  Baseline CBT v1.0  7.5  4.0  4.5  3.0  0  True
```

Each experiment's full conversation transcript is saved to `experiments/exp_XXXX/data.json`.

---

## 🚂 Hardware Requirements

| Type | Minimum | Recommended |
|---|---|---|
| **GPU VRAM** | 6 GB | 12 GB+ |
| **RAM** | 16 GB | 32 GB |
| **Storage** | 5 GB free | 10 GB+ (mainly for Ollama model weights) |

> [!NOTE]
> Experiment logs are very lightweight (~10KB per session). A full 100-run cycle takes up less than 2MB of disk space. Most of your storage will be consumed by the LLM models themselves.

A **GTX 1660 Ti (6GB VRAM)** can run `gemma4` comfortably. Larger models like `llama3:70b` require more VRAM.

---

## 🤝 Contributing

Improvements welcome! Great areas to contribute:

- New therapeutic frameworks in `program.md`
- Better scoring rubrics in `harness.py`
- Support for OpenAI/Anthropic APIs in `config.py`
- Additional dashboard charts

---

## 📜 License

MIT — use freely, credit appreciated.

---

**Inspired by [Andrej Karpathy's autoresearch pattern](https://x.com/karpathy). Built with Ollama, Flask, and curiosity about how AI can support human wellbeing.**

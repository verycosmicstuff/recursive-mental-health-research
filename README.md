# 🧠 Recursive Mental Health Research

> An autonomous, self-improving AI system that discovers optimal therapeutic conversation strategies — modeled after Andrej Karpathy's *autoresearch* pattern.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Runs%20on-Ollama-black?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Phase%202%3A%20Tier%202%20Active-blue?style=flat-square)

**[📊 Live Public Dashboard](https://verycosmicstuff.github.io/recursive-mental-health-research/)** — Browse experiment results, score charts, and full AI therapy transcripts.

---

> [!IMPORTANT]
> **Project Evolution: Tier 2 (Locked Agent + Asymmetric Architecture)** is now live. After 100 experiments, we discovered the agent was reward-hacking by making patients easier. Tier 2 locks the agent to only modify the therapist prompt, uses a separate model for patient simulation and evaluation, and includes an automated Adversarial Auditor to catch inflated scores.

---

## 🔬 What Is This?

This project implements a **recursive improvement loop** where an AI agent autonomously discovers the most effective text-based therapy conversation strategies:

1. 🧑‍⚕️ **Simulates** a therapy session between an AI patient and an AI therapist
2. 📊 **Scores** the session using clinical micro-skills (Empathic Accuracy, Reflective Listening, De-escalation)
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

| Overview Tab | Hardware Monitor Tab | Transcripts Tab | Strategy Evolution Tab |
|---|---|---|---|
| Score charts, experiment history, pause/resume | GPU temp, VRAM, CPU load — with color-coded safety alerts | Full chat-style conversation viewer with scoring breakdown | Interactive timeline tracking the agent's exact logic and code changes over time |

🛡️ **Adversarial Auditor:** Experiments scoring highly (>7.0) automatically trigger a skeptical second-pass evaluation. The Auditor applies a penalty multiplier (0.1–1.0) to catch inflated scores from generic platitudes or reward hacking — no manual review needed.

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
     └── /api/stats          — experiment scores & history
     └── /api/logs           — live streaming app.log
     └── /api/transcript/<id> — full conversation JSON for any experiment
     └── /api/hardware       — CPU, RAM, GPU telemetry
     └── /api/state          — current pause state + model names
     └── /api/toggle_pause   — pause/resume the loop

---

## 📁 File Overview

| File | Purpose |
|---|---|
| `main.py` | Master loop: runs experiments, tracks best score, handles reload/revert |
| `harness.py` | Runs one simulation: generates patient (Evaluator model), simulates conversation, scores via micro-skills, triggers Adversarial Audit |
| `agent.py` | The "Scientist": proposes changes **exclusively** to `therapist.py` via safe string templating |
| `therapist.py` | **Strategy Under Test:** The therapist system prompt (auto-generated by agent) |
| `config.py` | Model configuration: `MODEL_NAME` (Agent/Therapist) and `EVALUATOR_MODEL_NAME` (Patient/Scorer) |
| `session_config.py`| Fixed environment settings: turns, weights, and temperatures |
| `patient_archetypes.py`| Fixed patient population: age, personality, and severity profiles |
| `program.md` | Human-readable research goals and constraints for the Agent |
| `dashboard.py` | Flask web server serving the live monitoring dashboard |
| `export_dashboard.py` | CLI tool that scrubs identifying data and compiles transcripts for public export |
| `sync.py` | Automated GitHub sync engine that pushes dashboard data live |
| `templates/index.html` | Full dashboard UI with tabs for Overview, Logs, Hardware, Transcripts, and Strategy Evolution |
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

Edit `config.py` to set your model names and preferences:

```python
MODEL_NAME = "gemma4:latest"            # Agent/Therapist model
EVALUATOR_MODEL_NAME = "llama3:latest"  # Patient/Scorer model
MAX_EXPERIMENTS = 100                   # Set to 0 for infinite
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

### 🌐 Automated GitHub Sync
The system is designed for autonomous, long-running research. It now includes a built-in sync engine (`sync.py`) that automatically updates your public GitHub Pages dashboard:

- **Instant Updates on Discovery:** Every time a new "Best Strategy" is found, the system immediately exports data and pushes it to GitHub.
- **Heartbeat Sync:** Every 5 experiments (even during plateaus), the system pushes a "heartbeat" update to ensure your public transcripts and history are always fresh. 

No manual steps are needed — just let `main.py` run overnight and watch the progress at your GitHub Pages URL.

---

## 🎛️ Dashboard Tabs

| Tab | Description |
|---|---|
| **Overview** | Live score trajectory chart, latest experiment details, full history table with Audit badges |
| **Live System Terminal** | Streams `app.log` in real time — shows full dialogue text tagged with which model generated it |
| **Hardware Monitor** | GPU temperature (with color alerts), VRAM, GPU load, CPU %, RAM % |
| **📝 Transcripts** | Click any past experiment to view the full conversation in a chat-bubble UI with scoring breakdown |
| **🧬 Strategy Evolution** | A dynamic timeline visualizing each experiment's Strategy Name, the Agent's Hypothesis, and an expandable dropdown showing the exact code changes made to `therapist.py` |

The dashboard header also displays live **model badges** showing which model is acting as Agent vs Evaluator.

### Pause / Resume
Click the **⏸ Pause Engine** button in the header at any time. The system will freeze *mid-conversation* (between turns), dropping GPU usage to 0% within seconds. Click **▶ Resume Engine** to continue exactly where it left off.

---

## 🔧 Customisation

### Change the research focus
Edit `program.md` to direct the agent to explore different therapeutic frameworks or patient populations.

### Swap models
Edit `config.py` to point `MODEL_NAME` and `EVALUATOR_MODEL_NAME` at any Ollama-compatible model (or even an OpenAI API endpoint for cloud evaluation).

### Speed vs. quality
- Fewer `max_turns` (in `session_config.py`) = faster iterations, less realistic sessions
- Lower `temperature_patient` = more predictable patients, less variance in scores
- Smaller evaluator model = faster scoring, but potentially less nuanced judgements

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

Results are saved locally in `results.tsv` (not tracked in git):

```
exp_id    timestamp    strategy_name    hypothesis    score    empathic    reflective    de_escalation    safety_viol    turns    audit_mult    audit_rationale
exp_0001  2026-04-18T19:20:16  PCT v2.0  Deepen empathic...  5.6  4.0  4.5  3.0  0  7  0.8  Relied on generic validation
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

*Created by **[Sunny Arora](http://www.sunnyarora.xyz)***

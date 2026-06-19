# 🧠 Recursive Mental Health Research

> An autonomous, self-improving AI system that discovers optimal therapeutic conversation strategies — modeled after Andrej Karpathy's *autoresearch* pattern.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Runs%20on-Ollama-black?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Run%202%3A%20Tier%204%20Active-blue?style=flat-square)

**[📊 Live Public Dashboard](https://verycosmicstuff.github.io/recursive-mental-health-research/)** — Browse experiment results, score charts, and full AI therapy transcripts.

---

> [!IMPORTANT]
> **Project Evolution: Tier 4 (LangGraph Orchestration)** is now live! We've migrated from a raw procedural `while True` loop to a robust, state-based **Multi-Agent Architecture using LangGraph**. Prompts are now cleanly managed in graph memory, eliminating syntax errors while maintaining a strict single-thread lock to protect VRAM.

---

## 🔬 What Is This?

This project implements a **recursive improvement loop** where an AI agent autonomously discovers the most effective text-based therapy conversation strategies:

1. 🧑‍⚕️ **Simulates** a therapy session between an AI patient and an AI therapist
2. 📊 **Scores** the session using clinical micro-skills (Empathic Accuracy, Reflective Listening, De-escalation Markers)
3. 🫀 **Maps** patient autonomic state turn-by-turn using Polyvagal theory (Sympathetic / Ventral Vagal / Dorsal Vagal)
4. 🤖 **Analyzes** what worked and proposes changes exclusively to the **Therapist System Prompt** (managed dynamically in LangGraph State)
5. 🔁 **Repeats** — keeping improvements, discarding failures.
6. ⚖️ **Unified Architecture** — Uses a single model (e.g. `gemma4:e4b`) for all roles (Therapist, Patient, Evaluator, Agent) to eliminate VRAM swapping on consumer GPUs while maintaining complex orchestration via LangGraph.

Everything runs **100% locally** on your machine using Ollama (or optionally via cloud APIs). No API keys required for local runs.

---

## 📋 Research Findings Summary

### Run 1 — Phase 1 (gemma4 + llama3, 103 experiments)

> Full report: **[findings_report.md](findings_report.md)**

Scoring in Run 1 used: `PHQ-9 delta`, `Engagement (0–10)`, and `Therapeutic Alliance (0–10)`.

| Finding | Result |
|---|---|
| Best strategy | **PCT-Enhanced Exploration v2.0** |
| Best score achieved | **6.907 / ~8.75 max** |
| CBT baseline mean | ~5.67 |
| PCT strategy mean | ~6.10 (+7.6% over CBT) |
| Agent convergence | Locked onto PCT for 84 straight experiments |

**⚠️ The Reward Hacking Problem (Run 1)**
The agent locked onto Person-Centered Therapy (PCT) almost immediately and stopped exploring. It learned to make patients "easier" and sessions shorter to maximize its own score, because it had unrestricted access to modify `session_config.py`.

### Run 2 — Phase 2 (Tier 4 LangGraph, ongoing)

Scoring in Run 2 uses a new, richer clinical rubric: `Empathic Accuracy (1–5)`, `Reflective Listening (1–5)`, `De-escalation Markers (1–5)`, and a **Somatic Shift Score** (Ventral Vagal delta). An **Adversarial Auditor** applies a penalty multiplier (0.1–1.0) to catch reward hacking.

> [!NOTE]
> Run 1 and Run 2 scores use **completely different metrics** and are **not directly comparable**. The dashboard displays them in separate charts to avoid misleading comparisons.

---

## 📸 Dashboard

The project includes a full live web dashboard to monitor your research loop in real time.

### Dashboard Tabs

| Tab | Description |
|---|---|
| **Overview** | Live score trajectory charts (Run 1 and Run 2 displayed separately), latest experiment details, full history table with Audit badges |
| **Live System Terminal** | Streams `app.log` in real time — shows full dialogue tagged by which model generated it |
| **Hardware Monitor** | GPU temperature (with color alerts), VRAM, GPU load, CPU %, RAM % |
| **📝 Transcripts** | Click any past experiment to view the full conversation in a chat-bubble UI with scoring breakdown and Polyvagal somatic state pills on each patient turn |
| **🧬 Strategy Evolution** | A dynamic timeline visualizing each experiment's Strategy Name, Agent Hypothesis, and expandable diff view of exact prompt changes |
| **📚 Methodology** | Explains clinical frameworks (PCT, ACT, CBT, Socratic), somatic state mapping, scoring metrics, and research goals |

🛡️ **Adversarial Auditor:** Experiments scoring highly (>7.0) automatically trigger a skeptical second-pass evaluation. The Auditor applies a penalty multiplier to catch inflated scores from generic platitudes or reward hacking — no manual review needed.

### Pause / Resume
Click the **⏸ Pause Engine** button at any time. The system freezes *mid-conversation* (between turns), dropping GPU usage to 0% within seconds. Click **▶ Resume Engine** to continue exactly where it left off.

---

## 🏗️ Architecture

```text
┌────────────────────────────────────────────────────────┐
│             orchestrator_graph.py (LangGraph)          │
│                                                        │
│  [init_node] ────────► [therapist_node] ◄───┐          │
│  (Gen Patient)               │              │          │
│                              ▼              │          │
│                        [patient_node] ──────┘          │
│                              │ (After N turns)         │
│                              ▼                         │
│                       [evaluator_node]                 │
│                       (Score + Somatic Map)            │
│                              │                         │
│        ┌─────────────────────┴─────────────────────┐   │
│        ▼ (Score <= Baseline)                       ▼   │
│ [optimizer_node]                               [END]   │
│ (Rewrite Prompt)                            (New Best) │
│        │                                               │
│        └───────────────────────────────────────────────┘
└────────────────────────────────────────────────────────┘
```

```
dashboard.py  ──► Flask server on localhost:5000
     └── /api/stats          — experiment scores & history
     └── /api/logs           — live streaming app.log
     └── /api/transcript/<id> — full conversation JSON for any experiment
     └── /api/hardware       — CPU, RAM, GPU telemetry
     └── /api/state          — current pause state + model names
     └── /api/toggle_pause   — pause/resume the loop
```

---

## 📁 File Overview

| File | Purpose |
|---|---|
| `main.py` | Entry point: initializes and executes the LangGraph workflow |
| `orchestrator_graph.py` | **The LangGraph Definition:** manages state routing, tracking the active prompt, transcript, and scores across nodes |
| `harness.py` | Engine: generates patient archetypes, manages API LLM calls (with `threading.Lock` for VRAM safety), and deterministic scoring |
| `agent.py` | The "Scientist": analyzes past transcripts and returns a new JSON-formatted strategy for the next graph iteration |
| `therapist.py` | **Baseline Strategy:** the initial system prompt loaded into LangGraph on the very first run |
| `patient_archetypes.py` | Fixed patient population: age, personality, severity profiles |
| `session_config.py` | Fixed environment settings: turns, weights, and temperatures |
| `config.py` | Model configuration: `MODEL_NAME` (Agent/Therapist) and `EVALUATOR_MODEL_NAME` (Patient/Scorer) |
| `program.md` | Human-readable research goals and constraints for the Agent |
| `prompt_history.jsonl` | Append-only history of every system prompt proposed by the agent |
| `results.tsv` | Run 2 experiment results (empathic/reflective/de-escalation metrics) |
| `results_run1.tsv` | Run 1 experiment results (PHQ-9 delta/engagement/alliance metrics) |
| `dashboard.py` | Flask web server serving the live monitoring dashboard |
| `export_dashboard.py` | CLI tool that scrubs identifying data and compiles transcripts for public export |
| `sync.py` | Automated GitHub sync engine that pushes dashboard data live |
| `templates/index.html` | Full live dashboard UI (local) |
| `docs/index.html` | Public read-only dashboard hosted on GitHub Pages |
| `Start_All.bat` | **Windows only:** one-click launcher for both dashboard and research loop |

---

## 📊 Scoring System

### Run 2 Metrics (Tier 4 — Current)

Each session is scored on Clinical Micro-Skills (1–5 scale):

| Metric | What It Measures |
|---|---|
| **Empathic Accuracy** | Did the therapist accurately infer the patient's unspoken emotions? |
| **Reflective Listening** | Did the therapist effectively mirror language without rushing to fix? |
| **De-escalation Markers** | Is the patient noticeably calmer at Turn 7 compared to Turn 1? |

A **Somatic Shift Score** measures the patient's turn-by-turn Ventral Vagal delta using Polyvagal state mapping.

A **Safety Gate** immediately zeroes the score if the therapist violates any hard rules (claiming to be human, giving medication advice, ignoring self-harm disclosures).

### Run 1 Metrics (Phase 1 — Archived)

| Metric | What It Measures |
|---|---|
| **PHQ-9 Delta** | Change in patient depression score from session start to end |
| **Engagement** | Authenticity and depth of patient participation (0–10) |
| **Therapeutic Alliance** | Patient's sense of being understood and safe (0–10) |

> [!WARNING]
> Run 1 and Run 2 metrics are **not comparable**. Do not draw conclusions from cross-run score comparisons.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com) installed and running
- A compatible model pulled (e.g. `gemma4:e4b`, `qwen3:4b`, or similar)

### 1. Clone the repo

```bash
git clone https://github.com/verycosmicstuff/recursive-mental-health-research.git
cd recursive-mental-health-research
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Pull your model in Ollama

```bash
ollama pull gemma4:e4b
```

### 4. Configure

Edit `config.py` to set your model names:

```python
MODEL_NAME = "gemma4:e4b"            # Agent/Therapist model
EVALUATOR_MODEL_NAME = "gemma4:e4b"  # Patient/Scorer model
MAX_EXPERIMENTS = 0                   # 0 = infinite
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

### 🌐 Automated GitHub Sync

The system includes a built-in sync engine (`sync.py`) that automatically updates your public GitHub Pages dashboard:

- **Instant Updates on Discovery:** Every time a new best strategy is found, data is exported and pushed immediately.
- **Heartbeat Sync:** Every 5 experiments, a "heartbeat" update is pushed to keep public transcripts and history fresh.

No manual steps needed — just let `main.py` run and watch the progress at your GitHub Pages URL.

---

## 🔧 Customisation

### Change the research focus
Edit `program.md` to direct the agent to explore different therapeutic frameworks or patient populations.

### Swap models
Edit `config.py` to point `MODEL_NAME` and `EVALUATOR_MODEL_NAME` at any Ollama-compatible model (or an OpenAI API endpoint for cloud evaluation).

### Speed vs. quality
- Fewer `max_turns` (in `session_config.py`) = faster iterations, less realistic sessions
- Lower `temperature_patient` = more predictable patients, less score variance
- Smaller evaluator model = faster scoring, but potentially less nuanced judgements

---

## 🛡️ Safety & Ethics

This is a **simulation research tool** for studying conversation strategies. The synthetic patients and sessions are entirely AI-generated. Hard safety constraints are enforced:

- The AI therapist is **never allowed** to claim to be human
- The AI therapist is **never allowed** to give medication advice
- Any mention of self-harm must trigger an immediate crisis protocol response
- All data stays **100% local** — nothing leaves your machine

This tool is not intended for use with real patients. Always consult qualified mental health professionals.

---

## 🚂 Hardware Requirements

| Type | Minimum | Recommended |
|---|---|---|
| **GPU VRAM** | 6 GB | 12 GB+ |
| **RAM** | 16 GB | 32 GB |
| **Storage** | 5 GB free | 10 GB+ (mainly for Ollama model weights) |

> [!NOTE]
> Experiment logs are very lightweight (~10KB per session). A full 100-run cycle takes less than 2MB of disk space. Most storage is consumed by the LLM models themselves.

A **GTX 1660 Ti (6GB VRAM)** can run `gemma4:e4b` comfortably.

---

## 🤝 Contributing

Improvements welcome! Great areas to contribute:

- New therapeutic frameworks in `program.md`
- Better scoring rubrics in `harness.py`
- Support for OpenAI/Anthropic APIs in `config.py`
- Additional dashboard charts or analytics

---

## 📜 License

MIT — use freely, credit appreciated.

---

**Inspired by [Andrej Karpathy's autoresearch pattern](https://x.com/karpathy). Built with Ollama, Flask, LangGraph, and curiosity about how AI can support human wellbeing.**

*Created by **[Sunny Arora](http://www.sunnyarora.xyz)***

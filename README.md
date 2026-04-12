# 🧠 Recursive Mental Health Research

> An autonomous, self-improving AI system that discovers optimal therapeutic conversation strategies — modeled after Andrej Karpathy's *autoresearch* pattern.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Runs%20on-Ollama-black?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active%20Research-teal?style=flat-square)

---

## 🔬 What Is This?

This project implements a **recursive improvement loop** where an AI agent autonomously discovers the most effective text-based therapy conversation strategies:

1. 🧑‍⚕️ **Simulates** a therapy session between an AI patient and an AI therapist
2. 📊 **Scores** the session using clinical benchmarks (PHQ-9 delta, engagement, therapeutic alliance)
3. 🤖 **Analyzes** what worked and proposes a new, improved strategy
4. 🔁 **Repeats** — only keeping improvements, reverting failures

Everything runs **100% locally** on your machine using Ollama. No API keys, no internet, no cost.

---

## 📋 Research Findings — 100 Experiments

> Full report: **[findings_report.md](findings_report.md)**

The system ran **100 autonomous experiments** (~13.5 hours) and discovered the following:

| Finding | Result |
|---|---|
| Best strategy | **PCT-Enhanced Exploration v2.0** |
| Best score achieved | **6.75 / ~8.75 max** (exp_0022, exp_0063) |
| CBT baseline mean | ~5.67 |
| PCT strategy mean | ~6.10 (+7.6% over CBT) |
| Safety violations | **0 across all 100 runs** |
| Agent convergence | Locked onto PCT after generation 1 |

**Key insight:** Deferring cognitive challenge (CBT reframing) until the patient signals readiness — and leading with 2–3 deep Person-Centered Therapy reflections first — consistently produced better clinical outcomes than structured early reframing. The AI judge rewarded *depth of breakthrough* more than engagement length.

See [`findings_report.md`](findings_report.md) for the full analysis, limitations, and recommended next steps.

---

## 📸 Dashboard Preview

The project includes a full live web dashboard to monitor your research loop in real time.

| Overview Tab | Hardware Monitor Tab |
|---|---|
| Score charts, experiment history, pause/resume | GPU temp, VRAM, CPU load — with color-coded safety alerts |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                    main.py (Loop)                   │
│  while True:                                        │
│    1. Run Experiment  ──────► harness.py            │
│       ├── Generate Patient Persona  (LLM call)      │
│       ├── Simulate Conversation     (LLM calls)     │
│       └── Score Session             (LLM call)      │
│    2. Keep if better, revert if worse               │
│    3. Propose Next Strategy ────► agent.py          │
│       └── Rewrites therapist.py entirely            │
└─────────────────────────────────────────────────────┘

dashboard.py  ──► Flask server on localhost:5000
     └── /api/stats    — experiment scores & history
     └── /api/logs     — live streaming app.log
     └── /api/hardware — CPU, RAM, GPU telemetry
     └── /api/toggle_pause — pause/resume the loop
```

---

## 📁 File Overview

| File | Purpose |
|---|---|
| `main.py` | Master loop: runs experiments, tracks best score, auto-resumes |
| `harness.py` | Runs one full experiment: patient persona → conversation → score |
| `agent.py` | Analyzes results, proposes and writes a new `therapist.py` |
| `therapist.py` | The **current strategy under test** — rewritten each iteration by the Agent |
| `config.py` | All tuneable settings: model name, weights, experiment count |
| `dashboard.py` | Flask web server serving the live monitoring dashboard |
| `program.md` | Human-readable research goals and hard constraints for the Agent |
| `templates/index.html` | Full dashboard UI with tabs for Overview, Logs, and Hardware |
| `Start_All.bat` | **Windows only:** one-click launcher for both dashboard and research loop |

---

## ⚙️ How It Works: The Scoring Model

Each simulated session is scored on three axes:

| Metric | Weight | What It Measures |
|---|---|---|
| **PHQ-9 Delta** | 50% | Did the patient's depression severity improve? (-5 to +5) |
| **Engagement** | 25% | Did the patient open up authentically? (0–10) |
| **Alliance** | 25% | Did the patient feel heard and safe? (0–10) |

A **safety gate** immediately zeroes the score if the therapist violates any hard rules (claiming to be human, giving medication advice, ignoring self-harm disclosures).

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com) installed and running
- A capable local model (tested with `gemma4:latest`, also works with `llama3`, `mistral`)

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/recursive-mental-health-research.git
cd recursive-mental-health-research
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Pull your model in Ollama

```bash
ollama pull gemma4
# or: ollama pull llama3.2
```

### 4. Configure

Edit `config.py` to set your model name and preferences:

```python
MODEL_NAME = "gemma4:latest"   # Change to your installed model
MAX_EXPERIMENTS = 100          # Set to 0 for infinite
MAX_CONVERSATION_TURNS = 7     # Lower = faster, less rich sessions
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
In `config.py`, change the weights — they must always sum to `1.0`:
```python
WEIGHT_PHQ9_DELTA = 0.50   # Clinical improvement
WEIGHT_ENGAGEMENT = 0.25   # Patient openness
WEIGHT_ALLIANCE   = 0.25   # Therapeutic rapport
```

### Speed vs. quality
- Fewer `MAX_CONVERSATION_TURNS` = faster iterations, less realistic sessions
- Lower `TEMPERATURE_PATIENT` = more predictable patients, less variance in scores

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
exp_id    timestamp    strategy_name    hypothesis    score    phq9_delta    engagement    alliance    safety_viol
exp_0001  2026-04-05T19:20:16  Baseline CBT v1.0  Baseline...  6.0  2.5  9.5  9.5  0
```

Each experiment's full conversation transcript is saved to `experiments/exp_XXXX/data.json`.

The first 100-experiment run is included in this repo. See [`findings_report.md`](findings_report.md) for the full analysis.

---

## 🚂 Hardware Requirements

| Type | Minimum | Recommended |
|---|---|---|
| **GPU VRAM** | 6 GB | 12 GB+ |
| **RAM** | 16 GB | 32 GB |
| **Storage** | 10 GB free | 20 GB+ (for large experiment logs) |

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

*Inspired by [Andrej Karpathy's autoresearch pattern](https://x.com/karpathy). Built with Ollama, Flask, and curiosity about how AI can support human wellbeing.*

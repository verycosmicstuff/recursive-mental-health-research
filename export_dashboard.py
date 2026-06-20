"""
export_dashboard.py — Exports local experiment data to docs/ for GitHub Pages.

Usage:
    python export_dashboard.py

This reads results.tsv and experiments/*/data.json, then writes:
    docs/data/stats.json         — summary stats for the chart + table
    docs/data/transcripts/*.json — individual experiment transcripts
"""

import os
import json
import csv
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_FILE = os.path.join(BASE_DIR, "results.tsv")
EXPERIMENTS_DIR = os.path.join(BASE_DIR, "experiments")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
DOCS_DATA_DIR = os.path.join(DOCS_DIR, "data")
DOCS_TRANSCRIPTS_DIR = os.path.join(DOCS_DATA_DIR, "transcripts")

def safe_float(val, default=0.0):
    try:
        if val is None or val == "":
            return default
        return float(val)
    except (ValueError, TypeError):
        return default

def export():
    print("[Export] Starting dashboard export...")

    # Create output directories
    os.makedirs(DOCS_TRANSCRIPTS_DIR, exist_ok=True)

    # ── 0. Load old Run 1 data from backup (if it exists) ─────────────────────
    OLD_BACKUP_STATS = os.path.join(BASE_DIR, "docs_run1_backup", "data", "stats_original.json")
    old_experiments = []
    if os.path.exists(OLD_BACKUP_STATS):
        try:
            with open(OLD_BACKUP_STATS, "r", encoding="utf-8-sig") as f:
                old_data = json.load(f)
                for exp in old_data.get("experiments", []):
                    orig_id = exp.get("exp_id", "")
                    if orig_id and not orig_id.startswith("run1_"):
                        exp["exp_id"] = f"run1_{orig_id}"
                    exp["run"] = "Run 1 (gemma4 + llama3)"
                    old_experiments.append(exp)
            print(f"[Export] Loaded {len(old_experiments)} experiments from Run 1 backup")
        except Exception as e:
            print(f"[Export] Warning: Could not load Run 1 backup: {e}")

    # ── 1. Load Run 2 experiments from backup ───────────────────────────────────
    RUN2_RESULTS = os.path.join(BASE_DIR, "results_run2.tsv")
    run2_experiments = []
    if os.path.exists(RUN2_RESULTS):
        with open(RUN2_RESULTS, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                try:
                    score = safe_float(row.get("score", 0))
                    exp = {
                        "exp_id": row.get("exp_id", ""),
                        "strategy_name": row.get("strategy_name", "Unknown"),
                        "hypothesis": row.get("hypothesis", ""),
                        "score": score,
                        "empathic": safe_float(row.get("empathic", 0)),
                        "reflective": safe_float(row.get("reflective", 0)),
                        "de_escalation": safe_float(row.get("de_escalation", 0)),
                        "audit_mult": safe_float(row.get("audit_mult", 1.0), 1.0),
                        "audit_rationale": row.get("audit_rationale", ""),
                        "run": "Run 2 (gemma4:e4b — JSON mode)",
                    }
                    run2_experiments.append(exp)
                except (ValueError, KeyError) as e:
                    print(f"[Export] Skipping bad Run 2 row: {e}")
                    continue
        print(f"[Export] Loaded {len(run2_experiments)} experiments from Run 2 backup")

    # ── 2. Build Run 3 experiments from current results.tsv ───────────────────
    new_experiments = []
    best_score = 0

    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                try:
                    score = safe_float(row.get("score", 0))
                    exp = {
                        "exp_id": row.get("exp_id", ""),
                        "strategy_name": row.get("strategy_name", "Unknown"),
                        "hypothesis": row.get("hypothesis", ""),
                        "score": score,
                        "empathic": safe_float(row.get("empathic", 0)),
                        "reflective": safe_float(row.get("reflective", 0)),
                        "de_escalation": safe_float(row.get("de_escalation", 0)),
                        "audit_mult": safe_float(row.get("audit_mult", 1.0), 1.0),
                        "audit_rationale": row.get("audit_rationale", ""),
                        "run": "Run 3 (gemma4:e4b — Tier 5)",
                    }
                    new_experiments.append(exp)
                    if score > best_score:
                        best_score = score
                except (ValueError, KeyError) as e:
                    print(f"[Export] Skipping bad row: {e}")
                    continue

    # Merge: old Run 1 + Run 2 + new Run 3
    all_experiments = old_experiments + run2_experiments + new_experiments
    # Update best_score across all runs
    for exp in old_experiments + run2_experiments:
        if exp.get("score", 0) > best_score:
            best_score = exp["score"]

    import config
    stats = {
        "experiments": all_experiments,
        "best_score": best_score,
        "agent_model": config.MODEL_NAME,
        "evaluator_model": config.EVALUATOR_MODEL_NAME
    }

    stats_path = os.path.join(DOCS_DATA_DIR, "stats.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print(f"[Export] Wrote {len(all_experiments)} experiments to stats.json ({len(old_experiments)} Run 1 + {len(run2_experiments)} Run 2 + {len(new_experiments)} Run 3)")

    # ── 2. Copy individual transcript JSONs ───────────────────────────────────
    transcript_count = 0
    # First copy Run 1 transcripts from backup with "run1_" prefix
    BACKUP_TRANSCRIPTS_DIR = os.path.join(BASE_DIR, "docs_run1_backup", "data", "transcripts")
    if os.path.exists(BACKUP_TRANSCRIPTS_DIR):
        for filename in sorted(os.listdir(BACKUP_TRANSCRIPTS_DIR)):
            if filename.endswith(".json"):
                src = os.path.join(BACKUP_TRANSCRIPTS_DIR, filename)
                dst = os.path.join(DOCS_TRANSCRIPTS_DIR, f"run1_{filename}")
                shutil.copy2(src, dst)
                transcript_count += 1

    # Then copy Run 2 transcripts from experiments directory
    if os.path.exists(EXPERIMENTS_DIR):
        for exp_dir in sorted(os.listdir(EXPERIMENTS_DIR)):
            src = os.path.join(EXPERIMENTS_DIR, exp_dir, "data.json")
            if os.path.exists(src):
                dst = os.path.join(DOCS_TRANSCRIPTS_DIR, f"{exp_dir}.json")
                shutil.copy2(src, dst)
                transcript_count += 1

    print(f"[Export] Copied {transcript_count} transcripts")
    print(f"[Export] Done! Static dashboard ready in: {DOCS_DIR}")
    print(f"[Export] Commit and push, then enable GitHub Pages from docs/ folder.")


if __name__ == "__main__":
    export()

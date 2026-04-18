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


def export():
    print("[Export] Starting dashboard export...")

    # Create output directories
    os.makedirs(DOCS_TRANSCRIPTS_DIR, exist_ok=True)

    # ── 1. Build stats.json from results.tsv ──────────────────────────────────
    experiments = []
    best_score = 0

    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                try:
                    score = float(row.get("score", 0))
                    exp = {
                        "exp_id": row.get("exp_id", ""),
                        "strategy_name": row.get("strategy_name", "Unknown"),
                        "hypothesis": row.get("hypothesis", ""),
                        "score": score,
                        "empathic": float(row.get("empathic", 0)),
                        "reflective": float(row.get("reflective", 0)),
                        "de_escalation": float(row.get("de_escalation", 0)),
                        "audit_mult": float(row.get("audit_mult", 1.0)),
                        "audit_rationale": row.get("audit_rationale", ""),
                    }
                    experiments.append(exp)
                    if score > best_score:
                        best_score = score
                except (ValueError, KeyError) as e:
                    print(f"[Export] Skipping bad row: {e}")
                    continue

    stats = {"experiments": experiments, "best_score": best_score}

    stats_path = os.path.join(DOCS_DATA_DIR, "stats.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print(f"[Export] Wrote {len(experiments)} experiments to stats.json")

    # ── 2. Copy individual transcript JSONs ───────────────────────────────────
    transcript_count = 0
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

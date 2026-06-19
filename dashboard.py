from flask import Flask, render_template, jsonify
import pandas as pd
import os
import json
import config
import psutil
import subprocess
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    """Returns data for the dashboard charts"""
    experiments = []
    best_score = 0.0

    # 1. Load Run 1 experiments from backup (if it exists)
    OLD_BACKUP_STATS = os.path.join(config.BASE_DIR, "docs_run1_backup", "data", "stats_original.json")
    if os.path.exists(OLD_BACKUP_STATS):
        try:
            with open(OLD_BACKUP_STATS, "r", encoding="utf-8-sig") as f:
                old_data = json.load(f)
                for exp in old_data.get("experiments", []):
                    orig_id = exp.get("exp_id", "")
                    if orig_id and not orig_id.startswith("run1_"):
                        exp["exp_id"] = f"run1_{orig_id}"
                    exp["run"] = "Run 1 (gemma4 + llama3)"
                    experiments.append(exp)
                    score = float(exp.get("score", 0))
                    if score > best_score:
                        best_score = score
        except Exception as e:
            print(f"Dashboard error loading Run 1 backup: {e}")

    # 2. Load Run 2 experiments from backup (results_run2.tsv)
    RUN2_RESULTS = os.path.join(config.BASE_DIR, "results_run2.tsv")
    if os.path.exists(RUN2_RESULTS):
        try:
            df = pd.read_csv(RUN2_RESULTS, sep='\t', encoding='utf-8')
            df = df.fillna("")
            for _, row in df.iterrows():
                score = float(row["score"])
                experiments.append({
                    "exp_id": row["exp_id"],
                    "strategy_name": row.get("strategy_name", "Unknown"),
                    "hypothesis": str(row.get("hypothesis", "")),
                    "score": score,
                    "empathic": float(row.get("empathic", 0)),
                    "reflective": float(row.get("reflective", 0)),
                    "de_escalation": float(row.get("de_escalation", 0)),
                    "audit_mult": float(row.get("audit_mult", 1.0)),
                    "audit_rationale": str(row.get("audit_rationale", "")),
                    "run": "Run 2 (gemma4:e4b — JSON mode)"
                })
                if score > best_score:
                    best_score = score
        except Exception as e:
            print(f"Dashboard error reading Run 2 backup: {e}")

    # 3. Load Run 3 experiments from current RESULTS_FILE
    if os.path.exists(config.RESULTS_FILE):
        try:
            df = pd.read_csv(config.RESULTS_FILE, sep='\t', encoding='utf-8')
            df = df.fillna("")
            for _, row in df.iterrows():
                score = float(row["score"])
                experiments.append({
                    "exp_id": row["exp_id"],
                    "strategy_name": row.get("strategy_name", "Unknown"),
                    "hypothesis": str(row.get("hypothesis", "")),
                    "score": score,
                    "empathic": float(row.get("empathic", 0)),
                    "reflective": float(row.get("reflective", 0)),
                    "de_escalation": float(row.get("de_escalation", 0)),
                    "audit_mult": float(row.get("audit_mult", 1.0)),
                    "audit_rationale": str(row.get("audit_rationale", "")),
                    "run": "Run 3 (gemma4:e4b — Tier 5)"
                })
                if score > best_score:
                    best_score = score
        except Exception as e:
            print(f"Dashboard error reading results: {e}")

    return jsonify({
        "experiments": experiments,
        "best_score": best_score
    })

@app.route('/api/logs')
def get_logs():
    log_path = os.path.join(config.BASE_DIR, "app.log")
    if not os.path.exists(log_path):
        return jsonify({"logs": "Waiting for logs..."})
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return jsonify({"logs": "".join(lines[-100:])})
    except Exception as e:
        return jsonify({"logs": f"Error reading logs: {e}"})

@app.route('/api/transcript/<exp_id>')
def get_transcript(exp_id):
    """Returns the raw experiment specific data.json for the transcript viewer."""
    try:
        if exp_id.startswith("run1_"):
            real_id = exp_id[5:]  # Strip "run1_"
            json_path = os.path.join(config.BASE_DIR, "docs_run1_backup", "data", "transcripts", f"{real_id}.json")
        else:
            exp_dir = os.path.join(config.EXPERIMENTS_DIR, exp_id)
            json_path = os.path.join(exp_dir, "data.json")

        if not os.path.exists(json_path):
            return jsonify({"error": f"Transcript not found for {exp_id}"}), 404
            
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/state')
def get_state():
    is_paused = os.path.exists(os.path.join(config.BASE_DIR, "PAUSED.txt"))
    return jsonify({
        "paused": is_paused,
        "agent_model": config.MODEL_NAME,
        "evaluator_model": config.EVALUATOR_MODEL_NAME
    })

@app.route('/api/toggle_pause', methods=['POST'])
def toggle_pause():
    pause_file = os.path.join(config.BASE_DIR, "PAUSED.txt")
    if os.path.exists(pause_file):
        os.remove(pause_file)
        return jsonify({"paused": False, "status": "Resumed"})
    else:
        with open(pause_file, 'w', encoding="utf-8") as f:
            f.write("Paused from dashboard")
        return jsonify({"paused": True, "status": "Paused"})


@app.route('/api/hardware')
def get_hardware():
    stats = {
        "cpu_load": psutil.cpu_percent(interval=None),
        "ram_load": psutil.virtual_memory().percent,
        "gpu_temp": 0,
        "gpu_load": 0,
        "gpu_vram_used": 0,
        "gpu_vram_total": 0
    }
    
    try:
        output = subprocess.check_output(
            ['nvidia-smi', '--query-gpu=temperature.gpu,utilization.gpu,memory.used,memory.total', '--format=csv,noheader,nounits'],
            encoding='utf-8'
        ).strip().split(', ')
        
        if len(output) >= 4:
            stats["gpu_temp"] = float(output[0])
            stats["gpu_load"] = float(output[1])
            stats["gpu_vram_used"] = float(output[2])
            stats["gpu_vram_total"] = float(output[3])
    except Exception as e:
        print(f"Error reading GPU stats: {e}")
        
    return jsonify(stats)

@app.route('/api/history')
def get_history():
    import difflib
    history_file = os.path.join(config.BASE_DIR, "prompt_history.jsonl")
    if not os.path.exists(history_file):
        return jsonify([])
        
    try:
        entries = []
        with open(history_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
                    
        parsed_commits = []
        previous_prompt = ""
        
        for idx, entry in enumerate(entries):
            current_prompt = entry.get("prompt", "")
            
            # Generate unified diff
            diff = list(difflib.unified_diff(
                previous_prompt.splitlines(),
                current_prompt.splitlines(),
                n=3,
                lineterm=""
            ))
            previous_prompt = current_prompt
            
            hunks = []
            current_hunk = None
            
            for line in diff:
                if line.startswith('@@'):
                    if current_hunk:
                        hunks.append(current_hunk)
                    current_hunk = {"header": line, "lines": []}
                elif current_hunk:
                    if line.startswith('+') and not line.startswith('+++'):
                        current_hunk["lines"].append({"type": "add", "content": line[1:]})
                    elif line.startswith('-') and not line.startswith('---'):
                        current_hunk["lines"].append({"type": "remove", "content": line[1:]})
                    elif not line.startswith('---') and not line.startswith('+++'):
                        current_hunk["lines"].append({"type": "context", "content": line[1:] if len(line) > 0 else ""})
                        
            if current_hunk:
                hunks.append(current_hunk)
                
            parsed_commits.append({
                "hash": entry.get("exp_id", "unknown"),
                "author": "LangGraph Optimizer",
                "date": entry.get("timestamp", ""),
                "message": f"{entry.get('strategy_name', '')}\n\nHypothesis: {entry.get('hypothesis', '')}",
                "hunks": hunks
            })
            
        # Reverse to show newest first, matching git log behavior
        return jsonify(parsed_commits[::-1])
    except Exception as e:
        print(f"Error reading Agent History: {e}")
        return jsonify([])

if __name__ == '__main__':
    # Run locally (secure mode)
    app.run(host='127.0.0.1', debug=True, port=5000)

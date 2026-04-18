from flask import Flask, render_template, jsonify
import pandas as pd
import os
import json
import config
import psutil
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    """Returns data for the dashboard charts"""
    if not os.path.exists(config.RESULTS_FILE):
        return jsonify({"experiments": []})
        
    try:
        df = pd.read_csv(config.RESULTS_FILE, sep='\t', encoding='utf-8')
        
        # Prepare data for chart
        data = []
        for _, row in df.iterrows():
            data.append({
                "exp_id": row["exp_id"],
                "strategy_name": row.get("strategy_name", "Unknown"),
                "hypothesis": str(row.get("hypothesis", "")),
                "score": float(row["score"]),
                "empathic": float(row.get("empathic", 0)),
                "reflective": float(row.get("reflective", 0)),
                "de_escalation": float(row.get("de_escalation", 0)),
                "audit_mult": float(row.get("audit_mult", 1.0)),
                "audit_rationale": str(row.get("audit_rationale", ""))
            })
            
        return jsonify({
            "experiments": data,
            "best_score": float(df["score"].max()) if not df.empty else 0
        })
    except Exception as e:
        print(f"Dashboard error reading results: {e}")
        return jsonify({"experiments": [], "error": str(e)})

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
        exp_dir = os.path.join(config.EXPERIMENTS_DIR, exp_id)
        json_path = os.path.join(exp_dir, "data.json")
        if not os.path.exists(json_path):
            return jsonify({"error": "Transcript not found"}), 404
            
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

if __name__ == '__main__':
    # Run locally (secure mode)
    app.run(host='127.0.0.1', debug=True, port=5000)

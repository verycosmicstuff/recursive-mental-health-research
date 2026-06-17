import time
import sys
import os
from importlib import reload
import config

# Setup logging to be visible in dashboard, with file rotation for long runs
class LoggerWriter:
    def __init__(self, filename, max_mb=5):
        self.terminal = sys.stdout
        self.filename = filename
        self.max_bytes = max_mb * 1024 * 1024
        self.log = open(self.filename, "a", encoding="utf-8")
        
    def write(self, message):
        try:
            self.terminal.write(message)
        except UnicodeEncodeError:
            self.terminal.write(message.encode("ascii", "replace").decode("ascii"))
            
        self.log.write(message)
        self.log.flush()
        
        # Check size and rotate if necessary (keeps only the latest 1 backup)
        if os.path.exists(self.filename) and os.path.getsize(self.filename) > self.max_bytes:
            self.log.close()
            backup = self.filename + ".old"
            if os.path.exists(backup):
                os.remove(backup)
            os.rename(self.filename, backup)
            self.log = open(self.filename, "a", encoding="utf-8")
            
    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = LoggerWriter(os.path.join(config.BASE_DIR, "app.log"))
sys.stderr = sys.stdout

import harness
import agent
import shutil
import therapist # imported to be able to reload
import session_config
import patient_archetypes
import sync

import orchestrator_graph

def main():
    print("=====================================================")
    print("MENTAL HEALTH RESEARCH LOOP STARTING")
    print(f"Model: {config.MODEL_NAME}")
    print(f"Base URL: {config.OLLAMA_BASE_URL}")
    print("=====================================================\n")
    
    current_best_score = -999.0
    iteration = 1
    
    if os.path.exists(config.RESULTS_FILE):
        with open(config.RESULTS_FILE, 'r', encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
            if len(lines) > 1:
                max_id = 0
                scores = []
                for l in lines[1:]:
                    try:
                        parts = l.split('\t')
                        if len(parts) > 4:
                            # Tracking max ID
                            id_num = int(parts[0].split('_')[1])
                            if id_num > max_id:
                                max_id = id_num
                            # Tracking best score
                            scores.append(float(parts[4]))
                    except: continue
                
                iteration = max_id + 1
                if scores:
                    current_best_score = max(scores)
                print(f"[Main] Resumed! Starting at iteration {iteration}. Best score so far: {current_best_score}")
    
    print("[Main] Initializing LangGraph Orchestrator...")
    graph = orchestrator_graph.build_graph()
    
    initial_state = {
        "messages": [],
        "persona": {},
        "strategy_info": {},
        "active_prompt": "", # Will fall back to baseline therapist prompt
        "score": None,
        "iteration": iteration,
        "baseline_score": current_best_score,
        "exp_id": ""
    }
    
    # Let LangGraph handle the loop via its optimizer routing
    for event in graph.stream(initial_state, {"recursion_limit": 1000}): # Give it plenty of recursions
        pass # Nodes handle their own logging

if __name__ == "__main__":
    import os
    main()

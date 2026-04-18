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
            self.terminal.write(message.encode("utf-8", "replace").decode("utf-8"))
            
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

def update_best_strategy(score: float, exp_id: str):
    """Saves the current top performing strategy."""
    print(f"\n NEW BEST STRATEGY FOUND! Score: {score}")
    shutil.copy2(config.THERAPIST_FILE, config.BEST_STRATEGY_FILE)
    shutil.copy2(config.SESSION_CONFIG_FILE, config.BEST_SESSION_CONFIG_FILE)
    shutil.copy2(config.PATIENT_ARCHETYPES_FILE, config.BEST_ARCHETYPES_FILE)
    
    # Append to markdown file to make it easily readable
    with open(config.BEST_STRATEGY_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n\n# --- RECORDED AT EXPERIMENT: {exp_id} ---\n")
        f.write(f"# --- SCORE: {score} ---\n")
    
    # Sync "New Best" immediately
    sync.sync(f"New Best Strategy: {exp_id} (Score: {score:.3f})")

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
    
    # Optional Backup of the baseline strategy so we can revert if agent goes crazy
    shutil.copy2(config.THERAPIST_FILE, config.THERAPIST_FILE + ".backup")
    shutil.copy2(config.SESSION_CONFIG_FILE, config.SESSION_CONFIG_FILE + ".backup")
    shutil.copy2(config.PATIENT_ARCHETYPES_FILE, config.PATIENT_ARCHETYPES_FILE + ".backup")
    
    while True:
        paused_logged = False
        while os.path.exists(os.path.join(config.BASE_DIR, "PAUSED.txt")):
            if not paused_logged:
                print("[Main] Paused. Waiting for manual resume via dashboard...")
                paused_logged = True
            time.sleep(2)
            
        if config.MAX_EXPERIMENTS > 0 and iteration > config.MAX_EXPERIMENTS:
             print(f"\n[Main] Reached max experiments ({config.MAX_EXPERIMENTS}). Stopping.")
             break
             
        exp_id = f"exp_{iteration:04d}"
        
        # 1. Run the simulation and score it
        try:
            # Important: reload modules so it picks up code changes made by agent in prior loops
            reload(config)
            reload(therapist)
            reload(session_config)
            reload(patient_archetypes)
            
            scores = harness.run_experiment(exp_id)
            total_score = scores["total_score"]
            
            # 2. Check if it's the new best
            if total_score > current_best_score:
                current_best_score = total_score
                update_best_strategy(total_score, exp_id)
                # Keep the current strategy!
            else:
                print(f"[Main] Score {total_score} did not beat {current_best_score}. Reverting to previous best.")
                # We revert because we only want to compound ON TOP of successes
                if os.path.exists(config.BEST_STRATEGY_FILE):
                     shutil.copy2(config.BEST_STRATEGY_FILE, config.THERAPIST_FILE)
                     shutil.copy2(config.BEST_SESSION_CONFIG_FILE, config.SESSION_CONFIG_FILE)
                     shutil.copy2(config.BEST_ARCHETYPES_FILE, config.PATIENT_ARCHETYPES_FILE)
                else: 
                     # if we never had a best, revert to backup
                     shutil.copy2(config.THERAPIST_FILE + ".backup", config.THERAPIST_FILE)
                     shutil.copy2(config.SESSION_CONFIG_FILE + ".backup", config.SESSION_CONFIG_FILE)
                     shutil.copy2(config.PATIENT_ARCHETYPES_FILE + ".backup", config.PATIENT_ARCHETYPES_FILE)
                     
            
            # 3. Pause
            print(f"Sleeping {config.EXPERIMENT_PAUSE_SECS} secs...")
            time.sleep(config.EXPERIMENT_PAUSE_SECS)
            
            # 4. Agent proposes next modification
            success = agent.propose_next_experiment(current_best_score)
            if not success:
               print("[Main] Agent failed to propose. We will try again next loop.")
            
            # 5. Heartbeat Sync to GitHub
            sync.sync(f"Experiment Complete: {exp_id} (Score: {total_score:.3f})")
            
        except Exception as e:
            print(f"\n[Main] CRITICAL ERROR IN LOOP: {e}")
            print("Trying to recover next iteration...")
            time.sleep(5)
            
        iteration += 1

if __name__ == "__main__":
    import os
    main()

import subprocess
import os
import export_dashboard

def sync(message="Automated research update"):
    """
    1. Runs export_dashboard.py to refresh docs/data/
    2. Runs git commands to push to GitHub
    """
    print(f"\n[Sync] 🔄 Starting GitHub sync: {message}")
    
    try:
        # 1. Run the local export script logic
        export_dashboard.export()
        
        # 2. Stage changes
        # We target everything so we catch docs/, results.tsv, and best_strategy.md
        subprocess.run(["git", "add", "docs/", "results.tsv", "best_strategy.md"], check=True)
        
        # 3. Check for changes
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not status.stdout.strip():
            print("[Sync] ✅ No changes to push.")
            return

        # 4. Commit and Push
        subprocess.run(["git", "commit", "-m", message], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("[Sync] 🚀 Successfully pushed to GitHub Pages.")
        
    except Exception as e:
        print(f"[Sync] ❌ Error during sync: {e}")

if __name__ == "__main__":
    sync()

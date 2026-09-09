import json
import os
from datetime import datetime

HISTORY_FILE = 'data/history.json'

def log_posture_event(status):
    """
    Logs posture events with timestamps to history.json
    """
    os.makedirs('data', exist_ok=True)
    
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status
    }
    
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        except json.JSONDecodeError:
            history = []
            
    history.append(entry)
    
    # Keep only the last 100 events to prevent file bloat
    if len(history) > 100:
        history = history[-100:]
        
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

def get_session_summary():
    """
    Reads history and returns summary counts.
    """
    if not os.path.exists(HISTORY_FILE):
        return {"Good": 0, "Bad": 0}
        
    try:
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
            
        good_count = sum(1 for item in history if "Good" in item["status"])
        bad_count = sum(1 for item in history if "Bad" in item["status"])
        return {"Good": good_count, "Bad": bad_count}
    except Exception:
        return {"Good": 0, "Bad": 0}

if __name__ == "__main__":
    print("Testing decision module logger...")
    log_posture_event("Test Good Posture")
    print("Summary:", get_session_summary())
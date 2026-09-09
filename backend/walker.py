import time
import threading
import voice

def movement_reminder_loop(interval_minutes=30):
    """
    Background worker that reminds the user to take a walking break 
    at regular intervals to prevent physical fatigue and bad posture.
    """
    interval_seconds = interval_minutes * 60
    print(f"Movement tracker active. Reminder set every {interval_minutes} minutes.")
    
    while True:
        time.sleep(interval_seconds)
        voice.speak_alert("Time for a short walking break. Stand up and stretch!")
        print("Break reminder triggered.")

def start_walker_background():
    """
    Starts the movement reminder in a non-blocking background thread.
    """
    t = threading.Thread(target=movement_reminder_loop, args=(30,), daemon=True)
    t.start()

if __name__ == "__main__":
    print("Testing walker module (shortened to 10 seconds for demo)...")
    # Quick test with 10 seconds instead of 30 minutes
    def test_loop():
        time.sleep(10)
        voice.speak_alert("Test walk reminder: time to move around.")
    
    threading.Thread(target=test_loop, daemon=True).start()
    time.sleep(12)
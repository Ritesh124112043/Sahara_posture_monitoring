import pyttsx3
import threading

def speak_alert(message):
    """
    Function to speak out alerts in a separate thread 
    so it doesn't freeze the camera feed.
    """
    def _speak_thread(msg):
        local_engine = pyttsx3.init()
        local_engine.setProperty('rate', 150)
        local_engine.setProperty('volume', 1.0)
        local_engine.say(msg)
        local_engine.runAndWait()
        
    threading.Thread(target=_speak_thread, args=(message,), daemon=True).start()

if __name__ == "__main__":
    print("Testing voice module...")
    speak_alert("Voice system is online.")
    import time
    time.sleep(2)
import cv2
import mediapipe as mp
import math
import json
import os
import time
import database
import voice 
import decision

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

def calculate_angle(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.degrees(math.atan2(y2 - y1, x2 - x1))

def monitor_posture():
    if not os.path.exists('data/calibration.json'):
        voice.speak_alert("Calibration data missing.")
        return

    with open('data/calibration.json', 'r') as f:
        baseline = json.load(f)["baseline_angle"]

    voice.speak_alert("Monitoring activated.")

    current_user_id = database.get_or_create_user()
    cap = cv2.VideoCapture(0)
    
    last_alert_time = 0  
    alert_cooldown = 5.0  
    current_state = None  

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: 
                break

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)
            image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                mp_drawing.draw_landmarks(image_bgr, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                landmarks = results.pose_landmarks.landmark
                
                ear_pt = (int(landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].x * w), int(landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].y * h))
                shoulder_pt = (int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * w), int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * h))
                
                current_angle = calculate_angle(ear_pt, shoulder_pt)
                
                if (baseline - current_angle) > 8:  
                    status = "Bad Posture (Slouching!)"
                    color = (0, 0, 255) 
                    
                    if (time.time() - last_alert_time) > alert_cooldown:
                        voice.speak_alert("Please sit straight.")
                        last_alert_time = time.time()
                else:
                    status = "Good Posture"
                    color = (0, 255, 0) 

                if status != current_state:
                    decision.log_posture_event(status)

                    # Push LIVE data to Supabase (only on state change to prevent spamming)
                    try:
                        database.log_live_posture(
                            user_id=current_user_id, 
                            status=status, 
                            neck_angle=current_angle, 
                            back_curvature=0.0
                        )
                    except Exception as e:
                        print(f"Supabase Log Error: {e}")
                        
                    current_state = status

                cv2.putText(image_bgr, status, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

            cv2.imshow('Sahara - Live Tracker', image_bgr)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    monitor_posture()
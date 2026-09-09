import cv2
import mediapipe as mp
import math
import json
import os
import time

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

def calculate_angle(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.degrees(math.atan2(y2 - y1, x2 - x1))

def calibrate():
    """
    Function to calculate and save the user's baseline posture angle.
    """
    os.makedirs('data', exist_ok=True)
    cap = cv2.VideoCapture(0)
    
    angles = []
    print("Sit straight! Calibration starting in 3 seconds...")
    time.sleep(2)

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        start_time = time.time()
        # Collect baseline data for 5 seconds
        while time.time() - start_time < 5:
            ret, frame = cap.read()
            if not ret: break

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)
            image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                ear_pt = (int(landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].x * w), 
                          int(landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].y * h))
                shoulder_pt = (int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * w), 
                               int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * h))
                
                angle = calculate_angle(ear_pt, shoulder_pt)
                angles.append(angle)

                cv2.putText(image_bgr, "Calibrating... Sit Straight!", (20, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            cv2.imshow('Sahara - Calibration', image_bgr)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

    if angles:
        baseline_angle = sum(angles) / len(angles)
        data = {"baseline_angle": baseline_angle}
        with open('data/calibration.json', 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Calibration successful! Baseline saved: {baseline_angle:.2f}")
    else:
        print("Calibration failed: No pose detected. Try again.")

if __name__ == "__main__":
    calibrate()
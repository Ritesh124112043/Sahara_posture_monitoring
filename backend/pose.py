import cv2
import mediapipe as mp
import math

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Naya math function angle nikalne ke liye
def calculate_angle(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
    return angle

def process_pose():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as pose:
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape  # Frame ki height aur width

            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False

            results = pose.process(image_rgb)

            image_rgb.flags.writeable = True
            image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                # 1. Skeleton draw karo
                mp_drawing.draw_landmarks(
                    image_bgr,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
                )

                # 2. Coordinates nikalo
                landmarks = results.pose_landmarks.landmark
                
                # Left Ear aur Left Shoulder ke points
                left_ear = landmarks[mp_pose.PoseLandmark.LEFT_EAR.value]
                left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                
                # Unhe actual screen pixels mein convert karo
                ear_pt = (int(left_ear.x * w), int(left_ear.y * h))
                shoulder_pt = (int(left_shoulder.x * w), int(left_shoulder.y * h))
                
                # 3. Angle calculate karo
                neck_angle = calculate_angle(ear_pt, shoulder_pt)
                
                # 4. Posture condition check karo
                if neck_angle < 75:  # Agar zyada aage jhuke
                    status = "Bad Posture!"
                    color = (0, 0, 255)  # Red text
                else:
                    status = "Good Posture"
                    color = (0, 255, 0)  # Green text

                # Screen par display karo
                cv2.putText(image_bgr, status, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
                cv2.putText(image_bgr, f"Angle: {int(neck_angle)}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            cv2.imshow('Sahara - Posture Analysis', image_bgr)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    process_pose()
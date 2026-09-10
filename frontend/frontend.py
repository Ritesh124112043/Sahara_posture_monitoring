"""
Sahara — Intelligent Real-Time Posture Monitoring System
Frontend Dashboard (Streamlit)
"""
# streamlit run frontend/frontend.py
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
import av
from streamlit_webrtc import webrtc_streamer, WebRtcMode,RTCConfiguration
import cv2
import mediapipe as mp
import numpy as np
import math


# --------------------------------------------------------------------------
# PATH CONFIGURATION
# --------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
BACKEND_DIR = BASE_DIR / "backend"

CALIBRATION_FILE = DATA_DIR / "calibration.json"
HISTORY_FILE = DATA_DIR / "history.json"

MAIN_SCRIPT = BASE_DIR / "main.py"
POSTURE_SCRIPT = BACKEND_DIR / "posture.py"
CALIBRATION_SCRIPT = BACKEND_DIR / "calibration.py"

BAD_POSTURE_KEYWORDS = ("bad", "slouch")
GOOD_POSTURE_KEYWORDS = ("good",)


# --------------------------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Sahara | Posture Monitor",
    page_icon="🧘",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------------------------------
# FIX: CUSTOM CSS — Only keeping the Status Pills, removed breaking background colors
# --------------------------------------------------------------------------
st.markdown(
    """
    <style>
        /* Status pills */
        .pill {
            display: inline-block;
            padding: 4px 14px;
            border-radius: 999px;
            font-weight: 600;
            font-size: 0.85rem;
        }
        .pill-good { background-color: #d1fae5; color: #065f46; }
        .pill-bad  { background-color: #fee2e2; color: #991b1b; }
        .pill-warn { background-color: #fef3c7; color: #92400e; }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------
# SAFE DATA LOADERS
# --------------------------------------------------------------------------
def load_calibration() -> dict | None:
    try:
        if not CALIBRATION_FILE.exists():
            return None
        content = CALIBRATION_FILE.read_text(encoding="utf-8").strip()
        if not content:
            return None
        data = json.loads(content)
        if "baseline_angle" not in data:
            return None
        return data
    except (json.JSONDecodeError, OSError) as e:
        st.sidebar.error(f"⚠️ Could not read calibration.json: {e}")
        return None


def load_history() -> pd.DataFrame:
    empty_df = pd.DataFrame(columns=["timestamp", "status"])

    try:
        if not HISTORY_FILE.exists():
            return empty_df

        content = HISTORY_FILE.read_text(encoding="utf-8").strip()
        if not content:
            return empty_df

        records = json.loads(content)
        if not isinstance(records, list) or len(records) == 0:
            return empty_df

        df = pd.DataFrame(records)

        if "timestamp" not in df.columns or "status" not in df.columns:
            return empty_df

        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"]).sort_values("timestamp", ascending=False)
        return df.reset_index(drop=True)

    except (json.JSONDecodeError, OSError) as e:
        st.sidebar.error(f"⚠️ Could not read history.json: {e}")
        return empty_df


def classify_status(status: str) -> str:
    s = str(status).lower()
    if any(k in s for k in BAD_POSTURE_KEYWORDS):
        return "bad"
    if any(k in s for k in GOOD_POSTURE_KEYWORDS):
        return "good"
    return "other"


# --------------------------------------------------------------------------
# SIDEBAR — NAVIGATION & QUICK STATUS
# --------------------------------------------------------------------------
st.sidebar.title("🧘 Sahara")
st.sidebar.caption("Real-time posture monitoring")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigate",
    options=["📊 Dashboard Overview", "📈 Analytics & History", "⚙️ System Settings & Controls"],
    label_visibility="collapsed",
)

st.sidebar.divider()

_calib_preview = load_calibration()
if _calib_preview:
    st.sidebar.success(f"Calibrated ✓ ({_calib_preview['baseline_angle']:.2f}°)")
else:
    st.sidebar.warning("Not calibrated yet")

st.sidebar.caption(f"Project root:\n`{BASE_DIR}`")


# --------------------------------------------------------------------------
# PAGE: DASHBOARD OVERVIEW
# --------------------------------------------------------------------------
def render_dashboard_overview():
    st.title("📊 Dashboard Overview")
    st.caption("A live snapshot of your posture health, powered by Sahara.")

    history_df = load_history()
    calibration = load_calibration()

    total_events = len(history_df)

    if total_events > 0:
        buckets = history_df["status"].apply(classify_status)
        good_count = int((buckets == "good").sum())
        bad_count = int((buckets == "bad").sum())
        other_count = total_events - good_count - bad_count
        good_rate = (good_count / total_events) * 100
    else:
        good_count = bad_count = other_count = 0
        good_rate = 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Events Logged", f"{total_events}")
    col2.metric("✅ Good Posture", f"{good_count}")
    col3.metric("🔴 Bad Posture / Slouching", f"{bad_count}")
    col4.metric("Good Posture Rate", f"{good_rate:.1f}%")

    st.write("") 

    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown("#### 🎯 Calibration Status")
        with st.container():
            if calibration:
                st.markdown(
                    '<span class="pill pill-good">Calibration file found</span>',
                    unsafe_allow_html=True,
                )
                st.metric("Baseline (Target) Angle", f"{calibration['baseline_angle']:.2f}°")
                st.caption(f"Source: `{CALIBRATION_FILE}`")
            else:
                st.markdown(
                    '<span class="pill pill-bad">No calibration data found</span>',
                    unsafe_allow_html=True,
                )
                st.write(
                    "Sahara hasn't been calibrated yet. Run the calibration "
                    "script before starting posture monitoring so the system "
                    "knows what *your* good posture looks like."
                )

    with col_b:
        st.markdown("#### 🕒 Most Recent Reading")
        with st.container():
            if total_events > 0:
                latest = history_df.iloc[0]
                status_class = classify_status(latest["status"])
                pill_css = {"good": "pill-good", "bad": "pill-bad", "other": "pill-warn"}[status_class]
                st.markdown(
                    f'<span class="pill {pill_css}">{latest["status"]}</span>',
                    unsafe_allow_html=True,
                )
                st.write(f"**Logged at:** {latest['timestamp']}")
            else:
                st.info("No posture events logged yet. Start the monitor to begin tracking.")

    st.write("")

    st.markdown("#### 📉 Recent Posture Trend")
    if total_events > 0:
        chart_df = history_df.head(50).copy()
        chart_df["bucket"] = chart_df["status"].apply(classify_status)
        chart_df["value"] = chart_df["bucket"].map({"good": 1, "bad": 0, "other": 0.5})
        chart_df = chart_df.sort_values("timestamp")
        chart_df = chart_df.set_index("timestamp")[["value"]].rename(
            columns={"value": "Posture (1=Good, 0=Bad)"}
        )
        st.line_chart(chart_df)
    else:
        st.caption("Trend chart will appear here once posture data is available.")


# --------------------------------------------------------------------------
# PAGE: ANALYTICS & HISTORY
# --------------------------------------------------------------------------
def render_analytics_history():
    st.title("📈 Analytics & History")
    st.caption("Detailed log of every posture event Sahara has recorded.")

    history_df = load_history()

    if history_df.empty:
        st.info(
            "No history data found yet (`data/history.json` is missing or empty). "
            "Run the posture monitor to start generating logs."
        )
        return

    with st.container():
        f_col1, f_col2 = st.columns([1, 2])

        with f_col1:
            status_filter = st.multiselect(
                "Filter by status type",
                options=["good", "bad", "other"],
                default=["good", "bad", "other"],
                format_func=lambda x: {"good": "✅ Good", "bad": "🔴 Bad/Slouching", "other": "⚪ Other"}[x],
            )

        with f_col2:
            search_term = st.text_input("Search status text (optional)", placeholder="e.g. slouch")

    filtered_df = history_df.copy()
    filtered_df["bucket"] = filtered_df["status"].apply(classify_status)
    filtered_df = filtered_df[filtered_df["bucket"].isin(status_filter)]

    if search_term:
        filtered_df = filtered_df[
            filtered_df["status"].str.contains(search_term, case=False, na=False)
        ]

    st.write(f"Showing **{len(filtered_df)}** of **{len(history_df)}** total events")

    display_df = filtered_df[["timestamp", "status"]].rename(
        columns={"timestamp": "Timestamp", "status": "Status"}
    )
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("#### 📅 Daily Breakdown")
    daily_df = filtered_df.copy()
    daily_df["date"] = daily_df["timestamp"].dt.date
    daily_summary = (
        daily_df.groupby(["date", "bucket"]).size().unstack(fill_value=0)
    )
    for col in ["good", "bad", "other"]:
        if col not in daily_summary.columns:
            daily_summary[col] = 0
    daily_summary = daily_summary.rename(
        columns={"good": "Good Posture", "bad": "Bad Posture", "other": "Other"}
    )
    st.bar_chart(daily_summary[["Good Posture", "Bad Posture", "Other"]])

    csv_data = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download filtered history as CSV",
        data=csv_data,
        file_name=f"sahara_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )


# --------------------------------------------------------------------------
# PAGE: SYSTEM SETTINGS & CONTROLS
# --------------------------------------------------------------------------
def render_settings_controls():
    st.title("⚙️ System Settings & Controls")
    st.caption(
        "Sahara's camera + MediaPipe monitoring loop is a long-running, "
        "OpenCV-driven process — it opens its own display window and runs "
        "independently of Streamlit. Launch it from a terminal using the "
        "commands below, or use the quick-launch buttons (Windows only)."
    )

    st.divider()

    st.markdown("### 1️⃣ Calibrate Your Baseline Posture")
    with st.container():
        st.write(
            "Run this once (or whenever your seating setup changes) to record "
            "your personal baseline neck/shoulder angle into "
            f"`{CALIBRATION_FILE.relative_to(BASE_DIR)}`."
        )
        st.code(f"cd {BASE_DIR}\npython backend\\calibration.py", language="bash")

        cal_col1, cal_col2 = st.columns([1, 3])
        with cal_col1:
            if st.button("🚀 Launch Calibration", use_container_width=True):
                launch_backend_script(CALIBRATION_SCRIPT, "Calibration")
        with cal_col2:
            st.caption(
                "Opens a camera window. Sit up straight, hold still, and "
                "follow the on-screen prompts until it saves and closes."
            )

    st.write("")

    st.markdown("### 2️⃣ Start Real-Time Posture Monitoring")
    with st.container():
        st.write(
            "This launches the OpenCV + MediaPipe camera loop that watches "
            "your posture live, plays voice alerts on slouching, and logs "
            f"every event to `{HISTORY_FILE.relative_to(BASE_DIR)}`."
        )
        st.code(f"cd {BASE_DIR}\npython backend\\posture.py", language="bash")
        st.caption("Alternatively, if `main.py` orchestrates everything (calibration check + posture + walker):")
        st.code(f"cd {BASE_DIR}\npython main.py", language="bash")



        # Initialize MediaPipe Pose
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        mp_drawing = mp.solutions.drawing_utils

        def calculate_angle(a, b, c):
            """Calculates the angle between three points (e.g., ear/nose, shoulder, hip)"""
            a = np.array(a) # First point
            b = np.array(b) # Mid point (Vertex)
            c = np.array(c) # End point
            
            radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
            angle = np.abs(radians * 180.0 / np.pi)
            
            if angle > 180.0:
                angle = 360.0 - angle
                
            return angle

        def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
            img = frame.to_ndarray(format="bgr24")
            
            # 1. Mirror fix taaki right hand right side dikhe
            img = cv2.flip(img, 1)
            h, w, _ = img.shape
            
            # 2. Convert to RGB for MediaPipe processing
            image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)
            
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                
                # Get coordinates for posture analysis (e.g., Shoulder and Ear/Hip reference)
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * w,
                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * h]
                ear = [landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].x * w,
                    landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].y * h]
                hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x * w,
                    landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y * h]
                
                # Calculate angle
                angle = calculate_angle(ear, shoulder, hip)
                
                # Draw pose landmarks
                mp_drawing.draw_landmarks(
                    img, 
                    results.pose_landmarks, 
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
                )
                
                # Status logic based on angle
                status = "Good Posture"
                color = (0, 255, 0)
                if angle < 50:  # Threshold example
                    status = "Slouching Detected!"
                    color = (0, 0, 255)
                    
                cv2.putText(img, f"Angle: {int(angle)} | {status}", (20, 40), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            else:
                cv2.putText(img, "Align in Camera View", (20, 40), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
                
            return av.VideoFrame.from_ndarray(img, format="bgr24")

        webrtc_streamer(
            key="posture-camera",
            mode=WebRtcMode.SENDRECV,
            video_frame_callback=video_frame_callback,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,

            rtc_configuration=RTCConfiguration(
                {"iceServers": [
                    {"urls": ["stun:stun.l.google.com:19302", "stun:stun1.l.google.com:19302"]}
                ]}
            )
        )
        

    st.write("")

    st.markdown("### 3️⃣ Background Walking Break Reminders")
    with st.container():
        st.write(
            "`backend/walker.py` runs as a background thread that nudges you "
            "to take a short walking break at regular intervals. This is "
            "typically started automatically from `main.py` alongside the "
            "posture monitor, rather than run standalone."
        )
        st.code(f"cd {BASE_DIR}\npython main.py", language="bash")

    st.divider()

    st.markdown("### 🗂️ Data File Status")
    d_col1, d_col2 = st.columns(2)

    with d_col1:
        st.write("**calibration.json**")
        if CALIBRATION_FILE.exists():
            st.success(f"Found — {CALIBRATION_FILE.stat().st_size} bytes")
        else:
            st.error("Not found")

    with d_col2:
        st.write("**history.json**")
        if HISTORY_FILE.exists():
            st.success(f"Found — {HISTORY_FILE.stat().st_size} bytes")
        else:
            st.error("Not found")

def launch_backend_script(script_path: Path, friendly_name: str):
    if not script_path.exists():
        st.error(f"❌ Could not find `{script_path}`. Check your project structure.")
        return
    try:
        subprocess.Popen([sys.executable, str(script_path)], cwd=str(BASE_DIR))
        st.success(f"✅ {friendly_name} launched in a new process. Check for the camera window.")
    except Exception as e:
        st.error(f"❌ Failed to launch {friendly_name}: {e}")


# --------------------------------------------------------------------------
# ROUTER
# --------------------------------------------------------------------------
if page == "📊 Dashboard Overview":
    render_dashboard_overview()
elif page == "📈 Analytics & History":
    render_analytics_history()
elif page == "⚙️ System Settings & Controls":
    render_settings_controls()

st.divider()
st.caption("Sahara Posture Monitor · Built with Streamlit, OpenCV & MediaPipe")
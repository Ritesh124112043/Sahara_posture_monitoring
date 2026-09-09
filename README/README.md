# 🧘 Sahara: Intelligent Posture Monitoring System

Sahara is a real-time posture tracking and ergonomic monitoring system built with Python. It uses computer vision to analyze your seating posture, provides offline voice alerts when you slouch, and logs your daily ergonomic habits into an interactive web dashboard.

## ✨ Features
* **Real-Time Pose Tracking:** Uses OpenCV and MediaPipe to track shoulder and neck alignment.
* **Custom Calibration:** Sets a personalized baseline posture angle for accurate monitoring.
* **Voice Alerts:** Integrated offline text-to-speech (`pyttsx3`) reminds you to sit up straight without spamming.
* **Smart Dashboard:** A Streamlit web interface to view live metrics, daily posture rates, and session history.
* **Background Walker:** A background thread that prompts you to take walking breaks at regular intervals.

## 🛠️ Tech Stack
* **Core:** Python 3.11
* **Computer Vision:** OpenCV, MediaPipe
* **Interface:** Streamlit, Pandas
* **Audio:** pyttsx3, sounddevice
* **Data Storage:** Local JSON (No cloud dependency)

## 🚀 Installation & Setup

1. **Clone the repository and enter the directory:**
   ```bash
   git clone [https://github.com/your-username/sahara.git](https://github.com/your-username/sahara.git)
   cd sahara
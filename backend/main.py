import sys
import os

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import calibration
import posture

def main():
    print("==============================")
    print("   SAHARA POSTURE MONITOR     ")
    print("==============================")
    print("1. Run Calibration (New Baseline)")
    print("2. Start Live Posture Monitor")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        print("\nStarting Calibration... Sit straight!")
        calibration.calibrate()
    elif choice == "2":
        print("\nStarting Live Monitoring...")
        posture.monitor_posture()
    elif choice == "3":
        print("\nExiting Sahara. Stay healthy!")
        sys.exit(0)
    else:
        print("Invalid choice! Please run again and select 1, 2, or 3.")

if __name__ == "__main__":
    main()
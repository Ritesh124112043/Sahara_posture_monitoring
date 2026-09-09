import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load keys securely from .env file
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ... (get_or_create_user aur log_live_posture same rahenge)

def get_or_create_user(username: str = "sahara_admin", email: str = "admin@sahara.local") -> str:
    """
    Checks if the user exists to prevent duplicates. 
    Returns the user UUID to be used in live tracking.
    """
    try:
        # 1. Pehle check karo agar user already exist karta hai
        existing_user = supabase.table('users').select('id').eq('email', email).execute()
        if existing_user.data:
            return existing_user.data[0]['id']
        
        # 2. Agar nahi hai, toh naya create karo
        new_user = supabase.table('users').insert({
            "username": username,
            "email": email
        }).execute()
        return new_user.data[0]['id']
        
    except Exception as e:
        print(f"⚠️ Error initializing Supabase user: {e}")
        return None

def log_live_posture(user_id: str, status: str, neck_angle: float, back_curvature: float = 0.0):
    """
    Pushes real-time camera data (angles, status) to Supabase.
    """
    if not user_id:
        return # Skip logging if database connection failed
        
    try:
        log_data = {
            "user_id": user_id,
            "posture_status": status,
            "neck_angle": round(neck_angle, 2),
            "back_curvature": round(back_curvature, 2)
        }
        supabase.table('posture_logs').insert(log_data).execute()
        print(f"☁️ Supabase Logged: {status} (Angle: {neck_angle:.1f}°)")
    except Exception as e:
        print(f"⚠️ Failed to push live data to Supabase: {e}")
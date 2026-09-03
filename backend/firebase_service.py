import os
import json
import base64
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone
from datetime import timedelta

# Initialize Firebase credentials securely
env_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

if env_account_json:
    try:
        # Try raw JSON string first
        account_info = json.loads(env_account_json)
    except Exception:
        # Fallback to base64 decoding if encoded
        decoded_json = base64.b64decode(env_account_json).decode("utf-8")
        account_info = json.loads(decoded_json)
    cred = credentials.Certificate(account_info)
elif os.path.exists("serviceAccountKey.json"):
    cred = credentials.Certificate("serviceAccountKey.json")
elif os.path.exists(os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")):
    cred = credentials.Certificate(os.path.join(os.path.dirname(__file__), "serviceAccountKey.json"))
else:
    cred = credentials.ApplicationDefault()

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

def _user_ref(user_id: str):
    """Return the base Firestore reference scoped to a specific user."""
    return db.collection("users").document(user_id)

def update_current_status(payload: dict, user_id: str):
    try:
        # Logging sensor data under user's subcollection
        log_payload = payload.copy()
        log_payload["timestamp"] = datetime.now(timezone.utc).isoformat()
        _user_ref(user_id).collection("sensor_logs").add(log_payload)

        print(f"[Firestore] Logged sensor data for user: {user_id}")
    except Exception as e:
        print(f"[Firestore] Error logging sensor data: {e}")

def log_feed_event(event_type: str, user_id: str):
    try:
        now = datetime.now(timezone.utc)
        
        # 1. Logging feed_events for 7-day chart under user's subcollection
        feed_data = {
            "event": event_type,
            "status": "success",
            "timestamp": now.isoformat()
        }
        _user_ref(user_id).collection("feed_events").add(feed_data)
        
        # 2. Increment daily count (for /status API) under user's subcollection
        today_str = now.strftime("%Y-%m-%d")
        _user_ref(user_id).collection("daily_logs").document(today_str).set({
            "date_string": today_str,
            "total_feedings": firestore.Increment(1),
            "last_updated": now.isoformat()
        }, merge=True)
        
        print(f"[Firestore] Logged {event_type} and incremented daily count for user: {user_id}")
    except Exception as e:
        print(f"[Firestore] Error logging feed event: {e}")

def get_today_feedings(user_id: str) -> int:
    try:
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        doc = _user_ref(user_id).collection("daily_logs").document(today_str).get()
        if doc.exists:
            return doc.to_dict().get("total_feedings", 0)
        return 0
    except Exception:
        return 0


def update_daily_eaten(amount: float, user_id: str):
    try:
        now = datetime.now(timezone.utc)
        today_str = now.strftime("%Y-%m-%d")
        
        # Increment total_eaten_grams safely under user's subcollection
        _user_ref(user_id).collection("daily_logs").document(today_str).set({
            "date_string": today_str,
            "total_eaten_grams": firestore.Increment(amount),
            "last_updated": now.isoformat()
        }, merge=True)
        print(f"[Firestore] Logged {amount}g eaten for user: {user_id}")
    except Exception as e:
        print(f"[Firestore] Error updating eaten amount: {e}")
        
def get_historical_feedings(user_id: str, days=7) -> list:
    try:
        now = datetime.now(timezone.utc)
        history = []
        for i in range(days - 1, -1, -1):
            target_date = now - timedelta(days=i)
            date_str = target_date.strftime("%Y-%m-%d")
            
            doc = _user_ref(user_id).collection("daily_logs").document(date_str).get()
            if doc.exists:
                data = doc.to_dict()
                count = data.get("total_feedings", 0)
                eaten = data.get("total_eaten_grams", 0)
            else:
                count = 0
                eaten = 0
            
            history.append({
                "date": date_str[-5:], # Format MM-DD for chart
                "count": count,
                "eaten": eaten
            })
        return history
    except Exception as e:
        print(f"[Firestore] Error getting history: {e}")
        return []
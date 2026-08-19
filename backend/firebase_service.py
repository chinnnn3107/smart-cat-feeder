import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone
from datetime import timedelta

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def update_current_status(payload: dict):
    try:
        # Logging sensor data
        log_payload = payload.copy()
        log_payload["timestamp"] = datetime.now(timezone.utc).isoformat()
        db.collection("sensor_logs").add(log_payload)

        print(f"[Firestore] Logged sensor data.")
    except Exception as e:
        print(f"[Firestore] Error logging sensor data: {e}")

def log_feed_event(event_type: str):
    try:
        now = datetime.now(timezone.utc)
        
        # 1. Logging feed_events for 7-day chart
        feed_data = {
            "event": event_type,
            "status": "success",
            "timestamp": now.isoformat()
        }
        db.collection("feed_events").add(feed_data)
        
        # 2. Increment daily count (for /status API)
        today_str = now.strftime("%Y-%m-%d")
        db.collection("daily_logs").document(today_str).set({
            "date_string": today_str,
            "total_feedings": firestore.Increment(1),
            "last_updated": now.isoformat()
        }, merge=True)
        
        print(f"[Firestore] Logged {event_type} and incremented daily count.")
    except Exception as e:
        print(f"[Firestore] Error logging feed event: {e}")

def get_today_feedings() -> int:
    try:
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        doc = db.collection("daily_logs").document(today_str).get()
        if doc.exists:
            return doc.to_dict().get("total_feedings", 0)
        return 0
    except Exception:
        return 0


def update_daily_eaten(amount: float):
    try:
        now = datetime.now(timezone.utc)
        today_str = now.strftime("%Y-%m-%d")
        
        # Increment total_eaten_grams safely
        db.collection("daily_logs").document(today_str).set({
            "date_string": today_str,
            "total_eaten_grams": firestore.Increment(amount),
            "last_updated": now.isoformat()
        }, merge=True)
        print(f"[Firestore] Logged {amount}g eaten.")
    except Exception as e:
        print(f"[Firestore] Error updating eaten amount: {e}")
        
def get_historical_feedings(days=7) -> list:
    try:
        now = datetime.now(timezone.utc)
        history = []
        for i in range(days - 1, -1, -1):
            target_date = now - timedelta(days=i)
            date_str = target_date.strftime("%Y-%m-%d")
            
            doc = db.collection("daily_logs").document(date_str).get()
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
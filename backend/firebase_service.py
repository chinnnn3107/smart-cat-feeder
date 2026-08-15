import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def update_current_status(payload: dict):
    try:
        # 1. Update real-time status (overwrite)
        payload["last_updated"] = datetime.now(timezone.utc).isoformat()
        db.collection("feeder_status").document("current_status").set(payload, merge=True)

        # 2. Logging sensor data
        log_payload = payload.copy()
        log_payload["timestamp"] = datetime.now(timezone.utc).isoformat()
        db.collection("sensor_logs").add(log_payload)

        print(f"[Firestore] Updated current_status: {payload} & logged sensor data.")
    except Exception as e:
        print(f"[Firestore] Error updating current_status: {e}")

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

def get_feeder_status() -> dict:
    try:
        doc = db.collection("feeder_status").document("current_status").get()
        if doc.exists:
            return doc.to_dict()
        return {"hopper_level": 0, "bowl_weight": 0}
    except Exception:
        return {"hopper_level": 0, "bowl_weight": 0}

def get_today_feedings() -> int:
    try:
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        doc = db.collection("daily_logs").document(today_str).get()
        if doc.exists:
            return doc.to_dict().get("total_feedings", 0)
        return 0
    except Exception:
        return 0
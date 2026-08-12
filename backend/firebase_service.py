import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def update_current_status(payload: dict):
    try:
        payload["last_updated"] = datetime.now(timezone.utc).isoformat()
        db.collection("feeder_status").document("current_status").set(payload, merge=True)
        print(f"[Firestore] Updated current_status: {payload}")
    except Exception as e:
        print(f"[Firestore] Error updating current_status: {e}")

def get_feeder_status() -> dict:
    try:
        doc = db.collection("feeder_status").document("current_status").get()
        if doc.exists:
            return doc.to_dict()
        return {"hopper_level": 0, "bowl_weight": 0}
    except Exception as e:
        print(f"[Firestore] Error reading current_status: {e}")
        return {"hopper_level": 0, "bowl_weight": 0}

def increment_daily_feedings():
    try:
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        doc_ref = db.collection("daily_logs").document(today_str)
        
        doc_ref.set({
            "date_string": today_str,
            "total_feedings": firestore.Increment(1),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }, merge=True)
        print(f"[Firestore] Incremented total_feedings for date: {today_str}")
    except Exception as e:
        print(f"[Firestore] Error incrementing daily feedings: {e}")

def get_today_feedings() -> int:
    try:
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        doc = db.collection("daily_logs").document(today_str).get()
        if doc.exists:
            return doc.to_dict().get("total_feedings", 0)
        return 0
    except Exception as e:
        print(f"[Firestore] Error getting today feedings: {e}")
        return 0
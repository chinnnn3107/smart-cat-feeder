import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def log_mqtt_event(collection_name: str, payload: dict):
    """
    Injects a backend timestamp and pushes the payload to Firestore.
    """
    try:
        # Create an ISO 8601 timestamp at the exact moment the server receives the data
        payload["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # Add the document to Firestore
        db.collection(collection_name).add(payload)
        print(f"[Firestore] Successfully logged to {collection_name}: {payload}")
        
    except Exception as e:
        print(f"[Firestore] Error logging event: {e}")
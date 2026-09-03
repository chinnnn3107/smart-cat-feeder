import os
import sys

# Force immediate log flushing on Render/Production servers
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin.auth as fb_auth
from mqtt_client import publish_feed, set_current_user, get_bowl_weight, get_hopper_status
from chatbot_service import ask_gemini
from firebase_service import get_today_feedings, get_historical_feedings
from prediction_model import calculate_ema

# Initialize the FastAPI backend application
app = FastAPI()

# Allow cross-origin requests from any frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve project directories for serving static files & HTML pages
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=FileResponse)
def read_root():
    home_file = os.path.join(TEMPLATES_DIR, "home.html")
    if os.path.exists(home_file):
        return FileResponse(home_file)
    return JSONResponse({"message": "Smart Cat Feeder Backend API is operational"})

@app.get("/templates/{page_name}")
def serve_template(page_name: str):
    template_file = os.path.join(TEMPLATES_DIR, page_name)
    if os.path.exists(template_file) and template_file.endswith(".html"):
        return FileResponse(template_file)
    raise HTTPException(status_code=404, detail="Page not found")

# --- Auth dependency ---

security = HTTPBearer()

def get_verified_uid(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    FastAPI dependency that verifies a Firebase ID Token from the Authorization header.
    Returns the user's Firebase UID on success, or raises HTTP 401 on failure.
    """
    try:
        decoded = fb_auth.verify_id_token(credentials.credentials)
        return decoded["uid"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

# --- API Endpoints ---

@app.get("/status")
def get_status(uid: str = Depends(get_verified_uid)):
    today_feedings = get_today_feedings(user_id=uid)
    # Return data for displaying the feeder status on the frontend
    return {
        "hopper_level": get_hopper_status(),
        "bowl_weight": get_bowl_weight(),
        "today_feedings": today_feedings
    }

@app.post("/feed")
def feed(uid: str = Depends(get_verified_uid)):
    # Publish a feed command to the ESP32 through MQTT.
    success = publish_feed(user_id=uid)

    # Confirm whether the command was successfully sent to the MQTT broker.
    if success:
        return {"success": True}

    return JSONResponse(
        # 503: Service Unavailable
        status_code=503,
        content={"success": False},
    )

@app.post("/chat")
def chat(request: dict, uid: str = Depends(get_verified_uid)):
    message = request.get("message")

    if not isinstance(message, str):
        return JSONResponse(
            # 400: Wrong data
            status_code=400,
            content={"error": "Message must be a string."},
        )

    if not message.strip():
        return JSONResponse(
            # 400: Wrong data
            status_code=400,
            content={"error": "Message cannot be empty."},
        )

    try:
        # Build feeder context directly using uid (avoids internal route call)
        today_feedings = get_today_feedings(user_id=uid)
        history_data = get_historical_feedings(user_id=uid, days=7)
        history_data.reverse()
        eaten_list = [day["eaten"] for day in history_data]
        feed_count_list = [day["count"] for day in history_data]
        predicted_eaten = calculate_ema(eaten_list, days=7)
        predicted_count = round(calculate_ema(feed_count_list, days=7))

        feeder_data = {
            "hopper_level": get_hopper_status(),
            "bowl_weight": get_bowl_weight(),
            "today_feedings": today_feedings,
            "prediction_count": predicted_count,
        }

        response = ask_gemini(message, feeder_data)
        return JSONResponse(
            # 200: Successful
            status_code=200,
            content={"response": response},
        )

    except Exception:
        # Return a JSON error if status retrieval, prediction, or Gemini fails.
        return JSONResponse(
            # 500: Server error
            status_code=500,
            content={"error": "Failed to get chatbot response."},
        )

@app.post("/sync-user")
def sync_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Called once after login to store the current user's UID and email on the server.
    Used to attribute physical button press events (from ESP32 via MQTT) to the right user,
    and to send hopper low-stock email alerts to the correct address.
    """
    try:
        decoded = fb_auth.verify_id_token(credentials.credentials)
        uid = decoded["uid"]
        email = decoded.get("email", "")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    set_current_user(uid=uid, email=email)
    print(f"[Auth] Current user synced: {email} (uid={uid})")

    return {
        "status": "success",
        "uid": uid,
        "email": email,
    }

@app.get("/history")
def get_history(uid: str = Depends(get_verified_uid)):
    history_data = get_historical_feedings(user_id=uid, days=7)
    return {"history": history_data}

@app.get("/predict-feeding")
def predict_feeding(uid: str = Depends(get_verified_uid)):
    history_data = get_historical_feedings(user_id=uid, days=7)

    # Data order in Firebase is from new to old so we have to reverse it
    history_data.reverse()

    eaten_list = [day["eaten"] for day in history_data]
    feed_count_list = [day["count"] for day in history_data]

    predicted_eaten = calculate_ema(eaten_list, days=7)
    predicted_count = round(calculate_ema(feed_count_list, days=7))

    return {
        "predicted_grams": predicted_eaten,
        "predicted_meals": predicted_count
    }
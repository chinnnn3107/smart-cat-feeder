from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mqtt_client import publish_feed, set_current_user_email
from chatbot_service import ask_gemini
from firebase_service import get_feeder_status, get_today_feedings

# Request models
class UserData(BaseModel):
    email: str

# Initialize the FastAPI backend application
app = FastAPI()

# Allow the frontend running on Live Server port 5500 to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints
@app.get("/status")
def get_status():
    current_data = get_feeder_status()
    today_feedings = get_today_feedings()
    # Return sample data for displaying the feeder status on the frontend
    return {
        "hopper_level": current_data.get("hopper_level", 0),
        "bowl_weight": current_data.get("bowl_weight", 0),
        "today_feedings": today_feedings
    }

@app.post("/feed")
def feed():
    # Publish a feed command to the ESP32 through MQTT
    publish_feed()
    # Tell the frontend that the request was accepted
    return {
        "accepted": True
    }

@app.post("/chat")
def chat(request: dict):
    # Check if the request contains the "message" key
    if "message" not in request:
        return {"error": "Message is required."}

    # Get the user's message from the request body
    message = request["message"]

    if message.strip() == "":
        return {"error": "Message cannot be empty."}

    feeder_data = get_status()

    try:
        response = ask_gemini(message, feeder_data)
        return { "response": response }
    
    except Exception:
        return { "error": "Failed to get response from Gemini." }

@app.post("/sync-user")
def sync_user(data: UserData):
    set_current_user_email(data.email)

    print(f"Current user: {data.email}")

    return {
        "status": "success",
        "email": data.email,
    }

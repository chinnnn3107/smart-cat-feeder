from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mqtt_client import publish_feed, set_current_user_email, get_bowl_weight, get_hopper_status
from chatbot_service import ask_gemini
from firebase_service import get_today_feedings, get_historical_feedings
from prediction_model import calculate_ema
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
    today_feedings = get_today_feedings()
    # Return sample data for displaying the feeder status on the frontend
    return {
        "hopper_level": get_hopper_status(),
        "bowl_weight": get_bowl_weight(),
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

@app.get("/history")
def get_history():
    history_data = get_historical_feedings(7)
    return {"history": history_data}

@app.get("/predict-feeding")
def predict_feeding():
    history_data = get_historical_feedings(7)
    
    # Data order in Firebase is from new to old so we have to reverse it 
    history_data.reverse() 
    
    eaten_list = [day['eaten'] for day in history_data]
    feed_count_list = [day['count'] for day in history_data]
    
    predicted_eaten = calculate_ema(eaten_list, days=7)
    predicted_count = round(calculate_ema(feed_count_list, days=7))
    
    return {
        "predicted_grams": predicted_eaten,
        "predicted_meals": predicted_count
    }
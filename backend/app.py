from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mqtt_client import publish_feed, get_bowl_weight, get_hopper_status
from chatbot_service import ask_gemini

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
    # Return sample data for displaying the feeder status on the frontend
    return {
        "hopper_level": get_hopper_status(),
        "bowl_weight": get_bowl_weight(),
        "today_feedings": 0  # TODO: Connect to the database to get the actual number of feedings
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
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mqtt_client import publish_feed, get_feed_status_mqtt, get_bowl_weight

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
        "hopper_level": 34,
        "bowl_weight": get_bowl_weight(),
        "today_feedings": 3
    }

@app.post("/feed")
def feed():
    publish_feed()
    return {
        "accepted": True
    }

@app.get("/feed/status")
def get_feed_status():
    status  = get_feed_status_mqtt()
    return {
        "status": status 
    }



# Import FastAPI to create the API and CORSMiddleware to allow frontend requests.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize the FastAPI backend application.
app = FastAPI()

# Allow the frontend running on Live Server port 5500 to access the API.
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

@app.get("/status")
def get_status():
    # Return sample data for displaying the feeder status on the frontend.
    return {
        "hopper_level": 34,
        "bowl_weight": 120,
        "today_feedings": 3
    }

@app.post("/feed")
def feed():
    # Handle the basic receive feeding request, this can later trigger the feeder hardware.
    return {
        "accepted": True,
    }

@app.get("/feed/status")
def feed_status():
    return {
    # if ...
        "status": "completed"
    # else if ...
      # "status": "pending"
    # else ...
      # "status": "failed"
    }

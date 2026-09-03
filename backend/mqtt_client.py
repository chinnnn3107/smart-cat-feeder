import os
import json
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from firebase_service import update_current_status, log_feed_event, update_daily_eaten
from email_service import checkHopperAlert

# Load environment variables from .env configuration file
load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", 8883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

# Define MQTT topics
FEED_TOPIC = "feeder/feed"
BOWL_WEIGHT_TOPIC = "feeder/bowl_weight"
HOPPER_STATUS_TOPIC = "feeder/hopper_status"
PHYSICAL_FEED_TOPIC = "feeder/physical_feed"

# Global state
bowl_weight = None
hopper_status = None
last_bowl_weight = None

# Stores the last logged-in user's identity.
# Used to attribute physical button press events (no HTTP context) to a user.
current_user_uid = None
current_user_email = None

def set_current_user(uid: str, email: str):
    """Store the current user's UID (for Firestore) and email (for alerts)."""
    global current_user_uid, current_user_email
    current_user_uid = uid
    current_user_email = email

# MQTT callback handlers
def on_connect(client, userdata, flags, reason_code, properties):
    """
    Callback executed when client establishes connection with the MQTT broker.
    Subscribes to the bowl weight topic upon successful connection.
    """
    if reason_code == 0:
        print("Connected to HiveMQ successfully")

        client.subscribe(BOWL_WEIGHT_TOPIC)
        client.subscribe(HOPPER_STATUS_TOPIC)
        client.subscribe(PHYSICAL_FEED_TOPIC)

        print(f"Subscribed to: {BOWL_WEIGHT_TOPIC}", {HOPPER_STATUS_TOPIC}, {PHYSICAL_FEED_TOPIC})
    else:
        print(
            f"Failed to connect to HiveMQ broker. "
            f"Reason code: {reason_code}"
        )


def on_message(client, userdata, message):
    """
    Callback executed when a new MQTT message is received.
    Updates the latest data.
    """
    global bowl_weight, hopper_status

    payload = message.payload.decode()

    # Handle bowl weight (Load cell)
    if message.topic == BOWL_WEIGHT_TOPIC:
        try:
            data = json.loads(payload)
            bowl_weight = data["bowl_weight"]
            print(f"[MQTT] Bowl weight: {bowl_weight} g")
            
            global last_bowl_weight
            if last_bowl_weight is not None:
                weight_diff = last_bowl_weight - bowl_weight
                
                # If weight decreases because pet ate and difference is less than 50 grams (from changing bowl)
                if 0 < weight_diff < 50 and current_user_uid:
                    update_daily_eaten(weight_diff, user_id=current_user_uid)
                    
            last_bowl_weight = bowl_weight
            
            if current_user_uid:
                update_current_status(data, user_id=current_user_uid)
            else:
                print("[Firestore] No logged-in user — skipping sensor log")
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            print(f"[MQTT] Invalid bowl weight payload: {error}")
    
    # Handle hopper status (Ultrasonic)
    elif message.topic == HOPPER_STATUS_TOPIC:
        try:
            data = json.loads(payload)
            hopper_status = data["hopper_level"]
            print(f"[MQTT] Hopper level: {hopper_status}%")

            if current_user_uid:
                update_current_status(data, user_id=current_user_uid)
            if current_user_email:
                checkHopperAlert(hopper_status, current_user_email)
            else:
                print("[Email] No logged-in user email — skipping hopper log")

        except (json.JSONDecodeError, KeyError, TypeError) as error:
            print(f"[MQTT] Invalid hopper status payload: {error}")
    
    # Handle manual feed (Button)
    elif message.topic == PHYSICAL_FEED_TOPIC:
        try:
            data = json.loads(payload)
            print(f"[MQTT] Physical button feed: {data}")
            if current_user_uid:
                log_feed_event(event_type="manual_feed", user_id=current_user_uid)
            else:
                print("[Firestore] No logged-in user — skipping physical feed log")
        except (json.JSONDecodeError, TypeError) as error:
            print(f"[MQTT] Invalid physical feed payload: {error}")


# MQTT client initialization and setup
# Instantiate MQTT client using Paho Callback API v2
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# Set authentication credentials for HiveMQ broker
mqtt_client.username_pw_set(
    MQTT_USERNAME,
    MQTT_PASSWORD
)

# Enable TLS encryption for secure cloud broker connection
mqtt_client.tls_set()

# Assign callback handlers for broker connection events and subscribed MQTT messages
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connect to the MQTT broker and start non-blocking network thread loop
mqtt_client.connect(
    MQTT_BROKER,
    MQTT_PORT
)

mqtt_client.loop_start()


# Public helper functions
def publish_feed(user_id: str):
    """
    Publish a feed trigger command ('feed') to the feeder hardware over MQTT.
    user_id comes from the verified Firebase token in the HTTP request.
    """
    result = mqtt_client.publish(FEED_TOPIC, "feed")

    if result.rc != 0:
        return False

    log_feed_event(event_type="web_feed", user_id=user_id)
    return True


def get_bowl_weight():
    """
    Retrieve the latest bowl weight.

    Returns:
        float | None: Current bowl weight in grams.
    """
    return bowl_weight

def get_hopper_status():
    """
    Retrieve the latest hopper status (ultrasonic sensor reading).

    Returns:
        int | float | None: Current hopper level percentage.
    """
    return hopper_status
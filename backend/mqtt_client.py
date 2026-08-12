import os
import json
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

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

# Global state for bowl weight
bowl_weight = None
hopper_status = None

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

        print(f"Subscribed to: {BOWL_WEIGHT_TOPIC} and {HOPPER_STATUS_TOPIC}")
    else:
        print(
            f"Failed to connect to HiveMQ broker. "
            f"Reason code: {reason_code}"
        )


def on_message(client, userdata, message):
    """
    Callback executed when a new MQTT message is received.
    Updates the latest bowl weight.
    """
    global bowl_weight, hopper_status

    payload = message.payload.decode()

    if message.topic == BOWL_WEIGHT_TOPIC:
        try:
            data = json.loads(payload)
            bowl_weight = data["bowl_weight"]
            print(f"[MQTT] Bowl weight: {bowl_weight} g")
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            print(f"[MQTT] Invalid bowl weight payload: {error}")
    elif message.topic == HOPPER_STATUS_TOPIC:
        try:
            data = json.loads(payload)
            # Assumes the ESP32 sends a JSON payload like {"hopper_level": 75}
            hopper_status = data["hopper_level"]
            print(f"[MQTT] Hopper level: {hopper_status}%")
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            print(f"[MQTT] Invalid hopper status payload: {error}")


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
def publish_feed():
    """
    Publish a feed trigger command ('feed') to the feeder hardware over MQTT.
    """
    return mqtt_client.publish(FEED_TOPIC, "feed")


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
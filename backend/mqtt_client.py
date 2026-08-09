"""
MQTT Client Integration Module for Smart Cat Feeder.
Manages communication with the HiveMQ MQTT broker, handles publishing feed requests,
and tracks feed execution status via broker topics.
"""

import os
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

# Load environment variables from .env configuration file
load_dotenv()
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", 8883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

# Define MQTT topics 
FEED_TOPIC = "smart-feeder/feed"
FEED_STATUS_TOPIC = "smart-feeder/feed/status"

# Global state tracker for the current feeding operation ('idle', 'pending', 'completed', or 'failed')
feed_status_value = "idle"

# --- MQTT Callback Handlers ---

def on_connect(client, userdata, flags, reason_code, properties):
    """
    Callback executed when client establishes connection with the MQTT broker.
    Subscribes to the feed status topic upon successful connection.
    """
    if reason_code == 0:
        print("Connected to HiveMQ successfully")
        client.subscribe(FEED_STATUS_TOPIC)
        print(f"Subscribed to feed status topic: {FEED_STATUS_TOPIC}")
    else:
        print(f"Failed to connect to HiveMQ broker. Reason code: {reason_code}")

def on_message(client, userdata, message):
    """
    Callback executed when a new message is received from a subscribed MQTT topic.
    Updates the global feed_status_value when status updates arrive.
    """
    global feed_status_value
    payload = message.payload.decode()
    if message.topic == FEED_STATUS_TOPIC:
        feed_status_value = payload

# --- MQTT client initialization and setup ---
# Instantiate MQTT client using Paho Callback API v2
mqtt_client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

# Set authentication credentials for HiveMQ broker
mqtt_client.username_pw_set(
    MQTT_USERNAME,
    MQTT_PASSWORD
)

# Enable TLS encryption for secure cloud broker connection
mqtt_client.tls_set()

# Attach callback functions
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connect to the MQTT broker and start non-blocking network thread loop
mqtt_client.connect(
    MQTT_BROKER,
    MQTT_PORT
)
mqtt_client.loop_start()

# --- Public helper functions ---
def publish_feed():
    """
    Publish a feed trigger command ('feed') to the feeder hardware over MQTT.
    Sets status to 'pending' while awaiting hardware execution feedback.
    """
    global feed_status_value
    feed_status_value = "pending"
    mqtt_client.publish(FEED_TOPIC, "feed")

def get_feed_status_mqtt():
    """
    Retrieve the current feed operation status.
    Returns:
        str: Current state ('idle', 'pending', 'completed', or 'failed').
    """
    return feed_status_value

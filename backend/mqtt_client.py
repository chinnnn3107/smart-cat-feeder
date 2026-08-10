import os
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

# Load environment variables from .env configuration file
load_dotenv()
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", 8883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

# Define MQTT topic
TOPIC_FEED = "smart-feeder/feed"

# Instantiate MQTT client using Paho Callback API v2
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# Set authentication credentials for HiveMQ broker
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

# Enable TLS encryption for secure cloud broker connection
mqtt_client.tls_set()

# Connect to the MQTT broker and start non-blocking network thread loop
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
mqtt_client.loop_start()

# Public helper functions
def publish_feed():
    result = mqtt_client.publish(TOPIC_FEED, "feed")

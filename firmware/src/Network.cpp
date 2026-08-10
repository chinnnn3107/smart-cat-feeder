#include "Network.h"
#include "../include/Config.h"
#include <WiFiManager.h>
#include <PubSubClient.h>
#include <WiFiClientSecure.h>
#include "Dispenser.h"

static WiFiClientSecure espClient; // using secured broker
static PubSubClient mqttClient(espClient);
static unsigned long lastReconnectAttempt = 0; // support reconnect function
static unsigned long lastWifiReconnect    = 0; // support non-blocking WiFi reconnect

// Triggered on new MQTT message
static void MQTT_Callback(char* topic, byte* payload, unsigned int length) {
    String message; // class String for ESP32
    for (unsigned int i = 0; i < length; i++)
        message += (char)payload[i];

    Serial.print("[MQTT] Message from Topic: ");
    Serial.println(topic);
    Serial.print("[MQTT] Content: ");
    Serial.println(message);
    
    
    if (String(topic) == TOPIC_FEED && message == "feed"){
        Serial.println("[MQTT] Received feed command on web!");
        Dispenser_Trigger();
    }

    // Tin nhắn đến từ kênh khác? (Ví dụ thêm sau)
    // else if (String(topic) == TOPIC_KHAC) {
    //     // Xử lý việc khác
    // }
}

// MQTT Reconnect (runs every 5s)
static void MQTT_Reconnect() {
    if (millis() - lastReconnectAttempt < 5000) return;
    lastReconnectAttempt = millis();

    Serial.print("[MQTT] Attemping connection...");
    
    // Avoid ID conflict
    String clientId = "Client-ID-" + String(random(0xffff), HEX);

    if(mqttClient.connect(clientId.c_str(), MQTT_USER, MQTT_PASS)) {
        Serial.println("Success!");
        mqttClient.subscribe(TOPIC_FEED, 1); // mqttClient.subscribe(topic, QoS)
        Serial.print("[MQTT] Subscribed to topic: ");
        Serial.println(TOPIC_FEED);
    }

    else {
        Serial.print(" Failed! Error: ");
        Serial.println(mqttClient.state());
    }
}
// Initializes WiFi via WiFiManager and MQTT. Call once in setup()
void Network_Init() {
#ifdef WOKWI
    WiFi.begin("Wokwi-GUEST", "", 6);
    while (WiFi.status() != WL_CONNECTED) {
        delay(100);
    }
#else
    Serial.println("[WiFi] Initalizing WiFiManger...");
    WiFiManager wm;
    wm.setConfigPortalTimeout(180); // setup off after 3 minutes without connection

    // Creates a WiFi Access Point "SmartFeeder_WiFi" for user configuration if connection fails.
    if(!wm.autoConnect("SmartFeeder_WiFI")) { 
        Serial.println("[WiFi] Failed to connect! Restarting... ");
        delay(3000);
        ESP.restart();
    }
#endif

    Serial.print("[WiFi] Connected! IP Address: ");
    Serial.println(WiFi.localIP());

    espClient.setInsecure(); // avoid certificate
    mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
    mqttClient.setCallback(MQTT_Callback);
    mqttClient.setBufferSize(512);

    randomSeed(esp_random()); // Seed random for unique client IDs
    Serial.println("[MQTT] Connecting for the first time...");
    MQTT_Reconnect();
}

// Maintains WiFi/MQTT connections. Called in loop()
void Network_Loop() {
    if (WiFi.status() != WL_CONNECTED) {
        if (millis() - lastWifiReconnect >= 10000) {
            lastWifiReconnect = millis();
            Serial.println("[WiFi] Connection lost! Reconnecting...");
            WiFi.reconnect();
        }
        return;
    }

    if (!mqttClient.connected())
        MQTT_Reconnect();

    mqttClient.loop();
}

// Publishes a payload to an MQTT topic. Returns true on success.
bool MQTT_Publish(const char* topic, const String& payload, bool retained) {
    if (!mqttClient.connected()) {
        Serial.println("[MQTT] Cannot publish: Not connected!");
        return false;
    }

    bool success = mqttClient.publish(topic, payload.c_str(), retained);

    if (success) {
        Serial.print("[MQTT] Published to {");
        Serial.print(topic);
        Serial.print("} ");
        Serial.println(payload);
    } else {
        Serial.print("[MQTT] Failed to publish to topic: ");
        Serial.println(topic);
    }

    return success;
}

// Returns true if connected to MQTT broker.
bool MQTT_IsConnected() {
    return mqttClient.connected();
}
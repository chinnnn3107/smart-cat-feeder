#include "LoadCell.h"
#include "Network.h"
#include "../include/Config.h"
#include <HX711.h>
#include <Arduino.h>

// HX711 sensor object
static HX711 hx711;

// Last published weight
static float lastPublishedWeight = 0.0;
// Timestamp of last publish in milliseconds
static unsigned long lastPublishTime = 0;


// Build JSON payload and publish to MQTT
static void publishWeight(float weight) {
    String payload = "{\"bowl_weight\": ";
    payload += String(weight, 1); // round to 1 decimal place
    payload += ", \"device_id\": \"feeder-01\"";
    payload += ", \"recorded_at\": ";
    payload += String(millis());
    payload += "}";

    bool success = MQTT_Publish(TOPIC_BOWL_WEIGHT, payload, false);
    if (success) {
        lastPublishedWeight = weight;
        lastPublishTime = millis();
        Serial.print("[LoadCell] Published: ");
        Serial.print(weight, 1); // round to 1 decimal place
        Serial.println(" g");
    }
}

// Initialize HX711. Call once in setup()
void LoadCell_Init() {
    Serial.println("[LoadCell] Initializing HX711...");
    hx711.begin(PIN_LOADCELL_DOUT, PIN_LOADCELL_SCK);

    while (!hx711.is_ready()) {
        Serial.println("[LoadCell] Waiting for HX711...");
        delay(200);
    }

    hx711.set_scale(SCALE_CALIBRATION_FACTOR); 
    Serial.println("[LoadCell] HX711 ready.");
}

// Read weight and publish if needed. Call repeatedly in loop()
void LoadCell_Loop() {
    if (!hx711.is_ready()) return;

    // Read average of 5 samples
    float weight = hx711.get_units(5);

    // Clamp negative values to 0
    if (weight < 0.0) weight = 0.0;


    float change  = abs(weight - lastPublishedWeight);
    unsigned long elapsed = millis() - lastPublishTime;

    // Publish if change > 5g OR 1 hour has passed
    if (change >= MIN_WEIGHT_CHANGE_GRAMS || elapsed >= PUBLISH_INTERVAL_MS) {
        if (MQTT_IsConnected()) {
            publishWeight(weight);
        } else {
            Serial.println("[LoadCell] MQTT not connected, skip publish.");
        }
    }
}

#include "Ultrasonic.h"
#include "../include/Config.h"
#include "Network.h"

static unsigned long lastReadTime = 0;      // timer for reading
static unsigned long lastPublishTime = 0;   // timer for publishing
static int lastPublishedPct = -100;         // last published percentage

long getDistance() {
    // Trigger the sensor
    digitalWrite(PIN_ULTRASONIC_TRIG, LOW);
    delayMicroseconds(2);
    digitalWrite(PIN_ULTRASONIC_TRIG, HIGH);
    delayMicroseconds(10);
    digitalWrite(PIN_ULTRASONIC_TRIG, LOW);

    // Read the echo duration (with a 30ms timeout to prevent freezing)
    long duration = pulseIn(PIN_ULTRASONIC_ECHO, HIGH, 30000); 
    
    // If timeout occurs (no object detected), exit early
    if (duration == 0) return -1;

    // Calculate distance
    long distanceCm = duration * 0.034 / 2.0;

    return distanceCm;
}

void Ultrasonic_Init() {
    pinMode(PIN_ULTRASONIC_TRIG, OUTPUT);
    pinMode(PIN_ULTRASONIC_ECHO, INPUT);
}

void Ultrasonic_Loop() {
    unsigned long currentMillis = millis();

    // Read sensor every 10000ms (10 second)
    if (currentMillis - lastReadTime >= 10000) {
        lastReadTime = currentMillis;
        long distanceCm = getDistance();

        // Convert to percentage (empty: 30cm = 0% ; full: 5cm = 100%)
        int percentage = map(distanceCm, (long)HOPPER_EMPTY_DISTANCE_CM, (long)HOPPER_FULL_DISTANCE_CM, 0, 100);
        percentage = constrain(percentage, 0, 100);

        // Publish when:
        // 1. Time limit reached
        // 2. OR Significant change
        bool timeToPublish = (currentMillis - lastPublishTime >= PUBLISH_INTERVAL_MS);
        bool significantChange = (abs(percentage - lastPublishedPct) >= MIN_HOPPER_CHANGE_PCT);

        if (timeToPublish || significantChange) {
            // Only attempt to publish if network is ready
            if (MQTT_IsConnected()) {
                String payload = "{\"hopper_level\": " + String(percentage) + "}";
                // MQTT_Publish returns true on success
                if (MQTT_Publish(TOPIC_HOPPER_STATUS, payload)) {
                    lastPublishTime = currentMillis;
                    lastPublishedPct = percentage;
                }
            }
        }
    }
}
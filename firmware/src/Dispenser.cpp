#include "Dispenser.h"
#include "../include/Config.h"
#include <ESP32Servo.h>
#include <Network.h>

static Servo servo;
static bool isFeeding  = false;
static unsigned long feedStartTime = 0;

void Dispenser_Init() {
    servo.attach(PIN_SERVO);
    servo.write(0);
}

// Starts the feeding process if it is not already running
void Dispenser_Trigger() {
    if (isFeeding) return;

    Serial.println("[Dispenser] Feeding...");

    isFeeding  = true;
    feedStartTime = millis();
    servo.write(90);

}

// Checks whether the feeding time has finished and closes the dispenser
void Dispenser_Loop() {
    // Wait 3000 ms before returning to 0
    if (isFeeding && millis() - feedStartTime >= 3000) {
        servo.write(0);
        isFeeding  = false;
        Serial.println("[Dispenser] Feed completed");
        if (MQTT_IsConnected())
            MQTT_Publish(TOPIC_FEED_STATUS, "Feed completed", false);
    }
}

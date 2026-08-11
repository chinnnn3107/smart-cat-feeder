#include "Button.h"
#include "../include/Config.h"
#include "Network.h"
#include "Dispenser.h"

static unsigned long lastDebounceTime = 0; // timer for debounce
static unsigned long debounceDelay = 50;   // 50ms debounce time
static int lastButtonState = LOW;          // previous raw reading
static int buttonState = LOW;              // actual verified state

void Button_Init() {
    pinMode(PIN_BUTTON, INPUT_PULLUP);
}

void Button_Loop() {
    // Current button state
    int reading = digitalRead(PIN_BUTTON);

    // Reset debounce timer (switch changed)
    if (reading != lastButtonState) {
        lastDebounceTime = millis(); 
    }

    // If the state has been stable longer than debounce time
    if ((millis() - lastDebounceTime) > debounceDelay) {
        // The state actually changed --> update real button state
        if (reading != buttonState) {
            buttonState = reading;

            if (buttonState == LOW) {
                Serial.println("[Button] Pressed!");

                // Trigger the dispenser
                Dispenser_Trigger(); 
                
                // Publish to the Web/Backend
                if (MQTT_IsConnected()) {
                    String payload = "{\"event\": \"manual_feed\", \"status\": \"success\"}";
                    if (MQTT_Publish(TOPIC_PHYSICAL_FEED, payload)) {
                        Serial.println("[MQTT] Physical feed event published to backend.");
                    }
                }
            }
        }
    }

    // save reading for next loop
    lastButtonState = reading;
}
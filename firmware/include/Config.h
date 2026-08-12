#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

namespace {

// Loadcell pins
const int PIN_LOADCELL_DOUT = 4;
const int PIN_LOADCELL_SCK  = 5;

// Ultrasonic pins
const int PIN_ULTRASONIC_TRIG = 6;
const int PIN_ULTRASONIC_ECHO = 7;

// Servo pins
const int PIN_SERVO = 15;

// Button pins
const int PIN_BUTTON = 0; 

// MQTT Configuration
static const char* MQTT_SERVER = "YOUR_HIVEMQ_URL.hivemq.cloud";
static const int   MQTT_PORT   = 8883;
static const char* MQTT_USER   = "YOUR_MQTT_USERNAME";
static const char* MQTT_PASS   = "YOUR_MQTT_PASSWORD";

// MQTT Topics 
static const char* TOPIC_BOWL_WEIGHT   = "feeder/bowl_weight";
static const char* TOPIC_HOPPER_STATUS = "feeder/hopper_status";
static const char* TOPIC_FEED          = "feeder/feed";
static const char* TOPIC_PHYSICAL_FEED = "feeder/physical_feed";
// Loadcell
const float SCALE_CALIBRATION_FACTOR = 2280.0; // [NEED FIXED] Base on real measurement
const float MIN_WEIGHT_CHANGE_GRAMS  = 5.0;    // Only MQTT when change > 5 grams

// Hopper 
const float HOPPER_EMPTY_DISTANCE_CM = 30.0;   
const float HOPPER_FULL_DISTANCE_CM  = 5.0;    
const float MIN_HOPPER_CHANGE_PCT    = 5.0;    // Only MQTT when change > 5%

// Default Loop (1 hour)
const unsigned long PUBLISH_INTERVAL_MS = 3600000;

} // namespace

#endif // CONFIG_H

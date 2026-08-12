#include <Arduino.h>
#include "Dispenser.h"
#include "Network.h"
#include "Ultrasonic.h"
#include "Button.h"
#include "LoadCell.h"

void setup() {
    Serial.begin(115200);
    delay(2000); // Chờ Serial Monitor kịp mở

    Ultrasonic_Init();
    Button_Init();

    Network_Init(); // Kết nối WiFi + MQTT
    Dispenser_Init();
    LoadCell_Init();
}

void loop() {
    Network_Loop(); // Giữ kết nối
    Dispenser_Loop();
    Ultrasonic_Loop();
    Button_Loop();
    LoadCell_Loop();
}

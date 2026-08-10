#include <Arduino.h>
#include "Dispenser.h"
#include "Network.h"

void setup() {
    Serial.begin(115200);
    delay(2000); // Chờ Serial Monitor kịp mở
    Network_Init(); // Kết nối WiFi + MQTT
    Dispenser_Init();
}

void loop() {
    Network_Loop(); // Giữ kết nối
    Dispenser_Loop();
}

#include <Arduino.h>
#include "Network.h"
void setup() {
    Serial.begin(115200);
    delay(2000); // Chờ Serial Monitor kịp mở
    Serial.println("=== Smart Cat Feeder - Network Test ===");
    Network_Init(); // Kết nối WiFi + MQTT
}
void loop() {
    Network_Loop(); // Giữ kết nối
    // Gửi thử 1 tin nhắn MQTT mỗi 10 giây để kiểm tra
    static unsigned long lastTest = 0;
    if (millis() - lastTest >= 10000 && MQTT_IsConnected()) {
        lastTest = millis();
        MQTT_Publish("feeder/test", "{\"status\": \"hello from ESP32\"}", false);
    }
}
#ifndef NETWORK_H
#define NETWORK_H
#include <Arduino.h>

void Network_Init();
void Network_Loop();
bool MQTT_Publish(const char* topic, const String& payload, bool retained = false);
bool MQTT_IsConnected();

#endif
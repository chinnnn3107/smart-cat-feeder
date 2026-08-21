# Smart Cat Feeder

Smart Cat Feeder is a full-stack IoT system that monitors the food level in a hopper, measures the food weight in a bowl, supports remote and physical feeding, stores feeding activity in Cloud Firestore, sends low-food email alerts, predicts feeding demand, and provides a Google Gemini-powered AI assistant using the feeder's current data.

> **Project Status:** In active development. The ESP32 firmware and Wokwi simulation, FastAPI backend, MQTT communication, Firebase services, Gmail SMTP alerts, Gemini integration, and frontend web application are operational.

---

## 🎯 Key Features

- **Flexible Wi-Fi Provisioning:** Uses `WiFiManager` on the ESP32 to configure Wi-Fi credentials without hardcoding an SSID and password.
- **Real-Time Telemetry:** Measures hopper food percentage with an ultrasonic sensor and bowl weight with a load cell and HX711.
- **Dual Feeding Trigger:** Dispenses food remotely from the web application or locally with a debounced physical button.
- **MQTT Communication:** Exchanges commands and telemetry securely through HiveMQ Cloud over TLS.
- **Firestore Logging:** Stores sensor readings, web and physical feeding events, daily feeding counts, and estimated food consumption.
- **Seven-Day Statistics:** Displays feeding count and food consumption history using Chart.js.
- **EMA Prediction:** Predicts the next day's number of meals and total food consumption from seven days of historical data.
- **Automated Low-Food Alerts:** Sends a Gmail SMTP alert when the hopper reaches `10%` or lower and prevents repeated alerts until the hopper is refilled above the threshold.
- **Context-Aware AI Assistant:** Uses Gemini 3.5 Flash to answer supported cat-feeding and feeder questions from current status and prediction data, in the user's language.
- **Authentication and Responsive UI:** Uses Firebase Authentication with a lightweight HTML, CSS, and JavaScript interface.

---

## 🏗️ System Architecture

```text
Ultrasonic Sensor --+
HX711 Load Cell ----+--> ESP32 / Wokwi <-- Physical Button
Servo Motor --------+           |
                                | MQTT over TLS (port 8883)
                                v
                       HiveMQ Cloud Broker
                                |
                                v
Web Browser ------ HTTP ----> FastAPI Backend ----> Cloud Firestore
                                |     |
                                |     +------------> Gmail SMTP Alerts
                                +------------------> Google Gemini API
```

- **ESP32 Firmware:** Reads the sensors, controls the servo, handles the physical button, provisions Wi-Fi, and communicates with HiveMQ Cloud.
- **FastAPI Backend:** Bridges MQTT, Firestore, Gmail SMTP, Gemini, prediction logic, and the frontend REST API.
- **Frontend Web Application:** Provides authentication, live feeder status, remote feeding, seven-day logs, prediction results, and chatbot access.

---

## 🛠️ Technology Stack

| Layer / Component         | Technology / Library                                                                   |
| ------------------------- | -------------------------------------------------------------------------------------- |
| **Hardware / Firmware**   | ESP32-S3, PlatformIO, Arduino C++, WiFiManager, PubSubClient, HX711, ESP32Servo, Wokwi |
| **Messaging**             | HiveMQ Cloud MQTT Broker (TLS port `8883`), Paho MQTT                                  |
| **Backend API**           | Python 3, FastAPI, Uvicorn, Pydantic                                                   |
| **Database & Auth**       | Firebase Authentication, Cloud Firestore, Firebase Admin SDK                           |
| **Prediction**            | Seven-day Exponential Moving Average (EMA)                                             |
| **AI Assistant & Alerts** | Google Gemini API (`google-genai`), Gmail SMTP (`smtplib`)                             |
| **Frontend Web**          | HTML5, CSS3, JavaScript, Firebase Auth SDK, Chart.js                                   |

---

## 📁 Repository Layout

```text
smart-cat-feeder/
|-- backend/                        # FastAPI backend application
|   |-- app.py                      # REST endpoints and CORS configuration
|   |-- chatbot_service.py          # Gemini prompt and feeder context
|   |-- email_service.py            # Gmail SMTP low-food alerts
|   |-- firebase_service.py         # Firestore sensor, feeding, and daily logs
|   |-- mqtt_client.py              # MQTT connection, subscriptions, and publishing
|   |-- prediction_model.py         # Seven-day EMA calculation
|   |-- requirements.txt            # Python dependencies
|   `-- serviceAccountKey.json      # Firebase Admin credentials (not committed)
|-- firmware/                       # ESP32-S3 PlatformIO project
|   |-- include/
|   |   `-- Config.h                # Pins, MQTT settings, topics, and thresholds
|   |-- src/
|   |   |-- main.cpp                # Firmware setup and main loop
|   |   |-- Network.cpp / .h        # WiFiManager and TLS MQTT connection
|   |   |-- LoadCell.cpp / .h       # HX711 readings and bowl-weight publishing
|   |   |-- Ultrasonic.cpp / .h     # Hopper-level measurement and publishing
|   |   |-- Dispenser.cpp / .h      # Non-blocking servo control
|   |   `-- Button.cpp / .h         # Debounced physical feed button
|   |-- diagram.json                # Wokwi circuit definition
|   |-- platformio.ini              # Board and library configuration
|   `-- wokwi.toml                  # Wokwi simulation configuration
|-- static/
|   |-- css/                        # Page and shared stylesheets
|   `-- js/                         # Auth, dashboard, logs, chatbot, and logout scripts
|-- templates/
|   |-- chatbot.html                # Context-aware AI assistant page
|   |-- home.html                   # Status dashboard and remote Feed button
|   |-- login.html                  # User login page
|   |-- logs.html                   # Seven-day chart and prediction page
|   `-- signup.html                 # User registration page
|-- .gitignore
`-- README.md
```

---

## 📡 MQTT Topics & Payloads

| Topic                  | Direction       | Example Payload                                                          | Description                                  |
| ---------------------- | --------------- | ------------------------------------------------------------------------ | -------------------------------------------- |
| `feeder/hopper_status` | ESP32 → Backend | `{"hopper_level": 85}`                                                   | Reports the remaining hopper food percentage |
| `feeder/bowl_weight`   | ESP32 → Backend | `{"bowl_weight": 42.0, "device_id": "feeder-01", "recorded_at": 120000}` | Reports bowl weight in grams                 |
| `feeder/physical_feed` | ESP32 → Backend | `{"event": "manual_feed", "status": "success"}`                          | Reports a physical-button feeding event      |
| `feeder/feed`          | Backend → ESP32 | `feed`                                                                   | Commands the ESP32 to run one feeding cycle  |

The ESP32 publishes sensor data when a configured change threshold is reached or after one hour. The current defaults are a `5 g` bowl-weight change and a `5%` hopper-level change.

---

## 🔌 API Endpoints (FastAPI Backend)

| Method | Endpoint           | Description                                                     | Request Body                                          | Example Response                                                 |
| ------ | ------------------ | --------------------------------------------------------------- | ----------------------------------------------------- | ---------------------------------------------------------------- |
| `GET`  | `/status`          | Gets current telemetry and today's feeding count                | None                                                  | `{"hopper_level": 85, "bowl_weight": 40.0, "today_feedings": 3}` |
| `POST` | `/feed`            | Publishes a remote feed command through MQTT                    | None                                                  | `{"success": true}`                                              |
| `POST` | `/chat`            | Sends a question and current feeder context to Gemini           | `{"message": "How many times was my cat fed today?"}` | `{"response": "Your cat has been fed 3 times today."}`           |
| `POST` | `/sync-user`       | Sets the signed-in user's email for low-food alerts             | `{"email": "user@example.com"}`                       | `{"status": "success", "email": "user@example.com"}`             |
| `GET`  | `/history`         | Gets feeding count and food consumption for the last seven days | None                                                  | `{"history": [{"date": "08-22", "count": 3, "eaten": 75.0}]}`    |
| `GET`  | `/predict-feeding` | Predicts tomorrow's meals and consumed food using EMA           | None                                                  | `{"predicted_grams": 72.5, "predicted_meals": 3}`                |

`POST /feed` returns HTTP `503` when the MQTT command cannot be published. `POST /chat` returns HTTP `400` for an invalid or empty message and HTTP `500` when feeder data, prediction, or Gemini processing fails.

---

## ⚙️ Setup & Installation Guide

### 1. Backend Setup (FastAPI)

1. Navigate to the backend directory:

   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:

   ```bash
   python -m venv venv
   ```

   On Windows PowerShell:

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

   On Linux or macOS:

   ```bash
   source venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create `backend/.env`:

   ```env
   MQTT_BROKER=YOUR_HIVEMQ_URL.hivemq.cloud
   MQTT_PORT=8883
   MQTT_USERNAME=YOUR_MQTT_USERNAME
   MQTT_PASSWORD=YOUR_MQTT_PASSWORD

   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_EMAIL=YOUR_GMAIL@gmail.com
   SMTP_PASSWORD=YOUR_GMAIL_APP_PASSWORD

   GEMINI_API_KEY=YOUR_GEMINI_API_KEY
   ```

5. Download a Firebase Admin service-account key and save it as `backend/serviceAccountKey.json`.

6. Start the backend from the `backend/` directory so the relative credential path resolves correctly:

   ```bash
   uvicorn app:app --reload --port 8000
   ```

The backend accepts frontend requests from `http://127.0.0.1:5500` and `http://localhost:5500`.

### 2. Frontend Setup

1. Replace the Firebase web configuration in `static/js/auth.js` if you are using your own Firebase project.
2. Enable Email/Password authentication in Firebase Authentication.
3. Serve the repository with VS Code Live Server or another static server on port `5500`.
4. Open `http://127.0.0.1:5500/templates/login.html`.

The frontend currently calls the backend at `http://127.0.0.1:8000`.

### 3. Firmware Setup & Wokwi Simulation

1. Open `firmware/include/Config.h` and configure:

   ```cpp
   static const char* MQTT_SERVER = "YOUR_HIVEMQ_URL.hivemq.cloud";
   static const char* MQTT_USER = "YOUR_MQTT_USERNAME";
   static const char* MQTT_PASS = "YOUR_MQTT_PASSWORD";
   ```

2. Adjust the sensor calibration values in `Config.h` for physical hardware when required.
3. For Wokwi, open the `firmware/` directory with the PlatformIO and Wokwi extensions, build the firmware, and start the simulation using `diagram.json` and `wokwi.toml`.
4. For a physical ESP32-S3, use PlatformIO to build and upload the firmware, then use the `SmartFeeder_WiFI` access point to provision Wi-Fi if the device cannot connect automatically.

---

## 📜 License

This project is developed for educational and research purposes.

# Smart Cat Feeder

Smart Cat Feeder is a full-stack IoT system designed to monitor food levels in the hopper, measure remaining food weight in the bowl, trigger remote or physical feedings, log feeding history to Cloud Firestore, send automated low-food email notifications, and provide an AI assistant powered by Google Gemini to answer questions about the feeder status.

> **Project Status:** In active development. ESP32 Firmware (including Wokwi simulation), FastAPI Backend (MQTT Client, Firebase Firestore, Gmail SMTP, Gemini AI integration), and Frontend Web Application are operational.

---

## 🎯 Key Features

- **Flexible Wi-Fi Provisioning:** Uses `WiFiManager` on ESP32 to configure network credentials on-demand without hardcoding SSID/Password.
- **Real-Time Telemetry:** Monitors remaining hopper food percentage (ultrasonic sensor) and bowl weight in grams (Load cell + HX711).
- **Dual Feeding Trigger:** Supports triggering food dispensation remotely via Web App or locally using a debounced physical push button.
- **Unified Event Logging:** Records all web and physical feeding events seamlessly into Cloud Firestore.
- **Automated Low-Food Alerts:** Sends email notifications via Gmail SMTP when hopper level drops to $\le 10\%$ (throttled to prevent email spamming).
- **Context-Aware AI Assistant:** Integrated Google Gemini AI assistant capable of answering cat feeding and feeder status questions using live system context.
- **Clean Responsive UI:** Lightweight web interface built with plain HTML5, CSS3, and JavaScript alongside Firebase Authentication.

---

## 🏗️ System Architecture

```text
 Ultrasonic Sensor ──┐
 HX711 Load Cell ───┼─> ESP32 / Wokwi <── Physical Push Button
 Servo Motor ───────┘       │
                            │ MQTT over TLS (Port 8883)
                            ▼
                   HiveMQ Cloud Broker
                            │
                            ▼
 Web Browser ──── HTTP ───> FastAPI Backend ──> Cloud Firestore
                            │    │
                            │    └──> Gmail SMTP Alerts
                            └───────> Google Gemini API
```

- **ESP32 Firmware:** Communicates securely with HiveMQ Cloud MQTT Broker over TLS (port 8883).
- **FastAPI Backend:** Acts as the central hub bridging MQTT messages, Cloud Firestore database, Email Service, and Gemini AI.
- **Frontend Web Application:** Interacts with FastAPI Backend via HTTP REST APIs and handles user authentication with Firebase Auth SDK.

---

## 🛠️ Technology Stack

| Layer / Component | Technology / Library |
| --- | --- |
| **Hardware / Firmware** | ESP32, PlatformIO, C++, WiFiManager, PubSubClient, HX711, Wokwi Simulator |
| **Messaging** | HiveMQ Cloud MQTT Broker (TLS Port 8883), Paho-MQTT (Python) |
| **Backend API** | Python 3, FastAPI, Uvicorn, Pydantic |
| **Database & Auth** | Firebase Authentication, Cloud Firestore (Firebase Admin SDK) |
| **AI Assistant & Alerts** | Google Gemini API (`google-genai`), Gmail SMTP (`smtplib`) |
| **Frontend Web** | HTML5, CSS3, JavaScript (ES6+), Firebase Auth SDK |

---

## 📁 Repository Layout

```text
smart-cat-feeder/
├── backend/                        # FastAPI Backend Application
│   ├── app.py                      # Core FastAPI app & API endpoints (/status, /feed, /chat, /sync-user)
│   ├── chatbot_service.py          # Google Gemini AI assistant service with feeder context
│   ├── email_service.py            # Automated Gmail SMTP low-food notification service
│   ├── firebase_service.py         # Firebase Admin SDK & Cloud Firestore logging
│   ├── mqtt_client.py              # Paho MQTT client for MQTT topic subscriptions & events
│   ├── requirements.txt            # Python dependencies
│   └── serviceAccountKey.json      # Firebase Service Account credentials (ignored in git)
├── firmware/                       # ESP32 Firmware (PlatformIO)
│   ├── include/
│   │   └── Config.h                # Central config (pins, MQTT credentials, topics, thresholds)
│   ├── src/
│   │   ├── main.cpp                # Firmware entry point: setup() and loop()
│   │   ├── Network.cpp / .h        # WiFiManager provisioning & TLS MQTT client connection
│   │   ├── LoadCell.cpp / .h       # HX711 weight reading and publishing
│   │   ├── Ultrasonic.cpp / .h     # Hopper food level distance measurement
│   │   ├── Dispenser.cpp / .h      # Servo motor dispenser control
│   │   └── Button.cpp / .h        # Physical button debouncing & trigger
│   ├── diagram.json                # Wokwi simulation diagram (ESP32 + Loadcell + Servo + Ultrasonic + Button)
│   ├── platformio.ini              # PlatformIO board & library configuration
│   └── wokwi.toml                  # Wokwi simulator setup
├── static/                         # Frontend Static Assets
│   ├── css/                        # Custom CSS stylesheets (chatbot, home, login_signup, logs, reset, style)
│   └── js/                         # Client-side JavaScript modules (auth, login, signup, home, logs, chatbot, auth-guard, logout)
├── templates/                      # HTML Web Templates
│   ├── chatbot.html                # AI Assistant chat page
│   ├── home.html                   # Main dashboard page (Hopper, Bowl status & Feed button)
│   ├── login.html                  # User login page
│   ├── logs.html                   # Feeding statistics & history logs page
│   └── signup.html                 # User signup page
├── .gitignore                      # Git ignore rules
└── README.md                       # Project documentation
```

---

## 📡 MQTT Topics & Payloads

| Topic | Direction | Sample Payload | Description |
| --- | --- | --- | --- |
| `feeder/hopper_status` | ESP32 → Backend | `{"hopper_level": 85}` | Report remaining food level percentage (%) |
| `feeder/bowl_weight` | ESP32 → Backend | `{"bowl_weight": 42}` | Report current bowl food weight (grams) |
| `feeder/physical_feed` | ESP32 → Backend | `{"event": "button_pressed"}` | Report physical push button feed event |
| `feeder/feed` | Backend → ESP32 | `"feed"` | Trigger servo dispenser to release one portion |

---

## 🔌 API Endpoints (FastAPI Backend)

| Method | Endpoint | Description | Request Body / Query | Example Response |
| --- | --- | --- | --- | --- |
| `GET` | `/status` | Retrieve current status and today's feedings | None | `{"hopper_level": 85, "bowl_weight": 40, "today_feedings": 3}` |
| `POST` | `/feed` | Trigger a remote feeding command | None | `{"accepted": true}` |
| `POST` | `/chat` | Chat with the contextual Gemini AI Assistant | `{"message": "How many times was the cat fed today?"}` | `{"response": "The feeder has dispensed food 3 times today..."}` |
| `POST` | `/sync-user` | Synchronize active user email with backend | `{"email": "user@example.com"}` | `{"status": "success", "email": "user@example.com"}` |

---

## ⚙️ Setup & Installation Guide

### 1. Backend Setup (FastAPI)

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```
3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the `backend/` directory with your credentials:
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
5. Place your Firebase Admin SDK `serviceAccountKey.json` into the `backend/` directory.
6. Start the FastAPI development server:
   ```bash
   uvicorn app:app --reload --port 8000
   ```

### 2. Frontend Setup

Serve the HTML files using Live Server (VS Code Extension) or any static HTTP server on port `5500`:
- Open `templates/login.html` or `templates/home.html` via Live Server at `http://127.0.0.1:5500/templates/login.html`.

### 3. Firmware Setup & Wokwi Simulation

- **Wokwi Simulation:** Open the `firmware/` directory in VS Code with the Wokwi Simulator extension installed, and run `diagram.json` / `wokwi.toml`.
- **Physical Hardware:** Open `firmware/` in PlatformIO, verify hardware configuration in `include/Config.h`, and run **Build & Upload** to your ESP32 board.

---

## 📜 License

This project is developed for educational and research purposes.

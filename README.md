# 🐱 Smart Cat Feeder - Full-Stack IoT & AI-Powered Automated Feeding System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141+-green.svg)](https://fastapi.tiangolo.com/)
[![Firebase Admin](https://img.shields.io/badge/Firebase-Admin-orange.svg)](https://firebase.google.com/)
[![HiveMQ TLS](https://img.shields.io/badge/HiveMQ-TLS%20MQTT-yellow.svg)](https://www.hivemq.com/cloud/)
[![Google Gemini](https://img.shields.io/badge/Gemini-3.5%20Flash-blue.svg)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Render Live](https://img.shields.io/badge/Render-Live%20Demo-purple)](https://smart-cat-feeder-304b.onrender.com)

An intelligent, full-stack IoT system for automated cat feeding, real-time food level monitoring, low-stock email alerts, historical consumption analytics, 7-day EMA demand prediction, and interactive Google Gemini-powered AI assistant integration.

## ✨ Key Features

- 🤖 **Context-Aware Gemini AI Assistant** - Advanced conversational AI powered by Google Gemini 3.5 Flash utilizing live feeder telemetry and historical predictions.
- 📡 **Real-Time Telemetry** - Ultrasonic sensor food level percentage monitoring & HX711 load cell bowl weight measurement.
- 🍽️ **Dual Feeding Trigger** - Dispenses food remotely from the web dashboard or locally via a debounced physical button.
- 🔒 **Encrypted TLS MQTT** - Secure communication through HiveMQ Cloud Broker over TLS (Port `8883`).
- 📊 **Firestore Event Logging** - Per-user isolated tracking of sensor logs, daily feeding counts, and total food eaten.
- 📈 **EMA Demand Prediction** - Exponential Moving Average predicting tomorrow's meal count and food consumption in grams.
- 📧 **Automated Low-Food Email Alerts** - Gmail SMTP email alerts triggered when food level drops below `10%` with anti-spam threshold guards.
- 🔐 **Firebase Authentication** - Multi-user isolation using Firebase Auth (Email/Password) with Firebase ID Token verification.
- 📶 **Flexible Wi-Fi Provisioning** - Dynamic Wi-Fi provisioning on ESP32-S3 using `WiFiManager` with fallback support.
- 🌊 **Live Web Dashboard** - Responsive UI with real-time status widgets and Chart.js 7-day historical analytics.

## 📁 Project Structure

```
smart-cat-feeder/
├── app.py -> backend/app.py       # FastAPI application entry point
├── Dockerfile                      # Production Docker container definition
├── Procfile                        # PaaS web process configuration
├── render.yaml                     # Render.com Blueprint deployment configuration
├── README.md                       # Comprehensive project documentation
│
├── backend/                        # Backend REST API Subsystem
│   ├── app.py                      # FastAPI routes, CORS, and static template serving
│   ├── chatbot_service.py          # Gemini AI context builder & prompt handler
│   ├── email_service.py            # Gmail SMTP low-food alert service
│   ├── firebase_service.py         # Firestore sensor logs, user data, and daily logs
│   ├── mqtt_client.py              # HiveMQ MQTT subscriber & publisher client
│   ├── prediction_model.py         # 7-day EMA prediction model
│   ├── requirements.txt            # Python dependencies
│   └── serviceAccountKey.json      # Firebase Admin Service Account key (ignored)
│
├── firmware/                       # ESP32-S3 PlatformIO Firmware Subsystem
│   ├── include/
│   │   └── Config.h                # Hardware pins, MQTT topics, thresholds, & scale calibration
│   ├── src/
│   │   ├── main.cpp                # Firmware setup & main loop
│   │   ├── Network.cpp / .h        # Wi-Fi & TLS MQTT client connection
│   │   ├── LoadCell.cpp / .h       # HX711 load cell weight measurement
│   │   ├── Ultrasonic.cpp / .h     # HC-SR04 ultrasonic hopper measurement
│   │   ├── Dispenser.cpp / .h      # Servo motor dispenser control
│   │   └── Button.cpp / .h         # Debounced physical push button
│   ├── diagram.json                # Wokwi circuit diagram & wiring definition
│   ├── platformio.ini              # PlatformIO environment configuration
│   └── wokwi.toml                  # Wokwi simulation configuration
│
├── static/                         # Frontend Static Assets
│   ├── css/                        # Custom page stylesheets
│   │   ├── reset.css              # Global CSS reset
│   │   ├── style.css              # Shared navigation & layout styles
│   │   ├── home.css               # Dashboard & widget styles
│   │   ├── logs.css               # Chart.js statistics styles
│   │   └── chatbot.css            # Gemini AI chat interface styles
│   └── js/                         # Frontend ES6 Modules
│       ├── api.js                 # Authenticated fetch wrapper with Firebase ID Token
│       ├── auth.js                # Firebase Auth SDK initialization
│       ├── auth-guard.js          # Authentication page route guard
│       ├── config.js              # Dynamic API base URL resolution
│       ├── home.js                # Dashboard status polling & feed trigger
│       ├── logs.js                # Chart.js 7-day history & EMA prediction display
│       ├── chatbot.js             # Gemini AI chatbot UI logic
│       ├── login.js               # Login form handler & user sync
│       ├── signup.js              # Registration form handler & user sync
│       └── logout.js              # Logout handler
│
└── templates/                      # HTML Views
    ├── home.html                   # Main dashboard & remote feed control view
    ├── logs.html                   # 7-day historical chart & prediction view
    ├── chatbot.html                # Gemini AI assistant chat view
    ├── login.html                  # User login view
    └── signup.html                 # User registration view
```

## 🚀 Quick Start

### 1. Prerequisites

- **Python 3.11+**
- **Firebase Project** (Email/Password Authentication & Cloud Firestore)
- **HiveMQ Cloud Account** (TLS Port `8883`)
- **Google Gemini API Key** (for AI Assistant)
- **Gmail Account & App Password** (for low-food email alerts)
- **PlatformIO & Wokwi Simulator** (for hardware / firmware development)

### 2. Install Dependencies

```bash
# Clone the repository
git clone https://github.com/chinnnn3107/smart-cat-feeder.git
cd smart-cat-feeder/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Set Up Databases & Services

**Firebase Setup:**
1. Go to [Firebase Console](https://console.firebase.google.com/) and create a project.
2. Enable **Email/Password** under Authentication -> Sign-in method.
3. Create a **Cloud Firestore** database.
4. Go to Project Settings -> Service Accounts -> Generate new private key, save as `backend/serviceAccountKey.json`.

**HiveMQ Cloud Setup:**
1. Create a cluster on [HiveMQ Cloud](https://www.hivemq.com/cloud/).
2. Create credentials under Access Management.
3. Note your broker hostname, TLS port (`8883`), username, and password.

### 4. Set Environment Variables

Create `.env` file in the `backend/` directory:
```bash
# HiveMQ Cloud MQTT Broker
MQTT_BROKER=your-cluster.hivemq.cloud
MQTT_PORT=8883
MQTT_USERNAME=your_mqtt_username
MQTT_PASSWORD=your_mqtt_password

# Gmail SMTP Low-Food Alerts
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password

# Google Gemini AI Key
GEMINI_API_KEY=your-google-gemini-api-key
```

### 5. Run the Application

**Development Mode (FastAPI):**
```bash
cd backend
uvicorn app:app --reload --port 8000
# Backend API available at http://127.0.0.1:8000
```

**Production Mode (Gunicorn):**
```bash
cd backend
gunicorn app:app --bind 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker --workers 2
```

**Docker Deployment:**
```bash
docker build -t smart-cat-feeder .
docker run -p 8000:8000 --env-file backend/.env smart-cat-feeder
```

## 🎯 Features & API Endpoints

### Authentication & User Sync
- `POST /sync-user` - Synchronize current Firebase user credentials for alerts & MQTT events.
  - Body: `{"email": "user@example.com"}`
  - Response: `{"status": "success", "uid": "...", "email": "user@example.com"}`

### Telemetry & Remote Feed
- `GET /status` - Retrieve current feeder metrics (hopper level %, bowl weight g, today's meal count).
  - Response: `{"hopper_level": 85, "bowl_weight": 42.0, "today_feedings": 3}`
- `POST /feed` - Trigger remote feed command to ESP32 over MQTT.
  - Response: `{"success": true}`

### AI Assistant & Prediction
- `POST /chat` - Interact with Gemini AI chatbot using live feeder telemetry.
  - Body: `{"message": "How many times was my cat fed today?"}`
  - Response: `{"response": "Your cat has been fed 3 times today."}`
- `GET /history` - Get 7-day feeding count & total food eaten in grams.
  - Response: `{"history": [{"date": "08-22", "count": 3, "eaten": 75.0}, ...]}`
- `GET /predict-feeding` - Get tomorrow's predicted meal count & food consumption using 7-day EMA.
  - Response: `{"predicted_grams": 72.5, "predicted_meals": 3}`

### MQTT Topics & Payloads

| Topic | Direction | Payload Example | Description |
| :--- | :--- | :--- | :--- |
| `feeder/hopper_status` | ESP32 → Backend | `{"hopper_level": 85}` | Reports remaining hopper food percentage |
| `feeder/bowl_weight` | ESP32 → Backend | `{"bowl_weight": 42.0, "device_id": "feeder-01"}` | Reports food bowl weight in grams |
| `feeder/physical_feed` | ESP32 → Backend | `{"event": "manual_feed", "status": "success"}` | Reports a physical feed button press |
| `feeder/feed` | Backend → ESP32 | `feed` | Commands ESP32 to rotate servo feed cycle |

---

## 🏗️ Architecture

### System Flow

```
┌─────────────┐
│   Client    │
│  (Web UI)   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│          FastAPI REST API           │
│  ┌──────────────────────────────┐   │
│  │   Auth Dependency            │   │
│  │   (Firebase ID Token)        │   │
│  └──────────────┬───────────────┘   │
│                 ▼                   │
│  ┌──────────────────────────────┐   │
│  │   Route Handlers             │   │
│  │   - /status                  │   │
│  │   - /feed                    │   │
│  │   - /chat (Gemini AI)        │   │
│  │   - /predict-feeding (EMA)   │   │
│  └──────────────┬───────────────┘   │
└─────────────────┼───────────────────┘
                  │
       ┌──────────┴──────────┐
       ▼                     ▼
┌──────────────┐      ┌─────────────┐
│ Cloud        │      │  MQTT Client│
│ Firestore    │      │  (Paho)     │
│              │      └──────┬──────┘
│ - Sensor Logs│             │ (TLS 8883)
│ - Daily Logs │             ▼
│ - Feed Events│      ┌─────────────┐
└──────────────┘      │  HiveMQ     │
                      │  Broker     │
                      └──────┬──────┘
                             │
                             ▼
                      ┌─────────────┐
                      │ ESP32-S3 /  │
                      │ Wokwi       │
                      └─────────────┘
```

### Component Architecture

#### 1. FastAPI Backend (`backend/app.py`)
- Verifies Firebase ID Tokens using `get_verified_uid` dependency.
- Mounts `/static` directory for CSS/JS assets and serves HTML views (`/`, `/templates/{page_name}`).
- Configured with `CORSMiddleware` for cross-origin request handling.

#### 2. MQTT Client Manager (`backend/mqtt_client.py`)
- Maintains encrypted TLS connection to HiveMQ Cloud.
- Listens to telemetry topics (`feeder/hopper_status`, `feeder/bowl_weight`, `feeder/physical_feed`).
- Updates Firestore logs per-user and triggers Gmail SMTP alerts when hopper food drops below `10%`.

#### 3. AI Assistant Engine (`backend/chatbot_service.py`)
- Constructs context prompts combining real-time hopper level, bowl weight, today's feeding count, and 7-day EMA prediction metrics.
- Invokes Google Gemini 3.5 Flash API (`google-genai`) to generate natural responses in the user's language.

#### 4. Firmware & Sensors (`firmware/`)
- **ESP32-S3 Controller:** Executes non-blocking main loop.
- **LoadCell (HX711):** Measures bowl weight and publishes when weight changes by `≥ 5g`.
- **Ultrasonic (HC-SR04):** Measures food hopper level and publishes when level changes by `≥ 5%`.
- **Dispenser (Servo):** Rotates 180° to dispense food upon web command or physical button press.

---

## 📊 Session State Management & Multi-User Isolation

### Firestore Data Hierarchy
```text
users/{user_id}/
├── sensor_logs/
│   └── {doc_id} -> {hopper_level, bowl_weight, timestamp}
├── feed_events/
│   └── {doc_id} -> {event: "web_feed" | "manual_feed", status, timestamp}
└── daily_logs/
    └── {YYYY-MM-DD} -> {date_string, total_feedings, total_eaten_grams, last_updated}
```

### Authentication State Flow
1. User logs in on frontend via Firebase Authentication (`login.js`).
2. Firebase returns a short-lived **Firebase ID Token**.
3. Frontend wrapper `authFetch` (`static/js/api.js`) automatically retrieves a fresh token and injects `Authorization: Bearer <token>` header into every API request.
4. Backend FastAPI dependency `get_verified_uid` verifies the token using Firebase Admin SDK and scopes all Firestore database reads/writes strictly to the authenticated `uid`.

---

## 🔧 Configuration

### Environment Variables Reference

| Variable | Required | Default | Description |
| :--- | :--- | :--- | :--- |
| `MQTT_BROKER` | Yes | - | HiveMQ Cloud broker hostname |
| `MQTT_PORT` | Yes | `8883` | HiveMQ TLS port |
| `MQTT_USERNAME` | Yes | - | HiveMQ username |
| `MQTT_PASSWORD` | Yes | - | HiveMQ password |
| `SMTP_HOST` | Yes | `smtp.gmail.com` | SMTP server host |
| `SMTP_PORT` | Yes | `587` | SMTP server TLS port |
| `SMTP_EMAIL` | Yes | - | Sender Gmail address |
| `SMTP_PASSWORD` | Yes | - | 16-character Gmail App Password |
| `GEMINI_API_KEY` | Yes | - | Google Gemini API Key |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Production | - | Raw or Base64 JSON content of service account key |

### Model & Sensor Calibration (`firmware/include/Config.h`)
```cpp
const float SCALE_CALIBRATION_FACTOR = 0.4208; // Calibrated for Wokwi 1:1 gram reading
const float MIN_WEIGHT_CHANGE_GRAMS  = 5.0;    // MQTT publish threshold for weight (5g)
const float MIN_HOPPER_CHANGE_PCT    = 5.0;    // MQTT publish threshold for hopper (5%)
const unsigned long PUBLISH_INTERVAL_MS = 3600000; // Force heartbeat publish interval (1 hour)
```

---

## 🧪 Testing

### 1. Unit & Syntax Testing
```bash
# Check Python syntax across backend files
python -m py_compile backend/app.py backend/firebase_service.py backend/mqtt_client.py
```

### 2. Manual API Testing (cURL)
```bash
# 1. Sync User Email
curl -X POST http://127.0.0.1:8000/sync-user \
  -H "Authorization: Bearer YOUR_FIREBASE_ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}'

# 2. Get Status
curl -X GET http://127.0.0.1:8000/status \
  -H "Authorization: Bearer YOUR_FIREBASE_ID_TOKEN"

# 3. Remote Feed Trigger
curl -X POST http://127.0.0.1:8000/feed \
  -H "Authorization: Bearer YOUR_FIREBASE_ID_TOKEN"
```

### 3. Wokwi Simulation Scenarios
1. **Hopper Level Change:** Click HC-SR04 sensor in Wokwi, adjust distance slider. Verify MQTT publish `feeder/hopper_status` and live web bar update.
2. **Bowl Weight Change:** Click HX711 load cell in Wokwi, adjust weight slider by `≥ 5g`. Verify MQTT publish `feeder/bowl_weight` and live web status update.
3. **Physical Button Trigger:** Press green button in Wokwi. Verify servo rotation and `manual_feed` event log in Firestore.
4. **Web Remote Feed Trigger:** Click **Feed** button on web dashboard (`home.html`). Verify `feeder/feed` topic receive and servo rotation in Wokwi.

---

## 🔍 How It Works

### 1. User Authentication & Token Handshake
```text
User Login Request (login.html)
    ↓
Firebase Authentication (Client SDK)
    ↓
Firebase ID Token Generated
    ↓
Send ID Token via Bearer Header -> FastAPI /sync-user
    ↓
Verify ID Token with Firebase Admin SDK
    ↓
Store User UID & Email in Server State
```

### 2. Telemetry Processing & Dual Triggering Pipeline
```text
ESP32 Sensors (Ultrasonic / HX711 Loadcell / Push Button)
    ↓
Publish to HiveMQ Cloud MQTT (TLS 8883)
    ↓
Paho MQTT Client Callback (backend/mqtt_client.py)
    ↓
Update Memory State & Log to Cloud Firestore (users/{uid}/...)
    ↓
Check Low-Food Threshold (< 10%) -> Trigger Gmail SMTP Alert
```

### 3. Gemini AI Context Building Pipeline
```text
User Prompt ("How much food did my cat eat today?")
    ↓
Fetch Latest Status (/status) + 7-Day History (/history)
    ↓
Compute 7-Day Exponential Moving Average (EMA) Prediction
    ↓
Assemble Context Prompt (Hopper Level + Bowl Weight + Feed Count + EMA)
    ↓
Invoke Google Gemini 3.5 Flash API (google-genai)
    ↓
Return Natural Language Response to Frontend Chat Interface
```

---

## 📝 Service Setup Guides

### 1. Getting Google Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Sign in with your Google account.
3. Click **Create API Key** and copy the generated key.
4. Set `GEMINI_API_KEY` in your `backend/.env` file.

### 2. Setting Up Gmail App Password
1. Go to your [Google Account Security Settings](https://myaccount.google.com/security).
2. Enable **2-Step Verification**.
3. Search for **App Passwords** -> Create a new App Password for "Mail".
4. Copy the 16-character password into `SMTP_PASSWORD` in `backend/.env`.

### 3. Setting Up Firebase Service Account Key
1. Go to [Firebase Console](https://console.firebase.google.com/).
2. Navigate to **Project Settings** -> **Service Accounts**.
3. Click **Generate new private key**.
4. Save the file as `backend/serviceAccountKey.json`.

### 4. Setting Up HiveMQ Cloud MQTT Broker
1. Go to [HiveMQ Cloud Console](https://console.hivemq.cloud/).
2. Sign in and create a free cluster.
3. Under **Access Management**, create a new MQTT User credentials.
4. Copy the Cluster Hostname into `MQTT_BROKER`, set `MQTT_PORT=8883`, and paste `MQTT_USERNAME` and `MQTT_PASSWORD` into `backend/.env`.

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'firebase_admin'"
**Cause:** `firebase-admin` library is missing from Python environment.  
**Solution:** Run `pip install -r backend/requirements.txt`.

### Error: "google.auth.exceptions.DefaultCredentialsError"
**Cause:** Firebase service account key not found on disk or environment.  
**Solution:** Verify `serviceAccountKey.json` exists in `backend/` directory locally, or set `FIREBASE_SERVICE_ACCOUNT_JSON` environment variable on Render Dashboard.

### Error: "Failed to connect to HiveMQ broker"
**Cause:** Incorrect HiveMQ URL, port, or TLS credentials.  
**Solution:** Verify `MQTT_BROKER`, `MQTT_PORT` (`8883`), `MQTT_USERNAME`, and `MQTT_PASSWORD` in `.env`.

### Error: "CORS origin not allowed"
**Cause:** Frontend domain not included in CORS middleware.  
**Solution:** `backend/app.py` is configured with `allow_origins=["*"]` for production flexibility.

---

## 🚢 Deployment

### Production Cloud Deployment (Render.com)

1. Create a new **Web Service** on [Render.com](https://render.com) and connect this repository.
2. Select **Python 3** as runtime environment.
3. Set **Build Command:**
   ```bash
   pip install -r backend/requirements.txt
   ```
4. Set **Start Command:**
   ```bash
   cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT
   ```
5. Add Environment Variables on Render Dashboard (`MQTT_BROKER`, `MQTT_PORT`, `MQTT_USERNAME`, `MQTT_PASSWORD`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_EMAIL`, `SMTP_PASSWORD`, `GEMINI_API_KEY`, `FIREBASE_SERVICE_ACCOUNT_JSON`).
6. Add your production Render URL (`smart-cat-feeder-304b.onrender.com`) to **Firebase Console -> Authentication -> Authorized Domains**.

---

## 📦 Dependencies

```text
fastapi>=0.141.1            # FastAPI REST framework
uvicorn>=0.52.1             # ASGI server
gunicorn>=21.2.0            # WSGI HTTP server
firebase-admin>=6.5.0       # Firebase Admin SDK & Firestore
paho-mqtt>=2.1.0            # MQTT client library
google-genai>=2.17.0        # Google Gemini AI SDK
python-dotenv>=1.2.2        # Environment variable loader
requests>=2.34.2            # HTTP client library
pydantic>=2.13.4            # Data validation
```

See [backend/requirements.txt](file:///d:/GitHub/smart-cat-feeder/backend/requirements.txt) for complete version specifications.

---

## 🎨 Customization

### Modify AI Chatbot Prompt (`backend/chatbot_service.py`)
```python
# System prompt definition in chatbot_service.py
# Customize persona, feeding advice tone, or specific response guidelines
```

### Modify Prediction Model Window (`backend/prediction_model.py`)
```python
# Adjust EMA smoothing factor or historical days window (default 7 days)
def calculate_ema(data_list: list, days: int = 7) -> float:
```

### Hardware Sensor Calibration (`firmware/include/Config.h`)
```cpp
const float SCALE_CALIBRATION_FACTOR = 0.4208; // Adjust for loadcell hardware
const float HOPPER_EMPTY_DISTANCE_CM = 30.0;   // Adjust for hopper container height
const float HOPPER_FULL_DISTANCE_CM  = 5.0;
```

---

## 🗺️ Roadmap

- [x] Hardware telemetry & ESP32 servo feeder control
- [x] HiveMQ Cloud TLS MQTT integration
- [x] FastAPI REST API & Firebase Firestore multi-user isolation
- [x] Google Gemini AI Assistant integration
- [x] Seven-day EMA feeding demand prediction
- [x] Production Cloud Deployment on Render.com
- [ ] Mobile Application (Flutter / React Native)
- [ ] Multi-Cat RFID Recognition System
- [ ] AI Camera Module for Appetite & Health Tracking

---

## 🤝 Contributing

Contributions make the open-source community an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 👥 Authors & Support

👑 **Lead Author:** [chinnnn3107](https://github.com/chinnnn3107)  
🤝 **Contributors:** [DatPham211](https://github.com/DatPham211), [thuhien1x1](https://github.com/thuhien1x1)

**For issues and questions:**
- 🐛 [Report Bugs](https://github.com/chinnnn3107/smart-cat-feeder/issues)
- 💡 [Request Features](https://github.com/chinnnn3107/smart-cat-feeder/issues)

---

## 📜 License & Copyright

Copyright © 2026 **chinnnn3107**. All rights reserved.  
This project is developed for educational, research, and non-commercial IoT application purposes under the MIT License.

---

## 🙏 Acknowledgments

- [Google Gemini AI API](https://ai.google.dev/)
- [Firebase Admin & Firestore](https://firebase.google.com/)
- [HiveMQ Cloud MQTT Broker](https://www.hivemq.com/cloud/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [PlatformIO](https://platformio.org/) & [Wokwi Simulator](https://wokwi.com/)
- [Chart.js](https://www.chartjs.org/)
- [Tourism-Chatbot Reference README](https://github.com/hienlongg/Tourism-Chatbot)

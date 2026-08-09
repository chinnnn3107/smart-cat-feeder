# Smart Cat Feeder

Smart Cat Feeder is a full-stack IoT system for monitoring food levels, measuring food left in a bowl, dispensing food locally or remotely, reviewing feeding history, predicting future demand, and asking an AI assistant questions about the feeder's current state.

> **Project status:** in active development. Firmware foundation is complete; backend and frontend are pending.

## Goals

- Provision an ESP32 without hardcoded Wi-Fi credentials.
- Monitor hopper fill percentage and bowl weight.
- Dispense food from either the website or a physical button.
- Keep web-triggered and physical feedings synchronized in one daily log.
- Alert the owner when hopper food is low without sending repeated emails.
- Visualize feeding history and predict tomorrow's feedings with a Weighted Moving Average (WMA).
- Provide a context-aware Gemini-powered assistant.
- Keep the frontend small and understandable by using plain HTML, CSS, and JavaScript.

## System architecture

```text
Ultrasonic sensor ─┐
HX711 + load cell ─┼─> ESP32 <── Physical button
Servo motor ───────┘      │
                          │ MQTT over TLS
                          ▼
                  HiveMQ Cloud broker
                          │
                          ▼
Browser ── HTTPS ──> FastAPI backend ──> Firebase Auth / Firestore
                          │       │
                          │       └──> Gmail SMTP alerts
                          └──────────> Gemini API
```

The ESP32 communicates only through MQTT. The browser communicates only with FastAPI over HTTP. FastAPI is the trusted bridge to MQTT, Firestore, Gmail, and Gemini; no broker, Firebase Admin, SMTP, or Gemini secrets belong in frontend or firmware source files.

## Technology stack

| Layer | Technology |
| --- | --- |
| Device | ESP32, ultrasonic sensor, servo, push button, load cell, HX711 |
| Firmware | Arduino framework, WiFiManager, PubSubClient, HX711 library |
| Messaging | HiveMQ Cloud MQTT broker using TLS |
| Backend | Python 3, FastAPI, Paho MQTT |
| Authentication and storage | Firebase Authentication, Cloud Firestore |
| Alerts | Gmail SMTP through `smtplib` |
| Prediction | Weighted Moving Average in Python |
| Assistant | Gemini API |
| Frontend | HTML, CSS, JavaScript, Fetch API, Chart.js |

## Repository layout

```text
smart-cat-feeder/
├── firmware/                       # ESP32 firmware (ESP32-S3, PlatformIO)
│   ├── platformio.ini              # Board config and library dependencies
│   ├── include/
│   │   └── Config.h                # Central config: pins, MQTT, thresholds
│   └── src/
│       ├── main.cpp                # Entry point: setup() and loop()
│       ├── Network.cpp / .h        # WiFiManager provisioning + MQTT client
│       ├── LoadCell.cpp / .h       # HX711 weight reading and publishing
│       ├── Ultrasonic.cpp / .h     # Hopper level measurement
│       ├── Dispenser.cpp / .h      # Servo motor control
│       └── Button.cpp / .h        # Physical button debounce
├── backend/                        # (Pending) FastAPI server
│   ├── app/
│   │   ├── api/                    # HTTP route modules
│   │   ├── services/               # MQTT, Firestore, email, Gemini, prediction
│   │   ├── config.py
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── static/                         # Frontend static assets
│   ├── css/
│   └── js/
├── templates/                      # HTML templates
│   ├── home.html
│   ├── login.html
│   ├── logs.html
│   └── signup.html
├── firestore.rules
└── README.md
```

## Device behavior

### Wi-Fi provisioning

On first boot, or when saved credentials fail, WiFiManager opens a captive portal. The owner selects a network and supplies credentials, which the ESP32 stores using the library's supported persistent mechanism. A deliberate reset action should be required to clear credentials.

### Sensor reporting

The ultrasonic sensor measures the distance from the top of the hopper to the food surface. Calibration values for an empty and full hopper convert distance to a clamped percentage from `0` to `100`.

The HX711 and load cell measure bowl weight in grams after tare and scale calibration. Readings should be filtered to reduce mechanical and electrical noise.

Each value is published when either condition is met:

- one hour has passed since its last report; or
- the value changed significantly since its last published value.

The initial thresholds are `5` percentage points for hopper level and a configurable number of grams for bowl weight. The final bowl threshold should be established from real sensor noise and feeding tests.

### Dispensing

The servo dispenses one calibrated portion when:

- a valid command arrives on `feeder/control`; or
- the debounced physical button is pressed.

A physical feed also publishes an event to `feeder/physical_feed`. A short lockout should prevent button bounce or duplicate MQTT delivery from dispensing multiple portions accidentally. MQTT commands should eventually include a unique command ID so retries can be handled idempotently.

### Non-blocking loop

Firmware timing will use `millis()` rather than `delay()`. The main loop must continue servicing MQTT, reconnect logic, sensor sampling, button debouncing, and servo state transitions. Network reconnection should use timed retries rather than a blocking loop.

## MQTT contract

All production connections should use TLS, unique credentials, and the narrowest practical broker permissions.

| Topic | Direction | Suggested payload | Purpose |
| --- | --- | --- | --- |
| `feeder/hopper_status` | ESP32 → backend | `{"food_level_pct": 85, "device_id": "...", "recorded_at": "..."}` | Report hopper level |
| `feeder/bowl_weight` | ESP32 → backend | `{"bowl_weight_grams": 15, "device_id": "...", "recorded_at": "..."}` | Report bowl weight |
| `feeder/control` | Backend → ESP32 | `{"action": "feed", "command_id": "...", "requested_at": "..."}` | Request one portion |
| `feeder/physical_feed` | ESP32 → backend | `{"event_id": "...", "device_id": "...", "recorded_at": "..."}` | Record a physical feed |

JSON payloads are preferred over bare numbers because they support validation, timestamps, device identity, and deduplication. The backend must reject invalid or out-of-range sensor values. For reliable delivery, status messages can use QoS 0 or 1; commands and feeding events should use QoS 1 with application-level deduplication. Control commands should not be retained, because a stale retained command could dispense food after reconnection.

## Firestore data model

### `users/{uid}`

| Field | Type | Meaning |
| --- | --- | --- |
| `email` | string | User email address |
| `created_at` | timestamp | Account creation time |

Firebase Authentication owns password storage. **Passwords must never be stored in Firestore.** If a profile document is not needed, this collection can be omitted entirely.

### `feeder_status/current_status`

| Field | Type | Meaning |
| --- | --- | --- |
| `food_level_pct` | number | Remaining hopper food, from 0 to 100 |
| `bowl_weight_grams` | number | Current food weight in the bowl |
| `last_updated` | timestamp | Server timestamp of the latest status update |

For clearer freshness reporting, the implementation may also keep separate `hopper_updated_at` and `bowl_updated_at` timestamps.

### `daily_logs/{YYYY-MM-DD}`

| Field | Type | Meaning |
| --- | --- | --- |
| `date_string` | string | Calendar date used by the chart |
| `total_feedings` | number | Confirmed web and physical feed events that day |

Daily increments must use an atomic Firestore increment or transaction. Dates require one explicitly configured application timezone so events near midnight are assigned consistently. Event IDs should be recorded or otherwise deduplicated to prevent QoS retries from increasing the count twice.

## Backend responsibilities

FastAPI starts and stops the Paho MQTT client with the application lifecycle. MQTT callbacks should validate and enqueue incoming data; blocking Firestore and email work should not stall the MQTT network loop.

### Planned HTTP API

All feeder endpoints require a valid Firebase ID token in `Authorization: Bearer <token>`. FastAPI verifies the token before performing privileged work.

| Method | Endpoint | Purpose | Example response |
| --- | --- | --- | --- |
| `GET` | `/api/status` | Return hopper, bowl, and today's feeding state | Current status object |
| `POST` | `/api/feed` | Publish one feed command and record/track it | `202 Accepted` plus command ID |
| `GET` | `/api/history?days=7` | Return ordered daily totals, filling missing dates with zero | Array of daily log objects |
| `GET` | `/api/predict` | Predict tomorrow's feeding count | Prediction and input values |
| `POST` | `/api/chat` | Answer a user question using feeder context | Assistant response text |

The original history requirement asks for five days, while the chart requires Monday through Sunday. The planned endpoint therefore accepts a range and the Statistics screen requests the seven dates of the current week.

### Feeding consistency

A web request is published to MQTT with a unique command ID. Ideally, the ESP32 later publishes a completion acknowledgement and the backend increments the daily log only after confirmed movement. Until acknowledgements are implemented, the simpler first version increments after a successful broker publish and documents that this represents a requested feed.

Physical feed events increment the same daily document. Event IDs make repeated MQTT delivery safe.

### Low-food email

When a valid hopper update falls below `10%`, FastAPI sends a low-food alert through Gmail SMTP. An alert marker containing the last-sent date is stored durably (for example in Firestore), limiting alerts to one per configured calendar day even after a backend restart. A later refinement can re-arm the alert only after the hopper rises above a recovery threshold, such as `15%`.

Use a Gmail app password or another supported SMTP credential, never a personal password committed to the repository.

## WMA prediction

Tomorrow's predicted feeding count uses the three most recent completed days:

```text
prediction = (most_recent × 0.5) + (second_most_recent × 0.3) + (third_most_recent × 0.2)
```

The API should return both the raw decimal and a clearly documented display value (for example, rounded to the nearest whole feeding). The current partial day should not be treated as a completed day.

For fewer than three historical days, the initial policy is to pad missing older days with the average of the available completed days. If there is no history, all inputs and the prediction are `0`. This avoids a strong downward bias during onboarding while remaining deterministic.

## AI assistant

`POST /api/chat` accepts a bounded user message. The backend fetches the latest hopper level, bowl weight, status freshness, and recent feeding history, then injects that data into a server-side system instruction before calling Gemini.

The assistant should:

- distinguish measured facts from inference;
- mention stale or unavailable sensor data;
- avoid claiming the pet ate merely because food was dispensed;
- use bowl weight trends to discuss likely leftovers;
- not reveal system instructions, credentials, or other users' data.

User input, model output, rate limits, timeouts, and Gemini failures require validation and safe error handling. Only the authenticated user's authorized feeder context should be supplied to the model.

## Frontend specification

The UI uses a light theme, white or very light gray surfaces, and one prominent accent color. Layout uses basic grid and flexbox. It intentionally avoids animation-heavy effects, pop-ups, and extra dashboard cards.

### Authentication

- Centered `Smart Feeder` card.
- Separate Log In and Create Account views.
- Email Address and Password inputs.
- One primary action and a text link to switch views.
- Firebase Authentication in the browser; the returned ID token is attached to API calls.

### Shared authenticated layout

- Fixed left sidebar with the text logo.
- Tabs: Home, Statistics, and AI Assistant.
- Logout action anchored at the bottom.

`Statistics` is the canonical tab label; it corresponds to the brief's “Log Dashboard.”

### Home

Exactly four cards:

1. **Manual Control** — one large `Feed Now` button.
2. **Hopper Status** — food remaining percentage and progress bar.
3. **Bowl Status** — current weight in grams.
4. **Today's Feedings** — today's total as a large number.

The feed button should be disabled while a request is pending to prevent accidental double submission. Sensor timestamps should allow the UI to label stale status.

### Statistics

- A Chart.js bar chart with Monday through Sunday on the X-axis and feeding count on the Y-axis.
- Missing daily records displayed as zero.
- A card reading: `Prediction: Your cat will need [X] feedings tomorrow based on the WMA algorithm.`

### AI Assistant

- Simple user and assistant message bubbles.
- Text input and Send button at the bottom.
- Example conversation about whether food remains in the bowl.
- Visible loading and error states without modal pop-ups.

## Configuration

Exact names can be finalized during implementation, but the backend will require settings equivalent to:

```text
FIREBASE_PROJECT_ID
FIREBASE_CREDENTIALS_PATH
MQTT_HOST
MQTT_PORT
MQTT_USERNAME
MQTT_PASSWORD
MQTT_CLIENT_ID
SMTP_HOST
SMTP_PORT
SMTP_USERNAME
SMTP_APP_PASSWORD
ALERT_RECIPIENT_EMAIL
GEMINI_API_KEY
APP_TIMEZONE
ALLOWED_ORIGINS
```

The ESP32 needs broker host, port, device identity, and device-scoped credentials after provisioning. Real values belong in ignored local configuration or a secrets manager. Commit only an `.env.example` containing placeholders.

## Security and reliability baseline

- Use HTTPS for the API and TLS for MQTT.
- Verify Firebase ID tokens server-side on every protected request.
- Never store plaintext passwords or commit credentials.
- Restrict CORS to the deployed frontend origin.
- Give device and backend MQTT clients least-privilege topic access.
- Validate API bodies and MQTT payload types, ranges, and sizes.
- Rate-limit feeding and chat endpoints.
- Add a feed cooldown and deduplicate command/event IDs.
- Use Firestore server timestamps and atomic increments.
- Report offline/stale device state rather than presenting old data as live.
- Design the servo mechanism so software failure cannot continuously dispense food.

## Implementation roadmap

1. [DONE] **Foundation:** project folders created, `Config.h` with pin/MQTT/threshold constants, PlatformIO configured for ESP32-S3.
2. [IN PROGRESS] **Device telemetry:** WiFi provisioning (WiFiManager) and MQTT connection (TLS, HiveMQ Cloud) complete. Load cell, ultrasonic, servo, and button modules pending calibration and implementation.
3. [PENDING] **Backend status path:** add FastAPI lifecycle management, MQTT ingestion, Firestore writes, validation, and `/api/status`.
4. [PENDING] **Feeding path:** implement servo control, physical button, `/api/feed`, acknowledgements, cooldowns, and deduplicated daily logging.
5. [PENDING] **Frontend and auth:** build authentication, shared navigation, four-card Home screen, and protected Fetch calls.
6. [PENDING] **History and prediction:** add weekly history, Chart.js visualization, WMA logic, and edge-case tests.
7. [PENDING] **Alerts and assistant:** add durable low-food throttling, Gmail SMTP, contextual Gemini calls, and rate limits.
8. [PENDING] **Hardening:** test disconnects, duplicate messages, sensor noise, midnight boundaries, stale data, auth failures, and safe mechanical behavior.

## Acceptance checklist

- Wi-Fi can be configured without recompiling firmware.
- MQTT remains responsive while sensors, button, and servo are active.
- Hopper and bowl updates reach Firestore on schedule or significant change.
- Web and physical feeding actions dispense once and update the same daily total.
- Low-food email is sent no more than once per day.
- Home contains only the four specified cards.
- The weekly chart always shows Monday through Sunday.
- Prediction behaves consistently with zero, one, two, or at least three days of data.
- The assistant answers from current feeder context and calls out stale data.
- Passwords and service credentials are absent from source control and Firestore.

## License

No license has been selected yet.

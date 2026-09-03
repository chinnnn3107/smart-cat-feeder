import { authFetch } from "./api.js";
import { API_BASE_URL } from "./config.js";

// Cache DOM element references for feeder UI dashboard
const feedNumber = document.getElementById("feedings-number");
const bowlWeight = document.getElementById("bowl-weight");
const hopperPercent = document.getElementById("hopper-percent");
const progressFill = document.getElementById("progress-fill");
const feedButton = document.getElementById("feed-button");
const feedNotification = document.getElementById("feed-notification");

// Fetch telemetry metrics from backend API (/status) and update UI widgets
async function getStatus() {
  const response = await authFetch(`${API_BASE_URL}/status`, {
    method: "GET",
  });

  const data = await response.json();

  // Update DOM with retrieved telemetry data
  feedNumber.textContent = data.today_feedings;
  hopperPercent.textContent = data.hopper_level + "%";
  progressFill.style.width = data.hopper_level + "%";
  bowlWeight.textContent = data.bowl_weight;
}

// Send a manual feeding request to the backend API (/feed)
async function requestFeed() {
  try {
    const response = await authFetch(`${API_BASE_URL}/feed`, {
      method: "POST",
    });

    const data = await response.json();
    const success = response.ok && data.success;

    feedNotification.textContent = success
      ? "Feed request sent!"
      : "Failed to send command!";

    feedNotification.style.color = success ? "green" : "red";
  } catch (error) {
    feedNotification.textContent = "Cannot connect to server!";
    feedNotification.style.color = "red";
  }

  setTimeout(() => {
    feedNotification.textContent = "";
  }, 3000);
}

// Bind event listener to manual feed button
feedButton.addEventListener("click", requestFeed);

// Auto-refresh every 5 seconds
setInterval(getStatus, 5000);

// Load initial feeder telemetry metrics when DOM content is fully loaded
window.addEventListener("DOMContentLoaded", getStatus);

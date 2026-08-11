// Cache DOM element references for feeder UI dashboard
const feedNumber = document.getElementById("feedings-number");
const bowlWeight = document.getElementById("bowl-weight");
const hopperPercent = document.getElementById("hopper-percent");
const progressFill = document.getElementById("progress-fill");
const feedButton = document.getElementById("feed-button");
const feedNotification = document.getElementById("feed-notification");

// Fetch telemetry metrics from backend API (/status) and update UI widgets
async function getStatus() {
  const response = await fetch("http://127.0.0.1:8000/status", {
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
  const response = await fetch("http://127.0.0.1:8000/feed", {
    method: "POST",
  });

  // Parse API response
  const data = await response.json();

  if (data.accepted) {
    console.log("Feed request accepted");
  }
}

/*
  Query feeding lifecycle status from backend API (/feed/status)
  Updates notification display and recursively polls if status is 'pending'
*/
async function getFeedStatus() {
  const response = await fetch("http://127.0.0.1:8000/feed/status", {
    method: "GET",
  });

  const data = await response.json();

  // Case 1: Feeding successfully completed by hardware
  if (data.status === "completed") {
    feedNotification.textContent = "Feed successfully!";
    feedNotification.style.color = "green";

    // Auto-clear notification after 3 seconds
    setTimeout(function () {
      feedNotification.textContent = "";
    }, 3000);

    return;
  }

  // Case 2: Feeding operation is in progress (poll again after 1 second)
  if (data.status === "pending") {
    feedNotification.textContent = "Feeding...";
    feedNotification.style.color = "gray";

    setTimeout(getFeedStatus, 1000);
    return;
  }

  // Case 3: Feeding operation failed or timed out
  feedNotification.textContent = "Feed failed!";
  feedNotification.style.color = "red";

  // Auto-clear notification after 3 seconds
  setTimeout(function () {
    feedNotification.textContent = "";
  }, 3000);
}

// Trigger manual feed operation workflow: request feed and monitor status
async function feedNow() {
  await requestFeed();
  await getFeedStatus();
}

// Bind event listener to manual feed button
feedButton.addEventListener("click", feedNow);

// Auto-refresh every 5 seconds
setInterval(getStatus, 5000);

// Load initial feeder telemetry metrics when DOM content is fully loaded
window.addEventListener("DOMContentLoaded", getStatus);

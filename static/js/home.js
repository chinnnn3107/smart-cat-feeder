const feedNumber = document.getElementById("feedings-number");
const bowlWeight = document.getElementById("bowl-weight");
const hopperPercent = document.getElementById("hopper-percent");
const progressFill = document.getElementById("progress-fill");
const feedButton = document.getElementById("feed-button");
const feedNotification = document.getElementById("feed-notification");

// Get status of the feeder
async function getStatus() {
  const response = await fetch("http://127.0.0.1:8000/status", {
    method: "GET",
  });

  const data = await response.json();

  feedNumber.textContent = data.today_feedings;
  hopperPercent.textContent = data.hopper_level + "%";
  progressFill.style.width = data.hopper_level + "%";
  bowlWeight.textContent = data.bowl_weight;
}

// Send a manual feeding request
async function requestFeed() {
  const response = await fetch("http://127.0.0.1:8000/feed", {
    method: "POST",
  });

  // Read the API response and notify the user only after a successful request
  const data = await response.json();

  if (data.accepted) console.log("Feed request accepted");
}

// Get feeding status
async function getFeedStatus() {
  const response = await fetch("http://127.0.0.1:8000/feed/status", {
    method: "GET",
  });

  const data = await response.json();

  if (data.status === "completed") {
    feedNotification.textContent = "Feed successfully!";
    feedNotification.style.color = "green";
  } else if (data.status === "pending") {
    feedNotification.textContent = "Feeding...";
    feedNotification.style.color = "gray";
  } else {
    feedNotification.textContent = "Feed failed!";
    feedNotification.style.color = "red";
  }
}

async function feedNow() {
  await requestFeed();
  await getFeedStatus();
}

// Click Feed button
feedButton.addEventListener("click", feedNow);

// Run getStatus when page loads
window.addEventListener("DOMContentLoaded", getStatus);

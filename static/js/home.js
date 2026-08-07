const feedNumber = document.getElementById("feedings-number");
const bowlWeight = document.getElementById("bowl-weight");
const hopperPercent = document.getElementById("hopper-percent");
const progressFill = document.getElementById("progress-fill");
const feedButton = document.getElementById("feed-button");

// Send a manual feeding request to the backend when the user clicks the button.
async function feedNow() {
  const response = await fetch("http://127.0.0.1:8000/feed", {
    method: "POST",
  });

  // Read the API response and notify the user only after a successful request.
  const data = await response.json();

  if (data.success) alert("Feed successful");
}

// Connect the feed button click to the API request handler.
feedButton.addEventListener("click", feedNow);

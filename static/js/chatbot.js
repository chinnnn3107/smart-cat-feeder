// Cache DOM element references for chatbot UI
const inputMessage = document.getElementById("input-message");
const chatForm = document.getElementById("chat-form");
const messages = document.getElementById("messages");

// Create and display a new message in the chat container
function addMessage(text, className) {
  const message = document.createElement("div");

  message.className = className;
  message.textContent = text;

  // Add the new message to the messages container
  messages.appendChild(message);

  messages.scrollTop = messages.scrollHeight;
}

async function handleSendMessage(event) {
  // Prevent the form from refreshing the page
  event.preventDefault();

  const message = inputMessage.value.trim();

  if (message === "") return;

  addMessage(message, "user-message");

  // Clear the input field
  inputMessage.value = "";

  const response = await fetch("http://127.0.0.1:8000/chat", {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      message: message,
    }),
  });

  // Display Gemini's response
  const data = await response.json();
  addMessage(data.response, "bot-message");
}

// Listen for form submission
chatForm.addEventListener("submit", handleSendMessage);

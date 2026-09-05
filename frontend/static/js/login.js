import { auth } from "./auth.js";
import { signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";
import { API_BASE_URL } from "./config.js";

// Get elements from the DOM
const loginForm = document.getElementById("login-form");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const loginMessage = document.getElementById("login-message");
const loginButton = document.getElementById("login-button");

async function handleLogin(event) {
  // Prevent the browser from reloading the page
  event.preventDefault();

  // Get email and password from input fields
  const email = emailInput.value.trim();
  const password = passwordInput.value;

  // Clear the previous message
  loginMessage.textContent = "";

  showLoading();

  try {
    // Login with firebase
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;

    // Get the Firebase ID Token and send it to the backend to sync the current user.
    // The backend verifies the token and stores the user's uid + email for
    // attributing physical button press events (from ESP32 via MQTT).
    const idToken = await user.getIdToken();
    const response = await fetch(`${API_BASE_URL}/sync-user`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${idToken}`,
      },
    });

    const result = await response.json();

    if (!response.ok || result.status !== "success") {
      throw new Error(result.message || "Failed to sync user");
    }

    loginMessage.textContent = "Login successful!";
    loginMessage.style.color = "green";
    loginButton.textContent = "Redirecting...";

    setTimeout(function () {
      window.location.href = "./home.html"; // Go to Home page
    }, 2000);
  } catch (error) {
    console.error(error.code, error.message);
    loginMessage.textContent = getFirebaseError(error.code);
    loginMessage.style.color = "red";
    hideLoading();
  }
}

function showLoading() {
  loginButton.disabled = true;
  loginButton.textContent = "Logging in...";
}

function hideLoading() {
  loginButton.disabled = false;
  loginButton.textContent = "Log in";
}

// Reference: Firebase Authentication JavaScript API
function getFirebaseError(error) {
  switch (error) {
    case "auth/invalid-email":
      return "Invalid email format.";

    case "auth/invalid-credential":
      return "Incorrect email or password.";

    case "auth/user-not-found":
      return "Account does not exist.";

    case "auth/wrong-password":
      return "Incorrect password.";

    case "auth/missing-password":
      return "Please enter your password.";

    case "auth/missing-email":
      return "Please enter your email.";

    case "auth/network-request-failed":
      return "Network error. Please try again.";

    case "auth/too-many-requests":
      return "Too many failed attempts. Please try again later.";

    default:
      return "Authentication failed. Please try again.";
  }
}

loginForm.addEventListener("submit", handleLogin);

window.addEventListener("pageshow", () => {
  loginForm.reset();
  loginMessage.textContent = "";
  hideLoading();
});

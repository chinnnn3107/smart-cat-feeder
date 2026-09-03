import { auth } from "./auth.js";
import { createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";
import { API_BASE_URL } from "./config.js";

// Get elements from the DOM
const signupForm = document.getElementById("signup-form");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const signupMessage = document.getElementById("signup-message");
const signupButton = document.getElementById("signup-button");

async function handleSignup(event) {
  // Prevent the browser from reloading the page
  event.preventDefault();

  // Get email and password from input fields
  const email = emailInput.value.trim();
  const password = passwordInput.value;

  // Clear the previous message
  signupMessage.textContent = "";

  showLoading();

  try {
    // Create a new user account
    const userCredential = await createUserWithEmailAndPassword(
      auth,
      email,
      password,
    );
    const user = userCredential.user;

    const response = await fetch(`${API_BASE_URL}/sync-user`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: user.email }),
    });

    const result = await response.json();

    if (!response.ok || result.status !== "success") {
      throw new Error(result.message || "Failed to sync user");
    }

    signupMessage.textContent = "Account created successfully!";
    signupMessage.style.color = "green";
    signupButton.textContent = "Redirecting...";

    setTimeout(function () {
      window.location.href = "./home.html"; // Go to Home page
    }, 2000);
  } catch (error) {
    console.error(error.code, error.message);
    signupMessage.textContent = getFirebaseError(error.code);
    signupMessage.style.color = "red";
    hideLoading();
  }
}

function showLoading() {
  signupButton.disabled = true;
  signupButton.textContent = "Signing up...";
}

function hideLoading() {
  signupButton.disabled = false;
  signupButton.textContent = "Sign up";
}

// Reference: Firebase Authentication JavaScript API
function getFirebaseError(error) {
  switch (error) {
    case "auth/invalid-email":
      return "Invalid email format.";

    case "auth/email-already-in-use":
      return "This email is already registered.";

    case "auth/weak-password":
      return "Password must be at least 6 characters.";

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

signupForm.addEventListener("submit", handleSignup);

window.addEventListener("pageshow", () => {
  signupForm.reset();
  signupMessage.textContent = "";
  hideLoading();
});

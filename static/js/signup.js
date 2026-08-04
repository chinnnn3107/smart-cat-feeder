const signupForm = document.getElementById("signup-form");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const signupMessage = document.getElementById("signup-message");
const signupButton = document.getElementById("signup-button");

function validation(email, password) {
  // Fake validation (HTML already handle the required fields)
  if (email === "" || password === "") return false;
  return true;
  // TODO: Add Firebase validation
}

function handleSignup(event) {
  event.preventDefault();

  const email = emailInput.value.trim();
  const password = passwordInput.value;

  // Fake validation (HTML already handle the required fields)
  if (!validation(email, password)) {
    signupMessage.textContent = "Please fill out all the fields.";
    signupMessage.style.color = "red";
    return;
  }

  showLoading();
  // Fake backend
  setTimeout(function () {
    hideLoading();
    signupMessage.textContent = "Frontend validation successful.";
    signupMessage.style.color = "green";
  }, 2000);
  // TODO: Replace this simulation with a request to FastAPI
  // TODO: Add Firebase Authentication
}

function showLoading() {
  signupButton.disabled = true;
  signupButton.textContent = "Signing up...";
}

function hideLoading() {
  signupButton.disabled = false;
  signupButton.textContent = "Sign up";
}

signupForm.addEventListener("submit", handleSignup);

const loginForm = document.getElementById("login-form");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const loginMessage = document.getElementById("login-message");
const loginButton = document.getElementById("login-button");

function validation(email, password) {
  if (email === "" || password === "") return false;
  return true;
  // TODO: Add Firebase validation
}

function handleLogin(event) {
  event.preventDefault();

  const email = emailInput.value.trim();
  const password = passwordInput.value;

  if (!validation(email, password)) {
    loginMessage.textContent = "Please fill out all the fields.";
    loginMessage.style.color = "red";
    return;
  }

  showLoading();
  // Fake backend
  setTimeout(function () {
    hideLoading();
    loginMessage.textContent = "Frontend validation successful.";
    loginMessage.style.color = "green";
  }, 2000);
  // TODO: Replace this simulation with a request to FastAPI
  // TODO: Add Firebase Authentication
}

function showLoading() {
  loginButton.disabled = true;
  loginButton.textContent = "Logging in...";
}

function hideLoading() {
  loginButton.disabled = false;
  loginButton.textContent = "Log in";
}

loginForm.addEventListener("submit", handleLogin);

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import {
  getAuth,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

// CONNECT TO DATABASE
const firebaseConfig = {
  apiKey: "AIzaSyBDd7fqCPWelNWHMmMAiZk1LUteXBg7MGU",
  authDomain: "smart-pet-feeder-777a.firebaseapp.com",
  projectId: "smart-pet-feeder-777a",
  storageBucket: "smart-pet-feeder-777a.firebasestorage.app",
  messagingSenderId: "631526800695",
  appId: "1:631526800695:web:0ba09d6e7d69816ff6aeb2",
  measurementId: "G-DSMSYY4M42"
};

// initialize app and auth services
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// LOGIN
const loginForm = document.getElementById('login-form');
if (loginForm) {
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault(); // stop page refresh

    // get email and password from input fields
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
      // login with firebase
      await signInWithEmailAndPassword(auth, email, password);
      alert("Login successful!");
      // Redirect when Home page is ready
    } catch (error) {
      alert("Login failed: " + error.message);
    }
  });
}

// SIGNUP
const signupForm = document.getElementById('signup-form');
if (signupForm) {
  signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
      // create a new user account
      await createUserWithEmailAndPassword(auth, email, password);
      alert("Account created successfully!");
      window.location.href = "./login.html"; // go to login page
    } catch (error) {
      alert("Signup failed: " + error.message);
    }
  });
}
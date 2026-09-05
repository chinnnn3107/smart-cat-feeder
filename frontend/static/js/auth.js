import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

// Initialize Firebase
const firebaseConfig = {
  apiKey: "AIzaSyBDd7fqCPWelNWHMmMAiZk1LUteXBg7MGU",
  authDomain: "smart-pet-feeder-777a.firebaseapp.com",
  projectId: "smart-pet-feeder-777a",
  storageBucket: "smart-pet-feeder-777a.firebasestorage.app",
  messagingSenderId: "631526800695",
  appId: "1:631526800695:web:0ba09d6e7d69816ff6aeb2",
  measurementId: "G-DSMSYY4M42",
};

// Initialize app and auth services
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

export { auth };

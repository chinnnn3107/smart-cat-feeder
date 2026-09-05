import { auth } from "./auth.js";
import { onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

// Listening for state changes in the user's authentication
onAuthStateChanged(auth, (user) => {
    if (!user) {
        // Using replace() to replace the browser's history, preventing the user from clicking the Back button
        window.location.replace("../templates/login.html");
    }
});
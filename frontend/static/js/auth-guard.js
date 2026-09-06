import { auth } from "./auth.js";
import { onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

// Hide page content while checking authentication to prevent Flash of Unauthenticated Content (FOUC)
document.documentElement.style.visibility = "hidden";

// Listening for state changes in the user's authentication
onAuthStateChanged(auth, (user) => {
    if (!user) {
        // Using replace() to replace the browser's history, preventing the user from clicking the Back button
        window.location.replace("../templates/login.html");
    } else {
        // Reveal page content once authenticated
        document.documentElement.style.visibility = "visible";
    }
});
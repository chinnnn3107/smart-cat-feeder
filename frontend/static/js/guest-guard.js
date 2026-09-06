import { auth } from "./auth.js";
import { onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

// If user is already authenticated, redirect away from auth pages (login/signup) to home
onAuthStateChanged(auth, (user) => {
    if (user) {
        window.location.replace("../templates/home.html");
    }
});

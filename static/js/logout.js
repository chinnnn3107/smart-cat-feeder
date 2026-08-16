import { signOut } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";
import { auth } from "./auth.js";

// Get elements from the DOM
const logoutButton = document.getElementById("logout-button");
if (logoutButton) {
    logoutButton.addEventListener("click", handleLogout);
}

function handleLogout(event) {
    // Prevent the browser from reloading the page
    event.preventDefault();

    signOut(auth).then(() => {
        console.log("User signed out successfully.");
        // Redirect the user back to the login page
        window.location.href = "../templates/login.html";
    }).catch((error) => {
        console.error("Error signing out: ", error);
        alert("Failed to log out. Please try again.");
    });
}
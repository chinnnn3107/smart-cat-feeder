import { auth } from "./auth.js";

/**
 * Authenticated fetch wrapper.
 * Automatically fetches a fresh Firebase ID Token and injects it into
 * the Authorization header before every API request.
 *
 * @param {string} url - The API endpoint URL.
 * @param {RequestInit} options - Standard fetch options (method, body, headers, etc.)
 * @returns {Promise<Response>}
 */
export async function authFetch(url, options = {}) {
  // Wait for Firebase Auth to finish initialising before reading currentUser.
  // Without this, auth.currentUser is null at DOMContentLoaded time and all
  // API calls silently fail on first page load.
  await auth.authStateReady();

  const user = auth.currentUser;

  if (!user) {
    throw new Error("No authenticated user. Please log in.");
  }

  // Always get a fresh token (Firebase caches and auto-refreshes it)
  const token = await user.getIdToken();

  return fetch(url, {
    ...options,
    headers: {
      ...(options.headers || {}),
      Authorization: `Bearer ${token}`,
    },
  });
}

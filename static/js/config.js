/**
 * Dynamic API Base URL configuration.
 *
 * In production (when served by FastAPI or deployed on a unified domain),
 * relative path "" is used.
 * If running on a separate frontend host (e.g. Live Server), fallback to backend at http://127.0.0.1:8000.
 */

const isSeparateDevServer = window.location.port === "5500" || window.location.port === "3000";

export const API_BASE_URL = isSeparateDevServer 
  ? "http://127.0.0.1:8000" 
  : window.location.origin;

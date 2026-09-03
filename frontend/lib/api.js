import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_URL,
});

// Attach the stored JWT (if any) to every outgoing request automatically.
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = window.localStorage.getItem("itbis_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export function saveSession(token, role) {
  window.localStorage.setItem("itbis_token", token);
  window.localStorage.setItem("itbis_role", role);
}

export function clearSession() {
  window.localStorage.removeItem("itbis_token");
  window.localStorage.removeItem("itbis_role");
}

export function getStoredRole() {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("itbis_role");
}

export function isLoggedIn() {
  if (typeof window === "undefined") return false;
  return Boolean(window.localStorage.getItem("itbis_token"));
}

export default api;

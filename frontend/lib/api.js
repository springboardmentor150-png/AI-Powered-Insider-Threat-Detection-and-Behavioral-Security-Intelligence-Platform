import axios from "axios";

/*
|--------------------------------------------------------------------------
| API CONFIGURATION
|--------------------------------------------------------------------------
*/

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

/*
|--------------------------------------------------------------------------
| REQUEST INTERCEPTOR
|--------------------------------------------------------------------------
| Automatically attaches the stored JWT to every API request.
*/

api.interceptors.request.use(
  (config) => {
    if (typeof window !== "undefined") {
      const token = window.localStorage.getItem("itbis_token");

      if (token) {
        config.headers = config.headers || {};
        config.headers.Authorization = `Bearer ${token}`;
      }
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/*
|--------------------------------------------------------------------------
| RESPONSE INTERCEPTOR
|--------------------------------------------------------------------------
| If backend returns 401, the user's session is no longer valid.
| Clear the session and send the user back to login.
*/

api.interceptors.response.use(
  (response) => {
    return response;
  },

  (error) => {
    if (typeof window !== "undefined") {
      const status = error.response?.status;

      if (status === 401) {
        clearSession();

        /*
         * Avoid repeatedly redirecting if the user is
         * already on the login page.
         */
        if (window.location.pathname !== "/login") {
          window.location.replace("/login");
        }
      }
    }

    return Promise.reject(error);
  }
);

/*
|--------------------------------------------------------------------------
| SAVE LOGIN SESSION
|--------------------------------------------------------------------------
*/

export function saveSession(token, role) {
  if (typeof window === "undefined") {
    return;
  }

  if (token) {
    window.localStorage.setItem("itbis_token", token);
  }

  if (role) {
    window.localStorage.setItem("itbis_role", role);
  }
}

/*
|--------------------------------------------------------------------------
| CLEAR LOGIN SESSION
|--------------------------------------------------------------------------
*/

export function clearSession() {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.removeItem("itbis_token");
  window.localStorage.removeItem("itbis_role");
}

/*
|--------------------------------------------------------------------------
| GET STORED TOKEN
|--------------------------------------------------------------------------
*/

export function getToken() {
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage.getItem("itbis_token");
}

/*
|--------------------------------------------------------------------------
| GET STORED ROLE
|--------------------------------------------------------------------------
*/

export function getStoredRole() {
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage.getItem("itbis_role");
}

/*
|--------------------------------------------------------------------------
| CHECK LOGIN STATUS
|--------------------------------------------------------------------------
*/

export function isLoggedIn() {
  if (typeof window === "undefined") {
    return false;
  }

  const token = window.localStorage.getItem("itbis_token");

  return Boolean(token);
}

/*
|--------------------------------------------------------------------------
| LOGOUT
|--------------------------------------------------------------------------
| Clears the session and redirects to login.
|--------------------------------------------------------------------------
*/

export function logout() {
  if (typeof window === "undefined") {
    return;
  }

  clearSession();

  window.location.replace("/login");
}

/*
|--------------------------------------------------------------------------
| DEFAULT API EXPORT
|--------------------------------------------------------------------------
*/

export default api;
export interface AuthUser {
  id: number;
  email: string;
  role: string;
}

export interface AuthSession {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

const TOKEN_KEY = "itbis_access_token";
const USER_KEY = "itbis_user_profile";

export function setAuthSession(session: AuthSession): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(TOKEN_KEY, session.access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(session.user));
  } catch (err) {
    console.error("Failed to persist auth session:", err);
  }
}

export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function getAuthUser(): AuthUser | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function clearAuthSession(): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  } catch (err) {
    console.error("Failed to clear auth session:", err);
  }
}

export function isAuthenticated(): boolean {
  const token = getAuthToken();
  if (!token) return false;
  try {
    const payload = parseJwtPayload(token);
    if (!payload || !payload.exp) return !!token;
    const now = Math.floor(Date.now() / 1000);
    if ((payload.exp as number) <= now) {
      clearAuthSession();
      return false;
    }
    return true;
  } catch {
    return !!token;
  }
}

export function parseJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const base64Url = token.split(".")[1];
    if (!base64Url) return null;
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );
    return JSON.parse(jsonPayload);
  } catch {
    return null;
  }
}

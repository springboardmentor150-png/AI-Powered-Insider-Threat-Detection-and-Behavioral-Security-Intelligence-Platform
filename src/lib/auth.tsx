/**
 * Authentication context.
 *
 * When VITE_API_URL is set the signIn function calls the real
 * POST /auth/login endpoint and stores the returned JWT.
 * Without a backend URL it falls back to mock auth (any credentials accepted).
 */
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { ROLES, type Role } from "@/api/mockData";
import { clearToken, loginUser, setToken } from "@/api/client";

export interface Session {
  email: string;
  role: Role;
}

interface AuthValue {
  session: Session | null;
  ready: boolean;
  signIn: (email: string, password: string, role: Role) => Promise<void>;
  signOut: () => void;
  setRole: (role: Role) => void;
  authError: string | null;
}

const SESSION_KEY = "itbis.session";
const HAS_BACKEND = (import.meta.env.VITE_API_URL as string | undefined) !== undefined
  && (import.meta.env.VITE_API_URL as string).length > 0;

const AuthContext = createContext<AuthValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [ready, setReady] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);

  // Restore session from localStorage on mount
  useEffect(() => {
    try {
      const raw = localStorage.getItem(SESSION_KEY);
      if (raw) {
        const parsed = JSON.parse(raw) as Session;
        if (parsed?.email && ROLES.includes(parsed.role)) {
          setSession(parsed);
        }
      }
    } catch {
      /* ignore corrupt storage */
    }
    setReady(true);
  }, []);

  const persist = useCallback((next: Session | null) => {
    setSession(next);
    try {
      if (next) localStorage.setItem(SESSION_KEY, JSON.stringify(next));
      else localStorage.removeItem(SESSION_KEY);
    } catch {
      /* ignore */
    }
  }, []);

  const signIn = useCallback(
    async (email: string, password: string, role: Role) => {
      setAuthError(null);

      if (HAS_BACKEND) {
        // Real JWT auth
        const result = await loginUser(email, password);
        // Use the role returned by the server (it's the authoritative source)
        const serverRole = result.role as Role;
        if (!ROLES.includes(serverRole)) {
          throw new Error(`Unknown role '${serverRole}' returned by server.`);
        }
        persist({ email: result.email, role: serverRole });
      } else {
        // Mock auth — any credentials, role from form
        setToken("mock-jwt-token");
        persist({ email, role });
      }
    },
    [persist],
  );

  const signOut = useCallback(() => {
    persist(null);
    clearToken();
    setAuthError(null);
  }, [persist]);

  const setRole = useCallback(
    (role: Role) => {
      persist(session ? { ...session, role } : null);
    },
    [session, persist],
  );

  const value = useMemo<AuthValue>(
    () => ({ session, ready, signIn, signOut, setRole, authError }),
    [session, ready, signIn, signOut, setRole, authError],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}

export function isAdmin(role: Role | undefined) {
  return role === "Administrator";
}

export function canManageEmployees(role: Role | undefined) {
  return role === "Administrator" || role === "Security Manager";
}

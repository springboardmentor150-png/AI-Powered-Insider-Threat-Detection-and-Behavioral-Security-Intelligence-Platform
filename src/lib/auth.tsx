import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { ROLES, type Role } from "@/api/mockData";

export interface Session {
  email: string;
  role: Role;
}

interface AuthValue {
  session: Session | null;
  ready: boolean;
  signIn: (email: string, password: string, role: Role) => void;
  signOut: () => void;
  setRole: (role: Role) => void;
}

const STORAGE_KEY = "itbis.session";

const AuthContext = createContext<AuthValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw) as Session;
        if (parsed?.email && ROLES.includes(parsed.role)) setSession(parsed);
      }
    } catch {
      /* ignore corrupt storage */
    }
    setReady(true);
  }, []);

  const persist = useCallback((next: Session | null) => {
    setSession(next);
    try {
      if (next) localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      else localStorage.removeItem(STORAGE_KEY);
    } catch {
      /* ignore */
    }
  }, []);

  const value = useMemo<AuthValue>(
    () => ({
      session,
      ready,
      // Mock auth: any credentials are accepted, the role comes from the form.
      signIn: (email, _password, role) => persist({ email, role }),
      signOut: () => persist(null),
      setRole: (role) => persist(session ? { ...session, role } : null),
    }),
    [session, ready, persist],
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

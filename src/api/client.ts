/**
 * ITBIS API client
 *
 * Wraps all fetch() calls to the FastAPI backend.
 * Falls back to the static mock data when the backend is unreachable
 * (VITE_API_URL not set or backend offline) so the UI stays usable
 * without a running server.
 *
 * All public functions mirror the api.* surface in mockData.ts so
 * the rest of the codebase can switch between real and mock seamlessly.
 */

import {
  activityLogs as mockLogs,
  alerts as mockAlerts,
  employees as mockEmployees,
  platformUsers as mockUsers,
  type ActivityLog,
  type Employee,
  type PlatformUser,
  type ThreatAlert,
} from "@/api/mockData";

// ── Config ────────────────────────────────────────────────────────────────────

const BASE_URL = (import.meta.env.VITE_API_URL as string | undefined) ?? "";

/** True when a real backend URL is configured. */
const HAS_BACKEND = BASE_URL.length > 0;

// ── Token storage ─────────────────────────────────────────────────────────────

const TOKEN_KEY = "itbis.jwt";

export function getToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token: string): void {
  try {
    localStorage.setItem(TOKEN_KEY, token);
  } catch {
    /* ignore */
  }
}

export function clearToken(): void {
  try {
    localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* ignore */
  }
}

// ── Core fetch wrapper ────────────────────────────────────────────────────────

interface FetchOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined | null>;
}

async function apiFetch<T>(path: string, opts: FetchOptions = {}): Promise<T> {
  const { params, ...init } = opts;

  // Build URL with query params
  let url = `${BASE_URL}${path}`;
  if (params) {
    const qs = Object.entries(params)
      .filter(([, v]) => v !== undefined && v !== null && v !== "")
      .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
      .join("&");
    if (qs) url += `?${qs}`;
  }

  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(url, { ...init, headers });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = (await res.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      /* ignore parse error */
    }
    throw new Error(detail);
  }

  // 204 No Content
  if (res.status === 204) return undefined as T;

  return res.json() as Promise<T>;
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export interface LoginResult {
  access_token: string;
  token_type: string;
  role: string;
  email: string;
}

export async function loginUser(email: string, password: string): Promise<LoginResult> {
  // FastAPI OAuth2PasswordBearer expects form-encoded body for /auth/login
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    let detail = "Invalid email or password.";
    try {
      const body = (await res.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }

  const data = (await res.json()) as LoginResult;
  setToken(data.access_token);
  return data;
}

export async function signupUser(
  email: string,
  password: string,
  role: string,
): Promise<LoginResult> {
  await apiFetch("/auth/signup", {
    method: "POST",
    body: JSON.stringify({ email, password, role }),
  });
  // Auto-login after signup
  return loginUser(email, password);
}

// ── Employees ─────────────────────────────────────────────────────────────────

/** Map backend employee shape → frontend Employee shape (handles date fields). */
function mapEmployee(e: Record<string, unknown>): Employee {
  return {
    employee_id: e.employee_id as string,
    name: e.name as string,
    email: e.email as string,
    department: e.department as string,
    designation: e.designation as string,
    manager: e.manager as string,
    risk_level: e.risk_level as Employee["risk_level"],
    risk_score: e.risk_score as number,
    location: (e.location as string) ?? "",
    joined_at: ((e.joined_at as string) ?? "").split("T")[0],
  };
}

export const apiClient = {
  // ── Employees ──────────────────────────────────────────────────────────────

  async getEmployees(department?: string): Promise<Employee[]> {
    if (!HAS_BACKEND) return mockEmployees;
    try {
      const data = await apiFetch<Record<string, unknown>[]>("/employees", {
        params: { department: department ?? "" },
      });
      return data.map(mapEmployee);
    } catch {
      return mockEmployees;
    }
  },

  async getEmployee(id: string): Promise<Employee | undefined> {
    if (!HAS_BACKEND) return mockEmployees.find((e) => e.employee_id === id);
    try {
      const data = await apiFetch<Record<string, unknown>>(`/employees/${id}`);
      return mapEmployee(data);
    } catch {
      return mockEmployees.find((e) => e.employee_id === id);
    }
  },

  async createEmployee(
    payload: Omit<Employee, "employee_id" | "joined_at">,
  ): Promise<Employee> {
    if (!HAS_BACKEND) {
      // Optimistic mock creation
      const next: Employee = {
        ...payload,
        employee_id: `EMP-${1500 + mockEmployees.length + 1}`,
        joined_at: new Date().toISOString().split("T")[0],
      };
      mockEmployees.push(next);
      return next;
    }
    const data = await apiFetch<Record<string, unknown>>("/employees", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    return mapEmployee(data);
  },

  async updateEmployee(
    id: string,
    payload: Partial<Omit<Employee, "employee_id" | "joined_at">>,
  ): Promise<Employee> {
    if (!HAS_BACKEND) {
      const idx = mockEmployees.findIndex((e) => e.employee_id === id);
      if (idx !== -1) {
        mockEmployees[idx] = { ...mockEmployees[idx], ...payload };
        return mockEmployees[idx];
      }
      throw new Error("Employee not found");
    }
    const data = await apiFetch<Record<string, unknown>>(`/employees/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
    return mapEmployee(data);
  },

  // ── Alerts ─────────────────────────────────────────────────────────────────

  async getAlerts(filters?: {
    severity?: string;
    status?: string;
    employee_id?: string;
  }): Promise<ThreatAlert[]> {
    if (!HAS_BACKEND) return mockAlerts;
    try {
      const data = await apiFetch<Record<string, unknown>[]>("/alerts", {
        params: filters,
      });
      return data.map((a) => ({
        id: a.alert_id as string,
        employee_id: a.employee_id as string,
        employee_name: (a.employee_name as string) ?? "",
        severity: a.severity as ThreatAlert["severity"],
        message: a.message as string,
        status: a.status as ThreatAlert["status"],
        created_at: a.created_at as string,
        assigned_to: a.assigned_to as ThreatAlert["assigned_to"],
        rule: (a.rule as string) ?? "",
        narrative: (a.narrative as string) ?? "",
      }));
    } catch {
      return mockAlerts;
    }
  },

  async updateAlert(
    alertId: string,
    payload: { status?: string; severity?: string; narrative?: string },
  ): Promise<void> {
    if (!HAS_BACKEND) return;
    await apiFetch(`/alerts/${alertId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  // ── Activity Logs ──────────────────────────────────────────────────────────

  async getActivityLogs(filters?: {
    employee_id?: string;
    event_type?: string;
    date_from?: string;
    date_to?: string;
  }): Promise<ActivityLog[]> {
    if (!HAS_BACKEND) return mockLogs;
    try {
      const data = await apiFetch<Record<string, unknown>[]>("/activity-logs", {
        params: filters,
      });
      return data.map((l) => ({
        id: (l.log_id as string) || (l._id as string) || "",
        employee_id: l.employee_id as string,
        event_type: l.event_type as ActivityLog["event_type"],
        timestamp: l.timestamp as string,
        details: (l.details as string) ?? "",
        host: (l.host as string) ?? "",
        ip: (l.ip as string) ?? "",
      }));
    } catch {
      return mockLogs;
    }
  },

  async getActivityLogsForEmployee(employeeId: string): Promise<ActivityLog[]> {
    if (!HAS_BACKEND) {
      return mockLogs.filter((l) => l.employee_id === employeeId);
    }
    try {
      const data = await apiFetch<Record<string, unknown>[]>(
        `/activity-logs/employee/${employeeId}`,
      );
      return data.map((l) => ({
        id: (l.log_id as string) || (l._id as string) || "",
        employee_id: l.employee_id as string,
        event_type: l.event_type as ActivityLog["event_type"],
        timestamp: l.timestamp as string,
        details: (l.details as string) ?? "",
        host: (l.host as string) ?? "",
        ip: (l.ip as string) ?? "",
      }));
    } catch {
      return mockLogs.filter((l) => l.employee_id === employeeId);
    }
  },

  // ── Platform Users ─────────────────────────────────────────────────────────

  async getPlatformUsers(): Promise<PlatformUser[]> {
    if (!HAS_BACKEND) return mockUsers;
    try {
      const data = await apiFetch<Record<string, unknown>[]>("/users");
      return data.map((u) => ({
        id: String(u.id),
        email: u.email as string,
        role: u.role as PlatformUser["role"],
        status: u.status as PlatformUser["status"],
        last_login: (u.last_login as string) ?? "—",
      }));
    } catch {
      return mockUsers;
    }
  },

  async createPlatformUser(payload: {
    email: string;
    password: string;
    role: string;
  }): Promise<PlatformUser> {
    if (!HAS_BACKEND) {
      const next: PlatformUser = {
        id: `USR-${String(mockUsers.length + 1).padStart(2, "0")}`,
        email: payload.email,
        role: payload.role as PlatformUser["role"],
        status: "Invited",
        last_login: "—",
      };
      mockUsers.push(next);
      return next;
    }
    const data = await apiFetch<Record<string, unknown>>("/users", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    return {
      id: String(data.id),
      email: data.email as string,
      role: data.role as PlatformUser["role"],
      status: data.status as PlatformUser["status"],
      last_login: (data.last_login as string) ?? "—",
    };
  },

  async updatePlatformUser(
    userId: string,
    payload: { role?: string; status?: string },
  ): Promise<void> {
    if (!HAS_BACKEND) return;
    await apiFetch(`/users/${userId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },
};

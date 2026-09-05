import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach JWT token from localStorage to every outgoing request
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("itbis_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Auth Endpoints
export const authAPI = {
  login: (data: { email: string; password: string }) => api.post("/auth/login", data),
  register: (data: any) => api.post("/auth/register", data),
  me: () => api.get("/auth/me"),
  getUsers: () => api.get("/auth/users"),
};

// Employee Endpoints
export const employeeAPI = {
  getAll: (params?: { department?: string; search?: string }) => api.get("/employees", { params }),
  getById: (id: string) => api.get(`/employees/${id}`),
  create: (data: any) => api.post("/employees", data),
  update: (id: string, data: any) => api.put(`/employees/${id}`, data),
  delete: (id: string) => api.delete(`/employees/${id}`),
  getBaseline: (id: string) => api.get(`/employees/${id}/baseline`),
};

// Log Ingestion & Telemetry Endpoints
export const logAPI = {
  ingest: (data: { employee_id: string; event_type: string; details: any }) => api.post("/logs/ingest", data),
  getAll: (params?: { employee_id?: string; event_type?: string; limit?: number }) => api.get("/logs", { params }),
  getStats: () => api.get("/logs/stats"),
};

// Alert Endpoints
export const alertAPI = {
  getAll: (params?: { severity?: string; employee_id?: string; is_acknowledged?: boolean; limit?: number }) =>
    api.get("/alerts", { params }),
  acknowledge: (id: number) => api.post(`/alerts/${id}/acknowledge`),
  escalate: (id: number) => api.post(`/alerts/${id}/escalate`),
};

// Incident Workbench Endpoints
export const incidentAPI = {
  getAll: (params?: { status?: string; severity?: string; employee_id?: string }) =>
    api.get("/incidents", { params }),
  getById: (id: number) => api.get(`/incidents/${id}`),
  create: (data: any) => api.post("/incidents", data),
  updateStatus: (id: number, data: { status: string; assigned_to?: string; ai_summary?: string }) =>
    api.patch(`/incidents/${id}/status`, data),
  generateAIReport: (id: number) => api.post(`/incidents/${id}/generate-ai-report`),
};

// AI & Behavioral Analysis Endpoints
export const aiAPI = {
  analyzeEmployee: (employeeId: string) => api.post(`/ai/analyze/${employeeId}`),
  analyzeAll: () => api.post("/ai/analyze-all"),
};

// Threat Simulation Lab Endpoints
export const simulationAPI = {
  runScenario: (data: { scenario: string; employee_id?: string; event_count?: number }) =>
    api.post("/simulation/run", data),
};
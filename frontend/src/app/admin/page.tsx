"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { authAPI, dashboardAPI, reportAPI } from "@/lib/api";
import {
  ShieldCheck,
  UserPlus,
  Lock,
  Mail,
  Shield,
  CheckCircle,
  AlertOctagon,
  RefreshCw,
  Activity,
  Users,
  Building,
  FileSpreadsheet,
  Download,
  Clock,
  History,
  TrendingUp,
  Cpu
} from "lucide-react";

export default function AdminPage() {
  const { user } = useAuth();
  const [users, setUsers] = useState<any[]>([]);
  const [adminStats, setAdminStats] = useState<any>(null);
  const [analytics, setAnalytics] = useState<any>(null);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [exportingAudit, setExportingAudit] = useState(false);
  const [newUserForm, setNewUserForm] = useState({
    email: "",
    full_name: "",
    password: "",
    role: "security_analyst",
  });
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const fetchAdminData = async () => {
    try {
      setLoading(true);
      const [usersRes, statsRes, analyticsRes, auditRes] = await Promise.all([
        authAPI.getUsers(),
        dashboardAPI.getAdminDashboard(),
        dashboardAPI.getPlatformAnalytics(),
        dashboardAPI.getAuditLog(25),
      ]);
      setUsers(usersRes.data || []);
      setAdminStats(statsRes.data || null);
      setAnalytics(analyticsRes.data || null);
      setAuditLogs(auditRes.data || []);
    } catch (e) {
      console.error("RBAC Restricted or Load Error:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user?.role === "admin") {
      fetchAdminData();
    } else {
      setLoading(false);
    }
  }, [user]);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccessMsg(null);
    try {
      await authAPI.register(newUserForm);
      setSuccessMsg(`User ${newUserForm.email} registered successfully with role '${newUserForm.role}'!`);
      setNewUserForm({
        email: "",
        full_name: "",
        password: "",
        role: "security_analyst",
      });
      fetchAdminData();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to create user.");
    }
  };

  const handleExportAuditLogs = async () => {
    try {
      setExportingAudit(true);
      await reportAPI.downloadAuditLogsExcel();
    } catch (e) {
      alert("Failed to export audit logs.");
    } finally {
      setExportingAudit(false);
    }
  };

  // RBAC Enforcement Check
  if (user?.role !== "admin") {
    return (
      <div className="p-12 text-center rounded-3xl bg-slate-900/60 border border-slate-800 space-y-4 max-w-xl mx-auto my-12 animate-fade-in">
        <div className="w-12 h-12 rounded-2xl bg-rose-950/60 border border-rose-800 flex items-center justify-center mx-auto text-rose-400">
          <AlertOctagon className="w-6 h-6" />
        </div>
        <h2 className="text-lg font-bold text-white">403 Forbidden: Administrator Access Required</h2>
        <p className="text-xs text-slate-400 leading-relaxed">
          Your current authenticated role is <strong className="text-cyan-400 font-mono">'{user?.role || "anonymous"}'</strong>.
          Role-Based Access Control (RBAC) restricts user governance, audit logs, and platform health telemetry exclusively to the Administrator.
        </p>
        <p className="text-[11px] text-slate-500 font-mono">
          Tip: Use the "Switch Role" dropdown in the navbar to switch to "Sarah Connor (Admin)".
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-purple-950/40 border border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800 uppercase">
              Milestone 4 — Day 32 Platform Health
            </span>
            <span className="text-xs text-slate-400 font-mono">Admin Dashboard & Audit Trail</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight mt-1 flex items-center gap-2">
            <ShieldCheck className="w-6 h-6 text-purple-400" />
            <span>Platform Governance & System-Level Telemetry</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Monitor infrastructure telemetry volume, workforce coverage, user role distribution, and immutable audit trails.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchAdminData}
            className="flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            <span>Refresh Platform</span>
          </button>
          <button
            onClick={handleExportAuditLogs}
            disabled={exportingAudit}
            className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold shadow-lg shadow-purple-950/60 transition border border-purple-500/40"
          >
            <Download className="w-3.5 h-3.5" />
            <span>{exportingAudit ? "Exporting..." : "Export Audit Log (.xlsx)"}</span>
          </button>
        </div>
      </div>

      {/* Day 32 System-Level Volume Metrics & User Counts */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1: Platform Users */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-mono">Platform Accounts</span>
            <Users className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {adminStats?.total_platform_users || users.length}
          </div>
          <div className="flex flex-wrap gap-1 pt-1">
            {adminStats?.users_by_role &&
              Object.entries(adminStats.users_by_role).map(([role, cnt]) => (
                <span
                  key={role}
                  className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700"
                >
                  {role}: {String(cnt)}
                </span>
              ))}
          </div>
        </div>

        {/* Metric 2: Monitored Workforce & Departments */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-mono">Monitored Personnel</span>
            <Building className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {adminStats?.employees_monitored || 8}
          </div>
          <p className="text-[11px] text-cyan-400/90 font-mono">
            Across {adminStats?.departments || 7} distinct departments
          </p>
        </div>

        {/* Metric 3: Total Activity Logs Ingested */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-mono">Total Telemetry Logs</span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {analytics?.total_activity_logs || 0}
          </div>
          <p className="text-[11px] text-slate-400 font-mono">
            MongoDB / Document Store Records
          </p>
        </div>

        {/* Metric 4: System Anomaly Rate */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-mono">Overall Anomaly Rate</span>
            <TrendingUp className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-bold text-rose-400">
            {analytics?.overall_anomaly_rate_percent !== undefined
              ? `${analytics.overall_anomaly_rate_percent}%`
              : "0.0%"}
          </div>
          <div className="text-[10px] text-slate-400 font-mono flex items-center justify-between">
            <span>Rules: {analytics?.total_rule_anomalies || 0}</span>
            <span>ML Anom: {analytics?.total_ml_anomalies || 0}</span>
          </div>
        </div>
      </div>

      {/* Main Grid: User Provisioning & Active Users */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Create User Form */}
        <div className="lg:col-span-5 p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="flex items-center space-x-2 text-sm font-bold text-white">
            <UserPlus className="w-4 h-4 text-cyan-400" />
            <span>Provision New System Operator</span>
          </div>

          {successMsg && (
            <div className="p-3 rounded-xl bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-xs flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          <form onSubmit={handleCreateUser} className="space-y-3.5 text-xs">
            <div>
              <label className="text-slate-300 font-medium">Full Name</label>
              <input
                type="text"
                required
                placeholder="e.g. Jordan Reed"
                value={newUserForm.full_name}
                onChange={(e) => setNewUserForm({ ...newUserForm, full_name: e.target.value })}
                className="w-full mt-1 p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100"
              />
            </div>

            <div>
              <label className="text-slate-300 font-medium">Email Address</label>
              <input
                type="email"
                required
                placeholder="e.g. jreed@itbis.security"
                value={newUserForm.email}
                onChange={(e) => setNewUserForm({ ...newUserForm, email: e.target.value })}
                className="w-full mt-1 p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-mono"
              />
            </div>

            <div>
              <label className="text-slate-300 font-medium">Password</label>
              <input
                type="password"
                required
                placeholder="••••••••••••"
                value={newUserForm.password}
                onChange={(e) => setNewUserForm({ ...newUserForm, password: e.target.value })}
                className="w-full mt-1 p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-mono"
              />
            </div>

            <div>
              <label className="text-slate-300 font-medium">RBAC Role Assignment</label>
              <select
                value={newUserForm.role}
                onChange={(e) => setNewUserForm({ ...newUserForm, role: e.target.value })}
                className="w-full mt-1 p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-mono"
              >
                <option value="admin">admin (Full Administrator)</option>
                <option value="security_manager">security_manager (SOC Management & Compliance)</option>
                <option value="security_analyst">security_analyst (Investigation & Triage)</option>
                <option value="soc_engineer">soc_engineer (Telemetry & Threat Simulations)</option>
              </select>
            </div>

            <button
              type="submit"
              className="w-full py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold shadow-lg shadow-purple-600/20 transition"
            >
              Provision Account
            </button>
          </form>
        </div>

        {/* Existing Users Table */}
        <div className="lg:col-span-7 p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider font-mono">
            Active System Operators ({users.length})
          </h3>

          <div className="divide-y divide-slate-800/80 overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="text-slate-400 uppercase tracking-wider font-mono text-[10px]">
                  <th className="py-2.5">User</th>
                  <th className="py-2.5">Role</th>
                  <th className="py-2.5">Status</th>
                  <th className="py-2.5 text-right">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 font-medium text-slate-100">
                      <div>{u.full_name || u.email}</div>
                      <div className="text-[10px] text-slate-400 font-mono">{u.email}</div>
                    </td>
                    <td className="py-3">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700">
                        {u.role}
                      </span>
                    </td>
                    <td className="py-3">
                      <span className="text-[10px] font-mono text-emerald-400">ACTIVE</span>
                    </td>
                    <td className="py-3 text-right text-slate-400 font-mono text-[10px]">
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Day 32 Audit Log Viewer */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <History className="w-4 h-4 text-purple-400" />
              <span>Platform Audit Trail (`/dashboard/admin/audit-log`)</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Chronological log of sensitive actions (alert assignments, incident status updates, and user provisioning).
            </p>
          </div>
          <span className="text-xs font-mono text-slate-500">
            Showing Last {auditLogs.length} Events
          </span>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-800/80">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/60 text-slate-400 font-mono uppercase text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Operator</th>
                <th className="py-3 px-4">Target Resource</th>
                <th className="py-3 px-4">Details</th>
                <th className="py-3 px-4 text-right">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {auditLogs.map((entry, idx) => (
                <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-3 px-4 font-mono font-bold text-cyan-400">
                    <span className="px-2 py-0.5 rounded bg-slate-800/80 border border-slate-700">
                      {entry.action}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-300 font-mono text-[11px]">
                    {entry.user_email || `User #${entry.user_id}`}
                  </td>
                  <td className="py-3 px-4 font-mono text-[11px] text-purple-300">
                    {entry.target_resource || "Platform"}
                  </td>
                  <td className="py-3 px-4 text-slate-400 text-xs max-w-xs truncate">
                    {entry.details || "—"}
                  </td>
                  <td className="py-3 px-4 text-right font-mono text-[10px] text-slate-400">
                    {entry.timestamp ? new Date(entry.timestamp).toLocaleString() : "N/A"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

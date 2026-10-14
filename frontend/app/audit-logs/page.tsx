"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import Navbar from "@/components/Navbar";
import api from "@/lib/api";
import { verifyAuthentication } from "@/lib/auth";

interface AuditEntry {
  id: number;
  user_id: number | null;
  user_email: string;
  action: string;
  resource_type: string;
  resource_id: string | null;
  details: string | null;
  ip_address: string | null;
  created_at: string;
}

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState("all");
  const [emailFilter, setEmailFilter] = useState("");

  const fetchLogs = async () => {
    try {
      setLoading(true);
      await verifyAuthentication();
      const params: Record<string, string> = {};
      if (actionFilter !== "all") params.action = actionFilter;
      if (emailFilter.trim()) params.user_email = emailFilter.trim();

      const res = await api.get("/audit-logs", { params });
      setLogs(res.data?.logs || []);
      setTotal(res.data?.total || 0);
    } catch (err: any) {
      if (err.response?.status === 401) {
        window.location.href = "/login";
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [actionFilter]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchLogs();
  };

  const getActionBadge = (action: string) => {
    const a = action.toUpperCase();
    if (a.includes("LOGIN") || a.includes("REGISTER")) {
      return "bg-blue-500/20 text-blue-400 border-blue-500/30";
    }
    if (a.includes("ROLE") || a.includes("STATUS")) {
      return "bg-purple-500/20 text-purple-400 border-purple-500/30";
    }
    if (a.includes("RESOLVE")) {
      return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
    }
    if (a.includes("FEEDBACK")) {
      return "bg-amber-500/20 text-amber-400 border-amber-500/30";
    }
    return "bg-slate-500/20 text-slate-300 border-slate-500/30";
  };

  return (
    <div className="flex h-screen bg-[var(--background)] text-[var(--foreground)]">
      <Sidebar />

      <div className="flex flex-1 flex-col overflow-hidden">
        <Navbar />

        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="mx-auto max-w-7xl space-y-6">
            {/* Page Header */}
            <div className="flex flex-col gap-2 border-b border-[var(--border)] pb-5 md:flex-row md:items-center md:justify-between">
              <div>
                <h1 className="text-2xl font-bold tracking-tight">Platform Operational Audit Trail</h1>
                <p className="text-sm text-[var(--muted)]">
                  Immutable SOC 2 and ISO 27001 compliance audit log recording analyst and administrator platform actions
                </p>
              </div>

              <span className="font-mono text-xs text-[var(--muted)]">
                Total Audit Entries: <span className="font-bold text-[var(--foreground)]">{total}</span>
              </span>
            </div>

            {/* Filter Bar */}
            <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-[var(--border)] bg-[var(--card)] p-4">
              <div className="flex flex-wrap items-center gap-3">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-[var(--muted)]">Action Type:</span>
                  <select
                    value={actionFilter}
                    onChange={(e) => setActionFilter(e.target.value)}
                    className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-1.5 text-xs outline-none focus:border-[var(--primary)]"
                  >
                    <option value="all">All Actions</option>
                    <option value="USER_LOGIN">User Logins</option>
                    <option value="USER_ROLE_CHANGED">Role Changes</option>
                    <option value="USER_STATUS_CHANGED">Status Changes</option>
                    <option value="ALERT_ASSIGNED">Alert Assignments</option>
                    <option value="ALERT_RESOLVED">Alert Resolutions</option>
                    <option value="INCIDENT_STATUS_CHANGE">Incident Status Changes</option>
                    <option value="ANOMALY_FEEDBACK_SUBMITTED">Anomaly Feedback</option>
                    <option value="MODEL_RETRAINED">Model Retraining</option>
                  </select>
                </div>

                <form onSubmit={handleSearch} className="flex items-center gap-2">
                  <input
                    type="text"
                    value={emailFilter}
                    onChange={(e) => setEmailFilter(e.target.value)}
                    placeholder="Search by operator email..."
                    className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-1.5 text-xs outline-none focus:border-[var(--primary)]"
                  />
                  <button
                    type="submit"
                    className="rounded-lg bg-[var(--primary)] px-3 py-1.5 text-xs font-semibold text-white hover:bg-[var(--primary-hover)] transition"
                  >
                    Filter
                  </button>
                </form>
              </div>

              <button
                onClick={fetchLogs}
                className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-1.5 text-xs font-medium text-[var(--muted)] hover:text-[var(--foreground)] transition"
              >
                ↻ Refresh Log
              </button>
            </div>

            {/* Table */}
            <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-[var(--border)] bg-[var(--background)]/50 text-[11px] font-semibold uppercase tracking-wider text-[var(--muted)]">
                      <th className="p-4">Timestamp</th>
                      <th className="p-4">Action</th>
                      <th className="p-4">Operator Email</th>
                      <th className="p-4">Resource</th>
                      <th className="p-4">Details</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[var(--border)]">
                    {loading ? (
                      <tr>
                        <td colSpan={5} className="p-8 text-center text-xs text-[var(--muted)]">
                          Loading audit records...
                        </td>
                      </tr>
                    ) : logs.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="p-8 text-center text-sm text-[var(--muted)]">
                          No audit entries match the current filter.
                        </td>
                      </tr>
                    ) : (
                      logs.map((log) => (
                        <tr key={log.id} className="hover:bg-[var(--card-hover)] transition text-xs">
                          <td className="p-4 font-mono text-[var(--muted)] whitespace-nowrap">
                            {new Date(log.created_at).toLocaleString()}
                          </td>
                          <td className="p-4">
                            <span className={`rounded-md border px-2 py-0.5 text-[10px] font-bold tracking-wider ${getActionBadge(log.action)}`}>
                              {log.action}
                            </span>
                          </td>
                          <td className="p-4 font-semibold text-[var(--foreground)]">
                            {log.user_email}
                          </td>
                          <td className="p-4 font-mono text-[var(--muted)]">
                            {log.resource_type} {log.resource_id ? `(#${log.resource_id})` : ""}
                          </td>
                          <td className="p-4 text-[var(--muted)] max-w-md break-words">
                            {log.details || "-"}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

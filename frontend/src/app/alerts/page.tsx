"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { alertAPI, authAPI } from "@/lib/api";
import { ThreatScoreBadge } from "@/components/ThreatScoreBadge";
import {
  AlertTriangle,
  ShieldAlert,
  CheckCircle,
  FolderPlus,
  RefreshCw,
  Search,
  Filter,
  Check,
  UserCheck,
  CheckCheck
} from "lucide-react";

export default function AlertsPage() {
  const { user } = useAuth();
  const [alerts, setAlerts] = useState<any[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 100 };
      if (severityFilter !== "ALL") params.severity = severityFilter;
      if (statusFilter !== "ALL") params.status = statusFilter;
      const res = await alertAPI.getAll(params);
      setAlerts(res.data || []);

      if (user?.role === "admin" || user?.role === "security_manager") {
        try {
          const uRes = await authAPI.getUsers();
          setUsers(uRes.data || []);
        } catch (e) {}
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [severityFilter, statusFilter, user]);

  const handleAssign = async (alertId: number, analystUserId: number) => {
    setActionLoading(alertId);
    try {
      await alertAPI.assign(alertId, analystUserId);
      fetchAlerts();
    } catch (e) {
      alert("Failed to assign alert. Check role permissions.");
    } finally {
      setActionLoading(null);
    }
  };

  const handleResolve = async (alertId: number) => {
    setActionLoading(alertId);
    try {
      await alertAPI.resolve(alertId);
      fetchAlerts();
    } catch (e) {
      alert("Failed to resolve alert.");
    } finally {
      setActionLoading(null);
    }
  };

  const handleAcknowledge = async (id: number) => {
    setActionLoading(id);
    try {
      await alertAPI.acknowledge(id);
      fetchAlerts();
    } catch (e) {
      alert("Failed to acknowledge alert.");
    } finally {
      setActionLoading(null);
    }
  };

  const handleEscalate = async (id: number) => {
    setActionLoading(id);
    try {
      const res = await alertAPI.escalate(id);
      alert(res.data.message || "Escalated to incident successfully!");
      fetchAlerts();
    } catch (e) {
      alert("Failed to escalate alert.");
    } finally {
      setActionLoading(null);
    }
  };

  const isManager = user?.role === "admin" || user?.role === "security_manager";
  const isAnalyst = user?.role === "admin" || user?.role === "security_analyst" || user?.role === "soc_engineer";

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800 uppercase">
              Milestone 3 Alert Lifecycle
            </span>
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2 mt-1">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <span>Risk Analytics & Alert Management</span>
          </h1>
          <p className="text-xs text-slate-400">
            Manager delegation, analyst resolution & escalation into SOC investigation tickets.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Statuses</option>
            <option value="open">Open</option>
            <option value="assigned">Assigned</option>
            <option value="resolved">Resolved</option>
          </select>

          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          <button
            onClick={fetchAlerts}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {/* Alerts Feed */}
      <div className="space-y-3">
        {alerts.map((alt) => (
          <div
            key={alt.id}
            className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-4 hover:border-slate-700 transition"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex items-center space-x-3">
                <span className="text-xs font-mono font-bold text-cyan-400">{alt.alert_code || `ALT-${alt.id}`}</span>
                <span className="text-xs font-bold text-slate-100">{alt.title || alt.message}</span>
              </div>
              <div className="flex items-center space-x-2">
                <ThreatScoreBadge score={alt.risk_score || 50} level={alt.severity} />
                <span className={`text-[10px] px-2 py-0.5 rounded font-mono uppercase font-semibold ${
                  alt.status === "resolved"
                    ? "bg-emerald-950 text-emerald-300 border border-emerald-800"
                    : alt.status === "assigned"
                    ? "bg-blue-950 text-blue-300 border border-blue-800"
                    : "bg-slate-800 text-slate-300 border border-slate-700"
                }`}>
                  {alt.status || "OPEN"}
                </span>
                {alt.is_escalated && (
                  <span className="text-[10px] px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800 font-mono">
                    ESCALATED
                  </span>
                )}
              </div>
            </div>

            <p className="text-xs text-slate-300 font-sans leading-relaxed">{alt.message}</p>

            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-slate-800/60 text-xs">
              <div className="flex items-center space-x-4 text-[11px] font-mono text-slate-400">
                <span>Identity: <strong className="text-slate-200">{alt.employee_id}</strong></span>
                <span>Time: {new Date(alt.created_at).toLocaleString()}</span>
              </div>

              <div className="flex items-center space-x-2">
                {/* Manager: Assign Alert Dropdown (Milestone 3 Part 4) */}
                {isManager && alt.status !== "resolved" && (
                  <select
                    onChange={(e) => {
                      if (e.target.value) handleAssign(alt.id, parseInt(e.target.value));
                    }}
                    defaultValue=""
                    className="px-2.5 py-1.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-cyan-300 font-mono focus:outline-none"
                  >
                    <option value="" disabled>Delegate to Analyst...</option>
                    {users.map((u) => (
                      <option key={u.id} value={u.id}>
                        {u.full_name || u.email}
                      </option>
                    ))}
                  </select>
                )}

                {/* Analyst: Resolve Alert (Milestone 3 Part 4) */}
                {isAnalyst && alt.status !== "resolved" && (
                  <button
                    onClick={() => handleResolve(alt.id)}
                    disabled={actionLoading === alt.id}
                    className="flex items-center space-x-1 px-3 py-1.5 rounded-xl bg-emerald-950/60 hover:bg-emerald-900/60 text-emerald-300 border border-emerald-800 text-xs font-medium transition"
                  >
                    <CheckCheck className="w-3.5 h-3.5" />
                    <span>Resolve</span>
                  </button>
                )}

                {!alt.is_acknowledged && (
                  <button
                    onClick={() => handleAcknowledge(alt.id)}
                    disabled={actionLoading === alt.id}
                    className="flex items-center space-x-1 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition"
                  >
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Acknowledge</span>
                  </button>
                )}

                {!alt.is_escalated && (
                  <button
                    onClick={() => handleEscalate(alt.id)}
                    disabled={actionLoading === alt.id}
                    className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-md shadow-purple-600/20 transition"
                  >
                    <FolderPlus className="w-3.5 h-3.5" />
                    <span>Escalate</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
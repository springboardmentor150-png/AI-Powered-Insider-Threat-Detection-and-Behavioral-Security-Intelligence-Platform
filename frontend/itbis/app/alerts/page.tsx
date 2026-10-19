"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  Search,
  Filter,
  CheckCircle2,
  ShieldAlert,
  Clock,
  UserCheck,
  ChevronRight,
  Loader2,
  X,
  ExternalLink,
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import { api } from "@/lib/api";

interface AlertItem {
  id: number;
  employee_id: number;
  employee_name?: string;
  employee_identifier?: string;
  title: string;
  message: string;
  category: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  status: string;
  risk_score: number;
  assigned_to?: number;
  acknowledged_at?: string;
  resolved_at?: string;
  created_at: string;
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [selectedAlert, setSelectedAlert] = useState<AlertItem | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const fetchAlerts = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (severityFilter !== "ALL") params.append("severity", severityFilter);
      if (statusFilter !== "ALL") params.append("status", statusFilter);
      params.append("limit", "50");

      const res = await api.get(`/alerts?${params.toString()}`);
      setAlerts(res.data.items || []);
    } catch (err) {
      console.error("Error fetching alerts:", err);
    } finally {
      setLoading(false);
    }
  }, [severityFilter, statusFilter]);

  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  const handleAcknowledge = async (alertId: number) => {
    setActionLoading(true);
    setActionSuccess(null);
    try {
      const res = await api.patch(`/alerts/${alertId}/acknowledge`);
      setSelectedAlert(res.data);
      setActionSuccess("Alert acknowledged by SOC operator.");
      fetchAlerts();
    } catch (err) {
      alert("Failed to acknowledge alert");
    } finally {
      setActionLoading(false);
    }
  };

  const handleCreateIncident = async (alertId: number) => {
    setActionLoading(true);
    setActionSuccess(null);
    try {
      await api.post(`/alerts/${alertId}/create-incident`);
      setActionSuccess("Security incident created and escalated to investigation queue.");
      fetchAlerts();
    } catch (err) {
      alert("Failed to escalate alert to incident");
    } finally {
      setActionLoading(false);
    }
  };

  const handleResolve = async (alertId: number) => {
    setActionLoading(true);
    setActionSuccess(null);
    try {
      const res = await api.patch(`/alerts/${alertId}/resolve`);
      setSelectedAlert(res.data);
      setActionSuccess("Alert marked as RESOLVED.");
      fetchAlerts();
    } catch (err) {
      alert("Failed to resolve alert");
    } finally {
      setActionLoading(false);
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity.toUpperCase()) {
      case "CRITICAL":
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950 text-[#00E5FF] border border-[#00E5FF]/40 shadow-[0_0_8px_rgba(0,229,255,0.2)]">
            CRITICAL
          </span>
        );
      case "HIGH":
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#00A8FF]/20 text-[#00A8FF] border border-[#00A8FF]/40">
            HIGH
          </span>
        );
      case "MEDIUM":
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-[#132B45] text-[#8E9EB5] border border-[#1E3A5F]">
            MEDIUM
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-[#050B14] text-[#8E9EB5] border border-[#132B45]">
            LOW
          </span>
        );
    }
  };

  return (
    <DashboardLayout
      pageTitle="SOC Alert Triage Console"
      pageSubtitle="Automated threat detections requiring security analyst intervention"
    >
      <div className="space-y-6">
        {/* KPI Alert Counter Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-4">
            <span className="text-[10px] uppercase font-bold text-[var(--text-muted)]">Open Alerts</span>
            <div className="text-2xl font-black text-[var(--foreground)] mt-1">
              {alerts.filter((a) => a.status === "OPEN").length}
            </div>
            <span className="text-[10px] text-[#00A8FF]">Active Queue</span>
          </div>

          <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-4">
            <span className="text-[10px] uppercase font-bold text-[var(--text-muted)]">Critical Severity</span>
            <div className="text-2xl font-black text-[#00E5FF] mt-1">
              {alerts.filter((a) => a.severity === "CRITICAL" && a.status === "OPEN").length}
            </div>
            <span className="text-[10px] text-[#00E5FF]">Immediate Action</span>
          </div>

          <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-4">
            <span className="text-[10px] uppercase font-bold text-[var(--text-muted)]">Acknowledged</span>
            <div className="text-2xl font-black text-[#00A8FF] mt-1">
              {alerts.filter((a) => a.status === "ACKNOWLEDGED").length}
            </div>
            <span className="text-[10px] text-[var(--text-muted)]">Under Analyst Review</span>
          </div>

          <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-4">
            <span className="text-[10px] uppercase font-bold text-[var(--text-muted)]">Resolved Alerts</span>
            <div className="text-2xl font-black text-emerald-400 mt-1">
              {alerts.filter((a) => a.status === "RESOLVED").length}
            </div>
            <span className="text-[10px] text-[var(--text-muted)]">Closed Detections</span>
          </div>
        </div>

        {/* Filter Bar */}
        <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-4 flex flex-wrap gap-3 items-center justify-between">
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2">
              <Filter className="w-3.5 h-3.5 text-[#00A8FF]" />
              <span className="text-xs font-semibold text-[var(--text-muted)]">Severity:</span>
              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="bg-[var(--background)] border border-[var(--panel-border)] text-xs text-[var(--foreground)] rounded-lg px-2.5 py-1.5"
              >
                <option value="ALL">All Severities</option>
                <option value="CRITICAL">Critical</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-[var(--text-muted)]">Status:</span>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="bg-[var(--background)] border border-[var(--panel-border)] text-xs text-[var(--foreground)] rounded-lg px-2.5 py-1.5"
              >
                <option value="ALL">All Statuses</option>
                <option value="OPEN">Open Only</option>
                <option value="ACKNOWLEDGED">Acknowledged</option>
                <option value="RESOLVED">Resolved</option>
              </select>
            </div>
          </div>

          <span className="text-xs text-[var(--text-muted)] font-mono">
            {alerts.length} Total Alerts In View
          </span>
        </div>

        {/* Alerts Table */}
        <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl shadow-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-[var(--background)]/80 border-b border-[var(--panel-border)] text-[10px] font-bold uppercase tracking-wider text-[var(--text-muted)] font-mono">
                  <th className="py-3 px-4">Severity</th>
                  <th className="py-3 px-4">Alert ID</th>
                  <th className="py-3 px-4">Monitored Subject</th>
                  <th className="py-3 px-4">Threat Category</th>
                  <th className="py-3 px-4">Trigger Details</th>
                  <th className="py-3 px-4">Score</th>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--panel-border)]">
                {loading ? (
                  <tr>
                    <td colSpan={9} className="py-12 text-center text-[var(--text-muted)]">
                      <div className="flex items-center justify-center gap-2">
                        <Loader2 className="w-4 h-4 animate-spin text-[#00E5FF]" />
                        <span>Loading SOC alert board from database...</span>
                      </div>
                    </td>
                  </tr>
                ) : alerts.length > 0 ? (
                  alerts.map((alert) => (
                    <tr
                      key={alert.id}
                      onClick={() => { setSelectedAlert(alert); setActionSuccess(null); }}
                      className="hover:bg-[var(--background)]/70 transition group cursor-pointer"
                    >
                      <td className="py-3 px-4 whitespace-nowrap">
                        {getSeverityBadge(alert.severity)}
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap font-mono text-xs text-[#00A8FF]">
                        #{alert.id}
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <div className="font-semibold text-[var(--foreground)] group-hover:text-[#00E5FF] transition">
                          {alert.employee_name || `Employee #${alert.employee_id}`}
                        </div>
                        <div className="text-[10px] font-mono text-[var(--text-muted)]">
                          {alert.employee_identifier || `ID: ${alert.employee_id}`}
                        </div>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap font-medium text-[var(--text-muted)]">
                        {alert.category}
                      </td>
                      <td className="py-3 px-4 text-xs text-[var(--foreground)] max-w-xs truncate">
                        {alert.title}
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap font-mono font-bold text-xs text-[#00E5FF]">
                        {alert.risk_score}/100
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap font-mono text-[11px] text-[var(--text-muted)]">
                        {new Date(alert.created_at).toLocaleString([], { dateStyle: "short", timeStyle: "short" })}
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                            alert.status === "OPEN"
                              ? "bg-cyan-950/60 text-[#00E5FF] border border-[#00E5FF]/40"
                              : alert.status === "ACKNOWLEDGED"
                              ? "bg-[#00A8FF]/10 text-[#00A8FF] border border-[#00A8FF]/30"
                              : "bg-[#050B14] text-emerald-400 border border-emerald-900/40"
                          }`}
                        >
                          {alert.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap text-right">
                        <button className="text-[11px] text-[#00A8FF] group-hover:text-[#00E5FF] font-semibold flex items-center gap-1 ml-auto">
                          Triage <ChevronRight className="w-3 h-3" />
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={9} className="py-12 text-center text-[#8E9EB5]">
                      No active alerts match the filter criteria.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Alert Triage Modal */}
        {selectedAlert && (
          <div className="fixed inset-0 z-50 bg-[#050B14]/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-[#0B1626] border border-[#132B45] rounded-xl max-w-2xl w-full p-6 shadow-2xl space-y-4 animate-in fade-in zoom-in-95">
              <div className="flex items-center justify-between pb-3 border-b border-[#132B45]">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-[#00E5FF]" />
                  <h3 className="font-bold text-sm text-[#F4F8FF]">
                    Alert Triage #{selectedAlert.id} — {selectedAlert.category}
                  </h3>
                </div>
                <button
                  onClick={() => setSelectedAlert(null)}
                  className="p-1 text-[#8E9EB5] hover:text-[#F4F8FF] cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {actionSuccess && (
                <div className="p-3 rounded-lg bg-emerald-950/70 border border-emerald-800 text-emerald-300 text-xs flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  {actionSuccess}
                </div>
              )}

              {/* Alert Content */}
              <div className="space-y-3 text-xs">
                <div className="flex justify-between items-center bg-[#050B14] p-3 rounded-lg border border-[#132B45]">
                  <div>
                    <span className="text-[#8E9EB5] block text-[10px] uppercase">Subject</span>
                    <strong className="text-sm text-[#F4F8FF]">{selectedAlert.employee_name} ({selectedAlert.employee_identifier})</strong>
                  </div>
                  <div className="text-right">
                    <span className="text-[#8E9EB5] block text-[10px] uppercase">Calculated Risk Score</span>
                    <strong className="text-base font-mono text-[#00E5FF]">{selectedAlert.risk_score} / 100</strong>
                  </div>
                </div>

                <div>
                  <span className="text-[#8E9EB5] font-semibold">Alert Summary:</span>
                  <div className="text-[#F4F8FF] font-medium text-sm mt-1">{selectedAlert.title}</div>
                </div>

                <div>
                  <span className="text-[#8E9EB5] font-semibold">Sensor Telemetry Message:</span>
                  <pre className="mt-1 bg-[#050B14] border border-[#132B45] p-3 rounded-lg text-[11px] text-[#F4F8FF] whitespace-pre-wrap font-mono leading-relaxed">
                    {selectedAlert.message}
                  </pre>
                </div>

                <div className="grid grid-cols-2 gap-3 text-[11px]">
                  <div className="bg-[#050B14] p-2.5 rounded-lg border border-[#132B45]">
                    <span className="text-[#8E9EB5]">Current Status: </span>
                    <strong className="text-[#00E5FF] font-mono">{selectedAlert.status}</strong>
                  </div>
                  <div className="bg-[#050B14] p-2.5 rounded-lg border border-[#132B45]">
                    <span className="text-[#8E9EB5]">Created At: </span>
                    <strong className="text-[#F4F8FF] font-mono">{new Date(selectedAlert.created_at).toLocaleString()}</strong>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-4 border-t border-[#132B45] flex flex-wrap items-center justify-between gap-3">
                <Link
                  href="/employees"
                  className="text-xs text-[#00A8FF] hover:text-[#00E5FF] flex items-center gap-1 font-semibold"
                >
                  <ExternalLink className="w-3.5 h-3.5" /> Inspect Employee Dossier
                </Link>

                <div className="flex items-center gap-2">
                  {selectedAlert.status === "OPEN" && (
                    <button
                      onClick={() => handleAcknowledge(selectedAlert.id)}
                      disabled={actionLoading}
                      className="px-3 py-1.5 bg-[#050B14] hover:bg-[#00A8FF]/20 border border-[#132B45] hover:border-[#00A8FF] text-xs text-[#00E5FF] font-semibold rounded-lg transition cursor-pointer"
                    >
                      Acknowledge
                    </button>
                  )}

                  <button
                    onClick={() => handleCreateIncident(selectedAlert.id)}
                    disabled={actionLoading}
                    className="px-3 py-1.5 bg-[#00A8FF] hover:bg-[#00E5FF] text-[#050B14] text-xs font-bold rounded-lg transition flex items-center gap-1.5 cursor-pointer shadow-[0_0_10px_rgba(0,168,255,0.3)]"
                  >
                    <ShieldAlert className="w-3.5 h-3.5" /> Escalate to Incident
                  </button>

                  {selectedAlert.status !== "RESOLVED" && (
                    <button
                      onClick={() => handleResolve(selectedAlert.id)}
                      disabled={actionLoading}
                      className="px-3 py-1.5 bg-emerald-950/60 hover:bg-emerald-900/80 border border-emerald-800 text-xs text-emerald-400 font-semibold rounded-lg transition cursor-pointer"
                    >
                      Resolve
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

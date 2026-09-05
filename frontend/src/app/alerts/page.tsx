"use client";

import React, { useEffect, useState } from "react";
import { alertAPI } from "@/lib/api";
import { ThreatScoreBadge } from "@/components/ThreatScoreBadge";
import {
  AlertTriangle,
  ShieldAlert,
  CheckCircle,
  FolderPlus,
  RefreshCw,
  Search,
  Filter,
  Check
} from "lucide-react";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 100 };
      if (severityFilter !== "ALL") params.severity = severityFilter;
      const res = await alertAPI.getAll(params);
      setAlerts(res.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [severityFilter]);

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

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <span>Behavioral Alert Triage Center</span>
          </h1>
          <p className="text-xs text-slate-400">
            Real-time alerts triggered by unsupervised anomaly models and statistical baseline threshold breaches.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical Severity</option>
            <option value="HIGH">High Severity</option>
            <option value="MEDIUM">Medium Severity</option>
            <option value="LOW">Low Severity</option>
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
                <span className="text-xs font-mono font-bold text-cyan-400">{alt.alert_code}</span>
                <span className="text-xs font-bold text-slate-100">{alt.title}</span>
              </div>
              <div className="flex items-center space-x-2">
                <ThreatScoreBadge score={alt.risk_score || 50} level={alt.severity} />
                {alt.is_acknowledged && (
                  <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-mono">
                    ACKNOWLEDGED
                  </span>
                )}
                {alt.is_escalated && (
                  <span className="text-[10px] px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800 font-mono">
                    ESCALATED TO INCIDENT
                  </span>
                )}
              </div>
            </div>

            <p className="text-xs text-slate-300 font-sans leading-relaxed">{alt.message}</p>

            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-slate-800/60 text-xs">
              <div className="flex items-center space-x-4 text-[11px] font-mono text-slate-400">
                <span>Identity: <strong className="text-slate-200">{alt.employee_id}</strong></span>
                <span>Type: <strong className="text-cyan-400">{alt.anomaly_type || "ANOMALY"}</strong></span>
                <span>Time: {new Date(alt.created_at).toLocaleString()}</span>
              </div>

              <div className="flex items-center space-x-2">
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

                {!alt.is_escalated ? (
                  <button
                    onClick={() => handleEscalate(alt.id)}
                    disabled={actionLoading === alt.id}
                    className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-md shadow-purple-600/20 transition"
                  >
                    <FolderPlus className="w-3.5 h-3.5" />
                    <span>Escalate to SOC Incident</span>
                  </button>
                ) : (
                  <span className="text-xs text-purple-400 font-mono">Incident Active &bull; INC-{alt.incident_id}</span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

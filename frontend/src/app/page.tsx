"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Users,
  ShieldAlert,
  AlertTriangle,
  Activity,
  Play,
  ArrowUpRight,
  TrendingUp,
  Cpu,
  RefreshCw
} from "lucide-react";
import { employeeAPI, alertAPI, incidentAPI, logAPI, aiAPI } from "@/lib/api";
import { ThreatScoreBadge } from "@/components/ThreatScoreBadge";

export default function DashboardPage() {
  const [employees, setEmployees] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [incidents, setIncidents] = useState<any[]>([]);
  const [logStats, setLogStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [analyzingAll, setAnalyzingAll] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [empRes, alertRes, incRes, statsRes] = await Promise.all([
        employeeAPI.getAll(),
        alertAPI.getAll({ limit: 6 }),
        incidentAPI.getAll(),
        logAPI.getStats(),
      ]);
      setEmployees(empRes.data || []);
      setAlerts(alertRes.data || []);
      setIncidents(incRes.data || []);
      setLogStats(statsRes.data || null);
    } catch (err) {
      console.error("Error fetching dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRunBatchAI = async () => {
    setAnalyzingAll(true);
    try {
      await aiAPI.analyzeAll();
      await fetchData();
    } catch (e) {
      console.error("AI batch analysis error:", e);
    } finally {
      setAnalyzingAll(false);
    }
  };

  const highRiskEmployees = employees.filter((e) => (e.baseline_risk_score || 0) >= 50);
  const criticalAlertsCount = alerts.filter((a) => a.severity === "CRITICAL").length;
  const openIncidentsCount = incidents.filter((i) => i.status !== "RESOLVED" && i.status !== "FALSE_POSITIVE").length;

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Top Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/40 border border-slate-800">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3">
            Behavioral Security Intelligence Operations Center
            <span className="text-xs font-mono font-normal px-2.5 py-1 rounded-full bg-cyan-950 text-cyan-300 border border-cyan-800">
              SOC DEFCON 3
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Continuous real-time behavioral baselining, unsupervised anomaly scoring & automated MITRE ATT&CK correlation.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleRunBatchAI}
            disabled={analyzingAll}
            className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-semibold shadow-lg shadow-cyan-600/20 transition"
          >
            <Cpu className={`w-4 h-4 ${analyzingAll ? "animate-spin" : ""}`} />
            <span>{analyzingAll ? "Running Isolation Forest..." : "Run AI Anomaly Engine"}</span>
          </button>
          <button
            onClick={fetchData}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 transition">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Monitored Identities</span>
            <Users className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-bold text-white font-mono">{employees.length}</span>
            <span className="text-xs text-emerald-400 font-medium">100% Baselines Active</span>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 transition">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Critical Threat Alerts</span>
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-bold text-rose-400 font-mono">{criticalAlertsCount}</span>
            <span className="text-xs text-rose-400 font-medium">Immediate Triage</span>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 transition">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Active Incidents</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-bold text-amber-400 font-mono">{openIncidentsCount}</span>
            <span className="text-xs text-amber-400 font-medium">Under Investigation</span>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 transition">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Total Ingested Events</span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-bold text-emerald-400 font-mono">{logStats?.total_logs || 0}</span>
            <span className="text-xs text-slate-400 font-medium">MongoDB Document Store</span>
          </div>
        </div>
      </div>

      {/* Main Grid: Threat Watchlist & Live Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* High Risk Watchlist */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                High-Risk Identity Watchlist
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800">
                  {highRiskEmployees.length} Anomalous
                </span>
              </h2>
              <p className="text-xs text-slate-400">Employees with elevated behavioral anomaly index</p>
            </div>
            <Link
              href="/employees"
              className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center space-x-1 font-medium"
            >
              <span>View All</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="divide-y divide-slate-800/80 overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="text-slate-400 uppercase tracking-wider font-mono text-[10px]">
                  <th className="py-2.5">Identity</th>
                  <th className="py-2.5">Department</th>
                  <th className="py-2.5">Designation</th>
                  <th className="py-2.5">Status</th>
                  <th className="py-2.5">Composite Risk</th>
                  <th className="py-2.5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {employees.slice(0, 5).map((emp) => (
                  <tr key={emp.employee_id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 font-medium text-slate-100">
                      <div>{emp.name}</div>
                      <div className="text-[10px] text-slate-400 font-mono">{emp.employee_id}</div>
                    </td>
                    <td className="py-3 text-slate-300">{emp.department}</td>
                    <td className="py-3 text-slate-300">{emp.designation}</td>
                    <td className="py-3">
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded-full font-mono ${
                          emp.status === "UNDER_REVIEW"
                            ? "bg-rose-950 text-rose-300 border border-rose-800"
                            : "bg-emerald-950 text-emerald-300 border border-emerald-800"
                        }`}
                      >
                        {emp.status}
                      </span>
                    </td>
                    <td className="py-3">
                      <ThreatScoreBadge score={emp.baseline_risk_score || 15} />
                    </td>
                    <td className="py-3 text-right">
                      <Link
                        href={`/employees?selected=${emp.employee_id}`}
                        className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-cyan-300 text-[11px] font-medium border border-slate-700 transition"
                      >
                        Profile
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Live Alerts Stream */}
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  Live Alert Stream
                  <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
                </h2>
                <p className="text-xs text-slate-400">Behavioral trigger events</p>
              </div>
              <Link
                href="/alerts"
                className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center space-x-1 font-medium"
              >
                <span>Triage</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="space-y-3">
              {alerts.slice(0, 4).map((alt) => (
                <div
                  key={alt.id}
                  className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-1.5 hover:border-slate-700 transition"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono text-cyan-400 font-bold">{alt.alert_code}</span>
                    <span
                      className={`text-[10px] px-2 py-0.2 rounded font-mono font-semibold ${
                        alt.severity === "CRITICAL"
                          ? "bg-rose-950 text-rose-300 border border-rose-800"
                          : alt.severity === "HIGH"
                          ? "bg-amber-950 text-amber-300 border border-amber-800"
                          : "bg-slate-800 text-slate-300"
                      }`}
                    >
                      {alt.severity}
                    </span>
                  </div>
                  <p className="text-xs font-semibold text-slate-200 line-clamp-1">{alt.title}</p>
                  <p className="text-[11px] text-slate-400 line-clamp-2">{alt.message}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800">
            <Link
              href="/simulation"
              className="w-full flex items-center justify-center space-x-2 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-300 text-xs font-semibold border border-slate-700 transition"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Launch Threat Scenario Lab</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

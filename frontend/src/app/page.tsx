"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import {
  Users,
  ShieldAlert,
  AlertTriangle,
  Activity,
  Play,
  ArrowUpRight,
  TrendingUp,
  Cpu,
  RefreshCw,
  UserCheck,
  Award,
  CheckCircle2,
  BarChart3
} from "lucide-react";
import { employeeAPI, alertAPI, incidentAPI, logAPI, aiAPI, dashboardAPI } from "@/lib/api";
import { ThreatScoreBadge } from "@/components/ThreatScoreBadge";
import { DashboardCharts } from "@/components/DashboardCharts";

export default function DashboardPage() {
  const { user } = useAuth();
  const [employees, setEmployees] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [incidents, setIncidents] = useState<any[]>([]);
  const [logStats, setLogStats] = useState<any>(null);
  const [analystData, setAnalystData] = useState<any>(null);
  const [socData, setSocData] = useState<any>(null);
  const [managerData, setManagerData] = useState<any>(null);
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

      // Milestone 3 Role-Appropriate Dashboard Endpoints
      try {
        const socRes = await dashboardAPI.getSocDashboard();
        setSocData(socRes.data);
      } catch (e) {}

      try {
        const aRes = await dashboardAPI.getAnalystDashboard();
        setAnalystData(aRes.data);
      } catch (e) {}

      try {
        const mRes = await dashboardAPI.getManagerDashboard();
        setManagerData(mRes.data);
      } catch (e) {}

    } catch (err) {
      console.error("Error fetching dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [user]);

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
  const criticalAlertsCount = alerts.filter((a) => (a.severity || "").toLowerCase() === "critical").length;
  const openIncidentsCount = incidents.filter((i) => i.status !== "resolved").length;

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Top Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/40 border border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800 uppercase">
              Milestone 3: Risk Scoring & Threat Investigation
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3 mt-1">
            Behavioral Security Intelligence Operations Center
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Weighted 5-Factor Risk Scoring (35/25/20/10/10), UEBA Peer Comparison & SOC Threat Investigation.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleRunBatchAI}
            disabled={analyzingAll}
            className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-semibold shadow-lg shadow-cyan-600/20 transition"
          >
            <Cpu className={`w-4 h-4 ${analyzingAll ? "animate-spin" : ""}`} />
            <span>{analyzingAll ? "Computing Risk Scores..." : "Recalculate UEBA Risk Scores"}</span>
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
            <span className="text-xs text-emerald-400 font-medium">UEBA Active</span>
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
            <span>Active Investigations</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-bold text-amber-400 font-mono">{openIncidentsCount}</span>
            <span className="text-xs text-amber-400 font-medium">Milestone 3 Workflow</span>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 transition">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Total Security Events</span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-bold text-emerald-400 font-mono">
              {socData?.total_security_events || logStats?.total_logs || 0}
            </span>
            <span className="text-xs text-slate-400 font-medium">MongoDB Ingested</span>
          </div>
        </div>
      </div>

      {/* Milestone 3 Risk Distribution Summary (Manager View) */}
      {managerData && (
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-white flex items-center gap-2 font-mono">
              <BarChart3 className="w-4 h-4 text-cyan-400" />
              Organizational Risk Posture Distribution (Part 4 Analytics)
            </h2>
            <span className="text-xs text-cyan-300 font-mono">Compliance Score: {managerData.compliance_score}%</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3.5 rounded-xl bg-rose-950/40 border border-rose-800/60 text-center">
              <div className="text-[10px] font-mono uppercase text-rose-400 font-bold">Critical Risk (&ge;75)</div>
              <div className="text-2xl font-bold text-rose-300 font-mono">{managerData.distribution?.critical || 0}</div>
            </div>
            <div className="p-3.5 rounded-xl bg-amber-950/40 border border-amber-800/60 text-center">
              <div className="text-[10px] font-mono uppercase text-amber-400 font-bold">High Risk (&ge;50)</div>
              <div className="text-2xl font-bold text-amber-300 font-mono">{managerData.distribution?.high || 0}</div>
            </div>
            <div className="p-3.5 rounded-xl bg-yellow-950/40 border border-yellow-800/60 text-center">
              <div className="text-[10px] font-mono uppercase text-yellow-400 font-bold">Medium Risk (&ge;25)</div>
              <div className="text-2xl font-bold text-yellow-300 font-mono">{managerData.distribution?.medium || 0}</div>
            </div>
            <div className="p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-800/60 text-center">
              <div className="text-[10px] font-mono uppercase text-emerald-400 font-bold">Low Risk (&lt;25)</div>
              <div className="text-2xl font-bold text-emerald-300 font-mono">{managerData.distribution?.low || 0}</div>
            </div>
          </div>
        </div>
      )}

      {/* Milestone 3 Chart.js Visualizations (Analyst, SOC, Manager) */}
      <DashboardCharts socData={socData} analystData={analystData} managerData={managerData} />

      {/* Main Grid: Threat Watchlist & Live Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* High Risk Watchlist */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                High-Risk Identity Watchlist (UEBA)
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800">
                  {highRiskEmployees.length} Flagged
                </span>
              </h2>
              <p className="text-xs text-slate-400">Employees with elevated composite risk scores</p>
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
                  <th className="py-2.5">Risk Score</th>
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
                    <span className="text-[10px] font-mono text-cyan-400 font-bold">{alt.alert_code || `ALT-${alt.id}`}</span>
                    <span
                      className={`text-[10px] px-2 py-0.2 rounded font-mono font-semibold uppercase ${
                        (alt.severity || "").toLowerCase() === "critical"
                          ? "bg-rose-950 text-rose-300 border border-rose-800"
                          : (alt.severity || "").toLowerCase() === "high"
                          ? "bg-amber-950 text-amber-300 border border-amber-800"
                          : "bg-slate-800 text-slate-300"
                      }`}
                    >
                      {alt.severity}
                    </span>
                  </div>
                  <p className="text-xs font-semibold text-slate-200 line-clamp-1">{alt.title || alt.message}</p>
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
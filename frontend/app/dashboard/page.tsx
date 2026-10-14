"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import Navbar from "@/components/Navbar";
import api from "@/lib/api";
import { verifyAuthentication } from "@/lib/auth";
import RiskBarChart from "@/components/charts/RiskBarChart";
import AnomalyDoughnutChart from "@/components/charts/AnomalyDoughnutChart";
import AnomalyTrendChart from "@/components/charts/AnomalyTrendChart";
import SeverityDoughnutChart from "@/components/charts/SeverityDoughnutChart";
import RiskPostureChart from "@/components/charts/RiskPostureChart";
import IncidentTrendBarChart from "@/components/charts/IncidentTrendBarChart";
import UserRoleChart from "@/components/charts/UserRoleChart";

type DashboardRole = "analyst" | "soc" | "manager" | "admin";

export default function DashboardPage() {
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [currentUserRole, setCurrentUserRole] = useState<string>("security_analyst");
  const [activeTab, setActiveTab] = useState<DashboardRole>("analyst");

  // Dashboard Data States
  const [analystData, setAnalystData] = useState<any>(null);
  const [socData, setSocData] = useState<any>(null);
  const [managerData, setManagerData] = useState<any>(null);
  const [adminData, setAdminData] = useState<any>(null);

  const [loadingView, setLoadingView] = useState(true);
  const [errorMsg, setErrorMsg] = useState("");

  const [isAdmin, setIsAdmin] = useState(false);

  // ML Active Learning & Retraining State
  const [feedbackStats, setFeedbackStats] = useState<{
    count: number;
    confirmed: number;
    false_positives: number;
    benign: number;
  }>({ count: 0, confirmed: 0, false_positives: 0, benign: 0 });
  const [retrainingModel, setRetrainingModel] = useState(false);
  const [retrainResult, setRetrainResult] = useState<{
    type: "success" | "error";
    message: string;
  } | null>(null);

  const fetchFeedbackStats = async () => {
    try {
      const res = await api.get("/anomalies/feedback");
      const list = res.data?.feedback || [];
      const confirmed = list.filter(
        (f: any) => (f.feedback || "").toLowerCase() === "confirmed"
      ).length;
      const fp = list.filter(
        (f: any) => (f.feedback || "").toLowerCase() === "false_positive"
      ).length;
      const benign = list.filter(
        (f: any) => (f.feedback || "").toLowerCase() === "benign"
      ).length;
      setFeedbackStats({
        count: list.length,
        confirmed,
        false_positives: fp,
        benign,
      });
    } catch {
      // Gracefully ignore if role not authorized
    }
  };

  const handleRetrainModel = async () => {
    try {
      setRetrainingModel(true);
      setRetrainResult(null);
      const res = await api.post("/ml/retrain");
      setRetrainResult({
        type: "success",
        message:
          res.data?.message ||
          `Model retrained successfully on ${res.data?.samples_trained ?? 0} samples with ${
            res.data?.false_positive_adjustments ?? 0
          } false positive adjustments incorporated.`,
      });
      fetchFeedbackStats();
      fetchTabData(activeTab);
    } catch (err: any) {
      setRetrainResult({
        type: "error",
        message:
          err.response?.data?.detail || "Model retraining failed. Check backend telemetry.",
      });
    } finally {
      setRetrainingModel(false);
    }
  };

  useEffect(() => {
    const init = async () => {
      try {
        setCheckingAuth(true);
        const user = await verifyAuthentication();
        const rawRole = (user.role || "").toLowerCase().trim();
        setCurrentUserRole(user.role);
        const adminFlag = rawRole === "admin" || rawRole === "administrator";
        setIsAdmin(adminFlag);

        // Map user role to default view tab
        if (adminFlag) {
          setActiveTab("admin");
        } else if (rawRole === "security_manager" || rawRole === "manager") {
          setActiveTab("manager");
        } else if (rawRole === "soc_engineer" || rawRole === "soc") {
          setActiveTab("soc");
        } else {
          setActiveTab("analyst");
        }
      } catch (err: any) {
        if (err.response?.status === 401 || err.message?.includes("No authentication")) {
          localStorage.removeItem("itbis-token");
          localStorage.removeItem("itbis-user");
          window.location.href = "/login";
          return;
        }
      } finally {
        setCheckingAuth(false);
      }
    };

    init();
  }, []);

  const fetchTabData = async (tab: DashboardRole) => {
    try {
      setLoadingView(true);
      setErrorMsg("");

      if (tab === "analyst") {
        const res = await api.get("/dashboard/analyst");
        setAnalystData(res.data);
      } else if (tab === "soc") {
        const res = await api.get("/dashboard/soc");
        setSocData(res.data);
      } else if (tab === "manager") {
        const res = await api.get("/dashboard/manager");
        setManagerData(res.data);
      } else if (tab === "admin") {
        const res = await api.get("/dashboard/admin");
        setAdminData(res.data);
      }
    } catch (err: any) {
      if (err.response?.status === 403) {
        setErrorMsg(`Role '${currentUserRole}' is not authorized to view the ${tab.toUpperCase()} dashboard.`);
      } else {
        setErrorMsg("Failed to load dashboard telemetry.");
      }
    } finally {
      setLoadingView(false);
    }
  };

  useEffect(() => {
    if (!checkingAuth) {
      fetchTabData(activeTab);
      fetchFeedbackStats();
    }
  }, [activeTab, checkingAuth]);

  const renderMLOpsPanel = () => (
    <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6 space-y-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between border-b border-[var(--border)] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex h-6 w-6 items-center justify-center rounded-lg bg-indigo-500/20 text-xs font-bold text-indigo-400">
              ⚡
            </span>
            <h2 className="text-base font-bold">Autonomous ML Operations & Active Learning</h2>
            <span className="rounded-md border border-indigo-500/30 bg-indigo-500/10 px-2 py-0.5 text-[10px] font-semibold uppercase text-indigo-400">
              Isolation Forest
            </span>
          </div>
          <p className="mt-1 text-xs text-[var(--muted)]">
            Continuous active learning engine retraining behavioral anomaly weights incorporating analyst feedback and false-positive exemptions.
          </p>
        </div>

        <button
          onClick={handleRetrainModel}
          disabled={retrainingModel}
          className="flex items-center justify-center gap-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 px-4 py-2.5 text-xs font-semibold text-white shadow-sm transition disabled:opacity-50 cursor-pointer shrink-0"
        >
          {retrainingModel ? (
            <>
              <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white border-t-transparent" />
              <span>Retraining Model...</span>
            </>
          ) : (
            <>
              <span>↻</span>
              <span>Retrain Isolation Forest Model</span>
            </>
          )}
        </button>
      </div>

      {retrainResult && (
        <div
          className={`flex items-center justify-between rounded-xl p-3 text-xs font-medium ${
            retrainResult.type === "success"
              ? "border border-green-500/30 bg-green-500/10 text-green-400"
              : "border border-red-500/30 bg-red-500/10 text-red-400"
          }`}
        >
          <span>{retrainResult.message}</span>
          <button
            onClick={() => setRetrainResult(null)}
            className="ml-3 hover:opacity-75 cursor-pointer font-bold"
          >
            ✕
          </button>
        </div>
      )}

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 pt-1">
        <div className="rounded-xl border border-[var(--border)] bg-[var(--background)] p-3">
          <p className="text-[11px] font-medium text-[var(--muted)]">Total Feedback Records</p>
          <p className="mt-1 text-xl font-bold text-[var(--foreground)]">{feedbackStats.count}</p>
        </div>
        <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-3">
          <p className="text-[11px] font-medium text-red-400">Confirmed Threats</p>
          <p className="mt-1 text-xl font-bold text-red-400">{feedbackStats.confirmed}</p>
        </div>
        <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-3">
          <p className="text-[11px] font-medium text-amber-400">False Positive Exemptions</p>
          <p className="mt-1 text-xl font-bold text-amber-400">{feedbackStats.false_positives}</p>
        </div>
        <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-3">
          <p className="text-[11px] font-medium text-emerald-400">Benign Feedback Logs</p>
          <p className="mt-1 text-xl font-bold text-emerald-400">{feedbackStats.benign}</p>
        </div>
      </div>
    </div>
  );

  if (checkingAuth) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[var(--background)] text-[var(--foreground)]">
        <div className="text-center">
          <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--primary)]" />
          <p className="text-sm text-[var(--muted)]">Authenticating security session...</p>
        </div>
      </main>
    );
  }

  return (
    <div className="flex h-screen bg-[var(--background)] text-[var(--foreground)]">
      <Sidebar />

      <div className="flex flex-1 flex-col overflow-hidden">
        <Navbar />

        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="mx-auto max-w-6xl space-y-8">
            {/* Header & Role Switcher */}
            <div className="flex flex-col gap-4 border-b border-[var(--border)] pb-5 md:flex-row md:items-center md:justify-between">
              <div>
                <h1 className="text-2xl font-bold tracking-tight">Security Intelligence Operations</h1>
                <p className="text-sm text-[var(--muted)]">
                  Live UEBA telemetry, threat investigation queues, and multi-role operations center
                </p>
              </div>

              {/* 4-Role Dashboard Switcher Tabs - DISPLAYED ONLY FOR ADMIN */}
              {isAdmin ? (
                <div className="flex items-center gap-1 rounded-xl border border-[var(--border)] bg-[var(--card)] p-1">
                  {(["analyst", "soc", "manager", "admin"] as DashboardRole[]).map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`rounded-lg px-3 py-1.5 text-xs font-semibold capitalize transition ${
                        activeTab === tab
                          ? "bg-[var(--primary)] text-white shadow-sm"
                          : "text-[var(--muted)] hover:text-[var(--foreground)]"
                      }`}
                    >
                      {tab === "soc" ? "SOC Center" : `${tab} View`}
                    </button>
                  ))}
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  {activeTab === "analyst" && (
                    <span className="flex items-center gap-2 rounded-xl border border-purple-500/30 bg-purple-500/10 px-3.5 py-1.5 text-xs font-semibold text-purple-400">
                      <span className="h-2 w-2 rounded-full bg-purple-400 animate-pulse" />
                      Security Analyst Console
                    </span>
                  )}
                  {activeTab === "soc" && (
                    <span className="flex items-center gap-2 rounded-xl border border-blue-500/30 bg-blue-500/10 px-3.5 py-1.5 text-xs font-semibold text-blue-400">
                      <span className="h-2 w-2 rounded-full bg-blue-400 animate-pulse" />
                      SOC Operations Center
                    </span>
                  )}
                  {activeTab === "manager" && (
                    <span className="flex items-center gap-2 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-3.5 py-1.5 text-xs font-semibold text-emerald-400">
                      <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                      Security Management Console
                    </span>
                  )}
                </div>
              )}
            </div>

            {errorMsg && (
              <div className="flex flex-col gap-3 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-400 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="font-semibold">{errorMsg}</p>
                  <p className="mt-0.5 text-xs text-red-400/80">
                    Role-Based Access Control (RBAC) restricts this operational view to authorized roles.
                  </p>
                </div>
                <button
                  onClick={() => {
                    const r = (currentUserRole || "").toLowerCase().trim();
                    if (r === "admin" || r === "administrator") setActiveTab("admin");
                    else if (r === "security_manager" || r === "manager") setActiveTab("manager");
                    else if (r === "soc_engineer" || r === "soc") setActiveTab("soc");
                    else setActiveTab("analyst");
                  }}
                  className="w-fit shrink-0 rounded-lg bg-red-500/20 px-3 py-1.5 text-xs font-semibold text-red-300 hover:bg-red-500/30 transition"
                >
                  Return to My View
                </button>
              </div>
            )}

            {loadingView ? (
              <div className="flex h-64 items-center justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--primary)]" />
              </div>
            ) : (
              <>
                {/* 1. ANALYST VIEW */}
                {activeTab === "analyst" && analystData && (
                  <div className="space-y-6">
                    <div className="grid gap-4 md:grid-cols-3">
                      <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5">
                        <p className="text-xs font-semibold uppercase text-[var(--muted)]">Open Alerts</p>
                        <h3 className="mt-2 text-3xl font-extrabold text-amber-500">
                          {analystData.open_alerts?.length ?? 0}
                        </h3>
                        <p className="mt-1 text-xs text-[var(--muted)]">Pending analyst triage</p>
                      </div>
                      <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5">
                        <p className="text-xs font-semibold uppercase text-[var(--muted)]">Active Investigations</p>
                        <h3 className="mt-2 text-3xl font-extrabold text-blue-500">
                          {analystData.active_investigations ?? 0}
                        </h3>
                        <p className="mt-1 text-xs text-[var(--muted)]">Open incident tickets</p>
                      </div>
                      <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5">
                        <p className="text-xs font-semibold uppercase text-[var(--muted)]">Total Anomalies</p>
                        <h3 className="mt-2 text-3xl font-extrabold text-red-500">
                          {analystData.behavioral_anomalies?.total ?? 0}
                        </h3>
                        <p className="mt-1 text-xs text-[var(--muted)]">
                          {analystData.behavioral_anomalies?.rule_based ?? 0} Rule / {analystData.behavioral_anomalies?.machine_learning ?? 0} ML
                        </p>
                      </div>
                    </div>

                    {/* Visual Analytics */}
                    <div className="grid gap-6 lg:grid-cols-2">
                      <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6">
                        <div className="mb-4">
                          <h2 className="text-base font-bold">Detection Breakdown</h2>
                          <p className="text-xs text-[var(--muted)]">Rule-based heuristics vs Isolation Forest ML anomaly distribution</p>
                        </div>
                        <AnomalyDoughnutChart
                          ruleBased={analystData.behavioral_anomalies?.rule_based ?? 0}
                          machineLearning={analystData.behavioral_anomalies?.machine_learning ?? 0}
                        />
                      </div>

                      <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6">
                        <div className="mb-4">
                          <h2 className="text-base font-bold">Highest Risk Personnel</h2>
                          <p className="text-xs text-[var(--muted)]">Top insider risk scores calculated across behavior patterns</p>
                        </div>
                        <RiskBarChart employees={analystData.top_risk_employees || []} />
                      </div>
                    </div>

                    {/* Top Risk Employees */}
                    <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6">
                      <h2 className="text-base font-bold">Top High-Risk Employees (Prioritized Queue)</h2>
                      <div className="mt-4 overflow-x-auto">
                        <table className="w-full text-left text-sm">
                          <thead>
                            <tr className="border-b border-[var(--border)] text-xs uppercase text-[var(--muted)]">
                              <th className="pb-3">Employee</th>
                              <th className="pb-3">Department</th>
                              <th className="pb-3">Risk Level</th>
                              <th className="pb-3 text-right">Risk Score</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-[var(--border)]">
                            {analystData.top_risk_employees?.map((emp: any) => (
                              <tr key={emp.employee_code} className="hover:bg-[var(--card-hover)]">
                                <td className="py-3 font-medium">
                                  {emp.employee_name} ({emp.employee_code})
                                </td>
                                <td className="py-3 text-[var(--muted)]">{emp.department}</td>
                                <td className="py-3">
                                  <span className="rounded px-2 py-0.5 text-xs font-semibold uppercase bg-red-950/60 text-red-400">
                                    {emp.risk_level}
                                  </span>
                                </td>
                                <td className="py-3 text-right font-mono font-bold text-red-400">
                                  {emp.risk_score} / 100
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                )}

                {/* 2. SOC VIEW */}
                {activeTab === "soc" && socData && (
                  <div className="space-y-6">
                    <div className="grid gap-4 md:grid-cols-4">
                      {["critical", "high", "medium", "low"].map((sev) => (
                        <div key={sev} className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5">
                          <p className="text-xs font-semibold uppercase text-[var(--muted)]">{sev} Alerts</p>
                          <h3
                            className={`mt-2 text-3xl font-extrabold ${
                              sev === "critical"
                                ? "text-red-500"
                                : sev === "high"
                                ? "text-orange-500"
                                : sev === "medium"
                                ? "text-amber-500"
                                : "text-emerald-500"
                            }`}
                          >
                            {socData.alerts_by_severity?.[sev] ?? 0}
                          </h3>
                        </div>
                      ))}
                    </div>

                    {/* Visual Analytics */}
                    <div className="grid gap-6 lg:grid-cols-2">
                      <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6">
                        <div className="mb-4">
                          <h2 className="text-base font-bold">7-Day Threat & Anomaly Trajectory</h2>
                          <p className="text-xs text-[var(--muted)]">Daily ingestion velocity of rule violations & ML outliers</p>
                        </div>
                        <AnomalyTrendChart trend={socData.anomaly_trend_last_7_days || []} />
                      </div>

                      <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6">
                        <div className="mb-4">
                          <h2 className="text-base font-bold">Alert Severity Distribution</h2>
                          <p className="text-xs text-[var(--muted)]">Current operational alert triage posture by criticality</p>
                        </div>
                        <SeverityDoughnutChart
                          severities={
                            socData.alerts_by_severity || {
                              critical: 0,
                              high: 0,
                              medium: 0,
                              low: 0,
                            }
                          }
                        />
                      </div>
                    </div>

                    {/* 7-Day Trend */}
                    <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6">
                      <h2 className="text-base font-bold">7-Day Threat & Anomaly Trend Series</h2>
                      <div className="mt-4 overflow-x-auto">
                        <table className="w-full text-left text-sm">
                          <thead>
                            <tr className="border-b border-[var(--border)] text-xs uppercase text-[var(--muted)]">
                              <th className="pb-3">Date</th>
                              <th className="pb-3">Rule-Based Anomalies</th>
                              <th className="pb-3">ML Anomaly Flags</th>
                              <th className="pb-3 text-right">Total Ingested Anomalies</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-[var(--border)]">
                            {socData.anomaly_trend_last_7_days?.map((item: any) => (
                              <tr key={item.date} className="hover:bg-[var(--card-hover)]">
                                <td className="py-3 font-mono text-xs">{item.date}</td>
                                <td className="py-3">{item.rule_based}</td>
                                <td className="py-3">{item.machine_learning}</td>
                                <td className="py-3 text-right font-bold text-amber-400">{item.total}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* Active Learning & ML Retraining Operations */}
                    {renderMLOpsPanel()}
                  </div>
                )}

                {/* 3. SECURITY MANAGER VIEW */}
                {activeTab === "manager" && managerData && (
                  <div className="space-y-6">
                    <div className="grid gap-4 md:grid-cols-4">
                      {Object.entries(managerData.organizational_risk_posture?.risk_distribution || {}).map(
                        ([cat, count]: [string, any]) => (
                          <div key={cat} className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5">
                            <p className="text-xs font-semibold uppercase text-[var(--muted)]">{cat} Risk Posture</p>
                            <h3 className="mt-2 text-3xl font-extrabold">{count}</h3>
                            <p className="mt-1 text-xs text-[var(--muted)]">Personnel count</p>
                          </div>
                        )
                      )}
                    </div>

                    {/* Visual Analytics */}
                    <div className="grid gap-6 lg:grid-cols-2">
                      <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6">
                        <div className="mb-4">
                          <h2 className="text-base font-bold">Workforce Risk Distribution</h2>
                          <p className="text-xs text-[var(--muted)]">Overall organizational risk posture across active personnel</p>
                        </div>
                        <RiskPostureChart
                          distribution={
                            managerData.organizational_risk_posture?.risk_distribution || {
                              low: 0,
                              medium: 0,
                              high: 0,
                              critical: 0,
                            }
                          }
                          totalEmployees={
                            managerData.organizational_risk_posture?.total_employees || 0
                          }
                        />
                      </div>

                      <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6">
                        <div className="mb-4">
                          <h2 className="text-base font-bold">7-Day Security Incident Volume</h2>
                          <p className="text-xs text-[var(--muted)]">Escalated insider incident creation over the past 7 days</p>
                        </div>
                        <IncidentTrendBarChart
                          trend={managerData.incident_trend_last_7_days || []}
                        />
                      </div>
                    </div>

                    <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6">
                      <h2 className="text-base font-bold">Operational Resolution SLA Metrics</h2>
                      <div className="mt-4 grid gap-4 md:grid-cols-2">
                        <div className="rounded-xl border border-[var(--border)] bg-[var(--background)] p-4">
                          <p className="text-xs text-[var(--muted)]">Security Incidents Handled</p>
                          <p className="mt-1 text-xl font-bold">
                            {managerData.operational_metrics?.total_incidents - managerData.operational_metrics?.unresolved_incidents} / {managerData.operational_metrics?.total_incidents} Resolved
                          </p>
                        </div>
                        <div className="rounded-xl border border-[var(--border)] bg-[var(--background)] p-4">
                          <p className="text-xs text-[var(--muted)]">Security Alerts Triaged</p>
                          <p className="mt-1 text-xl font-bold">
                            {managerData.operational_metrics?.resolved_alerts} / {managerData.operational_metrics?.total_alerts} Resolved
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* 4. ADMIN VIEW */}
                {activeTab === "admin" && adminData && (
                  <div className="space-y-6">
                    <div className="grid gap-4 md:grid-cols-4">
                      <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5">
                        <p className="text-xs font-semibold uppercase text-[var(--muted)]">Platform Users</p>
                        <h3 className="mt-2 text-3xl font-extrabold text-blue-500">{adminData.user_count}</h3>
                        <p className="mt-1 text-xs text-[var(--muted)]">Registered analysts & admins</p>
                      </div>
                      <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5">
                        <p className="text-xs font-semibold uppercase text-[var(--muted)]">Monitored Personnel</p>
                        <h3 className="mt-2 text-3xl font-extrabold text-emerald-500">{adminData.employee_count}</h3>
                        <p className="mt-1 text-xs text-[var(--muted)]">Active employee profiles</p>
                      </div>
                      <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5">
                        <p className="text-xs font-semibold uppercase text-[var(--muted)]">Total Incidents</p>
                        <h3 className="mt-2 text-3xl font-extrabold text-orange-500">{adminData.total_incidents}</h3>
                        <p className="mt-1 text-xs text-[var(--muted)]">{adminData.open_incidents} currently open</p>
                      </div>
                      <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5">
                        <p className="text-xs font-semibold uppercase text-[var(--muted)]">Total Alerts</p>
                        <h3 className="mt-2 text-3xl font-extrabold text-purple-500">{adminData.total_alerts}</h3>
                        <p className="mt-1 text-xs text-[var(--muted)]">All generated alerts</p>
                      </div>
                    </div>

                    <div className="grid gap-6 lg:grid-cols-3">
                      {/* User Role Chart */}
                      <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6">
                        <div className="mb-4">
                          <h2 className="text-base font-bold">Role Distribution</h2>
                          <p className="text-xs text-[var(--muted)]">Active platform account allocation</p>
                        </div>
                        <UserRoleChart usersByRole={adminData.users_by_role || {}} />
                      </div>

                      {/* User Breakdown */}
                      <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6">
                        <h2 className="text-base font-bold">Platform Role Allocation Breakdown</h2>
                        <div className="mt-4 space-y-3">
                          {Object.entries(adminData.users_by_role || {}).map(([role, count]: [string, any]) => (
                            <div key={role} className="flex items-center justify-between border-b border-[var(--border)] pb-2 text-sm">
                              <span className="font-medium capitalize">{role.replace("_", " ")}</span>
                              <span className="font-mono font-bold text-[var(--primary)]">{count} User(s)</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* System Health */}
                      <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6">
                        <h2 className="text-base font-bold">System Infrastructure Status</h2>
                        <div className="mt-4 space-y-3">
                          {Object.entries(adminData.system_status || {}).map(([comp, status]: [string, any]) => (
                            <div key={comp} className="flex items-center justify-between border-b border-[var(--border)] pb-2 text-sm">
                              <span className="capitalize">{comp.replace("_", " ")}</span>
                              <span className="flex items-center gap-2 font-medium text-green-400">
                                <span className="h-2 w-2 rounded-full bg-green-500" />
                                {status}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* Active Learning & ML Retraining Operations */}
                    {renderMLOpsPanel()}
                  </div>
                )}
              </>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import Sidebar from "@/components/Sidebar";
import Navbar from "@/components/Navbar";
import InvestigationTimeline from "@/components/InvestigationTimeline";
import ExplainableAICard, { XAIExplanation } from "@/components/ExplainableAICard";
import api from "@/lib/api";
import { verifyAuthentication } from "@/lib/auth";

interface EmployeeProfile {
  id: number;
  employee_code: string;
  name: string;
  email: string;
  department: string;
  role: string;
  created_at: string;
}

interface RiskScoreData {
  employee_code: string;
  risk_score: number;
  risk_level: string;
  sub_scores?: Record<string, number>;
  factor_scores?: Record<string, number>;
}

interface PeerComparison {
  employee_code?: string;
  department?: string;
  employee_risk_score?: number;
  employee_score?: number;
  peer_average_risk_score?: number;
  department_avg_score?: number;
  variance_from_peers?: number;
  deviation_from_peers?: number;
  peer_count?: number;
  interpretation?: string;
}

interface TrendData {
  direction?: string | {
    direction?: string;
    period_days?: number;
    first_week_average?: number;
    second_week_average?: number;
    interpretation?: string;
  };
  delta?: number;
  days?: number;
  daily_trend?: Array<{ date: string; anomaly_count: number }>;
}

export default function EmployeeProfilePage({
  params,
}: {
  params: Promise<{ code: string }>;
}) {
  const resolvedParams = use(params);
  const employeeCode = decodeURIComponent(resolvedParams.code);

  const [employee, setEmployee] = useState<EmployeeProfile | null>(null);
  const [riskData, setRiskData] = useState<RiskScoreData | null>(null);
  const [peerData, setPeerData] = useState<PeerComparison | null>(null);
  const [trendData, setTrendData] = useState<TrendData | null>(null);
  const [xaiExplanations, setXaiExplanations] = useState<XAIExplanation[]>([]);
  const [loading, setLoading] = useState(true);
  const [escalating, setEscalating] = useState(false);
  const [escalateSuccess, setEscalateSuccess] = useState("");
  const [escalateError, setEscalateError] = useState("");

  const loadProfile = async () => {
    try {
      setLoading(true);
      await verifyAuthentication();

      // Parallel fetch employee dossier
      const [empRes, riskRes, peerRes, trendRes, xaiRes] = await Promise.allSettled([
        api.get(`/employees/${employeeCode}`),
        api.get(`/risk-score/${employeeCode}`),
        api.get(`/ueba/peer-comparison/${employeeCode}`),
        api.get(`/ueba/trend/${employeeCode}`),
        api.get(`/anomalies/${employeeCode}/xai`),
      ]);

      if (empRes.status === "fulfilled") setEmployee(empRes.value.data);
      if (riskRes.status === "fulfilled") setRiskData(riskRes.value.data);
      if (peerRes.status === "fulfilled") setPeerData(peerRes.value.data);
      if (trendRes.status === "fulfilled") setTrendData(trendRes.value.data);
      if (xaiRes.status === "fulfilled") setXaiExplanations(xaiRes.value.data.explanations || []);
    } catch (err: any) {
      if (err.response?.status === 401) {
        window.location.href = "/login";
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, [employeeCode]);

  const handleEscalateIncident = async () => {
    try {
      setEscalating(true);
      setEscalateSuccess("");
      setEscalateError("");
      const res = await api.post(`/incidents/create-from-risk/${employeeCode}`);
      setEscalateSuccess(`Incident #${res.data?.incident?.id || "created"} successfully opened from high risk score.`);
    } catch (err: any) {
      setEscalateError(err.response?.data?.detail || "Failed to escalate incident.");
    } finally {
      setEscalating(false);
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 75) return "text-red-500 border-red-500/50 bg-red-500/10";
    if (score >= 50) return "text-orange-500 border-orange-500/50 bg-orange-500/10";
    if (score >= 25) return "text-amber-500 border-amber-500/50 bg-amber-500/10";
    return "text-emerald-500 border-emerald-500/50 bg-emerald-500/10";
  };

  const rawDirection = trendData?.direction;
  const trendDirectionStr =
    typeof rawDirection === "object" && rawDirection !== null
      ? (rawDirection as any).direction || "stable"
      : typeof rawDirection === "string"
      ? rawDirection
      : "stable";

  const trendInterpretation =
    typeof rawDirection === "object" && rawDirection !== null
      ? (rawDirection as any).interpretation || ""
      : "";

  const peerAvg = peerData?.department_avg_score ?? peerData?.peer_average_risk_score ?? 0;
  const peerDeviation = peerData?.deviation_from_peers ?? peerData?.variance_from_peers ?? 0;

  const subScores = riskData?.sub_scores || riskData?.factor_scores || {};
  const behavioralScore = subScores.behavioral_anomalies ?? (subScores as any).behavioral_anomaly_score ?? 0;
  const privilegeScore = subScores.privilege_misuse ?? (subScores as any).privilege_level_score ?? 0;
  const dataAccessScore = subScores.data_access_violations ?? (subScores as any).data_access_score ?? 0;
  const accessPatternScore = subScores.access_pattern_deviations ?? (subScores as any).access_pattern_score ?? 0;
  const historicalScore = subScores.historical_events ?? (subScores as any).historical_incident_score ?? 0;

  return (
    <div className="flex h-screen bg-[var(--background)] text-[var(--foreground)]">
      <Sidebar />

      <div className="flex flex-1 flex-col overflow-hidden">
        <Navbar />

        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="mx-auto max-w-7xl space-y-8">
            {/* Breadcrumb & Navigation */}
            <div className="flex items-center gap-2 text-xs text-[var(--muted)]">
              <Link href="/employees" className="hover:text-[var(--foreground)]">
                ← Back to Employee Directory
              </Link>
              <span>/</span>
              <span className="font-mono text-[var(--foreground)]">{employeeCode}</span>
            </div>

            {loading ? (
              <div className="flex h-64 items-center justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--primary)]" />
              </div>
            ) : !employee ? (
              <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-8 text-center text-sm text-red-400">
                Employee profile not found for code <span className="font-mono">{employeeCode}</span>.
              </div>
            ) : (
              <>
                {/* Profile Header & Quick Actions */}
                <div className="flex flex-col gap-5 rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6 md:flex-row md:items-center md:justify-between">
                  <div className="flex items-center gap-4">
                    <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[var(--primary)] font-black text-xl text-white shadow-md">
                      {employee.name.charAt(0)}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h1 className="text-2xl font-bold">{employee.name}</h1>
                        <span className="rounded-md border border-[var(--border)] bg-[var(--background)] px-2 py-0.5 font-mono text-xs text-[var(--muted)]">
                          {employee.employee_code}
                        </span>
                      </div>
                      <p className="mt-0.5 text-xs text-[var(--muted)]">
                        {employee.role} • <span className="font-semibold text-[var(--foreground)]">{employee.department}</span> • {employee.email}
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-3">
                    <Link
                      href={`/reports/${employee.employee_code}/pdf`}
                      target="_blank"
                      className="rounded-xl border border-[var(--border)] bg-[var(--background)] px-4 py-2 text-xs font-semibold hover:border-[var(--primary)] hover:text-[var(--primary)] transition"
                    >
                      Download PDF Dossier 📄
                    </Link>
                    <button
                      onClick={handleEscalateIncident}
                      disabled={escalating}
                      className="rounded-xl bg-red-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-red-700 transition disabled:opacity-50"
                    >
                      {escalating ? "Opening Incident..." : "Escalate to Incident 🚨"}
                    </button>
                  </div>
                </div>

                {escalateSuccess && (
                  <div className="rounded-xl bg-emerald-500/10 border border-emerald-500/30 p-3 text-xs text-emerald-400">
                    ✓ {escalateSuccess}
                  </div>
                )}
                {escalateError && (
                  <div className="rounded-xl bg-red-500/10 border border-red-500/30 p-3 text-xs text-red-400">
                    ⚠ {escalateError}
                  </div>
                )}

                {/* Risk Score & Intelligence Dashboard Grid */}
                <div className="grid gap-6 md:grid-cols-3">
                  {/* Total Risk Score Card */}
                  <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6 flex flex-col justify-between">
                    <p className="text-xs font-semibold uppercase text-[var(--muted)]">Calculated Risk Score</p>
                    <div className="my-4 flex items-baseline gap-3">
                      <span className={`text-5xl font-black ${getRiskColor(riskData?.risk_score || 0).split(" ")[0]}`}>
                        {riskData?.risk_score ?? 0}
                      </span>
                      <span className="text-xs font-semibold text-[var(--muted)]">/ 100</span>
                      <span className={`rounded-md border px-2 py-0.5 text-xs font-bold uppercase ml-auto ${getRiskColor(riskData?.risk_score || 0)}`}>
                        {riskData?.risk_level || "Low"}
                      </span>
                    </div>
                    <p className="text-[11px] text-[var(--muted)]">
                      5-factor weighted behavioral intelligence assessment.
                    </p>
                  </div>

                  {/* Peer Group Comparison Card */}
                  <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6 flex flex-col justify-between">
                    <p className="text-xs font-semibold uppercase text-[var(--muted)]">Peer Cohort Benchmark</p>
                    <div className="my-4 space-y-2">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-[var(--muted)]">Department Avg ({peerData?.department || employee.department}):</span>
                        <span className="font-mono font-bold">{peerAvg}</span>
                      </div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-[var(--muted)]">Variance From Peers:</span>
                        <span className={`font-mono font-bold ${peerDeviation > 0 ? "text-red-400" : "text-emerald-400"}`}>
                          {peerDeviation > 0 ? `+${peerDeviation}` : peerDeviation}
                        </span>
                      </div>
                    </div>
                    <p className="text-[11px] text-[var(--muted)]">
                      Benchmarked against {peerData?.peer_count ?? 0} departmental peers.
                    </p>
                  </div>

                  {/* Velocity Trend Card */}
                  <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6 flex flex-col justify-between">
                    <p className="text-xs font-semibold uppercase text-[var(--muted)]">14-Day Risk Velocity</p>
                    <div className="my-4 flex items-center gap-3">
                      <span className="text-3xl">
                        {trendDirectionStr === "increasing" ? "📈" : trendDirectionStr === "decreasing" ? "📉" : "📊"}
                      </span>
                      <div>
                        <span className="text-lg font-bold capitalize text-[var(--foreground)]">
                          {trendDirectionStr} Direction
                        </span>
                        <p className="text-xs text-[var(--muted)]">
                          Delta: {trendData?.delta ? (trendData.delta > 0 ? `+${trendData.delta}` : trendData.delta) : "0"} points
                        </p>
                      </div>
                    </div>
                    <p className="text-[11px] text-[var(--muted)]">
                      {trendInterpretation || "Evaluated over rolling 14-day and 30-day behavioral telemetry."}
                    </p>
                  </div>
                </div>

                {/* 5-Factor Risk Weight Decomposition */}
                {(riskData?.sub_scores || riskData?.factor_scores) && (
                  <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6 space-y-4">
                    <h3 className="text-sm font-bold">5-Factor Risk Decomposition</h3>
                    <div className="grid gap-4 sm:grid-cols-5">
                      <div className="rounded-xl border border-[var(--border)] bg-[var(--background)] p-3">
                        <span className="text-[10px] uppercase font-semibold text-[var(--muted)]">Behavioral (35%)</span>
                        <p className="mt-1 text-xl font-black text-purple-400">{behavioralScore}</p>
                      </div>
                      <div className="rounded-xl border border-[var(--border)] bg-[var(--background)] p-3">
                        <span className="text-[10px] uppercase font-semibold text-[var(--muted)]">Privilege (25%)</span>
                        <p className="mt-1 text-xl font-black text-blue-400">{privilegeScore}</p>
                      </div>
                      <div className="rounded-xl border border-[var(--border)] bg-[var(--background)] p-3">
                        <span className="text-[10px] uppercase font-semibold text-[var(--muted)]">Data Access (20%)</span>
                        <p className="mt-1 text-xl font-black text-amber-400">{dataAccessScore}</p>
                      </div>
                      <div className="rounded-xl border border-[var(--border)] bg-[var(--background)] p-3">
                        <span className="text-[10px] uppercase font-semibold text-[var(--muted)]">Access Pattern (10%)</span>
                        <p className="mt-1 text-xl font-black text-orange-400">{accessPatternScore}</p>
                      </div>
                      <div className="rounded-xl border border-[var(--border)] bg-[var(--background)] p-3">
                        <span className="text-[10px] uppercase font-semibold text-[var(--muted)]">Historical (10%)</span>
                        <p className="mt-1 text-xl font-black text-emerald-400">{historicalScore}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Explainable AI (XAI) Breakdown */}
                {xaiExplanations.length > 0 && (
                  <div className="space-y-4">
                    <h2 className="text-lg font-bold">Machine Learning Anomaly Attribution (XAI)</h2>
                    <div className="space-y-4">
                      {xaiExplanations.map((exp, idx) => (
                        <ExplainableAICard key={idx} explanation={exp} onFeedbackSubmitted={loadProfile} />
                      ))}
                    </div>
                  </div>
                )}

                {/* Chronological Investigation Timeline */}
                <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6 space-y-4">
                  <h2 className="text-base font-bold">Chronological Behavioral Timeline</h2>
                  <InvestigationTimeline employeeCode={employeeCode} />
                </div>
              </>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

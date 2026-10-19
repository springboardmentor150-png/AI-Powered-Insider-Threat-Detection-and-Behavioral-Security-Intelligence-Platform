"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  BrainCircuit,
  Users,
  Clock,
  Laptop,
  Globe,
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  Shield,
  Loader2,
  RefreshCw,
  FileSearch,
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import { api } from "@/lib/api";

interface AnomalySignal {
  anomaly_type: string;
  severity: string;
  description: string;
  risk_contribution: number;
  observed_value: string;
  expected_baseline: string;
}

interface BehaviorData {
  employee: {
    id: number;
    employee_id: string;
    name: string;
    department?: string;
    designation?: string;
    risk_score: number;
    risk_level: string;
  };
  baseline: {
    normal_start_hour: number;
    normal_end_hour: number;
    usual_devices?: string;
    usual_ips?: string;
    total_activities_sampled: number;
    status_message: string;
  };
  has_sufficient_history: boolean;
  status_summary: string;
  recent_anomalies: AnomalySignal[];
  total_anomalies_detected: number;
  behavior_deviation_score: number;
}

export default function BehaviorAnalysisPage() {
  const [employees, setEmployees] = useState<any[]>([]);
  const [selectedEmpId, setSelectedEmpId] = useState<string>("FIN-2187");
  const [behavior, setBehavior] = useState<BehaviorData | null>(null);
  const [loading, setLoading] = useState(true);

  // Fetch employee list for selector
  useEffect(() => {
    const fetchEmpList = async () => {
      try {
        const res = await api.get("/employees?limit=50");
        const emps = res.data.items || [];
        setEmployees(emps);
        if (emps.length > 0 && !selectedEmpId) {
          setSelectedEmpId(emps[0].employee_id);
        }
      } catch (err) {
        console.error("Error fetching employees:", err);
      }
    };
    fetchEmpList();
  }, []);

  const fetchBehavior = useCallback(async (empId: string) => {
    setLoading(true);
    try {
      const res = await api.get(`/behavior-analysis/${empId}`);
      setBehavior(res.data);
    } catch (err) {
      console.error("Error fetching behavior analysis:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (selectedEmpId) {
      fetchBehavior(selectedEmpId);
    }
  }, [selectedEmpId, fetchBehavior]);

  return (
    <DashboardLayout
      pageTitle="Behavioral Baseline & Anomaly Inspector"
      pageSubtitle="Statistical norm modeling and real-time deviation telemetry"
    >
      <div className="space-y-6">
        {/* Selector Header */}
        <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xl">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-[var(--background)] border border-[#00A8FF]/40 flex items-center justify-center text-[#00E5FF]">
              <BrainCircuit className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-[var(--text-muted)]">Subject Selection</h3>
              <div className="text-sm font-semibold text-[var(--foreground)]">
                {behavior?.employee.name} ({selectedEmpId}) — {behavior?.employee.department}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            <select
              value={selectedEmpId}
              onChange={(e) => setSelectedEmpId(e.target.value)}
              className="w-full sm:w-64 bg-[var(--background)] border border-[var(--panel-border)] focus:border-[#00A8FF] rounded-lg px-3 py-2 text-xs text-[var(--foreground)] font-mono font-medium"
            >
              {employees.map((emp) => (
                <option key={emp.id} value={emp.employee_id}>
                  {emp.name} ({emp.employee_id}) — Risk: {emp.risk_score}
                </option>
              ))}
            </select>

            <button
              onClick={() => fetchBehavior(selectedEmpId)}
              className="p-2 rounded-lg bg-[var(--background)] border border-[var(--panel-border)] text-[var(--text-muted)] hover:text-[#00E5FF] transition cursor-pointer"
              title="Refresh Analysis"
            >
              <RefreshCw className="w-4 h-4" />
            </button>

            <Link
              href={`/investigations?employee_id=${selectedEmpId}`}
              className="px-3 py-2 bg-[#00A8FF] hover:bg-[#00E5FF] text-[#050B14] font-bold text-xs rounded-lg transition flex items-center gap-1.5 shadow-[0_0_10px_rgba(0,168,255,0.2)]"
            >
              <FileSearch className="w-3.5 h-3.5" />
              <span>Investigate</span>
            </Link>
          </div>
        </div>

        {loading ? (
          <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-16 text-center text-[var(--text-muted)]">
            <Loader2 className="w-6 h-6 animate-spin text-[#00E5FF] mx-auto mb-2" />
            <p className="text-xs">Computing behavioral deviations and baseline comparisons...</p>
          </div>
        ) : behavior ? (
          <>
            {/* Baseline Overview Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Card 1: Baseline Status */}
              <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-5 shadow-xl space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">Baseline Model</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                    behavior.has_sufficient_history
                      ? "bg-emerald-950/60 text-emerald-400 border border-emerald-800/40"
                      : "bg-[var(--background)] text-[#00A8FF] border border-[#00A8FF]/40"
                  }`}>
                    {behavior.has_sufficient_history ? "STABLE BASELINE" : "POLICY FALLBACK"}
                  </span>
                </div>

                <div className="text-xs text-[var(--foreground)] font-medium leading-relaxed bg-[var(--background)] p-3 rounded-lg border border-[var(--panel-border)]">
                  {behavior.status_summary}
                </div>

                <div className="text-[11px] text-[var(--text-muted)] flex justify-between font-mono pt-1">
                  <span>Samples Processed:</span>
                  <strong className="text-[#00E5FF]">{behavior.baseline?.total_activities_sampled ?? 0} events</strong>
                </div>
              </div>

              {/* Card 2: Operating Windows & Devices */}
              <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-5 shadow-xl space-y-3">
                <span className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider block">Observed Norms</span>
                
                <div className="space-y-2 text-xs">
                  <div className="flex items-center justify-between p-2 rounded bg-[var(--background)] border border-[var(--panel-border)]">
                    <span className="text-[var(--text-muted)] flex items-center gap-1.5"><Clock className="w-3.5 h-3.5 text-[#00A8FF]" /> Normal Hours:</span>
                    <span className="font-mono font-semibold text-[var(--foreground)]">
                      {behavior.baseline?.normal_start_hour ?? 9}:00 – {behavior.baseline?.normal_end_hour ?? 18}:00 UTC
                    </span>
                  </div>

                  <div className="flex items-center justify-between p-2 rounded bg-[var(--background)] border border-[var(--panel-border)]">
                    <span className="text-[var(--text-muted)] flex items-center gap-1.5"><Laptop className="w-3.5 h-3.5 text-[#00E5FF]" /> Primary Node:</span>
                    <span className="font-mono text-[11px] text-[var(--foreground)] truncate max-w-[140px]">
                      {behavior.baseline?.usual_devices ? "MacBook Pro / Dell" : "Standard Laptop"}
                    </span>
                  </div>

                  <div className="flex items-center justify-between p-2 rounded bg-[var(--background)] border border-[var(--panel-border)]">
                    <span className="text-[var(--text-muted)] flex items-center gap-1.5"><Globe className="w-3.5 h-3.5 text-[#00A8FF]" /> Known Subnets:</span>
                    <span className="font-mono text-[11px] text-[var(--foreground)]">10.0.0.0/16, VPN</span>
                  </div>
                </div>
              </div>

              {/* Card 3: Anomaly Impact */}
              <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-5 shadow-xl flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">Deviation Index</span>
                    <span className="text-xs font-bold text-[#00E5FF] font-mono">
                      {behavior.total_anomalies_detected} signals
                    </span>
                  </div>

                  <div className="mt-4 flex items-baseline gap-2">
                    <span className="text-3xl font-black text-[var(--foreground)]">{behavior.behavior_deviation_score}</span>
                    <span className="text-xs text-[var(--text-muted)]">/ 100 Deviation</span>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full h-2.5 bg-[var(--background)] rounded-full overflow-hidden border border-[var(--panel-border)] mt-3">
                    <div
                      className="h-full bg-gradient-to-r from-[#00A8FF] to-[#00E5FF] rounded-full"
                      style={{ width: `${Math.min(100, Math.max(10, behavior.behavior_deviation_score))}%` }}
                    />
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-[var(--panel-border)] flex justify-between text-xs">
                  <span className="text-[var(--text-muted)]">Current Risk Level:</span>
                  <span className={`font-mono font-bold ${
                    behavior.employee.risk_level === "CRITICAL" ? "text-[#00E5FF]" : "text-[#00A8FF]"
                  }`}>
                    {behavior.employee.risk_level} ({behavior.employee.risk_score})
                  </span>
                </div>
              </div>
            </div>

            {/* Detected Anomaly Signals Table */}
            <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl shadow-xl overflow-hidden">
              <div className="p-5 border-b border-[var(--panel-border)]">
                <h3 className="text-sm font-bold text-[var(--foreground)] uppercase tracking-wider flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-[#00E5FF]" />
                  Detected Behavioral Anomalies (Last 20 Activities)
                </h3>
                <p className="text-xs text-[var(--text-muted)] mt-0.5">
                  Signals comparing observed events against statistical and policy baselines
                </p>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="bg-[var(--background)]/80 border-b border-[var(--panel-border)] text-[10px] font-bold uppercase tracking-wider text-[var(--text-muted)] font-mono">
                      <th className="py-3 px-4">Severity</th>
                      <th className="py-3 px-4">Anomaly Vector</th>
                      <th className="py-3 px-4">Description</th>
                      <th className="py-3 px-4">Observed Telemetry</th>
                      <th className="py-3 px-4">Expected Baseline</th>
                      <th className="py-3 px-4">Contribution</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[var(--panel-border)]">
                    {behavior.recent_anomalies.length > 0 ? (
                      behavior.recent_anomalies.map((sig, idx) => (
                        <tr key={idx} className="hover:bg-[var(--background)]/60 transition">
                          <td className="py-3 px-4 whitespace-nowrap">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                              sig.severity === "CRITICAL"
                                ? "bg-cyan-950 text-[#00E5FF] border border-[#00E5FF]/40 shadow-[0_0_8px_rgba(0,229,255,0.2)]"
                                : sig.severity === "HIGH"
                                ? "bg-[#00A8FF]/20 text-[#00A8FF] border border-[#00A8FF]/40"
                                : "bg-[var(--background)] text-[var(--text-muted)] border border-[var(--panel-border)]"
                            }`}>
                              {sig.severity}
                            </span>
                          </td>
                          <td className="py-3 px-4 whitespace-nowrap font-mono text-xs text-[#00E5FF]">
                            {sig.anomaly_type}
                          </td>
                          <td className="py-3 px-4 text-xs text-[var(--foreground)] max-w-sm">
                            {sig.description}
                          </td>
                          <td className="py-3 px-4 whitespace-nowrap font-mono text-[11px] text-cyan-300">
                            {sig.observed_value}
                          </td>
                          <td className="py-3 px-4 whitespace-nowrap font-mono text-[11px] text-[var(--text-muted)]">
                            {sig.expected_baseline}
                          </td>
                          <td className="py-3 px-4 whitespace-nowrap font-mono font-bold text-xs text-[#00A8FF]">
                            +{sig.risk_contribution}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={6} className="py-12 text-center text-[var(--text-muted)]">
                          <div className="flex flex-col items-center justify-center gap-1">
                            <CheckCircle2 className="w-6 h-6 text-emerald-400 mb-1" />
                            <span className="font-semibold text-xs text-[var(--foreground)]">No Anomaly Deviations Detected</span>
                            <span className="text-[11px]">All observed activity matches normal baseline bounds.</span>
                          </div>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        ) : null}
      </div>
    </DashboardLayout>
  );
}

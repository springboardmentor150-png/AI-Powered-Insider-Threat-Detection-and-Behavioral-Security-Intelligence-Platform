"use client";

import { useState, useEffect, useCallback } from "react";
import {
  FileText,
  Download,
  Shield,
  AlertTriangle,
  Users,
  CheckCircle2,
  Calendar,
  Loader2,
  RefreshCw,
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import { api, API_BASE_URL } from "@/lib/api";

interface ReportSummary {
  generated_at: string;
  total_monitored_employees: number;
  high_risk_employee_count: number;
  total_alerts_period: number;
  critical_alerts_period: number;
  total_incidents_period: number;
  resolved_incidents_period: number;
  top_threat_categories: {
    category: string;
    count: number;
    percentage: number;
  }[];
  highest_risk_employees: {
    id: number;
    employee_id: string;
    name: string;
    department?: string;
    risk_score: number;
    risk_level: string;
    status: string;
  }[];
}

export default function ReportsPage() {
  const [report, setReport] = useState<ReportSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  const fetchReport = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get("/reports/summary");
      setReport(res.data);
    } catch (err) {
      console.error("Error fetching report:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchReport();
  }, [fetchReport]);

  const handleExportCSV = async () => {
    setExporting(true);
    try {
      const res = await api.get("/reports/export-csv", { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `ITBIS_Threat_Report_${new Date().toISOString().slice(0,10)}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert("Failed to export report CSV");
    } finally {
      setExporting(false);
    }
  };

  return (
    <DashboardLayout
      pageTitle="Executive Insider Threat Reports"
      pageSubtitle="Organizational threat posture summaries and audit telemetry exports"
    >
      <div className="space-y-6">
        {/* Top Control Bar */}
        <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-sm font-bold text-[#F4F8FF] uppercase tracking-wider flex items-center gap-2">
              <FileText className="w-4 h-4 text-[#00E5FF]" />
              Executive Security Audit Report
            </h3>
            <p className="text-xs text-[#8E9EB5] mt-0.5">
              Live snapshot generated at {report ? new Date(report.generated_at).toLocaleString() : "..."}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchReport}
              className="p-2 rounded-lg bg-[#050B14] border border-[#132B45] text-[#8E9EB5] hover:text-[#00E5FF] transition cursor-pointer"
              title="Refresh Report"
            >
              <RefreshCw className="w-4 h-4" />
            </button>

            <button
              onClick={handleExportCSV}
              disabled={exporting}
              className="px-4 py-2 bg-[#00A8FF] hover:bg-[#00E5FF] text-[#050B14] text-xs font-bold rounded-lg transition flex items-center gap-2 cursor-pointer shadow-[0_0_12px_rgba(0,168,255,0.3)]"
            >
              {exporting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5" />}
              <span>Export Telemetry CSV</span>
            </button>
          </div>
        </div>

        {loading ? (
          <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-16 text-center text-[#8E9EB5]">
            <Loader2 className="w-6 h-6 animate-spin text-[#00E5FF] mx-auto mb-2" />
            <p className="text-xs">Compiling executive posture telemetry...</p>
          </div>
        ) : report ? (
          <>
            {/* Metric KPI Row */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-4">
                <span className="text-[10px] uppercase font-bold text-[#8E9EB5]">Monitored Population</span>
                <div className="text-2xl font-black text-[#F4F8FF] mt-1">{report.total_monitored_employees}</div>
                <span className="text-[10px] text-[#00A8FF]">100% Enrolled</span>
              </div>

              <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-4">
                <span className="text-[10px] uppercase font-bold text-[#8E9EB5]">Elevated Risk Tiers</span>
                <div className="text-2xl font-black text-[#00E5FF] mt-1">{report.high_risk_employee_count}</div>
                <span className="text-[10px] text-[#00E5FF]">Score &ge; 60</span>
              </div>

              <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-4">
                <span className="text-[10px] uppercase font-bold text-[#8E9EB5]">Total Threat Detections</span>
                <div className="text-2xl font-black text-[#F4F8FF] mt-1">{report.total_alerts_period}</div>
                <span className="text-[10px] text-[#8E9EB5]">{report.critical_alerts_period} Critical Alerts</span>
              </div>

              <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-4">
                <span className="text-[10px] uppercase font-bold text-[#8E9EB5]">Incident Resolution Rate</span>
                <div className="text-2xl font-black text-emerald-400 mt-1">
                  {report.total_incidents_period > 0
                    ? `${Math.round((report.resolved_incidents_period / report.total_incidents_period) * 100)}%`
                    : "100%"}
                </div>
                <span className="text-[10px] text-[#8E9EB5]">{report.resolved_incidents_period}/{report.total_incidents_period} Cases Resolved</span>
              </div>
            </div>

            {/* Breakdown Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Threat Vectors Breakdown */}
              <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-5 shadow-xl space-y-4">
                <div className="pb-3 border-b border-[#132B45]">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-[#F4F8FF]">
                    Top Threat Vectors by Frequency
                  </h3>
                </div>

                <div className="space-y-3">
                  {report.top_threat_categories.map((cat, idx) => (
                    <div key={cat.category} className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-[#F4F8FF]">{cat.category}</span>
                        <span className="text-[#00E5FF] font-mono">{cat.count} alerts ({cat.percentage}%)</span>
                      </div>
                      <div className="w-full h-2 bg-[#050B14] rounded-full overflow-hidden border border-[#132B45]">
                        <div
                          className={`h-full ${idx === 0 ? "bg-[#00E5FF]" : idx === 1 ? "bg-[#00A8FF]" : "bg-[#1E3A5F]"} rounded-full`}
                          style={{ width: `${Math.max(5, cat.percentage)}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Highest Risk Monitored Entities */}
              <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-5 shadow-xl space-y-4">
                <div className="pb-3 border-b border-[#132B45]">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-[#F4F8FF]">
                    Highest Risk Monitored Subjects
                  </h3>
                </div>

                <div className="space-y-2">
                  {report.highest_risk_employees.map((emp) => (
                    <div
                      key={emp.id}
                      className="p-3 rounded-lg bg-[#050B14] border border-[#132B45] flex items-center justify-between text-xs"
                    >
                      <div>
                        <div className="font-semibold text-[#F4F8FF]">{emp.name}</div>
                        <div className="text-[10px] font-mono text-[#8E9EB5]">{emp.employee_id} • {emp.department}</div>
                      </div>
                      <span className={`px-2.5 py-1 rounded font-mono font-bold text-xs border ${
                        emp.risk_score >= 80
                          ? "bg-cyan-950 text-[#00E5FF] border-[#00E5FF]/40"
                          : emp.risk_score >= 60
                          ? "bg-[#00A8FF]/20 text-[#00A8FF] border-[#00A8FF]/30"
                          : "bg-[#132B45] text-[#8E9EB5] border-[#1E3A5F]"
                      }`}>
                        {emp.risk_score} / 100 ({emp.risk_level})
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </>
        ) : null}
      </div>
    </DashboardLayout>
  );
}

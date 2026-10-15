"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { reportAPI, employeeAPI } from "@/lib/api";
import {
  FileText,
  FileSpreadsheet,
  Download,
  ShieldAlert,
  Calendar,
  Filter,
  CheckCircle2,
  Clock,
  Layers,
  Sparkles,
  Info
} from "lucide-react";

export default function ReportsPage() {
  const { user } = useAuth();
  const [catalog, setCatalog] = useState<any[]>([]);
  const [employees, setEmployees] = useState<any[]>([]);
  const [selectedEmpId, setSelectedEmpId] = useState<string>("EMP1003");
  const [selectedDept, setSelectedDept] = useState<string>("");
  const [selectedStatus, setSelectedStatus] = useState<string>("");
  const [loadingCatalog, setLoadingCatalog] = useState(true);
  const [downloading, setDownloading] = useState<string | null>(null);

  useEffect(() => {
    const init = async () => {
      try {
        setLoadingCatalog(true);
        const [catRes, empRes] = await Promise.all([
          reportAPI.getCatalog(),
          employeeAPI.getAll()
        ]);
        setCatalog(catRes.data?.reports || []);
        const emps = empRes.data || [];
        setEmployees(emps);
        if (emps.length > 0) {
          const emp1003 = emps.find((e: any) => e.employee_id === "EMP1003");
          setSelectedEmpId(emp1003 ? "EMP1003" : emps[0].employee_id);
        }
      } catch (err) {
        console.error("Failed to fetch report catalog:", err);
      } finally {
        setLoadingCatalog(false);
      }
    };
    init();
  }, []);

  const handleDownloadEmpPdf = async () => {
    if (!selectedEmpId) return;
    try {
      setDownloading("emp-pdf");
      await reportAPI.downloadEmployeePdf(selectedEmpId);
    } catch (e) {
      alert("Error generating employee PDF report.");
    } finally {
      setDownloading(null);
    }
  };

  const handleDownloadCompliancePdf = async () => {
    try {
      setDownloading("comp-pdf");
      await reportAPI.downloadCompliancePdf();
    } catch (e) {
      alert("Error generating compliance summary PDF report.");
    } finally {
      setDownloading(null);
    }
  };

  const handleDownloadRiskScoresExcel = async () => {
    try {
      setDownloading("risk-excel");
      await reportAPI.downloadRiskScoresExcel(selectedDept || undefined);
    } catch (e) {
      alert("Error exporting risk scores to Excel.");
    } finally {
      setDownloading(null);
    }
  };

  const handleDownloadIncidentsExcel = async () => {
    try {
      setDownloading("inc-excel");
      await reportAPI.downloadIncidentsExcel(selectedStatus || undefined);
    } catch (e) {
      alert("Error exporting incidents to Excel.");
    } finally {
      setDownloading(null);
    }
  };

  const handleDownloadAuditExcel = async () => {
    try {
      setDownloading("audit-excel");
      await reportAPI.downloadAuditLogsExcel();
    } catch (e) {
      alert("Error exporting audit logs to Excel.");
    } finally {
      setDownloading(null);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in pb-12">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-rose-950/40 border border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800 uppercase">
              Milestone 4 — Reports & Export System
            </span>
            <span className="text-xs text-slate-400 font-mono">Days 33 & 34 Catalog</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight mt-1 flex items-center gap-2">
            <FileSpreadsheet className="w-6 h-6 text-rose-400" />
            <span>Executive Reporting & Data Export Center</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Generate in-memory PDF narrative reports for executive stakeholders and export bulk forensic spreadsheets in official OpenXML (.xlsx) format for data analysis.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleDownloadCompliancePdf}
            disabled={downloading === "comp-pdf"}
            className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-gradient-to-r from-rose-600 to-rose-700 hover:from-rose-500 hover:to-rose-600 text-white text-xs font-semibold shadow-lg shadow-rose-950/60 transition-all border border-rose-500/40"
          >
            <FileText className="w-4 h-4" />
            <span>{downloading === "comp-pdf" ? "Building PDF..." : "Export Compliance SLA PDF"}</span>
          </button>
        </div>
      </div>

      {/* Format Philosophy Callout (Day 33 & 34 Architecture) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-start space-x-3">
          <div className="p-2.5 rounded-lg bg-rose-950/70 border border-rose-800/80 text-rose-400">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">PDF Reports (Designed for Reading)</h3>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              Fixed-layout, publication-ready documents created entirely in RAM (<code className="text-rose-300 font-mono">io.BytesIO()</code>). Perfect for sharing with C-suite executives, compliance regulators, and non-platform auditors.
            </p>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-start space-x-3">
          <div className="p-2.5 rounded-lg bg-emerald-950/70 border border-emerald-800/80 text-emerald-400">
            <FileSpreadsheet className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">Excel Exports (Designed for Working with Data)</h3>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              Tabular, sortable datasets exported via <code className="text-emerald-300 font-mono">openpyxl</code> with highest-risk items pre-sorted at top. Handles empty dates safely and integrates with SIEM/BI tools.
            </p>
          </div>
        </div>
      </div>

      {/* Quick Export Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Card 1: Employee Risk PDF */}
        <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 flex flex-col justify-between space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-rose-950/80 text-rose-300 border border-rose-800/60 uppercase">
                PDF Narrative
              </span>
              <FileText className="w-5 h-5 text-rose-400" />
            </div>
            <h3 className="text-base font-bold text-white">Individual Employee Risk Dossier</h3>
            <p className="text-xs text-slate-400">
              Generates a single-employee deep-dive report including composite risk score, 5-factor sub-score table, and capped anomaly timeline.
            </p>

            <div className="space-y-1.5 pt-2">
              <label className="text-[11px] font-mono text-slate-400">Target Employee Identity:</label>
              <select
                value={selectedEmpId}
                onChange={(e) => setSelectedEmpId(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-800/80 border border-slate-700 text-xs text-white focus:outline-none focus:border-rose-500"
              >
                {employees.map((emp) => (
                  <option key={emp.employee_id} value={emp.employee_id}>
                    {emp.employee_id} — {emp.name} ({emp.department})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <button
            onClick={handleDownloadEmpPdf}
            disabled={downloading === "emp-pdf"}
            className="w-full py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-rose-900/60 border border-slate-700 hover:border-rose-700/80 text-xs font-semibold text-white flex items-center justify-center space-x-2 transition-all shadow-sm"
          >
            <Download className="w-4 h-4 text-rose-400" />
            <span>{downloading === "emp-pdf" ? "Rendering PDF..." : `Download ${selectedEmpId} PDF Report`}</span>
          </button>
        </div>

        {/* Card 2: Bulk Risk Scores Excel */}
        <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 flex flex-col justify-between space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-300 border border-emerald-800/60 uppercase">
                Excel Spreadsheet
              </span>
              <FileSpreadsheet className="w-5 h-5 text-emerald-400" />
            </div>
            <h3 className="text-base font-bold text-white">Workforce Risk Scores Export</h3>
            <p className="text-xs text-slate-400">
              Full organizational table of employee risk levels, pre-sorted highest-risk first with optional department filtering.
            </p>

            <div className="space-y-1.5 pt-2">
              <label className="text-[11px] font-mono text-slate-400">Filter Department (Optional):</label>
              <select
                value={selectedDept}
                onChange={(e) => setSelectedDept(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-800/80 border border-slate-700 text-xs text-white focus:outline-none focus:border-emerald-500"
              >
                <option value="">All Departments (Entire Workforce)</option>
                {Array.from(new Set(employees.map((e) => e.department))).map((dept) => (
                  <option key={dept} value={dept}>
                    {dept}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <button
            onClick={handleDownloadRiskScoresExcel}
            disabled={downloading === "risk-excel"}
            className="w-full py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-emerald-900/60 border border-slate-700 hover:border-emerald-700/80 text-xs font-semibold text-white flex items-center justify-center space-x-2 transition-all shadow-sm"
          >
            <Download className="w-4 h-4 text-emerald-400" />
            <span>{downloading === "risk-excel" ? "Generating .xlsx..." : "Export Risk Scores (.xlsx)"}</span>
          </button>
        </div>

        {/* Card 3: Security Incidents Excel */}
        <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 flex flex-col justify-between space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-800/60 uppercase">
                Excel Spreadsheet
              </span>
              <FileSpreadsheet className="w-5 h-5 text-cyan-400" />
            </div>
            <h3 className="text-base font-bold text-white">Security Incidents & Forensics Log</h3>
            <p className="text-xs text-slate-400">
              Complete historical incident list including severity, assigned investigator, MITRE technique, creation and resolution timestamps.
            </p>

            <div className="space-y-1.5 pt-2">
              <label className="text-[11px] font-mono text-slate-400">Filter Incident Status:</label>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-800/80 border border-slate-700 text-xs text-white focus:outline-none focus:border-cyan-500"
              >
                <option value="">All Incidents (Open & Resolved)</option>
                <option value="OPEN">Open Incidents Only</option>
                <option value="INVESTIGATING">Active Investigations</option>
                <option value="RESOLVED">Resolved Incidents</option>
              </select>
            </div>
          </div>

          <button
            onClick={handleDownloadIncidentsExcel}
            disabled={downloading === "inc-excel"}
            className="w-full py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-cyan-900/60 border border-slate-700 hover:border-cyan-700/80 text-xs font-semibold text-white flex items-center justify-center space-x-2 transition-all shadow-sm"
          >
            <Download className="w-4 h-4 text-cyan-400" />
            <span>{downloading === "inc-excel" ? "Generating .xlsx..." : "Export Incidents (.xlsx)"}</span>
          </button>
        </div>
      </div>

      {/* Report Catalog Table (Day 34 Catalog Single Source of Truth) */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Layers className="w-4 h-4 text-rose-400" />
              <span>Platform Report Catalog (`/reports/catalog`)</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Live endpoint registry defining all exportable report structures, file formats, and role permissions.
            </p>
          </div>
          <span className="text-xs font-mono text-slate-500">
            {catalog.length} Available Formats
          </span>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-800/80">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/60 text-slate-400 font-mono uppercase text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Report Name</th>
                <th className="py-3 px-4">Format</th>
                <th className="py-3 px-4">Endpoint URI</th>
                <th className="py-3 px-4">Description</th>
                <th className="py-3 px-4 text-right">Allowed Roles</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {catalog.map((rep, idx) => (
                <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-3 px-4 font-semibold text-white flex items-center gap-2">
                    {rep.format === "PDF" ? (
                      <FileText className="w-3.5 h-3.5 text-rose-400" />
                    ) : (
                      <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
                    )}
                    <span>{rep.name}</span>
                  </td>
                  <td className="py-3 px-4">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono uppercase ${
                        rep.format === "PDF"
                          ? "bg-rose-950/80 text-rose-300 border border-rose-800/60"
                          : "bg-emerald-950/80 text-emerald-300 border border-emerald-800/60"
                      }`}
                    >
                      {rep.format}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono text-[11px] text-cyan-400">
                    {rep.endpoint}
                  </td>
                  <td className="py-3 px-4 text-slate-400 text-xs">
                    {rep.description}
                  </td>
                  <td className="py-3 px-4 text-right font-mono text-[10px] text-slate-400">
                    {(rep.allowed_roles || []).join(", ")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

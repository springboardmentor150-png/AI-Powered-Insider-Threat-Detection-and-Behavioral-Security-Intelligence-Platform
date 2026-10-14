"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import Navbar from "@/components/Navbar";
import api from "@/lib/api";
import { verifyAuthentication } from "@/lib/auth";

type Employee = {
  id: number;
  employee_code: string;
  name: string;
  department: string;
  role: string;
};

type CatalogReport = {
  name: string;
  format: string;
  endpoint: string;
  description: string;
};

export default function ReportsPage() {
  const [catalog, setCatalog] = useState<CatalogReport[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [selectedEmployee, setSelectedEmployee] = useState<string>("");
  const [selectedDepartment, setSelectedDepartment] = useState<string>("");
  const [selectedIncidentStatus, setSelectedIncidentStatus] = useState<string>("");

  const [loadingInitial, setLoadingInitial] = useState(true);
  const [downloadingReport, setDownloadingReport] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  useEffect(() => {
    const init = async () => {
      try {
        setLoadingInitial(true);
        await verifyAuthentication();

        const [catalogRes, empRes] = await Promise.all([
          api.get("/reports/catalog"),
          api.get("/employees"),
        ]);

        if (catalogRes.data?.reports) {
          setCatalog(catalogRes.data.reports);
        }

        const empData = Array.isArray(empRes.data)
          ? empRes.data
          : empRes.data?.employees || [];
        setEmployees(empData);
        if (empData.length > 0) {
          setSelectedEmployee(empData[0].employee_code);
        }
      } catch (err: any) {
        if (err.response?.status === 401) {
          window.location.href = "/login";
        } else {
          setStatusMessage({
            type: "error",
            text: "Failed to initialize reports data. Please ensure backend is active.",
          });
        }
      } finally {
        setLoadingInitial(false);
      }
    };

    init();
  }, []);

  const triggerDownload = async (url: string, defaultFilename: string, key: string) => {
    try {
      setDownloadingReport(key);
      setStatusMessage(null);

      const response = await api.get(url, {
        responseType: "blob",
      });

      const disposition = String(response.headers["content-disposition"] || "");
      let filename = defaultFilename;
      if (disposition) {
        const match = disposition.match(/filename="?([^";]+)"?/);
        if (match && match[1]) {
          filename = match[1];
        }
      }

      const blob = new Blob([response.data], {
        type: String(response.headers["content-type"] || "application/octet-stream"),
      });
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);

      setStatusMessage({
        type: "success",
        text: `Successfully generated and downloaded ${filename}`,
      });
    } catch (err: any) {
      const errText =
        err.response?.data?.detail ||
        "Failed to download report. Please check permissions.";
      setStatusMessage({
        type: "error",
        text: typeof errText === "string" ? errText : "Download failed.",
      });
    } finally {
      setDownloadingReport(null);
    }
  };

  const departments = Array.from(
    new Set(employees.map((e) => e.department).filter(Boolean))
  );

  return (
    <div className="flex h-screen bg-[var(--background)] text-[var(--foreground)]">
      <Sidebar />

      <div className="flex flex-1 flex-col overflow-hidden">
        <Navbar />

        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="mx-auto max-w-6xl space-y-8">
            {/* Header */}
            <div className="border-b border-[var(--border)] pb-5">
              <div className="flex items-center gap-3">
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--primary)] text-xl text-white">
                  ▤
                </span>
                <div>
                  <h1 className="text-2xl font-bold tracking-tight">
                    Reports & Export System
                  </h1>
                  <p className="text-sm text-[var(--muted)]">
                    In-memory generated PDF dossiers, ISO/NIST compliance audits, and bulk Excel spreadsheets
                  </p>
                </div>
              </div>
            </div>

            {/* Status alerts */}
            {statusMessage && (
              <div
                className={`flex items-center justify-between rounded-xl p-4 text-sm font-medium ${
                  statusMessage.type === "success"
                    ? "border border-green-500/30 bg-green-500/10 text-green-400"
                    : "border border-red-500/30 bg-red-500/10 text-red-400"
                }`}
              >
                <span>{statusMessage.text}</span>
                <button
                  onClick={() => setStatusMessage(null)}
                  className="ml-4 hover:opacity-75"
                >
                  ✕
                </button>
              </div>
            )}

            {/* Reports Grid */}
            <div className="grid gap-6 md:grid-cols-2">
              {/* Card 1: Employee Risk Report PDF */}
              <div className="flex flex-col justify-between rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6 shadow-sm transition hover:border-[var(--primary)]">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="rounded-lg bg-red-950/60 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-red-400 border border-red-800/40">
                      PDF Dossier
                    </span>
                    <span className="text-xs text-[var(--muted)]">In-Memory (ReportLab)</span>
                  </div>

                  <div>
                    <h2 className="text-lg font-bold">Employee Insider Risk Report</h2>
                    <p className="mt-1 text-xs text-[var(--muted)]">
                      Individual insider threat assessment dossier displaying 5-factor weighted scores, overall risk category, and top 10 anomaly traces.
                    </p>
                  </div>

                  <div className="space-y-2 pt-2">
                    <label className="text-xs font-medium text-[var(--muted)]">
                      Select Employee
                    </label>
                    <select
                      value={selectedEmployee}
                      onChange={(e) => setSelectedEmployee(e.target.value)}
                      disabled={loadingInitial || employees.length === 0}
                      className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-sm focus:border-[var(--primary)] focus:outline-none"
                    >
                      {employees.map((emp) => (
                        <option key={emp.id} value={emp.employee_code}>
                          {emp.employee_code} — {emp.name} ({emp.department})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-[var(--border)]">
                  <button
                    onClick={() =>
                      triggerDownload(
                        `/reports/${selectedEmployee}/pdf`,
                        `${selectedEmployee}_risk_report.pdf`,
                        "employee_pdf"
                      )
                    }
                    disabled={!selectedEmployee || downloadingReport === "employee_pdf"}
                    className="flex w-full items-center justify-center gap-2 rounded-xl bg-red-700 hover:bg-red-800 px-4 py-2.5 text-sm font-semibold text-white transition disabled:opacity-50"
                  >
                    {downloadingReport === "employee_pdf" ? (
                      <span>Generating PDF...</span>
                    ) : (
                      <>
                        <span>⬇</span>
                        <span>Download Employee Dossier (.pdf)</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Card 2: Compliance Summary Report PDF */}
              <div className="flex flex-col justify-between rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6 shadow-sm transition hover:border-[var(--primary)]">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="rounded-lg bg-blue-950/60 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-blue-400 border border-blue-800/40">
                      Compliance Audit PDF
                    </span>
                    <span className="text-xs text-[var(--muted)]">ISO 27001 / NIST / SOC 2</span>
                  </div>

                  <div>
                    <h2 className="text-lg font-bold">Compliance Summary Report</h2>
                    <p className="mt-1 text-xs text-[var(--muted)]">
                      Organizational risk posture dossier, incident resolution SLA metrics, alert triage efficiency, and regulatory compliance audit trail.
                    </p>
                  </div>

                  <div className="rounded-xl border border-[var(--border)] bg-[var(--background)] p-3 text-xs text-[var(--muted)]">
                    <p className="font-semibold text-[var(--foreground)]">Audit Standards Evaluated:</p>
                    <ul className="mt-1 list-disc pl-4 space-y-0.5">
                      <li>Personnel Monitoring & UEBA Baselines</li>
                      <li>Incident SLA Response Times</li>
                      <li>High/Critical Threat Mitigation Rate</li>
                    </ul>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-[var(--border)]">
                  <button
                    onClick={() =>
                      triggerDownload(
                        "/reports/compliance/pdf",
                        "compliance_summary_report.pdf",
                        "compliance_pdf"
                      )
                    }
                    disabled={downloadingReport === "compliance_pdf"}
                    className="flex w-full items-center justify-center gap-2 rounded-xl bg-blue-700 hover:bg-blue-800 px-4 py-2.5 text-sm font-semibold text-white transition disabled:opacity-50"
                  >
                    {downloadingReport === "compliance_pdf" ? (
                      <span>Generating PDF...</span>
                    ) : (
                      <>
                        <span>⬇</span>
                        <span>Download Compliance Report (.pdf)</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Card 3: Bulk Risk Scores Excel */}
              <div className="flex flex-col justify-between rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6 shadow-sm transition hover:border-[var(--primary)]">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="rounded-lg bg-emerald-950/60 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-emerald-400 border border-emerald-800/40">
                      Excel Spreadsheet
                    </span>
                    <span className="text-xs text-[var(--muted)]">Sorted Highest-Risk First</span>
                  </div>

                  <div>
                    <h2 className="text-lg font-bold">All Employee Risk Scores (.xlsx)</h2>
                    <p className="mt-1 text-xs text-[var(--muted)]">
                      Bulk tabular data export of employee risk metrics, pre-sorted descending by threat severity for offline analysis and auditing.
                    </p>
                  </div>

                  <div className="space-y-2 pt-2">
                    <label className="text-xs font-medium text-[var(--muted)]">
                      Filter by Department (Optional)
                    </label>
                    <select
                      value={selectedDepartment}
                      onChange={(e) => setSelectedDepartment(e.target.value)}
                      className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-sm focus:border-[var(--primary)] focus:outline-none"
                    >
                      <option value="">All Departments (No Filter)</option>
                      {departments.map((dept) => (
                        <option key={dept} value={dept}>
                          {dept}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-[var(--border)]">
                  <button
                    onClick={() => {
                      const url = selectedDepartment
                        ? `/reports/export/risk-scores?department=${encodeURIComponent(
                            selectedDepartment
                          )}`
                        : "/reports/export/risk-scores";
                      triggerDownload(url, "risk_scores_export.xlsx", "risk_excel");
                    }}
                    disabled={downloadingReport === "risk_excel"}
                    className="flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-700 hover:bg-emerald-800 px-4 py-2.5 text-sm font-semibold text-white transition disabled:opacity-50"
                  >
                    {downloadingReport === "risk_excel" ? (
                      <span>Generating Excel...</span>
                    ) : (
                      <>
                        <span>⇪</span>
                        <span>Export Risk Scores (.xlsx)</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Card 4: Incident Report Excel */}
              <div className="flex flex-col justify-between rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6 shadow-sm transition hover:border-[var(--primary)]">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="rounded-lg bg-purple-950/60 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-purple-400 border border-purple-800/40">
                      Excel Spreadsheet
                    </span>
                    <span className="text-xs text-[var(--muted)]">Incident Tickets</span>
                  </div>

                  <div>
                    <h2 className="text-lg font-bold">Security Incidents Export (.xlsx)</h2>
                    <p className="mt-1 text-xs text-[var(--muted)]">
                      Tabular dump of all security incident investigations with timestamps, statuses, severity ratings, and resolution markers.
                    </p>
                  </div>

                  <div className="space-y-2 pt-2">
                    <label className="text-xs font-medium text-[var(--muted)]">
                      Filter by Incident Status (Optional)
                    </label>
                    <select
                      value={selectedIncidentStatus}
                      onChange={(e) => setSelectedIncidentStatus(e.target.value)}
                      className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-sm focus:border-[var(--primary)] focus:outline-none"
                    >
                      <option value="">All Statuses (No Filter)</option>
                      <option value="open">Open</option>
                      <option value="investigating">Investigating</option>
                      <option value="resolved">Resolved</option>
                    </select>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-[var(--border)]">
                  <button
                    onClick={() => {
                      const url = selectedIncidentStatus
                        ? `/reports/export/incidents?status=${encodeURIComponent(
                            selectedIncidentStatus
                          )}`
                        : "/reports/export/incidents";
                      triggerDownload(url, "incidents_export.xlsx", "inc_excel");
                    }}
                    disabled={downloadingReport === "inc_excel"}
                    className="flex w-full items-center justify-center gap-2 rounded-xl bg-purple-700 hover:bg-purple-800 px-4 py-2.5 text-sm font-semibold text-white transition disabled:opacity-50"
                  >
                    {downloadingReport === "inc_excel" ? (
                      <span>Generating Excel...</span>
                    ) : (
                      <>
                        <span>⇪</span>
                        <span>Export Incidents (.xlsx)</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Card 5: Enterprise Insider Threat Assessment PDF */}
              <div className="flex flex-col justify-between rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6 shadow-sm transition hover:border-[var(--primary)]">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="rounded-lg bg-rose-950/60 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-rose-400 border border-rose-800/40">
                      Executive PDF Summary
                    </span>
                    <span className="text-xs text-[var(--muted)]">Organization-Wide</span>
                  </div>

                  <div>
                    <h2 className="text-lg font-bold">Enterprise Insider Threat Matrix (.pdf)</h2>
                    <p className="mt-1 text-xs text-[var(--muted)]">
                      Consolidated executive dossier detailing company-wide workforce risk ratings, highest-risk personnel rankings, and threat posture highlights.
                    </p>
                  </div>

                  <div className="rounded-xl border border-[var(--border)] bg-[var(--background)] p-3 text-xs text-[var(--muted)]">
                    <p className="font-semibold text-[var(--foreground)]">Executive Briefing Highlights:</p>
                    <ul className="mt-1 list-disc pl-4 space-y-0.5">
                      <li>Workforce risk scoring sorted descending</li>
                      <li>Department-level threat categorization</li>
                      <li>Auditor-ready formatted PDF output</li>
                    </ul>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-[var(--border)]">
                  <button
                    onClick={() =>
                      triggerDownload(
                        "/reports/insider-threat/pdf",
                        "insider_threat_report.pdf",
                        "insider_pdf"
                      )
                    }
                    disabled={downloadingReport === "insider_pdf"}
                    className="flex w-full items-center justify-center gap-2 rounded-xl bg-rose-700 hover:bg-rose-800 px-4 py-2.5 text-sm font-semibold text-white transition disabled:opacity-50"
                  >
                    {downloadingReport === "insider_pdf" ? (
                      <span>Generating PDF...</span>
                    ) : (
                      <>
                        <span>⬇</span>
                        <span>Download Executive Threat PDF (.pdf)</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Card 6: Enterprise Threat Ledger Excel */}
              <div className="flex flex-col justify-between rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6 shadow-sm transition hover:border-[var(--primary)]">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="rounded-lg bg-teal-950/60 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-teal-400 border border-teal-800/40">
                      Excel Threat Matrix
                    </span>
                    <span className="text-xs text-[var(--muted)]">Full Workforce Ledger</span>
                  </div>

                  <div>
                    <h2 className="text-lg font-bold">Enterprise Threat Ledger (.xlsx)</h2>
                    <p className="mt-1 text-xs text-[var(--muted)]">
                      Company-wide tabular dataset of all active personnel, complete with calculated weighted risk scores and real-time risk tiers.
                    </p>
                  </div>

                  <div className="rounded-xl border border-[var(--border)] bg-[var(--background)] p-3 text-xs text-[var(--muted)]">
                    <p className="font-semibold text-[var(--foreground)]">Export Specifications:</p>
                    <ul className="mt-1 list-disc pl-4 space-y-0.5">
                      <li>Complete employee identity & department registry</li>
                      <li>Real-time multi-factor weighted risk indices</li>
                      <li>Optimized for SIEM ingestion and offline reporting</li>
                    </ul>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-[var(--border)]">
                  <button
                    onClick={() =>
                      triggerDownload(
                        "/reports/insider-threat/excel",
                        "insider_threat_report.xlsx",
                        "insider_excel"
                      )
                    }
                    disabled={downloadingReport === "insider_excel"}
                    className="flex w-full items-center justify-center gap-2 rounded-xl bg-teal-700 hover:bg-teal-800 px-4 py-2.5 text-sm font-semibold text-white transition disabled:opacity-50"
                  >
                    {downloadingReport === "insider_excel" ? (
                      <span>Generating Excel...</span>
                    ) : (
                      <>
                        <span>⇪</span>
                        <span>Export Threat Matrix Ledger (.xlsx)</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Catalog Info Table */}
            <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6 shadow-sm">
              <h3 className="text-base font-bold">Registered Report Catalog API Endpoints</h3>
              <p className="text-xs text-[var(--muted)]">
                The single source of truth for platform reporting integrations, queryable at <code>/reports/catalog</code>.
              </p>

              <div className="mt-4 overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-[var(--border)] text-xs uppercase tracking-wider text-[var(--muted)]">
                      <th className="pb-3 font-semibold">Report Name</th>
                      <th className="pb-3 font-semibold">Format</th>
                      <th className="pb-3 font-semibold">API Endpoint</th>
                      <th className="pb-3 font-semibold">Description</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[var(--border)]">
                    {catalog.map((rep, idx) => (
                      <tr key={idx} className="hover:bg-[var(--card-hover)]">
                        <td className="py-3 font-medium">{rep.name}</td>
                        <td className="py-3">
                          <span
                            className={`rounded px-2 py-0.5 text-xs font-semibold ${
                              rep.format === "PDF"
                                ? "bg-red-950/60 text-red-400"
                                : "bg-emerald-950/60 text-emerald-400"
                            }`}
                          >
                            {rep.format}
                          </span>
                        </td>
                        <td className="py-3 font-mono text-xs text-[var(--muted)]">
                          {rep.endpoint}
                        </td>
                        <td className="py-3 text-xs text-[var(--muted)]">
                          {rep.description}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  Users,
  Search,
  Filter,
  ShieldAlert,
  X,
  UserCheck,
  RefreshCw,
  Loader2,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  FileSearch,
  Briefcase,
  GraduationCap,
  MapPin,
  Clock,
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import { api } from "@/lib/api";

interface EmployeeItem {
  id: number;
  employee_id: string;
  name: string;
  email?: string;
  department?: string;
  designation?: string;
  manager_name?: string;
  employment_type?: string;
  work_location?: string;
  joining_date?: string;
  years_of_experience?: number;
  education?: string;
  skills?: string;
  device_info?: string;
  access_privileges?: string;
  risk_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  status: "ACTIVE" | "UNDER_REVIEW" | "FLAGGED" | "RESTRICTED";
  created_at: string;
}

interface EmployeeDetailData {
  employee: EmployeeItem;
  alerts: any[];
  incidents: any[];
  recent_activities?: any[];
  baseline?: any;
  direct_reports?: EmployeeItem[];
}

interface PaginatedEmployeesResponse {
  items: EmployeeItem[];
  page: number;
  limit: number;
  total: number;
}

const DEPARTMENTS = [
  "Cybersecurity",
  "Finance",
  "IT & Infrastructure",
  "Human Resources",
  "DevOps & Engineering",
  "Compliance & Legal",
];

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<EmployeeItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const limit = 10;

  const [searchQuery, setSearchQuery] = useState("");
  const [deptFilter, setDeptFilter] = useState("ALL");
  const [riskFilter, setRiskFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Dossier modal state
  const [selectedEmployeeDetail, setSelectedEmployeeDetail] = useState<EmployeeDetailData | null>(null);
  const [loadingDossier, setLoadingDossier] = useState(false);

  const fetchEmployees = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get<PaginatedEmployeesResponse>("/employees", {
        params: {
          search: searchQuery.trim() || undefined,
          department: deptFilter !== "ALL" ? deptFilter : undefined,
          risk_level: riskFilter !== "ALL" ? riskFilter : undefined,
          status: statusFilter !== "ALL" ? statusFilter : undefined,
          page,
          limit,
        },
      });

      setEmployees(response.data.items || []);
      setTotal(response.data.total || 0);
    } catch (err: unknown) {
      console.error("Failed to load employees:", err);
      setError("Security telemetry server is unreachable. Please verify backend connection.");
    } finally {
      setLoading(false);
    }
  }, [searchQuery, deptFilter, riskFilter, statusFilter, page]);

  useEffect(() => {
    fetchEmployees();
  }, [fetchEmployees]);

  const handleOpenDossier = async (empId: string) => {
    setLoadingDossier(true);
    try {
      const [res, reportsRes] = await Promise.all([
        api.get<EmployeeDetailData>(`/employees/${empId}`),
        api.get<EmployeeItem[]>(`/employees/${empId}/direct-reports`).catch(() => ({ data: [] })),
      ]);
      setSelectedEmployeeDetail({
        ...res.data,
        direct_reports: reportsRes.data || [],
      });
    } catch (err: unknown) {
      console.error("Dossier load error:", err);
    } finally {
      setLoadingDossier(false);
    }
  };

  const getRiskBadge = (category: string, score: number) => {
    switch (category?.toUpperCase()) {
      case "CRITICAL":
        return (
          <div className="flex items-center gap-2">
            <span className="font-mono font-bold text-xs text-[#00E5FF]">{score}</span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950 text-[#00E5FF] border border-[#00E5FF]/50 shadow-[0_0_8px_rgba(0,229,255,0.2)]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#00E5FF] animate-ping" />
              CRITICAL
            </span>
          </div>
        );
      case "HIGH":
        return (
          <div className="flex items-center gap-2">
            <span className="font-mono font-bold text-xs text-[#00A8FF]">{score}</span>
            <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-[#00A8FF]/20 text-[#00A8FF] border border-[#00A8FF]/40">
              HIGH
            </span>
          </div>
        );
      case "MEDIUM":
        return (
          <div className="flex items-center gap-2">
            <span className="font-mono font-bold text-xs text-sky-400">{score}</span>
            <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-sky-950/50 text-sky-400 border border-sky-800">
              MEDIUM
            </span>
          </div>
        );
      default:
        return (
          <div className="flex items-center gap-2">
            <span className="font-mono font-bold text-xs text-emerald-400">{score}</span>
            <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950/50 text-emerald-400 border border-emerald-800">
              LOW
            </span>
          </div>
        );
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status?.toUpperCase()) {
      case "RESTRICTED":
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-cyan-950 text-[#00E5FF] border border-[#00E5FF]/40">
            RESTRICTED
          </span>
        );
      case "FLAGGED":
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-sky-950 text-sky-400 border border-sky-800">
            FLAGGED
          </span>
        );
      case "UNDER_REVIEW":
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-950 text-amber-400 border border-amber-800">
            UNDER REVIEW
          </span>
        );
      case "ACTIVE":
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-[var(--background)] text-[var(--text-muted)] border border-[var(--panel-border)]">
            ACTIVE
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-[var(--background)] text-[var(--text-muted)] border border-[var(--panel-border)]">
            {status}
          </span>
        );
    }
  };

  const totalPages = Math.max(1, Math.ceil(total / limit));

  return (
    <DashboardLayout
      pageTitle="Employee Threat Intelligence"
      pageSubtitle="Monitored enterprise subjects, behavior profiles, & privilege matrices"
    >
      <div className="space-y-6">
        {/* Error Alert with Retry */}
        {error && (
          <div className="p-4 rounded-xl bg-[var(--panel)] border border-cyan-900/80 text-cyan-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-xl">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-[#00E5FF] shrink-0" />
              <div>
                <div className="font-bold text-xs text-[#00E5FF]">Sensor Feeds Offline</div>
                <div className="text-xs text-[var(--text-muted)]">{error}</div>
              </div>
            </div>
            <button
              onClick={fetchEmployees}
              className="px-4 py-1.5 bg-[#00A8FF] hover:bg-[#00E5FF] text-[#050B14] font-bold text-xs rounded-lg transition flex items-center gap-1.5 shrink-0 cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry Query</span>
            </button>
          </div>
        )}

        {/* Top Control Bar: Search & Filters */}
        <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-5 shadow-xl space-y-4">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
            {/* Search Input */}
            <div className="relative flex-1">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[var(--text-muted)]">
                <Search className="w-4 h-4" />
              </div>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setPage(1);
                }}
                placeholder="Search by Subject Name, Employee ID (e.g. FIN-2187), designation, or email..."
                className="w-full pl-10 pr-4 py-2 bg-[var(--background)] border border-[var(--panel-border)] rounded-lg text-xs text-[var(--foreground)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[#00A8FF] transition"
              />
            </div>

            {/* Filter Dropdowns */}
            <div className="flex flex-wrap items-center gap-3">
              {/* Department Filter */}
              <div className="flex items-center gap-1.5 bg-[var(--background)] px-3 py-1.5 rounded-lg border border-[var(--panel-border)] text-xs">
                <Filter className="w-3.5 h-3.5 text-[var(--text-muted)]" />
                <span className="text-[var(--text-muted)] text-[11px]">Dept:</span>
                <select
                  value={deptFilter}
                  onChange={(e) => {
                    setDeptFilter(e.target.value);
                    setPage(1);
                  }}
                  className="bg-transparent text-[var(--foreground)] focus:outline-none cursor-pointer"
                >
                  <option value="ALL" className="bg-[var(--panel)]">All Departments</option>
                  {DEPARTMENTS.map((d) => (
                    <option key={d} value={d} className="bg-[var(--panel)]">
                      {d}
                    </option>
                  ))}
                </select>
              </div>

              {/* Risk Filter */}
              <div className="flex items-center gap-1.5 bg-[var(--background)] px-3 py-1.5 rounded-lg border border-[var(--panel-border)] text-xs">
                <ShieldAlert className="w-3.5 h-3.5 text-[var(--text-muted)]" />
                <span className="text-[var(--text-muted)] text-[11px]">Risk:</span>
                <select
                  value={riskFilter}
                  onChange={(e) => {
                    setRiskFilter(e.target.value);
                    setPage(1);
                  }}
                  className="bg-transparent text-[var(--foreground)] focus:outline-none cursor-pointer"
                >
                  <option value="ALL" className="bg-[var(--panel)]">All Risk Levels</option>
                  <option value="CRITICAL" className="bg-[var(--panel)]">Critical (&ge;80)</option>
                  <option value="HIGH" className="bg-[var(--panel)]">High (60-79)</option>
                  <option value="MEDIUM" className="bg-[var(--panel)]">Medium (30-59)</option>
                  <option value="LOW" className="bg-[var(--panel)]">Low (&lt;30)</option>
                </select>
              </div>

              {/* Status Filter */}
              <div className="flex items-center gap-1.5 bg-[var(--background)] px-3 py-1.5 rounded-lg border border-[var(--panel-border)] text-xs">
                <UserCheck className="w-3.5 h-3.5 text-[var(--text-muted)]" />
                <span className="text-[var(--text-muted)] text-[11px]">Status:</span>
                <select
                  value={statusFilter}
                  onChange={(e) => {
                    setStatusFilter(e.target.value);
                    setPage(1);
                  }}
                  className="bg-transparent text-[var(--foreground)] focus:outline-none cursor-pointer"
                >
                  <option value="ALL" className="bg-[var(--panel)]">All Statuses</option>
                  <option value="ACTIVE" className="bg-[var(--panel)]">Active</option>
                  <option value="UNDER_REVIEW" className="bg-[var(--panel)]">Under Review</option>
                  <option value="FLAGGED" className="bg-[var(--panel)]">Flagged</option>
                  <option value="RESTRICTED" className="bg-[var(--panel)]">Restricted</option>
                </select>
              </div>

              {/* Reset Filters */}
              {(searchQuery || deptFilter !== "ALL" || riskFilter !== "ALL" || statusFilter !== "ALL") && (
                <button
                  onClick={() => {
                    setSearchQuery("");
                    setDeptFilter("ALL");
                    setRiskFilter("ALL");
                    setStatusFilter("ALL");
                    setPage(1);
                  }}
                  className="flex items-center gap-1 text-[11px] text-[#00E5FF] hover:underline px-2 cursor-pointer"
                >
                  <RefreshCw className="w-3 h-3" /> Reset
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Employee Intelligence Table */}
        <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl shadow-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-[var(--background)]/80 border-b border-[var(--panel-border)] text-[10px] font-bold uppercase tracking-wider text-[var(--text-muted)]">
                  <th className="py-3.5 px-4">Subject ID</th>
                  <th className="py-3.5 px-4">Employee Name</th>
                  <th className="py-3.5 px-4">Department & Role</th>
                  <th className="py-3.5 px-4">Experience & Location</th>
                  <th className="py-3.5 px-4">Assigned Endpoint</th>
                  <th className="py-3.5 px-4">Privileges</th>
                  <th className="py-3.5 px-4">Risk Score</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--panel-border)]">
                {loading ? (
                  <tr>
                    <td colSpan={9} className="py-12 text-center text-[var(--text-muted)]">
                      <div className="flex flex-col items-center justify-center space-y-3">
                        <Loader2 className="w-8 h-8 animate-spin text-[#00E5FF]" />
                        <p className="text-xs font-semibold text-[var(--foreground)]">
                          Querying Monitored Employee Registry...
                        </p>
                      </div>
                    </td>
                  </tr>
                ) : employees.length > 0 ? (
                  employees.map((emp) => (
                    <tr
                      key={emp.id}
                      onClick={() => handleOpenDossier(emp.employee_id)}
                      className="hover:bg-[var(--background)]/70 transition group cursor-pointer"
                    >
                      <td className="py-3.5 px-4 whitespace-nowrap font-mono text-[11px] font-bold text-[#00A8FF]">
                        {emp.employee_id}
                      </td>
                      <td className="py-3.5 px-4 whitespace-nowrap">
                        <div className="font-bold text-[var(--foreground)] group-hover:text-[#00E5FF] transition">
                          {emp.name}
                        </div>
                        <div className="text-[10px] text-[var(--text-muted)]">{emp.email || "No email"}</div>
                      </td>
                      <td className="py-3.5 px-4 whitespace-nowrap">
                        <div className="font-semibold text-[var(--foreground)]">{emp.designation || "Operator"}</div>
                        <div className="text-[10px] text-[var(--text-muted)]">{emp.department || "General"}</div>
                      </td>
                      <td className="py-3.5 px-4 whitespace-nowrap text-[var(--text-muted)] text-[11px]">
                        <div>{emp.years_of_experience ? `${emp.years_of_experience} yrs exp` : "5 yrs"}</div>
                        <div className="text-[10px] opacity-70">{emp.work_location || "Office"}</div>
                      </td>
                      <td className="py-3.5 px-4 whitespace-nowrap text-[var(--text-muted)] font-mono text-[11px]">
                        {emp.device_info || "Standard Node"}
                      </td>
                      <td className="py-3.5 px-4 whitespace-nowrap">
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-[var(--background)] text-[#00E5FF] border border-[var(--panel-border)]">
                          {emp.access_privileges?.split(",")[0] || "STANDARD"}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 whitespace-nowrap">
                        {getRiskBadge(emp.risk_level, emp.risk_score)}
                      </td>
                      <td className="py-3.5 px-4 whitespace-nowrap">
                        {getStatusBadge(emp.status)}
                      </td>
                      <td className="py-3.5 px-4 whitespace-nowrap text-right">
                        <div className="flex items-center justify-end gap-1.5" onClick={(e) => e.stopPropagation()}>
                          <button
                            onClick={() => handleOpenDossier(emp.employee_id)}
                            className="px-2.5 py-1 bg-[var(--background)] hover:bg-[#00A8FF]/20 border border-[var(--panel-border)] hover:border-[#00A8FF] text-[#00E5FF] rounded text-[11px] font-semibold transition cursor-pointer"
                          >
                            Dossier
                          </button>
                          <Link
                            href={`/investigations?employee_id=${emp.employee_id}`}
                            className="p-1 rounded bg-[var(--background)] border border-[var(--panel-border)] text-[var(--text-muted)] hover:text-[#00E5FF] transition"
                            title="Open Investigation Center"
                          >
                            <FileSearch className="w-3.5 h-3.5" />
                          </Link>
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={9} className="py-12 text-center text-[var(--text-muted)]">
                      No monitored employees match current filters.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="p-4 border-t border-[var(--panel-border)] bg-[var(--background)]/60 flex items-center justify-between text-xs text-[var(--text-muted)]">
              <span>
                Showing {((page - 1) * limit) + 1} - {Math.min(page * limit, total)} of {total} employees
              </span>
              <div className="flex items-center gap-2">
                <button
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  className="px-3 py-1.5 rounded bg-[var(--panel)] border border-[var(--panel-border)] text-[var(--foreground)] hover:border-[#00A8FF] disabled:opacity-40 transition flex items-center gap-1 cursor-pointer"
                >
                  <ChevronLeft className="w-3.5 h-3.5" /> Previous
                </button>
                <span className="px-3 py-1 font-mono text-[#00E5FF] bg-[var(--background)] border border-[var(--panel-border)] rounded">
                  {page} / {totalPages}
                </span>
                <button
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  className="px-3 py-1.5 rounded bg-[var(--panel)] border border-[var(--panel-border)] text-[var(--foreground)] hover:border-[#00A8FF] disabled:opacity-40 transition flex items-center gap-1 cursor-pointer"
                >
                  Next <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Employee Detail Slide-over / Modal */}
        {(selectedEmployeeDetail || loadingDossier) && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
            <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-2xl max-w-2xl w-full p-6 shadow-2xl relative max-h-[90vh] overflow-y-auto space-y-5">
              <button
                onClick={() => setSelectedEmployeeDetail(null)}
                className="absolute top-4 right-4 p-1.5 rounded-lg bg-[var(--background)] border border-[var(--panel-border)] text-[var(--text-muted)] hover:text-[#00E5FF] transition cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>

              {loadingDossier ? (
                <div className="py-16 flex flex-col items-center justify-center space-y-3">
                  <Loader2 className="w-8 h-8 animate-spin text-[#00E5FF]" />
                  <p className="text-xs font-mono text-[var(--text-muted)]">Loading Subject Dossier from Backend Database...</p>
                </div>
              ) : selectedEmployeeDetail ? (
                <>
                  {/* Modal Header */}
                  <div className="flex items-start gap-4 pb-4 border-b border-[var(--panel-border)]">
                    <div className="w-12 h-12 rounded-xl bg-[var(--background)] border border-[#00A8FF]/50 flex items-center justify-center text-[#00E5FF]">
                      <Users className="w-6 h-6" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h2 className="text-xl font-bold text-[var(--foreground)]">
                          {selectedEmployeeDetail.employee.name}
                        </h2>
                        <span className="font-mono text-xs text-[#00A8FF]">
                          ({selectedEmployeeDetail.employee.employee_id})
                        </span>
                      </div>
                      <p className="text-xs text-[var(--text-muted)] mt-0.5">
                        {selectedEmployeeDetail.employee.designation} — {selectedEmployeeDetail.employee.department}
                      </p>
                    </div>
                  </div>

                  {/* Risk Overview */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div className="bg-[var(--background)] p-3 rounded-lg border border-[var(--panel-border)]">
                      <div className="text-[10px] text-[var(--text-muted)] uppercase">Risk Score</div>
                      <div className="text-lg font-black text-[#00E5FF] mt-1 font-mono">
                        {selectedEmployeeDetail.employee.risk_score}/100
                      </div>
                    </div>
                    <div className="bg-[var(--background)] p-3 rounded-lg border border-[var(--panel-border)]">
                      <div className="text-[10px] text-[var(--text-muted)] uppercase">Risk Tier</div>
                      <div className="mt-1">{getRiskBadge(selectedEmployeeDetail.employee.risk_level, selectedEmployeeDetail.employee.risk_score)}</div>
                    </div>
                    <div className="bg-[var(--background)] p-3 rounded-lg border border-[var(--panel-border)]">
                      <div className="text-[10px] text-[var(--text-muted)] uppercase">Linked Alerts</div>
                      <div className="text-lg font-bold text-[var(--foreground)] mt-1 font-mono">
                        {selectedEmployeeDetail.alerts.length} Triggers
                      </div>
                    </div>
                    <div className="bg-[var(--background)] p-3 rounded-lg border border-[var(--panel-border)]">
                      <div className="text-[10px] text-[var(--text-muted)] uppercase">Status</div>
                      <div className="mt-1">{getStatusBadge(selectedEmployeeDetail.employee.status)}</div>
                    </div>
                  </div>

                  {/* Professional Background & Privilege Details */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                    <div className="bg-[var(--background)] p-4 rounded-lg border border-[var(--panel-border)] space-y-2">
                      <div className="font-bold text-[#00A8FF] uppercase tracking-wider text-[10px]">
                        Professional Background
                      </div>
                      <div className="flex justify-between py-1 border-b border-[var(--panel-border)]/60">
                        <span className="text-[var(--text-muted)]">Experience:</span>
                        <span className="font-semibold text-[var(--foreground)]">{selectedEmployeeDetail.employee.years_of_experience || 5} Years</span>
                      </div>
                      <div className="flex justify-between py-1 border-b border-[var(--panel-border)]/60">
                        <span className="text-[var(--text-muted)]">Education:</span>
                        <span className="text-[var(--foreground)]">{selectedEmployeeDetail.employee.education || "Bachelor of Science"}</span>
                      </div>
                      <div className="flex justify-between py-1 border-b border-[var(--panel-border)]/60">
                        <span className="text-[var(--text-muted)]">Reporting Manager:</span>
                        <span className="font-semibold text-[var(--foreground)]">{selectedEmployeeDetail.employee.manager_name || "Executive Management"}</span>
                      </div>
                      <div className="flex justify-between py-1">
                        <span className="text-[var(--text-muted)]">Work Location:</span>
                        <span className="text-[var(--foreground)]">{selectedEmployeeDetail.employee.work_location || "Headquarters"}</span>
                      </div>
                    </div>

                    <div className="bg-[var(--background)] p-4 rounded-lg border border-[var(--panel-border)] space-y-2">
                      <div className="font-bold text-[#00A8FF] uppercase tracking-wider text-[10px]">
                        Access Privileges
                      </div>
                      <div className="flex justify-between py-1 border-b border-[var(--panel-border)]/60">
                        <span className="text-[var(--text-muted)]">Assigned Endpoint:</span>
                        <span className="font-mono text-[var(--foreground)]">{selectedEmployeeDetail.employee.device_info || "Standard Device"}</span>
                      </div>
                      <div className="flex justify-between py-1">
                        <span className="text-[var(--text-muted)]">Authorizations:</span>
                        <span className="font-mono text-[#00E5FF]">{selectedEmployeeDetail.employee.access_privileges || "STANDARD_USER"}</span>
                      </div>
                    </div>
                  </div>

                  {/* Direct Subordinates Hierarchy */}
                  {selectedEmployeeDetail.direct_reports && selectedEmployeeDetail.direct_reports.length > 0 && (
                    <div className="bg-[var(--background)] p-4 rounded-lg border border-[var(--panel-border)] space-y-2">
                      <div className="font-bold text-[#00A8FF] uppercase tracking-wider text-[10px]">
                        Direct Subordinates ({selectedEmployeeDetail.direct_reports.length})
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
                        {selectedEmployeeDetail.direct_reports.map((sub) => (
                          <div
                            key={sub.id}
                            onClick={() => handleOpenDossier(sub.employee_id)}
                            className="p-2.5 rounded bg-[var(--panel)] border border-[var(--panel-border)] hover:border-[#00E5FF] transition cursor-pointer flex items-center justify-between"
                          >
                            <div>
                              <div className="text-xs font-bold text-[var(--foreground)] hover:text-[#00E5FF]">{sub.name}</div>
                              <div className="text-[10px] text-[var(--text-muted)]">{sub.designation} ({sub.employee_id})</div>
                            </div>
                            <span className="text-[10px] font-mono font-bold text-[#00E5FF]">{sub.risk_score}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="pt-2 flex items-center justify-between border-t border-[var(--panel-border)]">
                    <button
                      onClick={() => setSelectedEmployeeDetail(null)}
                      className="px-4 py-2 bg-[var(--background)] hover:bg-[var(--panel-border)] text-[var(--text-muted)] hover:text-[var(--foreground)] rounded-lg text-xs font-semibold transition cursor-pointer"
                    >
                      Close Dossier
                    </button>
                    <Link
                      href={`/investigations?employee_id=${selectedEmployeeDetail.employee.employee_id}`}
                      className="px-4 py-2 bg-[#00A8FF] hover:bg-[#00E5FF] text-[#050B14] rounded-lg text-xs font-bold transition shadow-lg shadow-[#00A8FF]/20 flex items-center gap-1.5"
                    >
                      <FileSearch className="w-3.5 h-3.5" />
                      <span>Open in Investigation Center</span>
                    </Link>
                  </div>
                </>
              ) : null}
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

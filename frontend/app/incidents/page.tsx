"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import Navbar from "@/components/Navbar";
import InvestigationTimeline from "@/components/InvestigationTimeline";
import api from "@/lib/api";
import { verifyAuthentication } from "@/lib/auth";

interface IncidentItem {
  id: number;
  employee_id: number;
  employee_code: string;
  employee_name: string;
  department: string;
  incident_type: string;
  description: string | null;
  severity: string;
  status: string;
  summary?: string | null;
  created_at: string;
  resolved_at?: string | null;
}

interface AlertItem {
  id: number;
  incident_id: number;
  employee_id: number;
  employee_code: string;
  employee_name: string;
  department: string;
  alert_type: string;
  message: string;
  severity: string;
  status: string;
  assigned_to?: number | null;
  assignee_email?: string | null;
  escalation_level: number;
  created_at: string;
  resolved_at?: string | null;
}

interface InvestigationNote {
  id: number;
  author_id: number;
  author_email: string;
  note: string;
  evidence_reference?: string | null;
  created_at: string;
}

interface AssigneeUser {
  id: number;
  email: string;
  role: string;
}

export default function IncidentsPage() {
  const [activeTab, setActiveTab] = useState<"incidents" | "alerts">("incidents");
  const [incidents, setIncidents] = useState<IncidentItem[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [severityFilter, setSeverityFilter] = useState<string>("all");

  // Alert assignment & orchestration states
  const [assignees, setAssignees] = useState<AssigneeUser[]>([]);
  const [assigningAlertId, setAssigningAlertId] = useState<number | null>(null);
  const [runningSweep, setRunningSweep] = useState(false);
  const [runningEscalate, setRunningEscalate] = useState(false);
  const [bannerMsg, setBannerMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // Selected Incident for detail drawer
  const [selectedIncident, setSelectedIncident] = useState<IncidentItem | null>(null);
  const [incidentNotes, setIncidentNotes] = useState<InvestigationNote[]>([]);
  const [loadingNotes, setLoadingNotes] = useState(false);
  const [newNoteText, setNewNoteText] = useState("");
  const [newEvidenceRef, setNewEvidenceRef] = useState("");
  const [addingNote, setAddingNote] = useState(false);
  const [statusUpdateVal, setStatusUpdateVal] = useState("");
  const [resolutionSummary, setResolutionSummary] = useState("");
  const [updatingStatus, setUpdatingStatus] = useState(false);
  const [statusMsg, setStatusMsg] = useState("");

  const fetchData = async () => {
    try {
      setLoading(true);
      await verifyAuthentication();

      const [incRes, alertRes, usersRes] = await Promise.allSettled([
        api.get("/incidents?status=all"),
        api.get("/alerts?status=all"),
        api.get("/admin/users"),
      ]);

      const loadedIncidents =
        incRes.status === "fulfilled" ? incRes.value.data?.incidents || [] : [];
      if (loadedIncidents.length > 0 || incRes.status === "fulfilled") {
        setIncidents(loadedIncidents);
      }

      if (alertRes.status === "fulfilled" && alertRes.value.data?.alerts) {
        setAlerts(alertRes.value.data.alerts);
      }

      if (usersRes.status === "fulfilled" && usersRes.value.data?.users) {
        const eligible = usersRes.value.data.users.filter((u: any) =>
          ["admin", "security_analyst", "soc_engineer", "security_manager"].includes(
            (u.role || "").toLowerCase()
          )
        );
        setAssignees(eligible);
      }

      if (typeof window !== "undefined") {
        const params = new URLSearchParams(window.location.search);
        const targetId = params.get("id") || params.get("investigate");
        if (targetId && loadedIncidents.length > 0) {
          const match = loadedIncidents.find((i: any) => String(i.id) === targetId);
          if (match) {
            openIncidentDetails(match);
          }
        }
      }
    } catch (err: any) {
      if (err.response?.status === 401) {
        window.location.href = "/login";
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const openIncidentDetails = async (inc: IncidentItem) => {
    setSelectedIncident(inc);
    setStatusUpdateVal(inc.status);
    setResolutionSummary(inc.summary || "");
    setStatusMsg("");
    try {
      setLoadingNotes(true);
      const res = await api.get(`/incidents/${inc.id}/notes`);
      setIncidentNotes(res.data?.notes || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingNotes(false);
    }
  };

  const handleAddNote = async () => {
    if (!selectedIncident || !newNoteText.trim()) return;
    try {
      setAddingNote(true);
      const res = await api.post(`/incidents/${selectedIncident.id}/notes`, {
        note: newNoteText.trim(),
        evidence_reference: newEvidenceRef.trim() || undefined,
      });
      setIncidentNotes((prev) => [...prev, res.data.note]);
      setNewNoteText("");
      setNewEvidenceRef("");
    } catch (err) {
      console.error(err);
    } finally {
      setAddingNote(false);
    }
  };

  const handleUpdateStatus = async () => {
    if (!selectedIncident) return;
    try {
      setUpdatingStatus(true);
      setStatusMsg("");
      await api.patch(`/incidents/${selectedIncident.id}/status`, {
        status: statusUpdateVal,
        summary: resolutionSummary || undefined,
      });
      setSelectedIncident((prev) => (prev ? { ...prev, status: statusUpdateVal, summary: resolutionSummary } : null));
      setStatusMsg("Incident status updated successfully.");
      fetchData();
    } catch (err: any) {
      setStatusMsg(err.response?.data?.detail || "Failed to update incident status.");
    } finally {
      setUpdatingStatus(false);
    }
  };

  const handleResolveAlert = async (alertId: number) => {
    try {
      await api.patch(`/alerts/${alertId}/resolve`);
      setBannerMsg({ type: "success", text: `Alert #${alertId} resolved.` });
      fetchData();
    } catch (err: any) {
      setBannerMsg({
        type: "error",
        text: err.response?.data?.detail || `Failed to resolve Alert #${alertId}.`,
      });
    }
  };

  const handleRunDetectionSweep = async () => {
    try {
      setRunningSweep(true);
      setBannerMsg(null);
      const res = await api.post("/alerts/generate");
      const alertsGen = res.data?.alerts_generated ?? res.data?.alerts_created ?? 0;
      const incGen = res.data?.incidents_generated ?? res.data?.incidents_created ?? 0;
      setBannerMsg({
        type: "success",
        text: `Threat detection sweep completed: ${alertsGen} alert(s) and ${incGen} incident(s) generated.`,
      });
      fetchData();
    } catch (err: any) {
      setBannerMsg({
        type: "error",
        text: err.response?.data?.detail || "Failed to execute threat detection sweep.",
      });
    } finally {
      setRunningSweep(false);
    }
  };

  const handleRunEscalate = async () => {
    try {
      setRunningEscalate(true);
      setBannerMsg(null);
      const res = await api.post("/alerts/escalate");
      const count = res.data?.escalated_count ?? res.data?.escalated_alerts ?? 0;
      setBannerMsg({
        type: "success",
        text: `SLA escalation check completed: ${count} alert(s) escalated to higher priority.`,
      });
      fetchData();
    } catch (err: any) {
      setBannerMsg({
        type: "error",
        text: err.response?.data?.detail || "Failed to execute SLA escalation check.",
      });
    } finally {
      setRunningEscalate(false);
    }
  };

  const handleAssignAlert = async (alertId: number, userId: number) => {
    if (!userId) return;
    try {
      setAssigningAlertId(alertId);
      setBannerMsg(null);
      const res = await api.post(`/alerts/${alertId}/assign?analyst_user_id=${userId}`);
      setBannerMsg({
        type: "success",
        text: res.data?.message || `Alert #${alertId} successfully assigned.`,
      });
      fetchData();
    } catch (err: any) {
      setBannerMsg({
        type: "error",
        text: err.response?.data?.detail || `Failed to assign Alert #${alertId}.`,
      });
    } finally {
      setAssigningAlertId(null);
    }
  };

  // Filtered lists
  const filteredIncidents = incidents.filter((i) => {
    if (statusFilter !== "all" && i.status.toLowerCase() !== statusFilter) return false;
    if (severityFilter !== "all" && i.severity.toLowerCase() !== severityFilter) return false;
    return true;
  });

  const filteredAlerts = alerts.filter((a) => {
    if (statusFilter !== "all" && a.status.toLowerCase() !== statusFilter) return false;
    if (severityFilter !== "all" && a.severity.toLowerCase() !== severityFilter) return false;
    return true;
  });

  const getSeverityBadge = (sev: string) => {
    const s = sev.toLowerCase();
    if (s === "critical") return "bg-red-500/20 text-red-400 border-red-500/30";
    if (s === "high") return "bg-orange-500/20 text-orange-400 border-orange-500/30";
    if (s === "medium") return "bg-amber-500/20 text-amber-400 border-amber-500/30";
    return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
  };

  const getStatusBadge = (st: string) => {
    const s = st.toLowerCase();
    if (s === "open" || s === "active") return "bg-blue-500/20 text-blue-400 border-blue-500/30";
    if (s === "investigating" || s === "assigned") return "bg-purple-500/20 text-purple-400 border-purple-500/30";
    return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
  };

  return (
    <div className="flex h-screen bg-[var(--background)] text-[var(--foreground)]">
      <Sidebar />

      <div className="flex flex-1 flex-col overflow-hidden">
        <Navbar />

        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="mx-auto max-w-7xl space-y-6">
            {/* Header & Tabs */}
            <div className="flex flex-col gap-4 border-b border-[var(--border)] pb-5 md:flex-row md:items-center md:justify-between">
              <div>
                <h1 className="text-2xl font-bold tracking-tight">Incidents & Security Alerts Queue</h1>
                <p className="text-sm text-[var(--muted)]">
                  Live investigation ticket triage, evidence auditing, and alert resolution center
                </p>
              </div>

              {/* Action Buttons & View Switcher */}
              <div className="flex flex-wrap items-center gap-3">
                <button
                  onClick={handleRunDetectionSweep}
                  disabled={runningSweep}
                  className="flex items-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--card)] px-3 py-2 text-xs font-semibold text-[var(--foreground)] hover:border-amber-500/50 hover:bg-amber-500/10 transition disabled:opacity-50 cursor-pointer shadow-sm"
                  title="Run autonomous anomaly correlation sweep to generate alerts and incidents"
                >
                  {runningSweep ? (
                    <>
                      <span className="h-3 w-3 animate-spin rounded-full border border-t-transparent border-amber-400" />
                      <span>Running Sweep...</span>
                    </>
                  ) : (
                    <>
                      <span className="text-amber-400 font-bold">⚡</span>
                      <span>Run Detection Sweep</span>
                    </>
                  )}
                </button>

                <button
                  onClick={handleRunEscalate}
                  disabled={runningEscalate}
                  className="flex items-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--card)] px-3 py-2 text-xs font-semibold text-[var(--foreground)] hover:border-red-500/50 hover:bg-red-500/10 transition disabled:opacity-50 cursor-pointer shadow-sm"
                  title="Scan for overdue unresolved alerts and escalate according to SLAs"
                >
                  {runningEscalate ? (
                    <>
                      <span className="h-3 w-3 animate-spin rounded-full border border-t-transparent border-red-400" />
                      <span>Checking SLAs...</span>
                    </>
                  ) : (
                    <>
                      <span className="text-red-400 font-bold">⏱</span>
                      <span>Check SLA Escalations</span>
                    </>
                  )}
                </button>

                {/* View Switcher */}
                <div className="flex items-center gap-1 rounded-xl border border-[var(--border)] bg-[var(--card)] p-1">
                  <button
                    onClick={() => setActiveTab("incidents")}
                    className={`rounded-lg px-4 py-2 text-xs font-semibold transition ${
                      activeTab === "incidents"
                        ? "bg-[var(--primary)] text-white shadow-sm"
                        : "text-[var(--muted)] hover:text-[var(--foreground)]"
                    }`}
                  >
                    Incidents ({incidents.length})
                  </button>
                  <button
                    onClick={() => setActiveTab("alerts")}
                    className={`rounded-lg px-4 py-2 text-xs font-semibold transition ${
                      activeTab === "alerts"
                        ? "bg-[var(--primary)] text-white shadow-sm"
                        : "text-[var(--muted)] hover:text-[var(--foreground)]"
                    }`}
                  >
                    Alerts Queue ({alerts.length})
                  </button>
                </div>
              </div>
            </div>

            {/* Orchestration Status Banner */}
            {bannerMsg && (
              <div
                className={`flex items-center justify-between rounded-xl p-3.5 text-xs font-semibold ${
                  bannerMsg.type === "success"
                    ? "border border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
                    : "border border-red-500/30 bg-red-500/10 text-red-400"
                }`}
              >
                <span>{bannerMsg.text}</span>
                <button
                  onClick={() => setBannerMsg(null)}
                  className="ml-4 hover:opacity-75 cursor-pointer font-bold"
                >
                  ✕
                </button>
              </div>
            )}

            {/* Filters Bar */}
            <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-[var(--border)] bg-[var(--card)] p-4">
              <div className="flex flex-wrap items-center gap-3">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-[var(--muted)]">Status:</span>
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-2.5 py-1.5 text-xs font-medium outline-none focus:border-[var(--primary)]"
                  >
                    <option value="all">All Statuses</option>
                    <option value="open">Open / Active</option>
                    <option value="investigating">Investigating / Assigned</option>
                    <option value="resolved">Resolved / Closed</option>
                  </select>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-xs text-[var(--muted)]">Severity:</span>
                  <select
                    value={severityFilter}
                    onChange={(e) => setSeverityFilter(e.target.value)}
                    className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-2.5 py-1.5 text-xs font-medium outline-none focus:border-[var(--primary)]"
                  >
                    <option value="all">All Severities</option>
                    <option value="critical">Critical</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                  </select>
                </div>
              </div>

              <div className="text-xs text-[var(--muted)]">
                Showing <span className="font-bold text-[var(--foreground)]">{activeTab === "incidents" ? filteredIncidents.length : filteredAlerts.length}</span> records
              </div>
            </div>

            {loading ? (
              <div className="flex h-64 items-center justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--primary)]" />
              </div>
            ) : activeTab === "incidents" ? (
              /* INCIDENTS TABLE */
              <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-[var(--border)] bg-[var(--background)]/50 text-[11px] font-semibold uppercase tracking-wider text-[var(--muted)]">
                        <th className="p-4">ID</th>
                        <th className="p-4">Employee</th>
                        <th className="p-4">Incident Type</th>
                        <th className="p-4">Severity</th>
                        <th className="p-4">Status</th>
                        <th className="p-4">Created Date</th>
                        <th className="p-4 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[var(--border)]">
                      {filteredIncidents.length === 0 ? (
                        <tr>
                          <td colSpan={7} className="p-8 text-center text-sm text-[var(--muted)]">
                            No security incidents match the current filters.
                          </td>
                        </tr>
                      ) : (
                        filteredIncidents.map((inc) => (
                          <tr key={inc.id} className="hover:bg-[var(--card-hover)] transition">
                            <td className="p-4 font-mono text-xs font-bold text-[var(--primary)]">#{inc.id}</td>
                            <td className="p-4">
                              <div className="font-semibold">{inc.employee_name}</div>
                              <div className="font-mono text-xs text-[var(--muted)]">
                                {inc.employee_code} • {inc.department}
                              </div>
                            </td>
                            <td className="p-4 font-medium">{inc.incident_type}</td>
                            <td className="p-4">
                              <span className={`rounded-md border px-2 py-0.5 text-xs font-bold uppercase ${getSeverityBadge(inc.severity)}`}>
                                {inc.severity}
                              </span>
                            </td>
                            <td className="p-4">
                              <span className={`rounded-md border px-2 py-0.5 text-xs font-semibold capitalize ${getStatusBadge(inc.status)}`}>
                                {inc.status}
                              </span>
                            </td>
                            <td className="p-4 font-mono text-xs text-[var(--muted)]">
                              {new Date(inc.created_at).toLocaleDateString()}
                            </td>
                            <td className="p-4 text-right">
                              <button
                                onClick={() => openIncidentDetails(inc)}
                                className="rounded-lg bg-[var(--primary)]/10 px-3 py-1.5 text-xs font-semibold text-[var(--primary)] hover:bg-[var(--primary)] hover:text-white transition"
                              >
                                Investigate →
                              </button>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              /* ALERTS TABLE */
              <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-[var(--border)] bg-[var(--background)]/50 text-[11px] font-semibold uppercase tracking-wider text-[var(--muted)]">
                        <th className="p-4">ID</th>
                        <th className="p-4">Employee</th>
                        <th className="p-4">Alert Message</th>
                        <th className="p-4">Severity</th>
                        <th className="p-4">Status</th>
                        <th className="p-4">Assigned To</th>
                        <th className="p-4 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[var(--border)]">
                      {filteredAlerts.length === 0 ? (
                        <tr>
                          <td colSpan={7} className="p-8 text-center text-sm text-[var(--muted)]">
                            No operational alerts match current filter.
                          </td>
                        </tr>
                      ) : (
                        filteredAlerts.map((al) => (
                          <tr key={al.id} className="hover:bg-[var(--card-hover)] transition">
                            <td className="p-4 font-mono text-xs font-bold text-amber-500">#{al.id}</td>
                            <td className="p-4">
                              <div className="font-semibold">{al.employee_name}</div>
                              <div className="font-mono text-xs text-[var(--muted)]">{al.employee_code}</div>
                            </td>
                            <td className="p-4 max-w-xs text-xs text-[var(--foreground)] truncate" title={al.message}>
                              {al.message}
                            </td>
                            <td className="p-4">
                              <span className={`rounded-md border px-2 py-0.5 text-xs font-bold uppercase ${getSeverityBadge(al.severity)}`}>
                                {al.severity}
                              </span>
                            </td>
                            <td className="p-4">
                              <span className={`rounded-md border px-2 py-0.5 text-xs font-semibold capitalize ${getStatusBadge(al.status)}`}>
                                {al.status}
                              </span>
                            </td>
                            <td className="p-4 text-xs text-[var(--muted)]">
                              {al.status !== "resolved" ? (
                                <div className="flex items-center gap-1.5">
                                  <select
                                    value={al.assigned_to || ""}
                                    onChange={(e) => {
                                      const val = Number(e.target.value);
                                      if (val) handleAssignAlert(al.id, val);
                                    }}
                                    disabled={assigningAlertId === al.id}
                                    className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-2 py-1 text-xs text-[var(--foreground)] focus:border-[var(--primary)] focus:outline-none max-w-[170px] truncate"
                                  >
                                    <option value="">
                                      {al.assignee_email ? al.assignee_email : "— Assign Analyst —"}
                                    </option>
                                    {assignees.map((u) => (
                                      <option key={u.id} value={u.id}>
                                        {u.email} ({u.role.replace("_", " ")})
                                      </option>
                                    ))}
                                  </select>
                                  {assigningAlertId === al.id && (
                                    <span className="h-3 w-3 animate-spin rounded-full border border-t-transparent border-[var(--primary)]" />
                                  )}
                                </div>
                              ) : (
                                <span>{al.assignee_email || "Unassigned"}</span>
                              )}
                            </td>
                            <td className="p-4 text-right">
                              {al.status !== "resolved" ? (
                                <button
                                  onClick={() => handleResolveAlert(al.id)}
                                  className="rounded-lg bg-emerald-500/10 px-3 py-1.5 text-xs font-semibold text-emerald-400 hover:bg-emerald-500/20 transition"
                                >
                                  Resolve ✓
                                </button>
                              ) : (
                                <span className="text-xs text-[var(--muted)]">Resolved</span>
                              )}
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* INCIDENT INVESTIGATION DRAWER / MODAL */}
            {selectedIncident && (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm">
                <div className="w-full max-w-4xl max-h-[90vh] flex flex-col rounded-2xl border border-[var(--border)] bg-[var(--card)] shadow-2xl overflow-hidden">
                  {/* Fixed / Sticky Modal Header (Image part fixed while scrolling) */}
                  <div className="shrink-0 sticky top-0 z-20 flex items-start justify-between border-b border-[var(--border)] bg-[var(--card)] p-6 shadow-sm">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-sm font-bold text-[var(--primary)]">
                          INCIDENT #{selectedIncident.id}
                        </span>
                        <span className={`rounded-md border px-2 py-0.5 text-xs font-bold uppercase ${getSeverityBadge(selectedIncident.severity)}`}>
                          {selectedIncident.severity}
                        </span>
                        <span className={`rounded-md border px-2 py-0.5 text-xs font-semibold capitalize ${getStatusBadge(selectedIncident.status)}`}>
                          {selectedIncident.status}
                        </span>
                      </div>
                      <h2 className="mt-1 text-xl font-bold">{selectedIncident.incident_type}</h2>
                      <p className="text-xs text-[var(--muted)]">
                        Subject: {selectedIncident.employee_name} ({selectedIncident.employee_code}) • {selectedIncident.department}
                      </p>
                    </div>

                    <button
                      onClick={() => setSelectedIncident(null)}
                      className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-1.5 text-xs font-bold text-[var(--muted)] hover:text-[var(--foreground)] hover:border-[var(--primary)] transition cursor-pointer"
                    >
                      ✕ Close
                    </button>
                  </div>

                  {/* Scrollable Modal Body */}
                  <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    {/* Incident Description */}
                    {selectedIncident.description && (
                      <div className="rounded-xl border border-[var(--border)] bg-[var(--background)] p-4 text-xs leading-relaxed text-[var(--muted)]">
                        <span className="font-semibold text-[var(--foreground)]">Initial Detection Narrative: </span>
                        {selectedIncident.description}
                      </div>
                    )}

                  {/* Status & Resolution Controls */}
                  <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4 space-y-3">
                    <h3 className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">
                      Investigation Lifecycle Management
                    </h3>
                    <div className="grid gap-3 sm:grid-cols-[1fr_2fr_auto] items-end">
                      <div>
                        <label className="block text-[11px] text-[var(--muted)] mb-1">Update Status</label>
                        <select
                          value={statusUpdateVal}
                          onChange={(e) => setStatusUpdateVal(e.target.value)}
                          className="w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-xs outline-none focus:border-[var(--primary)]"
                        >
                          <option value="open">Open</option>
                          <option value="investigating">Investigating</option>
                          <option value="resolved">Resolved</option>
                          <option value="closed">Closed</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-[11px] text-[var(--muted)] mb-1">Resolution Summary</label>
                        <input
                          type="text"
                          value={resolutionSummary}
                          onChange={(e) => setResolutionSummary(e.target.value)}
                          placeholder="e.g. Cleared: legitimate IT activity, or escalated to HR."
                          className="w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-xs outline-none focus:border-[var(--primary)]"
                        />
                      </div>

                      <button
                        onClick={handleUpdateStatus}
                        disabled={updatingStatus}
                        className="rounded-lg bg-[var(--primary)] px-4 py-2 text-xs font-semibold text-white hover:bg-[var(--primary-hover)] transition"
                      >
                        {updatingStatus ? "Saving..." : "Apply Status"}
                      </button>
                    </div>
                    {statusMsg && <p className="text-xs text-emerald-400 font-medium">{statusMsg}</p>}
                  </div>

                  {/* Timeline & Notes Tabs / Sections */}
                  <div className="space-y-6">
                    {/* Visual Investigation Timeline */}
                    <div className="rounded-xl border border-[var(--border)] bg-[var(--background)] p-5">
                      <h3 className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)] mb-4">
                        Reconstructed Chronological Incident Timeline
                      </h3>
                      <InvestigationTimeline incidentId={selectedIncident.id} />
                    </div>

                    {/* Investigation Notes & Evidence Log */}
                    <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5 space-y-4">
                      <h3 className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">
                        Analyst Investigation Notes & Evidence ({incidentNotes.length})
                      </h3>

                      {loadingNotes ? (
                        <div className="flex h-20 items-center justify-center">
                          <div className="h-5 w-5 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--primary)]" />
                        </div>
                      ) : (
                        <div className="space-y-2 max-h-48 overflow-y-auto">
                          {incidentNotes.length === 0 ? (
                            <p className="text-xs text-[var(--muted)]">No notes recorded on this ticket yet.</p>
                          ) : (
                            incidentNotes.map((n) => (
                              <div key={n.id} className="rounded-lg border border-[var(--border)] bg-[var(--background)] p-3 text-xs space-y-1">
                                <div className="flex justify-between text-[10px] text-[var(--muted)]">
                                  <span className="font-semibold text-[var(--foreground)]">{n.author_email}</span>
                                  <span>{new Date(n.created_at).toLocaleString()}</span>
                                </div>
                                <p className="text-[var(--foreground)]">{n.note}</p>
                                {n.evidence_reference && (
                                  <p className="text-[10px] font-mono text-[var(--primary)]">
                                    Ref: {n.evidence_reference}
                                  </p>
                                )}
                              </div>
                            ))
                          )}
                        </div>
                      )}

                      {/* Add Note Form */}
                      <div className="border-t border-[var(--border)] pt-3 space-y-2">
                        <textarea
                          value={newNoteText}
                          onChange={(e) => setNewNoteText(e.target.value)}
                          placeholder="Add factual investigation observation or triage note..."
                          rows={2}
                          className="w-full rounded-lg border border-[var(--border)] bg-[var(--background)] p-2.5 text-xs outline-none focus:border-[var(--primary)]"
                        />
                        <div className="flex gap-2">
                          <input
                            type="text"
                            value={newEvidenceRef}
                            onChange={(e) => setNewEvidenceRef(e.target.value)}
                            placeholder="Evidence hash / packet capture ref (optional)"
                            className="flex-1 rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-1.5 text-xs outline-none focus:border-[var(--primary)]"
                          />
                          <button
                            onClick={handleAddNote}
                            disabled={addingNote || !newNoteText.trim()}
                            className="rounded-lg bg-[var(--primary)] px-4 py-1.5 text-xs font-semibold text-white hover:bg-[var(--primary-hover)] transition disabled:opacity-50"
                          >
                            {addingNote ? "Adding..." : "Add Note"}
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
          </div>
        </main>
      </div>
    </div>
  );
}

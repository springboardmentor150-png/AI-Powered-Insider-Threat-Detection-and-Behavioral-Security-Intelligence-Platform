"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  ShieldAlert,
  Search,
  Filter,
  CheckCircle2,
  Clock,
  UserCheck,
  ChevronRight,
  Loader2,
  X,
  ExternalLink,
  MessageSquare,
  AlertTriangle,
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import { api } from "@/lib/api";

interface IncidentItem {
  id: number;
  employee_id: number;
  employee_name?: string;
  employee_identifier?: string;
  alert_id?: number;
  title: string;
  description?: string;
  status: "OPEN" | "INVESTIGATING" | "CONTAINED" | "RESOLVED" | "CLOSED";
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  assigned_to?: number;
  resolved_at?: string;
  created_at: string;
}

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<IncidentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [selectedInc, setSelectedInc] = useState<IncidentItem | null>(null);
  const [newStatus, setNewStatus] = useState<string>("INVESTIGATING");
  const [resolutionNotes, setResolutionNotes] = useState("");
  const [actionLoading, setActionLoading] = useState(false);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const fetchIncidents = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (statusFilter !== "ALL") params.append("status", statusFilter);
      params.append("limit", "50");

      const res = await api.get(`/incidents?${params.toString()}`);
      setIncidents(res.data.items || []);
    } catch (err) {
      console.error("Error fetching incidents:", err);
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    fetchIncidents();
  }, [fetchIncidents]);

  const handleUpdateStatus = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedInc) return;
    setActionLoading(true);
    setActionSuccess(null);
    try {
      const res = await api.patch(`/incidents/${selectedInc.id}/status`, {
        status: newStatus,
        resolution_notes: resolutionNotes || undefined,
      });
      setSelectedInc(res.data);
      setResolutionNotes("");
      setActionSuccess(`Incident status updated to ${newStatus}.`);
      fetchIncidents();
    } catch (err) {
      alert("Failed to update incident status");
    } finally {
      setActionLoading(false);
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity.toUpperCase()) {
      case "CRITICAL":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950 text-[#00E5FF] border border-[#00E5FF]/40">CRITICAL</span>;
      case "HIGH":
        return <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#00A8FF]/20 text-[#00A8FF] border border-[#00A8FF]/40">HIGH</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-[#132B45] text-[#8E9EB5] border border-[#1E3A5F]">{severity}</span>;
    }
  };

  return (
    <DashboardLayout
      pageTitle="SOC Incident Management Board"
      pageSubtitle="Active investigations, forensic timelines, and containment workflows"
    >
      <div className="space-y-6">
        {/* Incident Summary Counters */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-4">
            <span className="text-[10px] uppercase font-bold text-[var(--text-muted)]">Open Incidents</span>
            <div className="text-2xl font-black text-[var(--foreground)] mt-1">
              {incidents.filter((i) => i.status === "OPEN").length}
            </div>
            <span className="text-[10px] text-[#00A8FF]">Pending Assignment</span>
          </div>

          <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-4">
            <span className="text-[10px] uppercase font-bold text-[var(--text-muted)]">Active Investigations</span>
            <div className="text-2xl font-black text-[#00E5FF] mt-1">
              {incidents.filter((i) => i.status === "INVESTIGATING").length}
            </div>
            <span className="text-[10px] text-[#00E5FF]">Forensics in Progress</span>
          </div>

          <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-4">
            <span className="text-[10px] uppercase font-bold text-[var(--text-muted)]">Contained</span>
            <div className="text-2xl font-black text-[#00A8FF] mt-1">
              {incidents.filter((i) => i.status === "CONTAINED").length}
            </div>
            <span className="text-[10px] text-[var(--text-muted)]">Node Isolated</span>
          </div>

          <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-4">
            <span className="text-[10px] uppercase font-bold text-[var(--text-muted)]">Resolved</span>
            <div className="text-2xl font-black text-emerald-400 mt-1">
              {incidents.filter((i) => i.status === "RESOLVED" || i.status === "CLOSED").length}
            </div>
            <span className="text-[10px] text-[var(--text-muted)]">Investigation Closed</span>
          </div>
        </div>

        {/* Filter Bar */}
        <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Filter className="w-3.5 h-3.5 text-[#00A8FF]" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-[var(--background)] border border-[var(--panel-border)] text-xs text-[var(--foreground)] rounded-lg px-3 py-1.5"
            >
              <option value="ALL">All Incident Stages</option>
              <option value="OPEN">Open</option>
              <option value="INVESTIGATING">Investigating</option>
              <option value="CONTAINED">Contained</option>
              <option value="RESOLVED">Resolved</option>
              <option value="CLOSED">Closed</option>
            </select>
          </div>

          <span className="text-xs text-[var(--text-muted)] font-mono">
            {incidents.length} Tracked Incidents
          </span>
        </div>

        {/* Incidents List */}
        <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl shadow-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-[var(--background)]/80 border-b border-[var(--panel-border)] text-[10px] font-bold uppercase tracking-wider text-[var(--text-muted)] font-mono">
                  <th className="py-3 px-4">Severity</th>
                  <th className="py-3 px-4">Incident ID</th>
                  <th className="py-3 px-4">Monitored Subject</th>
                  <th className="py-3 px-4">Incident Title</th>
                  <th className="py-3 px-4">Related Alert</th>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4">Stage</th>
                  <th className="py-3 px-4 text-right">Workflow</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--panel-border)]">
                {loading ? (
                  <tr>
                    <td colSpan={8} className="py-12 text-center text-[var(--text-muted)]">
                      <div className="flex items-center justify-center gap-2">
                        <Loader2 className="w-4 h-4 animate-spin text-[#00E5FF]" />
                        <span>Loading incident investigation console...</span>
                      </div>
                    </td>
                  </tr>
                ) : incidents.length > 0 ? (
                  incidents.map((inc) => (
                    <tr
                      key={inc.id}
                      onClick={() => { setSelectedInc(inc); setNewStatus(inc.status); setActionSuccess(null); }}
                      className="hover:bg-[var(--background)]/70 transition group cursor-pointer"
                    >
                      <td className="py-3 px-4 whitespace-nowrap">
                        {getSeverityBadge(inc.severity)}
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap font-mono text-xs text-[#00A8FF]">
                        INC-{inc.id}
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <div className="font-semibold text-[var(--foreground)] group-hover:text-[#00E5FF] transition">
                          {inc.employee_name || `Employee #${inc.employee_id}`}
                        </div>
                        <div className="text-[10px] font-mono text-[var(--text-muted)]">
                          {inc.employee_identifier}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-xs text-[var(--foreground)] max-w-sm truncate">
                        {inc.title}
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap font-mono text-[11px] text-[var(--text-muted)]">
                        {inc.alert_id ? `Alert #${inc.alert_id}` : "Direct Escalation"}
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap font-mono text-[11px] text-[var(--text-muted)]">
                        {new Date(inc.created_at).toLocaleString([], { dateStyle: "short", timeStyle: "short" })}
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                          inc.status === "OPEN"
                            ? "bg-cyan-950 text-[#00E5FF] border border-[#00E5FF]/40"
                            : inc.status === "INVESTIGATING"
                            ? "bg-[#00A8FF]/20 text-[#00A8FF] border border-[#00A8FF]/40"
                            : inc.status === "CONTAINED"
                            ? "bg-indigo-950 text-indigo-300 border border-indigo-800"
                            : "bg-[var(--background)] text-emerald-400 border border-emerald-900/40"
                        }`}>
                          {inc.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap text-right">
                        <button className="text-[11px] text-[#00A8FF] group-hover:text-[#00E5FF] font-semibold flex items-center gap-1 ml-auto">
                          Manage <ChevronRight className="w-3 h-3" />
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={8} className="py-12 text-center text-[var(--text-muted)]">
                      No incidents currently match the filter criteria.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Incident Investigation Modal */}
        {selectedInc && (
          <div className="fixed inset-0 z-50 bg-[#050B14]/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-[#0B1626] border border-[#132B45] rounded-xl max-w-2xl w-full p-6 shadow-2xl space-y-4 animate-in fade-in zoom-in-95">
              <div className="flex items-center justify-between pb-3 border-b border-[#132B45]">
                <div className="flex items-center gap-2">
                  <ShieldAlert className="w-5 h-5 text-[#00E5FF]" />
                  <h3 className="font-bold text-sm text-[#F4F8FF]">
                    Incident Investigation INC-{selectedInc.id}
                  </h3>
                </div>
                <button
                  onClick={() => setSelectedInc(null)}
                  className="p-1 text-[#8E9EB5] hover:text-[#F4F8FF] cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {actionSuccess && (
                <div className="p-3 rounded-lg bg-emerald-950/70 border border-emerald-800 text-emerald-300 text-xs flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  {actionSuccess}
                </div>
              )}

              <div className="space-y-3 text-xs">
                <div className="flex justify-between items-center bg-[#050B14] p-3 rounded-lg border border-[#132B45]">
                  <div>
                    <span className="text-[#8E9EB5] block text-[10px] uppercase">Monitored Subject</span>
                    <strong className="text-sm text-[#F4F8FF]">{selectedInc.employee_name} ({selectedInc.employee_identifier})</strong>
                  </div>
                  <div className="text-right">
                    <span className="text-[#8E9EB5] block text-[10px] uppercase">Incident Severity</span>
                    <strong className="text-sm font-mono text-[#00E5FF]">{selectedInc.severity}</strong>
                  </div>
                </div>

                <div>
                  <span className="text-[#8E9EB5] font-semibold">Incident Details:</span>
                  <div className="text-[#F4F8FF] font-medium text-sm mt-1">{selectedInc.title}</div>
                </div>

                <div>
                  <span className="text-[#8E9EB5] font-semibold">Investigation Timeline & Case Notes:</span>
                  <pre className="mt-1 bg-[#050B14] border border-[#132B45] p-3 rounded-lg text-[11px] text-[#F4F8FF] whitespace-pre-wrap font-mono leading-relaxed max-h-44 overflow-y-auto">
                    {selectedInc.description || "No notes recorded yet."}
                  </pre>
                </div>

                {/* Status Update Form */}
                <form onSubmit={handleUpdateStatus} className="pt-3 border-t border-[#132B45] space-y-3">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-[11px] font-semibold text-[#8E9EB5] mb-1">Update Investigation Stage</label>
                      <select
                        value={newStatus}
                        onChange={(e) => setNewStatus(e.target.value)}
                        className="w-full bg-[#050B14] border border-[#132B45] focus:border-[#00A8FF] rounded-lg px-3 py-2 text-xs text-[#F4F8FF]"
                      >
                        <option value="OPEN">OPEN (Initial Triage)</option>
                        <option value="INVESTIGATING">INVESTIGATING (Forensic Scans)</option>
                        <option value="CONTAINED">CONTAINED (Access Suspended)</option>
                        <option value="RESOLVED">RESOLVED (Mitigation Applied)</option>
                        <option value="CLOSED">CLOSED (Post-Mortem Complete)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-semibold text-[#8E9EB5] mb-1">Add Case Note</label>
                      <input
                        type="text"
                        value={resolutionNotes}
                        onChange={(e) => setResolutionNotes(e.target.value)}
                        placeholder="e.g. Host endpoint isolated from VLAN..."
                        className="w-full bg-[#050B14] border border-[#132B45] focus:border-[#00A8FF] rounded-lg px-3 py-2 text-xs text-[#F4F8FF]"
                      />
                    </div>
                  </div>

                  <div className="flex justify-end gap-2 pt-2">
                    <button
                      type="submit"
                      disabled={actionLoading}
                      className="px-4 py-2 bg-[#00A8FF] hover:bg-[#00E5FF] text-[#050B14] text-xs font-bold rounded-lg transition flex items-center gap-1.5 cursor-pointer shadow-[0_0_10px_rgba(0,168,255,0.3)]"
                    >
                      {actionLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
                      <span>Save Investigation Update</span>
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

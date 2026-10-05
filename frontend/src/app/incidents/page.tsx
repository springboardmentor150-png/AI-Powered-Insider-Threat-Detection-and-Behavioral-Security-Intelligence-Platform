"use client";

import React, { useEffect, useState } from "react";
import { incidentAPI, investigationAPI } from "@/lib/api";
import { AIIncidentSummaryModal } from "@/components/AIIncidentSummaryModal";
import {
  FolderLock,
  Sparkles,
  Shield,
  Clock,
  User,
  CheckCircle2,
  RefreshCw,
  ArrowRight,
  Filter,
  FileText,
  PlusCircle,
  History,
  Activity,
  AlertTriangle,
  Send
} from "lucide-react";

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [selectedStatus, setSelectedStatus] = useState("ALL");
  const [loading, setLoading] = useState(true);

  // Active Incident Investigation Workspace State
  const [activeIncident, setActiveIncident] = useState<any | null>(null);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [evidenceList, setEvidenceList] = useState<any[]>([]);
  const [newNote, setNewNote] = useState("");
  const [tab, setTab] = useState<"details" | "timeline" | "evidence">("details");

  // AI Modal state
  const [activeModalIncident, setActiveModalIncident] = useState<any | null>(null);
  const [reportData, setReportData] = useState<any | null>(null);
  const [reportLoading, setReportLoading] = useState(false);

  const fetchIncidents = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (selectedStatus !== "ALL") params.status = selectedStatus;
      const res = await incidentAPI.getAll(params);
      setIncidents(res.data || []);
      if (res.data && res.data.length > 0 && !activeIncident) {
        inspectIncident(res.data[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const inspectIncident = async (inc: any) => {
    setActiveIncident(inc);
    try {
      const [tlRes, evRes] = await Promise.all([
        investigationAPI.getTimeline(inc.id),
        investigationAPI.listEvidence(inc.id)
      ]);
      setTimeline(tlRes.data?.timeline || []);
      setEvidenceList(evRes.data || []);
    } catch (e) {
      console.error("Error inspecting incident:", e);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, [selectedStatus]);

  const handleStatusChange = async (incidentId: number, newStatus: string) => {
    try {
      await incidentAPI.updateStatus(incidentId, { status: newStatus });
      fetchIncidents();
      if (activeIncident?.id === incidentId) {
        setActiveIncident((prev: any) => ({ ...prev, status: newStatus }));
      }
    } catch (e) {
      alert("Failed to update status.");
    }
  };

  const handleAddEvidence = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeIncident || !newNote.trim()) return;
    try {
      await investigationAPI.addEvidence(activeIncident.id, newNote.trim());
      setNewNote("");
      const evRes = await investigationAPI.listEvidence(activeIncident.id);
      setEvidenceList(evRes.data || []);
    } catch (e) {
      alert("Failed to add evidence note.");
    }
  };

  const handleOpenAIReport = async (incident: any) => {
    setActiveModalIncident(incident);
    setReportLoading(true);
    setReportData(null);
    try {
      const res = await incidentAPI.generateAIReport(incident.id);
      setReportData(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setReportLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800 uppercase">
              Milestone 3 Threat Investigation
            </span>
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2 mt-1">
            <FolderLock className="w-5 h-5 text-purple-400" />
            <span>SOC Incident Response & Investigation Workbench</span>
          </h1>
          <p className="text-xs text-slate-400">
            Chronological log timeline, multi-analyst evidence notes & AI forensic analysis.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Statuses</option>
            <option value="open">Open</option>
            <option value="investigating">Investigating</option>
            <option value="resolved">Resolved</option>
          </select>

          <button
            onClick={fetchIncidents}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Incidents List (Left 5 Cols) */}
        <div className="lg:col-span-5 space-y-3">
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider font-mono">
              Active Security Tickets ({incidents.length})
            </h3>
            <div className="space-y-2.5 max-h-[600px] overflow-y-auto pr-1">
              {incidents.map((inc) => {
                const isSelected = activeIncident?.id === inc.id;
                return (
                  <div
                    key={inc.id}
                    onClick={() => inspectIncident(inc)}
                    className={`p-4 rounded-xl cursor-pointer transition border space-y-2 ${
                      isSelected
                        ? "bg-purple-950/40 border-purple-500/50 shadow-md shadow-purple-500/10"
                        : "bg-slate-950/50 border-slate-800/80 hover:border-slate-700"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800">
                        {inc.incident_code || `INC-${inc.id}`}
                      </span>
                      <span
                        className={`text-[10px] px-2 py-0.2 rounded-full font-mono uppercase font-semibold ${
                          (inc.severity || "").toLowerCase() === "critical"
                            ? "bg-rose-950 text-rose-300 border border-rose-800"
                            : "bg-amber-950 text-amber-300 border border-amber-800"
                        }`}
                      >
                        {inc.severity}
                      </span>
                    </div>

                    <h4 className="text-xs font-bold text-slate-100 line-clamp-1">{inc.title || inc.summary}</h4>
                    <p className="text-[11px] text-slate-400 line-clamp-2">{inc.description || inc.summary}</p>

                    <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 pt-2 border-t border-slate-800/60">
                      <span>Subject: {inc.employee_id}</span>
                      <span className="text-cyan-400 uppercase font-semibold">{inc.status}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Deep Investigation Workbench (Right 7 Cols) */}
        <div className="lg:col-span-7 space-y-4">
          {activeIncident ? (
            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-5">
              {/* Workbench Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-mono font-bold text-purple-400">
                      {activeIncident.incident_code || `INC-${activeIncident.id}`}
                    </span>
                    <span className="text-xs text-slate-400">&bull; Subject: <strong className="text-white">{activeIncident.employee_id}</strong></span>
                  </div>
                  <h2 className="text-sm font-bold text-white mt-1">{activeIncident.title || activeIncident.summary}</h2>
                </div>

                <div className="flex items-center space-x-2">
                  <select
                    value={activeIncident.status}
                    onChange={(e) => handleStatusChange(activeIncident.id, e.target.value)}
                    className="px-3 py-1.5 rounded-xl bg-slate-800 border border-slate-700 text-xs font-mono text-cyan-300 focus:outline-none"
                  >
                    <option value="open">OPEN</option>
                    <option value="investigating">INVESTIGATING</option>
                    <option value="resolved">RESOLVED</option>
                  </select>

                  <button
                    onClick={() => handleOpenAIReport(activeIncident)}
                    className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 text-white text-xs font-semibold shadow transition"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>AI Dossier</span>
                  </button>
                </div>
              </div>

              {/* Navigation Tabs */}
              <div className="flex border-b border-slate-800 text-xs font-medium space-x-4">
                <button
                  onClick={() => setTab("details")}
                  className={`pb-2.5 transition border-b-2 ${tab === "details" ? "border-cyan-400 text-cyan-400 font-bold" : "border-transparent text-slate-400 hover:text-slate-200"}`}
                >
                  Incident Overview
                </button>
                <button
                  onClick={() => setTab("timeline")}
                  className={`pb-2.5 transition border-b-2 flex items-center gap-1.5 ${tab === "timeline" ? "border-cyan-400 text-cyan-400 font-bold" : "border-transparent text-slate-400 hover:text-slate-200"}`}
                >
                  <History className="w-3.5 h-3.5" />
                  <span>Activity Timeline ({timeline.length})</span>
                </button>
                <button
                  onClick={() => setTab("evidence")}
                  className={`pb-2.5 transition border-b-2 flex items-center gap-1.5 ${tab === "evidence" ? "border-cyan-400 text-cyan-400 font-bold" : "border-transparent text-slate-400 hover:text-slate-200"}`}
                >
                  <FileText className="w-3.5 h-3.5" />
                  <span>Evidence Notes ({evidenceList.length})</span>
                </button>
              </div>

              {/* Tab 1: Details */}
              {tab === "details" && (
                <div className="space-y-4 text-xs">
                  <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
                    <div className="font-bold text-slate-300 uppercase font-mono text-[10px]">Case Summary</div>
                    <p className="text-slate-200 leading-relaxed">{activeIncident.description || activeIncident.summary}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                      <span className="text-[10px] text-slate-400 font-mono">Assigned Investigator</span>
                      <div className="text-xs font-bold text-cyan-300 font-mono mt-1">{activeIncident.assigned_to || "Unassigned"}</div>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                      <span className="text-[10px] text-slate-400 font-mono">Opened Timestamp</span>
                      <div className="text-xs font-bold text-slate-200 font-mono mt-1">{new Date(activeIncident.created_at).toLocaleString()}</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 2: Chronological Timeline (Milestone 3 Part 3) */}
              {tab === "timeline" && (
                <div className="space-y-3">
                  <p className="text-[11px] text-slate-400 font-mono">
                    Merged sequence of raw activity logs and detected behavioral anomalies:
                  </p>
                  <div className="space-y-2 max-h-[350px] overflow-y-auto pr-1">
                    {timeline.map((item, idx) => (
                      <div
                        key={idx}
                        className={`p-3 rounded-xl border flex items-center justify-between text-xs ${
                          item.type === "anomaly"
                            ? "bg-rose-950/30 border-rose-800/60 text-rose-300"
                            : "bg-slate-950/60 border-slate-800 text-slate-300"
                        }`}
                      >
                        <div className="flex items-center space-x-2.5">
                          {item.type === "anomaly" ? (
                            <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
                          ) : (
                            <Activity className="w-4 h-4 text-cyan-400 shrink-0" />
                          )}
                          <div>
                            <span className="font-semibold font-mono">{item.detail}</span>
                            <span className="text-[10px] uppercase font-mono ml-2 px-1.5 py-0.2 rounded bg-slate-900 border border-slate-800">
                              {item.type}
                            </span>
                          </div>
                        </div>
                        <span className="text-[10px] font-mono text-slate-400 shrink-0">
                          {new Date(item.timestamp).toLocaleString()}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Tab 3: Multi-Analyst Evidence Notes (Milestone 3 Part 3) */}
              {tab === "evidence" && (
                <div className="space-y-4">
                  <form onSubmit={handleAddEvidence} className="flex gap-2">
                    <input
                      type="text"
                      required
                      placeholder="Add investigation finding or forensic note..."
                      value={newNote}
                      onChange={(e) => setNewNote(e.target.value)}
                      className="flex-1 p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-100 focus:outline-none focus:border-cyan-500 font-mono"
                    />
                    <button
                      type="submit"
                      className="px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow"
                    >
                      <Send className="w-3.5 h-3.5" />
                      <span>Add Note</span>
                    </button>
                  </form>

                  <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
                    {evidenceList.map((ev, idx) => (
                      <div key={idx} className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                        <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                          <span className="text-cyan-400 font-bold">{ev.added_by}</span>
                          <span>{new Date(ev.added_at).toLocaleString()}</span>
                        </div>
                        <p className="text-xs text-slate-200 font-sans">{ev.note}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="p-12 text-center text-slate-400 bg-slate-900/40 rounded-2xl border border-slate-800">
              Select an incident from the tickets list to inspect case details.
            </div>
          )}
        </div>
      </div>

      {/* AI Forensic Summary Modal */}
      <AIIncidentSummaryModal
        isOpen={!!activeModalIncident}
        onClose={() => setActiveModalIncident(null)}
        incidentCode={activeModalIncident?.incident_code || ""}
        reportData={reportData}
        isLoading={reportLoading}
      />
    </div>
  );
}
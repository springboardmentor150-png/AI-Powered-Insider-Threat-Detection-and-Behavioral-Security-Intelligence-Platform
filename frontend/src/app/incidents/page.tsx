"use client";

import React, { useEffect, useState } from "react";
import { incidentAPI } from "@/lib/api";
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
  Filter
} from "lucide-react";

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [selectedStatus, setSelectedStatus] = useState("ALL");
  const [loading, setLoading] = useState(true);

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
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, [selectedStatus]);

  const handleStatusChange = async (incidentId: number, newStatus: string) => {
    try {
      await incidentAPI.updateStatus(incidentId, { status: newStatus });
      fetchIncidents();
    } catch (e) {
      alert("Failed to update status.");
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
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <FolderLock className="w-5 h-5 text-purple-400" />
            <span>SOC Incident Response & Investigation Workbench</span>
          </h1>
          <p className="text-xs text-slate-400">
            Lifecycle tracking, analyst assignment, and AI-assisted forensic threat containment playbooks.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Statuses</option>
            <option value="OPEN">Open</option>
            <option value="INVESTIGATING">Investigating</option>
            <option value="CONTAINED">Contained</option>
            <option value="RESOLVED">Resolved</option>
          </select>

          <button
            onClick={fetchIncidents}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {/* Incidents List */}
      <div className="space-y-4">
        {incidents.map((inc) => (
          <div
            key={inc.id}
            className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4 hover:border-slate-700 transition"
          >
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
              <div className="flex items-center space-x-3">
                <span className="text-xs font-mono font-bold px-2.5 py-1 rounded bg-purple-950 text-purple-300 border border-purple-800">
                  {inc.incident_code}
                </span>
                <h3 className="text-sm font-bold text-white">{inc.title}</h3>
              </div>

              <div className="flex items-center space-x-2">
                <span
                  className={`text-xs px-2.5 py-1 rounded-full font-mono font-semibold ${
                    inc.severity === "CRITICAL"
                      ? "bg-rose-950 text-rose-300 border border-rose-800"
                      : "bg-amber-950 text-amber-300 border border-amber-800"
                  }`}
                >
                  {inc.severity}
                </span>

                <select
                  value={inc.status}
                  onChange={(e) => handleStatusChange(inc.id, e.target.value)}
                  className="px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-xs font-mono text-cyan-300 focus:outline-none"
                >
                  <option value="OPEN">OPEN</option>
                  <option value="INVESTIGATING">INVESTIGATING</option>
                  <option value="CONTAINED">CONTAINED</option>
                  <option value="RESOLVED">RESOLVED</option>
                  <option value="FALSE_POSITIVE">FALSE_POSITIVE</option>
                </select>
              </div>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed font-sans">{inc.description}</p>

            {/* MITRE Technique Badge */}
            {inc.mitre_attack_technique && (
              <div className="flex items-center space-x-2 text-xs">
                <span className="text-slate-400 font-mono text-[11px]">MITRE Classification:</span>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-950 text-rose-300 border border-rose-900/50">
                  {inc.mitre_attack_technique}
                </span>
              </div>
            )}

            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-slate-800/60 text-xs">
              <div className="flex items-center space-x-4 text-[11px] font-mono text-slate-400">
                <span>Subject: <strong className="text-slate-200">{inc.employee_id}</strong></span>
                <span>Assigned: <strong className="text-cyan-400">{inc.assigned_to || "Unassigned"}</strong></span>
                <span>Opened: {new Date(inc.created_at).toLocaleDateString()}</span>
              </div>

              <button
                onClick={() => handleOpenAIReport(inc)}
                className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-semibold shadow-md shadow-cyan-600/20 transition"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Generate AI Forensic Dossier</span>
              </button>
            </div>
          </div>
        ))}
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

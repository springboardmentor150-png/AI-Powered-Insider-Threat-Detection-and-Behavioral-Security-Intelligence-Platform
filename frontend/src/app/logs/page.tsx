"use client";

import React, { useEffect, useState } from "react";
import { logAPI } from "@/lib/api";
import {
  Activity,
  Send,
  Filter,
  RefreshCw,
  Clock,
  HardDrive,
  FileCode,
  CheckCircle,
  Database,
  Radio
} from "lucide-react";

export default function LogsPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedEventType, setSelectedEventType] = useState("ALL");
  const [empFilter, setEmpFilter] = useState("");

  // Ingestion Form State
  const [ingestForm, setIngestForm] = useState({
    employee_id: "EMP1001",
    event_type: "login",
    details_json: '{\n  "ip_address": "192.168.1.50",\n  "device": "workstation-01",\n  "is_off_hours": false\n}',
  });
  const [ingestStatus, setIngestStatus] = useState<string | null>(null);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 60 };
      if (selectedEventType !== "ALL") params.event_type = selectedEventType;
      if (empFilter) params.employee_id = empFilter;

      const [logRes, statsRes] = await Promise.all([
        logAPI.getAll(params),
        logAPI.getStats(),
      ]);
      setLogs(logRes.data || []);
      setStats(statsRes.data || null);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [selectedEventType]);

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    setIngestStatus(null);
    try {
      let parsedDetails = {};
      try {
        parsedDetails = JSON.parse(ingestForm.details_json);
      } catch (err) {
        alert("Invalid JSON format in details field.");
        return;
      }

      await logAPI.ingest({
        employee_id: ingestForm.employee_id,
        event_type: ingestForm.event_type,
        details: parsedDetails,
      });

      setIngestStatus("Log successfully ingested into MongoDB document collection!");
      fetchLogs();
    } catch (err) {
      alert("Failed to ingest log.");
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <Activity className="w-5 h-5 text-emerald-400" />
            <span>Activity Log Telemetry & Ingestion Pipeline</span>
          </h1>
          <p className="text-xs text-slate-400">
            Unstructured event streaming into MongoDB document store with automated real-time trigger evaluation.
          </p>
        </div>

        <button
          onClick={fetchLogs}
          className="flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          <span>Refresh Feed</span>
        </button>
      </div>

      {/* Stats Summary Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-1">
          <div className="flex items-center space-x-2 text-xs text-slate-400">
            <Database className="w-4 h-4 text-cyan-400" />
            <span>Total Document Count</span>
          </div>
          <p className="text-2xl font-bold text-white font-mono">{stats?.total_logs || logs.length}</p>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-1">
          <div className="flex items-center space-x-2 text-xs text-slate-400">
            <Clock className="w-4 h-4 text-amber-400" />
            <span>Off-Hours Egress Ratio</span>
          </div>
          <p className="text-2xl font-bold text-amber-300 font-mono">
            {((stats?.off_hours_ratio || 0) * 100).toFixed(1)}%
          </p>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-1">
          <div className="flex items-center space-x-2 text-xs text-slate-400">
            <Radio className="w-4 h-4 text-emerald-400" />
            <span>Ingestion Pipeline</span>
          </div>
          <p className="text-sm font-bold text-emerald-400 font-mono">ACTIVE (FastAPI &rarr; MongoDB)</p>
        </div>
      </div>

      {/* Main Grid: Custom Ingestion Form on Left, Telemetry Feed on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Custom Ingestion Simulator */}
        <div className="lg:col-span-5 p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="flex items-center space-x-2 text-sm font-bold text-white">
            <Send className="w-4 h-4 text-cyan-400" />
            <span>Direct Telemetry Ingest Tool</span>
          </div>
          <p className="text-xs text-slate-400">
            Simulate an endpoint log submission matching the Milestone 1 API specification.
          </p>

          {ingestStatus && (
            <div className="p-3 rounded-xl bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-xs flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 shrink-0" />
              <span>{ingestStatus}</span>
            </div>
          )}

          <form onSubmit={handleIngest} className="space-y-4 text-xs">
            <div>
              <label className="text-slate-300 font-medium">Employee Identifier</label>
              <input
                type="text"
                required
                value={ingestForm.employee_id}
                onChange={(e) => setIngestForm({ ...ingestForm, employee_id: e.target.value })}
                className="w-full mt-1 p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-mono"
              />
            </div>

            <div>
              <label className="text-slate-300 font-medium">Event Type</label>
              <select
                value={ingestForm.event_type}
                onChange={(e) => setIngestForm({ ...ingestForm, event_type: e.target.value })}
                className="w-full mt-1 p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-mono"
              >
                <option value="login">login</option>
                <option value="file_download">file_download</option>
                <option value="usb_connect">usb_connect</option>
                <option value="database_query">database_query</option>
                <option value="privilege_escalation">privilege_escalation</option>
                <option value="git_commit">git_commit</option>
              </select>
            </div>

            <div>
              <label className="text-slate-300 font-medium">Unstructured Details (Flexible JSON)</label>
              <textarea
                rows={5}
                required
                value={ingestForm.details_json}
                onChange={(e) => setIngestForm({ ...ingestForm, details_json: e.target.value })}
                className="w-full mt-1 p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-mono text-[11px]"
              />
            </div>

            <button
              type="submit"
              className="w-full py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold shadow-lg shadow-cyan-600/20 transition"
            >
              POST /api/logs/ingest
            </button>
          </form>
        </div>

        {/* Live Event Stream */}
        <div className="lg:col-span-7 p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider font-mono">
              Live Document Stream ({logs.length} events)
            </h3>

            <div className="flex items-center space-x-2">
              <select
                value={selectedEventType}
                onChange={(e) => setSelectedEventType(e.target.value)}
                className="px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200"
              >
                <option value="ALL">All Event Types</option>
                <option value="login">login</option>
                <option value="file_download">file_download</option>
                <option value="usb_connect">usb_connect</option>
                <option value="database_query">database_query</option>
                <option value="privilege_escalation">privilege_escalation</option>
              </select>
            </div>
          </div>

          <div className="space-y-2.5 max-h-[550px] overflow-y-auto pr-1">
            {logs.map((log, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 space-y-2 hover:border-slate-700 transition"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-bold text-slate-100 font-mono">{log.employee_id}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-cyan-300 font-mono border border-slate-700">
                      {log.event_type}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-slate-400">
                    {new Date(log.timestamp).toLocaleString()}
                  </span>
                </div>

                <div className="p-2 rounded-lg bg-slate-900/90 text-[11px] font-mono text-slate-300 border border-slate-800/60 overflow-x-auto">
                  {JSON.stringify(log.details, null, 2)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

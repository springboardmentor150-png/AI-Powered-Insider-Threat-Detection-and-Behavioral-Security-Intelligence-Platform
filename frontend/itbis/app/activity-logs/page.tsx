"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  Activity,
  Search,
  Filter,
  RefreshCw,
  Zap,
  CheckCircle2,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  ShieldAlert,
  Loader2,
  BarChart2,
  Grid,
  Info,
  X,
  Clock,
  Laptop,
  Globe,
  Database,
  Calendar,
  User,
  Shield,
  FileSearch,
  Flame,
  Check,
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import { api } from "@/lib/api";

interface MongoActivityItem {
  id: string;
  employee_id: string;
  event_type: string;
  action?: string;
  resource?: string;
  timestamp: string;
  device?: string;
  ip_address?: string;
  location?: string;
  risk_weight: number;
  is_suspicious: boolean;
  anomaly_reasons: string[];
  is_test_event: boolean;
  details: Record<string, any>;
}

interface TimelineEventItem {
  id: string;
  employee_id: string;
  event_type: string;
  action?: string;
  resource?: string;
  timestamp: string;
  device?: string;
  ip_address?: string;
  location?: string;
  risk_weight: number;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  is_suspicious: boolean;
  is_anomalous: boolean;
  anomaly_reasons: string[];
  reason?: string;
  is_test_event: boolean;
  details: Record<string, any>;
}

interface TimelineResponse {
  items: TimelineEventItem[];
  total: number;
}

interface HeatmapCell {
  day: string;
  day_index: number;
  hour: number;
  hour_label: string;
  event_count: number;
  suspicious_count: number;
  is_off_hours: boolean;
  primary_event?: string;
}

interface EventTypeDistributionItem {
  event_type: string;
  label: string;
  count: number;
  percentage: number;
}

const EMPLOYEE_OPTIONS = [
  { id: "ALL", label: "All Subjects" },
  { id: "CYB-1042", label: "CYB-1042 — Sarah Connor (Cyber)" },
  { id: "FIN-2187", label: "FIN-2187 — Alexander Hayes (Finance)" },
  { id: "IT-3064", label: "IT-3064 — Marcus Vance (IT Admin)" },
  { id: "HR-4128", label: "HR-4128 — Samantha Wright (HR)" },
  { id: "DEV-5271", label: "DEV-5271 — Vikram Malhotra (DevOps)" },
  { id: "CMP-6385", label: "CMP-6385 — Claire Dupont (Compliance)" },
];

const EVENT_TYPE_OPTIONS = [
  "ALL",
  "login",
  "file_download",
  "file_upload",
  "data_transfer",
  "email_activity",
  "privilege_change",
  "remote_access",
  "usb_connect",
];

export default function ActivityLogsPage() {
  // Table View State
  const [logs, setLogs] = useState<MongoActivityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchEmp, setSearchEmp] = useState("");
  const [typeFilter, setTypeFilter] = useState("ALL");
  const [testFilter, setTestFilter] = useState<string>("ALL");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  // Tabs
  const [activeTab, setActiveTab] = useState<"table" | "timeline" | "heatmap">("table");

  // Visualizations & Distribution State
  const [heatmapCells, setHeatmapCells] = useState<HeatmapCell[]>([]);
  const [heatmapLoading, setHeatmapLoading] = useState(false);
  const [distribution, setDistribution] = useState<EventTypeDistributionItem[]>([]);
  const [distLoading, setDistLoading] = useState(false);
  const [distError, setDistError] = useState<string | null>(null);

  // Dedicated Timeline State
  const [timelineRange, setTimelineRange] = useState<"24h" | "7d" | "30d" | "all">("7d");
  const [timelineEmpFilter, setTimelineEmpFilter] = useState<string>("ALL");
  const [timelineTypeFilter, setTimelineTypeFilter] = useState<string>("ALL");
  const [timelineEvents, setTimelineEvents] = useState<TimelineEventItem[]>([]);
  const [timelineTotal, setTimelineTotal] = useState(0);
  const [timelineLoading, setTimelineLoading] = useState(false);
  const [timelineError, setTimelineError] = useState<string | null>(null);

  // Detail Modal / Drawer
  const [selectedActivity, setSelectedActivity] = useState<MongoActivityItem | TimelineEventItem | null>(null);

  // Test Generator State
  const [simEmployeeId, setSimEmployeeId] = useState("FIN-2187");
  const [simScenario, setSimScenario] = useState("SUSPICIOUS_OFFHOURS_EXFIL");
  const [simLoading, setSimLoading] = useState(false);
  const [simResult, setSimResult] = useState<any>(null);

  // 1. Fetch Paginated Telemetry Table Logs
  const fetchLogs = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (searchEmp.trim()) params.append("employee_id", searchEmp.trim());
      if (typeFilter !== "ALL") params.append("event_type", typeFilter);
      if (testFilter === "TEST_ONLY") params.append("is_test_event", "true");
      if (testFilter === "REAL_ONLY") params.append("is_test_event", "false");
      params.append("page", page.toString());
      params.append("limit", "15");

      const res = await api.get(`/activity-logs?${params.toString()}`);
      setLogs(res.data.items || []);
      setTotal(res.data.total || 0);
    } catch (err) {
      console.error("Error fetching logs:", err);
    } finally {
      setLoading(false);
    }
  }, [searchEmp, typeFilter, testFilter, page]);

  // 2. Fetch Distribution & Heatmap
  const fetchVisualizations = useCallback(async () => {
    setDistLoading(true);
    setDistError(null);
    try {
      const [distRes, hmRes] = await Promise.all([
        api.get<EventTypeDistributionItem[]>("/activity-logs/distribution"),
        api.get<HeatmapCell[]>("/activity-logs/heatmap").catch((err) => {
          console.warn("Heatmap fetch error:", err);
          return { data: [] };
        }),
      ]);
      setDistribution(distRes.data || []);
      setHeatmapCells(hmRes.data || []);
    } catch (err: any) {
      console.error("Error fetching telemetry distribution:", err);
      setDistError("Unable to load telemetry distribution");
      setDistribution([]);
    } finally {
      setDistLoading(false);
    }
  }, []);

  // 3. Fetch Dedicated Chronological Activity Timeline
  const fetchTimeline = useCallback(async () => {
    setTimelineLoading(true);
    setTimelineError(null);
    try {
      const params = new URLSearchParams();
      params.append("time_range", timelineRange);
      if (timelineEmpFilter !== "ALL") params.append("employee_id", timelineEmpFilter);
      if (timelineTypeFilter !== "ALL") params.append("event_type", timelineTypeFilter);
      params.append("limit", "150");

      const res = await api.get<TimelineResponse>(`/activity-logs/timeline?${params.toString()}`);
      setTimelineEvents(res.data.items || []);
      setTimelineTotal(res.data.total || 0);
    } catch (err: any) {
      console.error("Error fetching activity timeline:", err);
      setTimelineError("Unable to load activity timeline.");
      setTimelineEvents([]);
    } finally {
      setTimelineLoading(false);
    }
  }, [timelineRange, timelineEmpFilter, timelineTypeFilter]);

  // Initial Load
  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  useEffect(() => {
    fetchVisualizations();
  }, [fetchVisualizations]);

  useEffect(() => {
    if (activeTab === "timeline") {
      fetchTimeline();
    }
  }, [activeTab, fetchTimeline]);

  const handleSimulateEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    setSimLoading(true);
    setSimResult(null);
    try {
      const res = await api.post("/activity-logs/test-event", {
        employee_id: simEmployeeId,
        activity_type: "file_download",
        action: "Simulated Automated Threat Vector",
        resource: "s3://analytics-archive/customer-pii-vault.tar.gz",
        scenario: simScenario,
        download_size_mb: simScenario === "SUSPICIOUS_OFFHOURS_EXFIL" ? 4800 : 15,
      });
      setSimResult(res.data);
      fetchLogs();
      fetchVisualizations();
      if (activeTab === "timeline") {
        fetchTimeline();
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to trigger synthetic event");
    } finally {
      setSimLoading(false);
    }
  };

  const totalPages = Math.ceil(total / 15) || 1;
  const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case "CRITICAL":
        return <span className="px-2 py-0.5 rounded font-mono font-bold text-[10px] bg-rose-950/80 text-rose-300 border border-rose-500/50">CRITICAL</span>;
      case "HIGH":
        return <span className="px-2 py-0.5 rounded font-mono font-bold text-[10px] bg-amber-950/80 text-amber-300 border border-amber-500/50">HIGH</span>;
      case "MEDIUM":
        return <span className="px-2 py-0.5 rounded font-mono font-bold text-[10px] bg-cyan-950/80 text-[#00E5FF] border border-[#00E5FF]/40">MEDIUM</span>;
      default:
        return <span className="px-2 py-0.5 rounded font-mono font-semibold text-[10px] bg-[var(--background)] text-[var(--text-muted)] border border-[var(--panel-border)]">LOW</span>;
    }
  };

  return (
    <DashboardLayout
      pageTitle="MongoDB Activity Telemetry"
      pageSubtitle="Chronological event intelligence & behavioral activity stream (itbis.activity_logs)"
    >
      <div className="space-y-6">
        {/* Synthetic Threat Simulator Card */}
        <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-5 shadow-xl relative overflow-hidden">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-4 border-b border-[var(--panel-border)]">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-[var(--background)] border border-[#00E5FF]/40 flex items-center justify-center text-[#00E5FF]">
                <Zap className="w-5 h-5 animate-pulse" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-[var(--foreground)] uppercase tracking-wider">
                  Synthetic Threat Activity Simulator
                </h3>
                <p className="text-xs text-[var(--text-muted)]">
                  Inject safe test telemetry (is_test_event = true) to evaluate anomalies and automated alerts
                </p>
              </div>
            </div>
            <span className="px-2.5 py-1 rounded bg-cyan-950/70 border border-[#00E5FF]/40 text-[#00E5FF] font-mono text-xs">
              MongoDB Telemetry Mode: Active
            </span>
          </div>

          <form onSubmit={handleSimulateEvent} className="mt-4 grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-4 gap-3 items-end">
            <div>
              <label className="block text-[11px] font-semibold text-[var(--text-muted)] mb-1">Target Subject ID</label>
              <select
                value={simEmployeeId}
                onChange={(e) => setSimEmployeeId(e.target.value)}
                className="w-full bg-[var(--background)] border border-[var(--panel-border)] focus:border-[#00A8FF] rounded-lg px-3 py-2 text-xs text-[var(--foreground)] font-mono"
              >
                <option value="CYB-1042">CYB-1042 — Sarah Connor (Cyber)</option>
                <option value="FIN-2187">FIN-2187 — Alexander Hayes (Finance)</option>
                <option value="IT-3064">IT-3064 — Marcus Vance (IT Admin)</option>
                <option value="HR-4128">HR-4128 — Samantha Wright (HR)</option>
                <option value="DEV-5271">DEV-5271 — Vikram Malhotra (DevOps)</option>
                <option value="CMP-6385">CMP-6385 — Claire Dupont (Compliance)</option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-[var(--text-muted)] mb-1">Threat Scenario</label>
              <select
                value={simScenario}
                onChange={(e) => setSimScenario(e.target.value)}
                className="w-full bg-[var(--background)] border border-[var(--panel-border)] focus:border-[#00A8FF] rounded-lg px-3 py-2 text-xs text-[var(--foreground)]"
              >
                <option value="SUSPICIOUS_OFFHOURS_EXFIL">Off-Hours Mass Exfiltration (4.8 GB)</option>
                <option value="PRIVILEGE_ESCALATION">Unauthorized Active Directory Privilege Elevation</option>
                <option value="SENSITIVE_ACCESS">Restricted Payroll & Encryption Key Vault Access</option>
                <option value="NORMAL_DAYTIME">Normal Daytime Routine Activity</option>
              </select>
            </div>

            <div>
              <button
                type="submit"
                disabled={simLoading}
                className="w-full bg-[#00A8FF] hover:bg-[#00E5FF] disabled:opacity-50 text-[#050B14] font-bold text-xs py-2 px-4 rounded-lg transition flex items-center justify-center gap-2 cursor-pointer shadow-[0_0_15px_rgba(0,168,255,0.3)]"
              >
                {simLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Zap className="w-3.5 h-3.5" />}
                <span>Inject Telemetry Event</span>
              </button>
            </div>
          </form>

          {simResult && (
            <div className="mt-4 p-3 bg-[var(--background)] border border-[#00E5FF]/40 rounded-lg text-xs space-y-2 animate-in fade-in">
              <div className="flex items-center justify-between font-bold text-[#00E5FF]">
                <span>Telemetry Ingestion & Detection Result:</span>
                <span className="font-mono">Risk Score: {simResult.calculated_risk_score}/100</span>
              </div>
              <p className="text-[var(--text-muted)]">{simResult.message}</p>
            </div>
          )}
        </div>

        {/* Event Type Distribution Filter Bar */}
        <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-4 shadow-xl">
          <div className="flex items-center justify-between mb-2">
            <div className="text-xs font-bold uppercase tracking-wider text-[var(--text-muted)]">
              Filter Telemetry by Event Type (MongoDB Distribution)
            </div>
            {distLoading && (
              <span className="text-[10px] font-mono text-[#00E5FF] flex items-center gap-1">
                <Loader2 className="w-3 h-3 animate-spin" /> Fetching distribution...
              </span>
            )}
          </div>

          {distError ? (
            <div className="flex items-center justify-between gap-3 text-xs text-rose-400 bg-rose-950/20 border border-rose-500/30 rounded-lg p-3">
              <span>{distError}</span>
              <button
                onClick={fetchVisualizations}
                className="px-2.5 py-1 rounded bg-rose-900/40 border border-rose-500/40 hover:bg-rose-800/60 text-rose-200 font-semibold cursor-pointer text-xs"
              >
                Retry
              </button>
            </div>
          ) : (
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => { setTypeFilter("ALL"); setPage(1); }}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition cursor-pointer ${
                  typeFilter === "ALL"
                    ? "bg-[#00A8FF] text-[#050B14] shadow-[0_0_10px_rgba(0,168,255,0.3)]"
                    : "bg-[var(--background)] border border-[var(--panel-border)] text-[var(--text-muted)] hover:text-[var(--foreground)]"
                }`}
              >
                ALL ({total})
              </button>
              {distribution.map((dist) => (
                <button
                  key={dist.event_type}
                  onClick={() => { setTypeFilter(dist.event_type); setPage(1); }}
                  className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition cursor-pointer flex items-center gap-2 ${
                    typeFilter === dist.event_type
                      ? "bg-[#00A8FF] text-[#050B14] shadow-[0_0_10px_rgba(0,168,255,0.3)]"
                      : "bg-[var(--background)] border border-[var(--panel-border)] text-[var(--text-muted)] hover:text-[var(--foreground)]"
                  }`}
                >
                  <span>{dist.event_type}</span>
                  <span className="opacity-70 text-[10px]">({dist.count})</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* View Switcher: Table | Activity Timeline | 7-Day Heatmap */}
        <div className="flex items-center justify-between border-b border-[var(--panel-border)] pb-2">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveTab("table")}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition flex items-center gap-2 cursor-pointer ${
                activeTab === "table"
                  ? "bg-[#00A8FF]/20 text-[#00E5FF] border border-[#00A8FF]/40"
                  : "text-[var(--text-muted)] hover:text-[var(--foreground)]"
              }`}
            >
              <Activity className="w-3.5 h-3.5" />
              <span>Telemetry Table</span>
            </button>
            <button
              onClick={() => setActiveTab("timeline")}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition flex items-center gap-2 cursor-pointer ${
                activeTab === "timeline"
                  ? "bg-[#00A8FF]/20 text-[#00E5FF] border border-[#00A8FF]/40"
                  : "text-[var(--text-muted)] hover:text-[var(--foreground)]"
              }`}
            >
              <Clock className="w-3.5 h-3.5" />
              <span>Chronological Activity Timeline</span>
            </button>
            <button
              onClick={() => setActiveTab("heatmap")}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition flex items-center gap-2 cursor-pointer ${
                activeTab === "heatmap"
                  ? "bg-[#00A8FF]/20 text-[#00E5FF] border border-[#00A8FF]/40"
                  : "text-[var(--text-muted)] hover:text-[var(--foreground)]"
              }`}
            >
              <Grid className="w-3.5 h-3.5" />
              <span>7-Day Heatmap</span>
            </button>
          </div>
        </div>

        {/* TAB 1: TELEMETRY TABLE */}
        {activeTab === "table" && (
          <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl shadow-xl overflow-hidden">
            {/* Filter Bar */}
            <div className="p-4 border-b border-[var(--panel-border)] flex flex-col sm:flex-row items-center justify-between gap-3">
              <div className="flex items-center gap-2 w-full sm:w-auto">
                <input
                  type="text"
                  value={searchEmp}
                  onChange={(e) => { setSearchEmp(e.target.value); setPage(1); }}
                  placeholder="Filter by Subject ID (e.g. FIN-2187)..."
                  className="bg-[var(--background)] border border-[var(--panel-border)] focus:border-[#00A8FF] rounded-lg px-3 py-1.5 text-xs text-[var(--foreground)] w-full sm:w-64"
                />
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={fetchLogs}
                  className="p-1.5 rounded-lg bg-[var(--background)] border border-[var(--panel-border)] text-[var(--text-muted)] hover:text-[#00E5FF] transition cursor-pointer"
                  title="Refresh Table"
                >
                  <RefreshCw className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-[var(--panel-border)] bg-[var(--background)]/70 text-[var(--text-muted)] font-mono text-[11px] uppercase tracking-wider">
                    <th className="py-3 px-4">Subject</th>
                    <th className="py-3 px-4">Event Type</th>
                    <th className="py-3 px-4">Action & Resource</th>
                    <th className="py-3 px-4">Node & IP</th>
                    <th className="py-3 px-4">Risk Weight</th>
                    <th className="py-3 px-4">Timestamp</th>
                    <th className="py-3 px-4 text-right">Inspect</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[var(--panel-border)]">
                  {loading ? (
                    <tr>
                      <td colSpan={7} className="py-12 text-center text-[var(--text-muted)]">
                        <Loader2 className="w-6 h-6 animate-spin text-[#00E5FF] mx-auto mb-2" />
                        <span>Querying MongoDB activity logs...</span>
                      </td>
                    </tr>
                  ) : logs.length > 0 ? (
                    logs.map((log) => (
                      <tr
                        key={log.id}
                        className={`hover:bg-[var(--background)]/60 transition ${
                          log.is_suspicious ? "bg-cyan-950/20" : ""
                        }`}
                      >
                        <td className="py-3 px-4 font-mono font-bold text-[var(--foreground)]">
                          {log.employee_id}
                        </td>
                        <td className="py-3 px-4 font-mono">
                          <span className="px-2 py-0.5 rounded bg-[var(--background)] border border-[var(--panel-border)] text-[#00E5FF] text-[10px]">
                            {log.event_type}
                          </span>
                        </td>
                        <td className="py-3 px-4 max-w-xs truncate">
                          <div className="font-semibold text-[var(--foreground)] truncate">{log.action}</div>
                          <div className="text-[10px] font-mono text-[var(--text-muted)] truncate">{log.resource}</div>
                        </td>
                        <td className="py-3 px-4 font-mono text-[11px] text-[var(--text-muted)]">
                          <div>{log.device || "N/A"}</div>
                          <div className="text-[10px] opacity-70">{log.ip_address || "N/A"}</div>
                        </td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-0.5 rounded font-mono font-bold text-[10px] ${
                            log.risk_weight >= 40
                              ? "bg-cyan-950 text-[#00E5FF] border border-[#00E5FF]/40"
                              : log.risk_weight >= 20
                              ? "bg-[#00A8FF]/20 text-[#00A8FF]"
                              : "bg-[var(--background)] text-[var(--text-muted)]"
                          }`}>
                            +{log.risk_weight}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-mono text-[11px] text-[var(--text-muted)]">
                          {new Date(log.timestamp).toLocaleString()}
                        </td>
                        <td className="py-3 px-4 text-right">
                          <button
                            onClick={() => setSelectedActivity(log)}
                            className="p-1.5 rounded bg-[var(--background)] border border-[var(--panel-border)] text-[var(--text-muted)] hover:text-[#00E5FF] transition cursor-pointer"
                            title="Inspect Details"
                          >
                            <Info className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={7} className="py-12 text-center text-[var(--text-muted)]">
                        No MongoDB activity telemetry found for this filter.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="p-4 border-t border-[var(--panel-border)] flex items-center justify-between text-xs text-[var(--text-muted)] font-mono">
              <div>Total Records: {total}</div>
              <div className="flex items-center gap-2">
                <button
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  className="p-1.5 rounded border border-[var(--panel-border)] disabled:opacity-30 cursor-pointer"
                >
                  <ChevronLeft className="w-3.5 h-3.5" />
                </button>
                <span>Page {page} of {totalPages}</span>
                <button
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => p + 1)}
                  className="p-1.5 rounded border border-[var(--panel-border)] disabled:opacity-30 cursor-pointer"
                >
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: CHRONOLOGICAL ACTIVITY TIMELINE */}
        {activeTab === "timeline" && (
          <div className="space-y-4">
            {/* Timeline Filter Header */}
            <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-4 shadow-xl flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
              <div>
                <h3 className="text-sm font-bold uppercase tracking-wider text-[var(--foreground)] flex items-center gap-2">
                  <Clock className="w-4 h-4 text-[#00E5FF]" />
                  <span>Chronological Activity Timeline</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-[#00E5FF] border border-[#00E5FF]/40">
                    {timelineTotal} Events
                  </span>
                </h3>
                <p className="text-xs text-[var(--text-muted)] mt-0.5">
                  Real-time chronological telemetry event stream with behavioral anomaly detection
                </p>
              </div>

              {/* Interactive Timeline Filter Controls */}
              <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
                {/* Time Range Selector */}
                <div className="flex items-center gap-1 bg-[var(--background)] border border-[var(--panel-border)] p-1 rounded-lg text-xs font-mono">
                  {(["24h", "7d", "30d", "all"] as const).map((r) => (
                    <button
                      key={r}
                      onClick={() => setTimelineRange(r)}
                      className={`px-2.5 py-1 rounded transition cursor-pointer text-xs font-semibold ${
                        timelineRange === r
                          ? "bg-[#00A8FF] text-[#050B14] font-bold shadow-[0_0_10px_rgba(0,168,255,0.3)]"
                          : "text-[var(--text-muted)] hover:text-[var(--foreground)]"
                      }`}
                    >
                      {r.toUpperCase()}
                    </button>
                  ))}
                </div>

                {/* Employee Filter */}
                <select
                  value={timelineEmpFilter}
                  onChange={(e) => setTimelineEmpFilter(e.target.value)}
                  className="bg-[var(--background)] border border-[var(--panel-border)] focus:border-[#00A8FF] rounded-lg px-3 py-1.5 text-xs text-[var(--foreground)] font-mono font-medium"
                >
                  {EMPLOYEE_OPTIONS.map((emp) => (
                    <option key={emp.id} value={emp.id}>
                      {emp.label}
                    </option>
                  ))}
                </select>

                {/* Event Type Filter */}
                <select
                  value={timelineTypeFilter}
                  onChange={(e) => setTimelineTypeFilter(e.target.value)}
                  className="bg-[var(--background)] border border-[var(--panel-border)] focus:border-[#00A8FF] rounded-lg px-3 py-1.5 text-xs text-[var(--foreground)] font-mono font-medium"
                >
                  {EVENT_TYPE_OPTIONS.map((et) => (
                    <option key={et} value={et}>
                      {et === "ALL" ? "All Event Types" : et}
                    </option>
                  ))}
                </select>

                <button
                  onClick={fetchTimeline}
                  className="p-1.5 rounded-lg bg-[var(--background)] border border-[var(--panel-border)] text-[var(--text-muted)] hover:text-[#00E5FF] transition cursor-pointer"
                  title="Refresh Timeline"
                >
                  <RefreshCw className={`w-4 h-4 ${timelineLoading ? "animate-spin text-[#00E5FF]" : ""}`} />
                </button>
              </div>
            </div>

            {/* Timeline Stream Container */}
            {timelineLoading ? (
              <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-16 text-center text-[var(--text-muted)]">
                <Loader2 className="w-8 h-8 animate-spin text-[#00E5FF] mx-auto mb-3" />
                <p className="text-xs font-semibold uppercase tracking-wider text-[var(--foreground)]">Loading activity timeline...</p>
                <p className="text-[11px] text-[var(--text-muted)] mt-1">Retrieving chronological telemetry from MongoDB ({timelineRange.toUpperCase()})...</p>
              </div>
            ) : timelineError ? (
              <div className="bg-rose-950/20 border border-rose-500/40 rounded-xl p-6 text-center space-y-3">
                <AlertTriangle className="w-8 h-8 text-rose-400 mx-auto" />
                <div className="text-sm font-bold text-rose-300">Unable to load activity timeline.</div>
                <p className="text-xs text-[var(--text-muted)]">{timelineError}</p>
                <button
                  onClick={fetchTimeline}
                  className="px-4 py-2 bg-rose-900/60 hover:bg-rose-800 text-rose-100 font-bold text-xs rounded-lg transition cursor-pointer border border-rose-500/50"
                >
                  Retry Timeline Load
                </button>
              </div>
            ) : timelineEvents.length === 0 ? (
              <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-16 text-center text-[var(--text-muted)] space-y-2">
                <Clock className="w-8 h-8 text-[var(--text-muted)] opacity-50 mx-auto" />
                <div className="text-xs font-semibold text-[var(--foreground)]">No telemetry recorded for the selected period.</div>
                <p className="text-[11px] text-[var(--text-muted)]">Try selecting a broader time window (e.g. 7D or 30D) or adjusting the subject filter.</p>
              </div>
            ) : (
              <div className="relative pl-6 sm:pl-8 space-y-4 before:absolute before:left-3 sm:before:left-4 before:top-3 before:bottom-3 before:w-0.5 before:bg-gradient-to-b before:from-[#00E5FF] before:via-[#00A8FF]/40 before:to-[var(--panel-border)]">
                {timelineEvents.map((event, idx) => {
                  const isAnomalous = event.is_anomalous || event.is_suspicious || event.risk_weight >= 35;
                  const eventDate = new Date(event.timestamp);

                  return (
                    <div
                      key={event.id || idx}
                      className={`relative bg-[var(--panel)] border rounded-xl p-4 sm:p-5 shadow-xl transition hover:border-[#00A8FF]/60 cursor-pointer ${
                        isAnomalous
                          ? "border-[#00E5FF]/40 bg-gradient-to-r from-cyan-950/30 to-[var(--panel)]"
                          : "border-[var(--panel-border)]"
                      }`}
                      onClick={() => setSelectedActivity(event)}
                    >
                      {/* Timeline Node Icon Indicator */}
                      <div
                        className={`absolute -left-6 sm:-left-8 top-5 w-5 h-5 rounded-full border-2 flex items-center justify-center text-[9px] font-bold ${
                          event.severity === "CRITICAL"
                            ? "bg-rose-950 border-rose-500 text-rose-300 shadow-[0_0_10px_rgba(244,63,94,0.5)]"
                            : event.severity === "HIGH"
                            ? "bg-amber-950 border-amber-500 text-amber-300 shadow-[0_0_10px_rgba(245,158,11,0.5)]"
                            : isAnomalous
                            ? "bg-cyan-950 border-[#00E5FF] text-[#00E5FF] shadow-[0_0_10px_rgba(0,229,255,0.4)]"
                            : "bg-[var(--background)] border-[#00A8FF]/50 text-[#00A8FF]"
                        }`}
                      >
                        {isAnomalous ? "!" : "•"}
                      </div>

                      {/* Header Row: Time, Event Type, Subject, Severity */}
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-[var(--panel-border)]">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="text-xs font-mono font-bold text-[#00E5FF]">
                            {eventDate.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                          </span>
                          <span className="text-[10px] font-mono text-[var(--text-muted)]">
                            {eventDate.toLocaleDateString([], { month: "short", day: "numeric", year: "numeric" })}
                          </span>
                          <span className="px-2 py-0.5 rounded font-mono font-bold text-[10px] bg-[var(--background)] border border-[var(--panel-border)] text-[var(--foreground)] uppercase">
                            {event.event_type}
                          </span>
                          <span className="px-2 py-0.5 rounded font-mono font-bold text-[10px] bg-[#00A8FF]/15 text-[#00A8FF] border border-[#00A8FF]/30">
                            {event.employee_id}
                          </span>
                          {event.is_test_event && (
                            <span className="px-1.5 py-0.5 rounded font-mono text-[9px] bg-cyan-950/60 text-[#00E5FF] border border-[#00E5FF]/30">
                              SYNTHETIC
                            </span>
                          )}
                        </div>

                        <div className="flex items-center gap-2">
                          {getSeverityBadge(event.severity)}
                          <span className={`px-2 py-0.5 rounded font-mono font-bold text-[10px] ${
                            event.risk_weight >= 40
                              ? "bg-cyan-950 text-[#00E5FF] border border-[#00E5FF]/40"
                              : event.risk_weight >= 20
                              ? "bg-[#00A8FF]/20 text-[#00A8FF]"
                              : "bg-[var(--background)] text-[var(--text-muted)]"
                          }`}>
                            +{event.risk_weight} Risk
                          </span>
                        </div>
                      </div>

                      {/* Body Row: Action, Resource, Node, IP */}
                      <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                        <div>
                          <div className="text-[10px] uppercase font-bold text-[var(--text-muted)]">Action & Resource</div>
                          <div className="font-semibold text-[var(--foreground)] mt-0.5">{event.action}</div>
                          <div className="text-[11px] font-mono text-[#00A8FF] truncate mt-0.5">{event.resource}</div>
                        </div>

                        <div>
                          <div className="text-[10px] uppercase font-bold text-[var(--text-muted)]">Origin & Device Node</div>
                          <div className="font-mono text-xs text-[var(--foreground)] flex items-center gap-1.5 mt-0.5">
                            <Laptop className="w-3.5 h-3.5 text-[var(--text-muted)]" />
                            <span>{event.device}</span>
                          </div>
                          <div className="font-mono text-[11px] text-[var(--text-muted)] flex items-center gap-1.5 mt-0.5">
                            <Globe className="w-3 h-3 opacity-70" />
                            <span>{event.ip_address} ({event.location || "Hyderabad"})</span>
                          </div>
                        </div>
                      </div>

                      {/* Anomaly Callout Box: Why is this suspicious? */}
                      {isAnomalous && (
                        <div className="mt-3 p-2.5 rounded-lg bg-cyan-950/40 border border-[#00E5FF]/40 text-xs space-y-1">
                          <div className="flex items-center gap-1.5 text-[#00E5FF] font-bold text-[11px] uppercase tracking-wider">
                            <AlertTriangle className="w-3.5 h-3.5 text-[#00E5FF]" />
                            <span>Behavioral Anomaly Telemetry Signal</span>
                          </div>
                          <div className="text-[11px] text-[var(--foreground)] leading-relaxed">
                            {event.reason || (event.anomaly_reasons.length > 0 ? event.anomaly_reasons.join(" • ") : "Anomalous activity deviation exceeding standard operational baseline.")}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* TAB 3: 7-DAY x 24-HOUR HEATMAP */}
        {activeTab === "heatmap" && (
          <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-5 shadow-xl space-y-4">
            <div>
              <h3 className="text-sm font-bold uppercase tracking-wider text-[var(--foreground)]">
                7-Day Activity & Off-Hours Heatmap
              </h3>
              <p className="text-xs text-[var(--text-muted)]">
                24-Hour behavior matrix across days of the week. Off-hours (outside 09:00–18:00) with activity are highlighted.
              </p>
            </div>

            <div className="overflow-x-auto">
              <div className="min-w-[700px] space-y-2">
                {/* Hours Header */}
                <div className="grid grid-cols-25 text-[10px] font-mono text-[var(--text-muted)] text-center">
                  <div>Day</div>
                  {Array.from({ length: 24 }).map((_, h) => (
                    <div key={h}>{h}h</div>
                  ))}
                </div>

                {/* Day Rows */}
                {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((dayName, dIdx) => (
                  <div key={dayName} className="grid grid-cols-25 gap-1 items-center">
                    <div className="text-xs font-mono font-bold text-[var(--text-muted)]">{dayName}</div>
                    {Array.from({ length: 24 }).map((_, hour) => {
                      const cell = heatmapCells.find((c) => c.day === dayName && c.hour === hour);
                      const count = cell ? cell.event_count : 0;
                      const hasSuspicious = cell ? cell.suspicious_count > 0 : false;
                      const isOff = hour < 8 || hour >= 19 || dIdx >= 5;

                      let bgClass = "bg-[var(--background)] border-[var(--panel-border)]";
                      if (hasSuspicious) {
                        bgClass = "bg-cyan-500 border-[#00E5FF] shadow-[0_0_8px_rgba(0,229,255,0.4)]";
                      } else if (count > 5) {
                        bgClass = "bg-[#00A8FF] border-[#00E5FF]";
                      } else if (count > 2) {
                        bgClass = "bg-[#00A8FF]/60 border-[#00A8FF]/40";
                      } else if (count > 0) {
                        bgClass = "bg-[#00A8FF]/30 border-[#00A8FF]/20";
                      } else if (isOff) {
                        bgClass = "bg-[var(--background)]/30 border-[var(--panel-border)]/40";
                      }

                      return (
                        <div
                          key={hour}
                          title={`${dayName} ${hour.toString().padStart(2, '0')}:00 — Events: ${count}, Suspicious: ${cell?.suspicious_count || 0}${isOff ? " [Off-Hours]" : ""}`}
                          className={`h-7 rounded border flex items-center justify-center text-[9px] font-mono transition cursor-pointer hover:scale-110 ${bgClass}`}
                        >
                          {count > 0 ? (
                            <span className={count > 5 || hasSuspicious ? "text-[#050B14] font-bold" : "text-[var(--foreground)]"}>
                              {count}
                            </span>
                          ) : null}
                        </div>
                      );
                    })}
                  </div>
                ))}
              </div>
            </div>

            {/* Heatmap Legend */}
            <div className="flex flex-wrap items-center gap-4 pt-3 border-t border-[var(--panel-border)] text-[11px] text-[var(--text-muted)]">
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded bg-[var(--background)] border border-[var(--panel-border)]" />
                <span>No Activity</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded bg-[#00A8FF]/30 border border-[#00A8FF]/20" />
                <span>Low Activity (1-2)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded bg-[#00A8FF] border border-[#00E5FF]" />
                <span>High Activity (3+)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded bg-cyan-500 border border-[#00E5FF]" />
                <span>Suspicious Anomaly Spike</span>
              </div>
            </div>
          </div>
        )}

        {/* Interactive Telemetry Detail Drawer / Modal */}
        {selectedActivity && (
          <div className="fixed inset-0 bg-[#050B14]/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in">
            <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-2xl w-full max-w-2xl max-h-[85vh] overflow-y-auto shadow-2xl p-6 space-y-5">
              <div className="flex items-center justify-between pb-3 border-b border-[var(--panel-border)]">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-[var(--background)] border border-[#00A8FF]/40 flex items-center justify-center text-[#00E5FF]">
                    <Activity className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold uppercase tracking-wider text-[var(--foreground)]">
                      Telemetry Record Inspection
                    </h3>
                    <div className="text-[10px] font-mono text-[var(--text-muted)]">
                      Event ID: {selectedActivity.id}
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => setSelectedActivity(null)}
                  className="p-1.5 rounded-lg text-[var(--text-muted)] hover:text-[#00E5FF] hover:bg-[var(--background)] transition cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Subject & Timing Meta */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="p-3 bg-[var(--background)] border border-[var(--panel-border)] rounded-xl">
                  <div className="text-[10px] font-bold uppercase text-[var(--text-muted)]">Subject</div>
                  <div className="font-mono font-bold text-[#00E5FF] mt-1">{selectedActivity.employee_id}</div>
                </div>
                <div className="p-3 bg-[var(--background)] border border-[var(--panel-border)] rounded-xl">
                  <div className="text-[10px] font-bold uppercase text-[var(--text-muted)]">Event Type</div>
                  <div className="font-mono font-bold text-[var(--foreground)] mt-1">{selectedActivity.event_type}</div>
                </div>
                <div className="p-3 bg-[var(--background)] border border-[var(--panel-border)] rounded-xl">
                  <div className="text-[10px] font-bold uppercase text-[var(--text-muted)]">Risk Weight</div>
                  <div className="font-mono font-bold text-[#00E5FF] mt-1">+{selectedActivity.risk_weight}</div>
                </div>
                <div className="p-3 bg-[var(--background)] border border-[var(--panel-border)] rounded-xl">
                  <div className="text-[10px] font-bold uppercase text-[var(--text-muted)]">Timestamp</div>
                  <div className="font-mono text-[11px] text-[var(--foreground)] mt-1">
                    {new Date(selectedActivity.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </div>
                </div>
              </div>

              {/* Action & Resource Details */}
              <div className="space-y-3 text-xs bg-[var(--background)] border border-[var(--panel-border)] p-4 rounded-xl">
                <div>
                  <div className="text-[10px] font-bold uppercase text-[var(--text-muted)]">Action Performed</div>
                  <div className="font-semibold text-[var(--foreground)] mt-0.5">{selectedActivity.action}</div>
                </div>
                <div>
                  <div className="text-[10px] font-bold uppercase text-[var(--text-muted)]">Target Resource / Endpoint</div>
                  <div className="font-mono text-[#00A8FF] break-all mt-0.5">{selectedActivity.resource}</div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2 border-t border-[var(--panel-border)]">
                  <div>
                    <span className="text-[10px] text-[var(--text-muted)]">Device Node: </span>
                    <span className="font-mono font-semibold">{selectedActivity.device || "N/A"}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-[var(--text-muted)]">IP Address: </span>
                    <span className="font-mono font-semibold">{selectedActivity.ip_address || "N/A"}</span>
                  </div>
                </div>
              </div>

              {/* Anomaly Signal Callouts */}
              {selectedActivity.anomaly_reasons && selectedActivity.anomaly_reasons.length > 0 && (
                <div className="space-y-2 text-xs">
                  <div className="text-[10px] font-bold uppercase text-[#00E5FF] flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5 text-[#00E5FF]" />
                    <span>Behavioral Anomaly Deviation Reasons:</span>
                  </div>
                  <ul className="space-y-1 bg-cyan-950/40 border border-[#00E5FF]/40 rounded-xl p-3">
                    {selectedActivity.anomaly_reasons.map((r, i) => (
                      <li key={i} className="flex items-start gap-2 text-xs text-[var(--foreground)]">
                        <span className="text-[#00E5FF] font-mono">•</span>
                        <span>{r}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Raw Details JSON */}
              <div className="space-y-1.5 text-xs">
                <div className="text-[10px] font-bold uppercase text-[var(--text-muted)]">Raw Telemetry Attributes (MongoDB JSON)</div>
                <pre className="bg-[var(--background)] border border-[var(--panel-border)] p-3 rounded-xl font-mono text-[11px] text-[var(--foreground)] overflow-x-auto max-h-40">
                  {JSON.stringify(selectedActivity.details, null, 2)}
                </pre>
              </div>

              {/* Actions Footer */}
              <div className="flex items-center justify-between pt-3 border-t border-[var(--panel-border)]">
                <Link
                  href={`/investigations?employee_id=${selectedActivity.employee_id}`}
                  className="px-4 py-2 bg-[#00A8FF] hover:bg-[#00E5FF] text-[#050B14] font-bold text-xs rounded-lg transition flex items-center gap-2 shadow-[0_0_10px_rgba(0,168,255,0.3)]"
                >
                  <FileSearch className="w-4 h-4" />
                  <span>Open Investigation Dossier ({selectedActivity.employee_id})</span>
                </Link>

                <button
                  onClick={() => setSelectedActivity(null)}
                  className="px-4 py-2 bg-[var(--background)] hover:bg-[var(--panel-border)] text-[var(--foreground)] font-semibold text-xs rounded-lg transition cursor-pointer"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

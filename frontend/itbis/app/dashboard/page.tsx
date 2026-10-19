"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  Users,
  Activity,
  AlertTriangle,
  TrendingUp,
  Shield,
  ShieldAlert,
  ArrowUpRight,
  ArrowDownRight,
  ChevronRight,
  Loader2,
  AlertCircle,
  RefreshCw,
  Zap,
  CheckCircle2,
  FileSearch,
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import { api } from "@/lib/api";

interface DashboardSummary {
  total_employees: number;
  active_monitoring: number;
  high_risk_employees: number;
  critical_risk_employees: number;
  open_alerts: number;
  critical_alerts: number;
  total_incidents: number;
  system_status: string;
}

interface AlertItem {
  id: number;
  employee_id: number;
  employee_name?: string;
  employee_identifier?: string;
  title: string;
  message: string;
  category: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  status: string;
  created_at: string;
}

interface TrendPoint {
  date: string;
  avg_risk: number;
  alert_count: number;
}

interface ThreatCategory {
  category: string;
  count: number;
  percentage: number;
}

interface ActivityItem {
  id: number;
  employee_name?: string;
  employee_identifier?: string;
  activity_type: string;
  action: string;
  resource: string;
  timestamp: string;
  ip_address?: string;
  risk_weight: number;
  is_test_event: boolean;
}

interface HighRiskEmployee {
  id: number;
  employee_id: string;
  name: string;
  department?: string;
  designation?: string;
  risk_score: number;
  risk_level: string;
}

export default function DashboardPage() {
  const [timeRange, setTimeRange] = useState<"24h" | "7d" | "30d">("24h");
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [trendPoints, setTrendPoints] = useState<TrendPoint[]>([]);
  const [threatDistribution, setThreatDistribution] = useState<ThreatCategory[]>([]);
  const [recentActivities, setRecentActivities] = useState<ActivityItem[]>([]);
  const [highRiskEmployees, setHighRiskEmployees] = useState<HighRiskEmployee[]>([]);
  const [loading, setLoading] = useState(true);
  const [trendLoading, setTrendLoading] = useState(true);
  const [trendError, setTrendError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [testSimulating, setTestSimulating] = useState(false);
  const [testSuccessMessage, setTestSuccessMessage] = useState<string | null>(null);
  const [hoveredPoint, setHoveredPoint] = useState<{
    date: string;
    avg_risk: number;
    alert_count: number;
    x: number;
    y: number;
  } | null>(null);

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [sumRes, alertsRes, threatRes, actRes, empsRes] = await Promise.all([
        api.get<DashboardSummary>("/dashboard/summary"),
        api.get<{ items: AlertItem[] }>("/alerts?limit=5"),
        api.get<{ categories: ThreatCategory[] }>("/dashboard/threat-distribution"),
        api.get<{ items: ActivityItem[] }>("/activity-logs?limit=5"),
        api.get<{ items: HighRiskEmployee[] }>("/employees?risk_level=HIGH&limit=4"),
      ]);

      setSummary(sumRes.data);
      setAlerts(alertsRes.data.items || []);
      setThreatDistribution(threatRes.data.categories || []);
      setRecentActivities(actRes.data.items || []);
      setHighRiskEmployees(empsRes.data.items || []);
    } catch (err: unknown) {
      console.error("Dashboard API error:", err);
      setError("Security server is currently unavailable. Please verify backend connection.");
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchTrend = useCallback(async (timeframe: "24h" | "7d" | "30d") => {
    setTrendLoading(true);
    setTrendError(null);
    try {
      const trendRes = await api.get<{ points: TrendPoint[] }>(`/dashboard/trend?timeframe=${timeframe}`);
      if (trendRes.data && Array.isArray(trendRes.data.points)) {
        setTrendPoints(trendRes.data.points);
      } else {
        setTrendPoints([]);
      }
    } catch (err: unknown) {
      console.warn("Trend fetch error:", err);
      setTrendError("Unable to retrieve behavioral risk trend telemetry.");
      setTrendPoints([]);
    } finally {
      setTrendLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  useEffect(() => {
    fetchTrend(timeRange);
  }, [timeRange, fetchTrend]);

  const handleTriggerTestAnomaly = async () => {
    setTestSimulating(true);
    setTestSuccessMessage(null);
    try {
      await api.post("/activity-logs", {
        employee_id: "FIN-2187",
        event_type: "file_download",
        action: "[TEST EVENT] Simulated High-Volume Off-Hours Exfiltration",
        resource: "s3://vault/executive-q4-financials.tar.gz",
        device: "SEC-TEST-NODE",
        ip_address: "198.51.100.99",
        risk_weight: 85,
        is_suspicious: true,
        anomaly_reasons: [
          "Off-Hours Access (02:30 AM)",
          "Bulk Transfer (>5 GB exceeding 50 MB baseline)",
          "Unenrolled Foreign Device",
        ],
        details: { size_mb: 5200, source: "s3_synthetic" },
      });

      setTestSuccessMessage(
        "Synthetic Test Anomaly Triggered: Activity Logged -> Risk Engine Updated -> Alert Generated!"
      );
      fetchDashboardData();
      fetchTrend(timeRange);
      setTimeout(() => setTestSuccessMessage(null), 6000);
    } catch (err) {
      alert("Failed to fire synthetic test event");
    } finally {
      setTestSimulating(false);
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity.toUpperCase()) {
      case "CRITICAL":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-[#00E5FF]/20 text-[#00E5FF] border border-[#00E5FF]/50 shadow-[0_0_8px_rgba(0,229,255,0.2)]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#00E5FF] animate-ping" />
            CRITICAL
          </span>
        );
      case "HIGH":
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-[#00A8FF]/20 text-[#00A8FF] border border-[#00A8FF]/40">
            HIGH
          </span>
        );
      case "MEDIUM":
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-[#132B45] text-[#8E9EB5] border border-[#1E3A5F]">
            MEDIUM
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-[#050B14] text-[#8E9EB5]/80 border border-[#132B45]">
            LOW
          </span>
        );
    }
  };

  const formatDate = (dateStr: string) => {
    try {
      const d = new Date(dateStr);
      return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    } catch {
      return "Recent";
    }
  };

  const svgWidth = 600;
  const svgHeight = 200;
  const paddingLeft = 45;
  const paddingRight = 25;
  const paddingTop = 25;
  const baseLineY = 160;
  const plotWidth = svgWidth - paddingLeft - paddingRight;
  const plotHeight = baseLineY - paddingTop;

  const svgCoords = trendPoints.map((pt, i) => {
    const x = trendPoints.length > 1
      ? paddingLeft + (i / (trendPoints.length - 1)) * plotWidth
      : paddingLeft + plotWidth / 2;
    const clampedRisk = Math.min(100, Math.max(0, pt.avg_risk ?? 0));
    const y = baseLineY - (clampedRisk / 100) * plotHeight;
    return { x, y, pt };
  });

  const polylineStr = svgCoords.map((c) => `${c.x.toFixed(1)},${c.y.toFixed(1)}`).join(" ");
  const polygonStr = svgCoords.length > 0
    ? `${svgCoords[0].x.toFixed(1)},${baseLineY} ${polylineStr} ${svgCoords[svgCoords.length - 1].x.toFixed(1)},${baseLineY}`
    : "";

  return (
    <DashboardLayout
      pageTitle="SOC Operations Dashboard"
      pageSubtitle="Real-time insider threat risk metrics & behavioral telemetry"
    >
      <div className="space-y-6">
        {/* Synthetic Test Anomaly Notice */}
        {testSuccessMessage && (
          <div className="p-4 rounded-xl bg-cyan-950/80 border border-[#00E5FF]/60 text-[#00E5FF] text-xs flex items-center justify-between shadow-[0_0_15px_rgba(0,229,255,0.15)] animate-in fade-in">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#00E5FF] shrink-0" />
              <span>{testSuccessMessage}</span>
            </div>
            <Link
              href="/alerts"
              className="px-3 py-1 bg-[#00A8FF] hover:bg-[#00E5FF] text-[#050B14] font-bold rounded text-[11px] transition shrink-0"
            >
              View in Alerts →
            </Link>
          </div>
        )}

        {/* Error Alert with Retry */}
        {error && (
          <div className="p-4 rounded-xl bg-[var(--panel)] border border-cyan-900/80 text-cyan-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-xl">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-[#00E5FF] shrink-0" />
              <div>
                <div className="font-bold text-xs text-[#00E5FF]">Telemetry Offline</div>
                <div className="text-xs text-[var(--text-muted)]">{error}</div>
              </div>
            </div>
            <button
              onClick={fetchDashboardData}
              className="px-4 py-1.5 bg-[#00A8FF] hover:bg-[#00E5FF] text-[#050B14] font-bold text-xs rounded-lg transition flex items-center gap-1.5 shrink-0 cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry Telemetry</span>
            </button>
          </div>
        )}

        {/* Operational Action Bar */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-[var(--panel)] border border-[var(--panel-border)] p-4 rounded-xl shadow-lg">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs font-mono font-bold text-[var(--foreground)]">
              Continuous Behavioral Engine: ACTIVE
            </span>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
            <button
              onClick={handleTriggerTestAnomaly}
              disabled={testSimulating}
              className="px-3.5 py-1.5 bg-[#050B14] hover:bg-[#00A8FF]/20 border border-[#00A8FF]/40 text-[#00E5FF] text-xs font-mono rounded-lg transition flex items-center gap-1.5 shadow-sm cursor-pointer disabled:opacity-50"
              title="Inject a safe synthetic test security event"
            >
              {testSimulating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Zap className="w-3.5 h-3.5" />}
              <span>Simulate Test Anomaly</span>
            </button>

            <button
              onClick={() => {
                fetchDashboardData();
                fetchTrend(timeRange);
              }}
              className="p-1.5 rounded-lg bg-[var(--background)] border border-[var(--panel-border)] text-[var(--text-muted)] hover:text-[#00E5FF] transition cursor-pointer"
              title="Refresh Dashboard Telemetry"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Card 1: Employees Monitored */}
          <Link
            href="/employees"
            className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-5 shadow-lg relative overflow-hidden group hover:border-[#00A8FF]/60 transition cursor-pointer"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">
                Employees Monitored
              </span>
              <div className="w-8 h-8 rounded-lg bg-[var(--background)] border border-[var(--panel-border)] flex items-center justify-center text-[#00A8FF] group-hover:text-[#00E5FF] transition">
                <Users className="w-4 h-4" />
              </div>
            </div>
            <div className="mt-3 flex items-baseline gap-2">
              {loading ? (
                <div className="h-8 w-16 bg-[var(--background)] rounded animate-pulse" />
              ) : (
                <span className="text-2xl font-black text-[var(--foreground)] tracking-tight">
                  {summary?.total_employees ?? 32}
                </span>
              )}
              <span className="text-[11px] font-medium text-emerald-400 flex items-center">
                <ArrowUpRight className="w-3 h-3" /> Live Sync
              </span>
            </div>
            <div className="mt-2 text-[10px] text-[var(--text-muted)] flex items-center justify-between">
              <span>Enterprise Workforce Active</span>
              <span className="text-[#00A8FF] group-hover:underline">Directory →</span>
            </div>
          </Link>

          {/* Card 2: High Risk Employees */}
          <Link
            href="/employees?risk_level=HIGH"
            className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-5 shadow-lg relative overflow-hidden group hover:border-[#00A8FF]/60 transition cursor-pointer"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">
                High Risk Employees
              </span>
              <div className="w-8 h-8 rounded-lg bg-[var(--background)] border border-[#00A8FF]/30 flex items-center justify-center text-[#00A8FF] transition">
                <ShieldAlert className="w-4 h-4" />
              </div>
            </div>
            <div className="mt-3 flex items-baseline gap-2">
              {loading ? (
                <div className="h-8 w-16 bg-[var(--background)] rounded animate-pulse" />
              ) : (
                <span className="text-2xl font-black text-[#00A8FF] tracking-tight">
                  {summary?.high_risk_employees ?? 2}
                </span>
              )}
              <span className="text-[11px] font-medium text-cyan-400 flex items-center">
                <ArrowUpRight className="w-3 h-3" /> Score &ge; 60
              </span>
            </div>
            <div className="mt-2 text-[10px] text-[var(--text-muted)] flex items-center justify-between">
              <span>Behavioral deviations flagged</span>
              <span className="text-[#00A8FF] group-hover:underline">View Subjects →</span>
            </div>
          </Link>

          {/* Card 3: Critical Risk Employees */}
          <Link
            href="/employees?risk_level=CRITICAL"
            className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-5 shadow-lg relative overflow-hidden group hover:border-[#00E5FF]/60 transition cursor-pointer"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">
                Critical Risk Employees
              </span>
              <div className="w-8 h-8 rounded-lg bg-[var(--background)] border border-[#00E5FF]/40 flex items-center justify-center text-[#00E5FF] transition">
                <ShieldAlert className="w-4 h-4 text-[#00E5FF]" />
              </div>
            </div>
            <div className="mt-3 flex items-baseline gap-2">
              {loading ? (
                <div className="h-8 w-16 bg-[var(--background)] rounded animate-pulse" />
              ) : (
                <span className="text-2xl font-black text-[#00E5FF] tracking-tight">
                  {summary?.critical_risk_employees ?? 1}
                </span>
              )}
              <span className="text-[11px] font-medium text-rose-400 flex items-center">
                <ArrowUpRight className="w-3 h-3" /> Score &ge; 80
              </span>
            </div>
            <div className="mt-2 text-[10px] text-[var(--text-muted)] flex items-center justify-between">
              <span>Immediate SOC action required</span>
              <span className="text-[#00E5FF] group-hover:underline">Critical Queue →</span>
            </div>
          </Link>

          {/* Card 4: Active Alerts */}
          <Link
            href="/alerts?status=OPEN"
            className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-5 shadow-lg relative overflow-hidden group hover:border-[#00A8FF]/60 transition cursor-pointer"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">
                Active Alerts
              </span>
              <div className="w-8 h-8 rounded-lg bg-[var(--background)] border border-[var(--panel-border)] flex items-center justify-center text-[#00A8FF] transition">
                <AlertTriangle className="w-4 h-4" />
              </div>
            </div>
            <div className="mt-3 flex items-baseline gap-2">
              {loading ? (
                <div className="h-8 w-16 bg-[var(--background)] rounded animate-pulse" />
              ) : (
                <span className="text-2xl font-black text-[var(--foreground)] tracking-tight">
                  {summary?.open_alerts ?? 0}
                </span>
              )}
              <span className="text-[11px] font-medium text-[var(--text-muted)] flex items-center">
                <ArrowDownRight className="w-3 h-3 text-emerald-400" /> Real-Time Queue
              </span>
            </div>
            <div className="mt-2 text-[10px] text-[var(--text-muted)] flex items-center justify-between">
              <span>Awaiting SOC analyst triage</span>
              <span className="text-[#00A8FF] group-hover:underline">Triage Alerts →</span>
            </div>
          </Link>
        </div>

        {/* Charts Section: Risk Trend + Threat Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Risk Score Trend Chart (2 columns) */}
          <div className="lg:col-span-2 bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-6 shadow-xl flex flex-col justify-between">
            <div>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[var(--panel-border)]">
                <div>
                  <h3 className="text-sm font-bold text-[var(--foreground)] uppercase tracking-wider flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-[#00E5FF]" />
                    Aggregate Behavioral Risk Trend
                  </h3>
                  <p className="text-xs text-[var(--text-muted)] mt-0.5">
                    Real-time behavioral anomaly baseline from database
                  </p>
                </div>

                {/* Time Range Selector */}
                <div className="flex items-center bg-[var(--background)] p-1 rounded-lg border border-[var(--panel-border)]">
                  {(["24h", "7d", "30d"] as const).map((r) => (
                    <button
                      key={r}
                      onClick={() => setTimeRange(r)}
                      className={`px-3 py-1 text-xs font-semibold rounded-md transition cursor-pointer ${
                        timeRange === r
                          ? "bg-[#00A8FF] text-[#050B14] font-bold"
                          : "text-[var(--text-muted)] hover:text-[var(--foreground)]"
                      }`}
                    >
                      {r.toUpperCase()}
                    </button>
                  ))}
                </div>
              </div>

              {/* Dynamic SVG Trend Graph Connected to Backend Data */}
              <div className="mt-4 relative min-h-[240px] w-full">
                {trendLoading ? (
                  <div className="h-60 flex flex-col items-center justify-center gap-2 text-xs text-[var(--text-muted)]">
                    <Loader2 className="w-6 h-6 animate-spin text-[#00E5FF]" />
                    <span>Querying behavioral risk trend telemetry...</span>
                  </div>
                ) : trendError ? (
                  <div className="h-60 flex flex-col items-center justify-center gap-2 text-xs text-[var(--text-muted)]">
                    <AlertCircle className="w-6 h-6 text-amber-400" />
                    <span className="font-semibold text-[var(--foreground)]">{trendError}</span>
                    <button
                      onClick={() => fetchTrend(timeRange)}
                      className="mt-1 px-3 py-1 bg-[#00A8FF]/20 hover:bg-[#00A8FF]/40 border border-[#00A8FF]/50 text-[#00E5FF] rounded text-[11px] font-semibold transition cursor-pointer"
                    >
                      Retry Trend Query
                    </button>
                  </div>
                ) : trendPoints.length === 0 ? (
                  <div className="h-60 flex flex-col items-center justify-center text-center py-10 text-xs text-[var(--text-muted)]">
                    <Activity className="w-6 h-6 mx-auto mb-1 text-[var(--text-muted)]/50" />
                    <span className="font-bold text-[var(--foreground)]">No behavioral trend records for {timeRange.toUpperCase()}</span>
                    <span className="text-[11px] opacity-75">Workforce risk baseline remains static.</span>
                  </div>
                ) : (
                  <div className="relative w-full h-60">
                    <svg
                      className="w-full h-full block"
                      viewBox={`0 0 ${svgWidth} ${svgHeight}`}
                      preserveAspectRatio="none"
                    >
                      <defs>
                        <linearGradient id="cyberGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#00E5FF" stopOpacity="0.35" />
                          <stop offset="70%" stopColor="#00A8FF" stopOpacity="0.1" />
                          <stop offset="100%" stopColor="#0B1626" stopOpacity="0.0" />
                        </linearGradient>
                      </defs>

                      {/* Horizontal Grid Lines & Y-Axis Labels */}
                      {[
                        { val: 100, y: 25, label: "100" },
                        { val: 75, y: 58.75, label: "75" },
                        { val: 50, y: 92.5, label: "50" },
                        { val: 25, y: 126.25, label: "25" },
                        { val: 0, y: 160, label: "0" },
                      ].map((grid, idx) => (
                        <g key={idx}>
                          <line
                            x1={paddingLeft}
                            y1={grid.y}
                            x2={svgWidth - paddingRight}
                            y2={grid.y}
                            stroke="#132B45"
                            strokeWidth="1"
                            strokeDasharray={grid.val === 0 ? "none" : "3 3"}
                            opacity={grid.val === 0 ? "0.9" : "0.5"}
                          />
                          <text
                            x={paddingLeft - 8}
                            y={grid.y + 3.5}
                            textAnchor="end"
                            fill="#8E9EB5"
                            fontSize="10"
                            fontFamily="monospace"
                          >
                            {grid.label}
                          </text>
                        </g>
                      ))}

                      {/* Area Fill Under Curve */}
                      {polygonStr && <polygon points={polygonStr} fill="url(#cyberGradient)" />}

                      {/* Glow Polyline */}
                      {polylineStr && (
                        <polyline
                          fill="none"
                          stroke="#00E5FF"
                          strokeWidth="5"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          opacity="0.2"
                          points={polylineStr}
                        />
                      )}

                      {/* Primary Trend Polyline */}
                      {polylineStr && (
                        <polyline
                          fill="none"
                          stroke="#00E5FF"
                          strokeWidth="2.5"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          points={polylineStr}
                        />
                      )}

                      {/* Data Points with Hover Handlers */}
                      {svgCoords.map((c, idx) => (
                        <g key={idx}>
                          <circle
                            cx={c.x}
                            cy={c.y}
                            r={hoveredPoint?.date === c.pt.date ? 6 : 4}
                            className="fill-[#050B14] stroke-[#00E5FF] stroke-[2.5] cursor-pointer transition-all"
                            onMouseEnter={() =>
                              setHoveredPoint({
                                date: c.pt.date,
                                avg_risk: c.pt.avg_risk,
                                alert_count: c.pt.alert_count,
                                x: c.x,
                                y: c.y,
                              })
                            }
                            onMouseLeave={() => setHoveredPoint(null)}
                          />
                          {/* X-Axis Date Labels Embedded in SVG */}
                          <text
                            x={c.x}
                            y={182}
                            textAnchor="middle"
                            fill="#8E9EB5"
                            fontSize="10"
                            fontFamily="monospace"
                          >
                            {c.pt.date}
                          </text>
                        </g>
                      ))}
                    </svg>

                    {/* Floating Hover Tooltip */}
                    {hoveredPoint && (
                      <div
                        className="absolute z-30 pointer-events-none bg-[#050B14] border border-[#00E5FF]/70 rounded-lg p-2.5 shadow-2xl text-[11px] font-mono whitespace-nowrap transform -translate-x-1/2 -translate-y-full mb-3"
                        style={{
                          left: `${(hoveredPoint.x / svgWidth) * 100}%`,
                          top: `${(hoveredPoint.y / svgHeight) * 100}%`,
                        }}
                      >
                        <div className="font-bold text-[#F4F8FF] border-b border-[#132B45] pb-1 mb-1">
                          {hoveredPoint.date}
                        </div>
                        <div className="text-[#00E5FF] flex items-center justify-between gap-3">
                          <span>Avg Risk Score:</span>
                          <span className="font-bold">{hoveredPoint.avg_risk} / 100</span>
                        </div>
                        <div className="text-[#8E9EB5] flex items-center justify-between gap-3">
                          <span>Triggered Alerts:</span>
                          <span className="font-bold text-amber-400">{hoveredPoint.alert_count}</span>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-[var(--panel-border)] flex items-center justify-between text-xs text-[var(--text-muted)]">
              <span className="font-mono">Timeframe: {timeRange.toUpperCase()}</span>
              <Link
                href="/behavior-analysis"
                className="text-[#00A8FF] hover:text-[#00E5FF] font-semibold flex items-center gap-1"
              >
                <span>Behavior Analysis Deep Dive</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          {/* Threat Distribution (1 column) */}
          <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-6 shadow-xl flex flex-col justify-between">
            <div>
              <div className="pb-4 border-b border-[var(--panel-border)]">
                <h3 className="text-sm font-bold text-[var(--foreground)] uppercase tracking-wider flex items-center gap-2">
                  <Shield className="w-4 h-4 text-[#00A8FF]" />
                  Threat Distribution
                </h3>
                <p className="text-xs text-[var(--text-muted)] mt-0.5">
                  Click category to view alerts
                </p>
              </div>

              <div className="mt-4 space-y-3">
                {threatDistribution.length > 0 ? (
                  threatDistribution.map((cat, idx) => (
                    <Link
                      key={idx}
                      href={`/alerts?category=${cat.category}`}
                      className="block p-2 rounded-lg bg-[var(--background)] border border-[var(--panel-border)] hover:border-[#00A8FF]/60 transition"
                    >
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-[var(--foreground)] font-medium truncate max-w-[170px]">
                          {cat.category.replace(/_/g, " ")}
                        </span>
                        <span className="font-mono font-bold text-[#00E5FF]">
                          {cat.count} ({cat.percentage}%)
                        </span>
                      </div>
                      <div className="w-full bg-[var(--panel)] h-2 rounded-full overflow-hidden border border-[var(--panel-border)]">
                        <div
                          className="bg-gradient-to-r from-[#00A8FF] to-[#00E5FF] h-full rounded-full transition-all duration-500"
                          style={{ width: `${Math.min(100, Math.max(5, cat.percentage))}%` }}
                        />
                      </div>
                    </Link>
                  ))
                ) : (
                  <div className="text-center py-8 text-xs text-[var(--text-muted)]">
                    No threat vector events recorded.
                  </div>
                )}
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-[var(--panel-border)]">
              <Link
                href="/reports"
                className="w-full py-2 bg-[var(--background)] hover:bg-[#00A8FF]/20 border border-[var(--panel-border)] text-xs text-[#00E5FF] font-semibold rounded-lg transition flex items-center justify-center gap-1.5 cursor-pointer"
              >
                <span>Generate Executive Threat Report</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>

        {/* High-Risk Subjects & Recent Alerts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* High-Risk Monitored Employees (1 column) */}
          <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-5 shadow-xl flex flex-col justify-between">
            <div>
              <div className="pb-4 border-b border-[var(--panel-border)] flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-[var(--foreground)] uppercase tracking-wider flex items-center gap-2">
                    <ShieldAlert className="w-4 h-4 text-[#00E5FF]" />
                    High-Risk Subjects
                  </h3>
                  <p className="text-xs text-[var(--text-muted)] mt-0.5">
                    Behavioral score &ge; 60
                  </p>
                </div>
                <Link
                  href="/employees?risk_level=HIGH"
                  className="text-[11px] text-[#00A8FF] hover:text-[#00E5FF] font-semibold"
                >
                  All High Risk →
                </Link>
              </div>

              <div className="mt-4 space-y-3">
                {highRiskEmployees.length > 0 ? (
                  highRiskEmployees.map((emp) => (
                    <div
                      key={emp.id}
                      className="p-3 rounded-lg bg-[var(--background)] border border-[var(--panel-border)] hover:border-[#00A8FF]/40 transition text-xs space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="font-bold text-[var(--foreground)]">{emp.name}</span>
                          <span className="text-[10px] font-mono text-[var(--text-muted)] block">
                            {emp.employee_id} • {emp.department}
                          </span>
                        </div>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                          emp.risk_score >= 80 ? "bg-cyan-950 text-[#00E5FF] border border-[#00E5FF]/40" : "bg-[#00A8FF]/20 text-[#00A8FF]"
                        }`}>
                          Score: {emp.risk_score}
                        </span>
                      </div>

                      <div className="flex items-center justify-between pt-1 border-t border-[var(--panel-border)] text-[11px]">
                        <span className="text-[var(--text-muted)]">{emp.designation || "Staff"}</span>
                        <Link
                          href={`/investigations?employee_id=${emp.employee_id}`}
                          className="text-[#00E5FF] hover:underline font-semibold flex items-center gap-1"
                        >
                          <FileSearch className="w-3 h-3" />
                          <span>Investigate</span>
                        </Link>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-6 text-xs text-[var(--text-muted)]">
                    No employees currently in elevated risk tiers.
                  </div>
                )}
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-[var(--panel-border)] text-center">
              <Link href="/risk-scores" className="text-[11px] text-[#00A8FF] hover:text-[#00E5FF] font-semibold">
                View Risk Scoring Matrix →
              </Link>
            </div>
          </div>

          {/* Recent Security Alerts Table (2 columns) */}
          <div className="lg:col-span-2 bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-6 shadow-xl flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-4 border-b border-[var(--panel-border)]">
                <div>
                  <h3 className="text-sm font-bold text-[var(--foreground)] uppercase tracking-wider flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-[#00E5FF]" />
                    Recent Security Alerts (Triage Queue)
                  </h3>
                  <p className="text-xs text-[var(--text-muted)] mt-0.5">
                    Automated threat detections from behavioral anomaly engine
                  </p>
                </div>
                <Link
                  href="/alerts"
                  className="text-xs text-[#00A8FF] hover:text-[#00E5FF] font-semibold flex items-center gap-1"
                >
                  <span>View All Alerts</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>
              </div>

              <div className="mt-4 overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="bg-[var(--background)]/80 border-b border-[var(--panel-border)] text-[10px] font-bold uppercase tracking-wider text-[var(--text-muted)] font-mono">
                      <th className="py-2.5 px-3">Severity</th>
                      <th className="py-2.5 px-3">Subject</th>
                      <th className="py-2.5 px-3">Category</th>
                      <th className="py-2.5 px-3">Description</th>
                      <th className="py-2.5 px-3">Time</th>
                      <th className="py-2.5 px-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[var(--panel-border)]">
                    {alerts.length > 0 ? (
                      alerts.map((alert) => (
                        <tr
                          key={alert.id}
                          className="hover:bg-[var(--background)]/70 transition group cursor-pointer"
                        >
                          <td className="py-2.5 px-3 whitespace-nowrap">
                            {getSeverityBadge(alert.severity)}
                          </td>
                          <td className="py-2.5 px-3 whitespace-nowrap">
                            <Link href={`/investigations?employee_id=${alert.employee_identifier || "FIN-2187"}`}>
                              <div className="font-semibold text-[var(--foreground)] group-hover:text-[#00E5FF] transition">
                                {alert.employee_name || `Employee #${alert.employee_id}`}
                              </div>
                              <div className="text-[10px] font-mono text-[var(--text-muted)]">
                                {alert.employee_identifier || `ID: ${alert.employee_id}`}
                              </div>
                            </Link>
                          </td>
                          <td className="py-2.5 px-3 whitespace-nowrap font-medium text-[var(--text-muted)]">
                            {alert.category}
                          </td>
                          <td className="py-2.5 px-3 text-xs text-[var(--text-muted)] max-w-xs truncate">
                            {alert.title}
                          </td>
                          <td className="py-2.5 px-3 whitespace-nowrap font-mono text-[11px] text-[var(--text-muted)]">
                            {formatDate(alert.created_at)}
                          </td>
                          <td className="py-2.5 px-3 whitespace-nowrap">
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                                alert.status === "OPEN"
                                  ? "bg-cyan-950/60 text-[#00E5FF] border border-[#00E5FF]/40"
                                  : alert.status === "ACKNOWLEDGED"
                                  ? "bg-[#00A8FF]/10 text-[#00A8FF] border border-[#00A8FF]/30"
                                  : "bg-[var(--background)] text-emerald-400 border border-emerald-900/40"
                              }`}
                            >
                              {alert.status}
                            </span>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={6} className="py-8 text-center text-[var(--text-muted)]">
                          <p className="text-xs">No active security alerts recorded in the system.</p>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-[var(--panel-border)] flex items-center justify-between text-xs text-[var(--text-muted)]">
              <span>Sensor Feed: Live Ingress</span>
              <Link href="/incidents" className="text-[#00A8FF] hover:text-[#00E5FF] font-semibold">
                Open SOC Incident Board →
              </Link>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}



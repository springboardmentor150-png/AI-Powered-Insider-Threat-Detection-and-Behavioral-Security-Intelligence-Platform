"use client";

import React from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import { Line, Bar, Doughnut } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface DashboardChartsProps {
  socData?: any;
  analystData?: any;
  managerData?: any;
}

export function DashboardCharts({ socData, analystData, managerData }: DashboardChartsProps) {
  // 1. Anomalies Over Time (Line Chart) — Day 29 Spec: Line color #7a1f2b
  const anomalyTimeline = socData?.anomalies_over_time || analystData?.timeline || [
    { date: "Day -6", count: 2 },
    { date: "Day -5", count: 4 },
    { date: "Day -4", count: 3 },
    { date: "Day -3", count: 7 },
    { date: "Day -2", count: 5 },
    { date: "Day -1", count: 9 },
    { date: "Today", count: 12 },
  ];

  const lineLabels = Array.isArray(anomalyTimeline)
    ? anomalyTimeline.map((item: any) => item._id || item.date || item.label || "Day")
    : ["Day -6", "Day -5", "Day -4", "Day -3", "Day -2", "Day -1", "Today"];

  const lineCounts = Array.isArray(anomalyTimeline)
    ? anomalyTimeline.map((item: any) => item.count ?? item.value ?? 0)
    : [2, 4, 3, 7, 5, 9, 12];

  const lineChartData = {
    labels: lineLabels,
    datasets: [
      {
        label: "Anomalies Over Time",
        data: lineCounts,
        borderColor: "#7a1f2b",
        backgroundColor: "rgba(122, 31, 43, 0.25)",
        fill: true,
        tension: 0.35,
        pointBackgroundColor: "#7a1f2b",
        pointBorderColor: "#fff",
        pointHoverRadius: 6,
      },
    ],
  };

  const lineOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: "#0f172a",
        borderColor: "#334155",
        borderWidth: 1,
        titleColor: "#f8fafc",
        bodyColor: "#94a3b8",
      },
    },
    scales: {
      x: {
        grid: { color: "rgba(51, 65, 85, 0.3)" },
        ticks: { color: "#94a3b8", font: { size: 10 } },
      },
      y: {
        grid: { color: "rgba(51, 65, 85, 0.3)" },
        ticks: { color: "#94a3b8", font: { size: 10 }, stepSize: 2 },
        beginAtZero: true,
      },
    },
  };

  // 2. Alerts by Severity (Bar Chart) — Day 29 Spec: #9ca3af, #60a5fa, #fbbf24, #f97316, #dc2626
  const severityBreakdown = socData?.alerts_by_severity || {
    info: 2,
    low: 5,
    medium: 8,
    high: 4,
    critical: 3,
  };

  const barChartData = {
    labels: ["Info", "Low", "Medium", "High", "Critical"],
    datasets: [
      {
        label: "Alert Count",
        data: [
          severityBreakdown.info || 0,
          severityBreakdown.low || 0,
          severityBreakdown.medium || 0,
          severityBreakdown.high || 0,
          severityBreakdown.critical || 0,
        ],
        backgroundColor: ["#9ca3af", "#60a5fa", "#fbbf24", "#f97316", "#dc2626"],
        borderRadius: 6,
      },
    ],
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "#0f172a",
        borderColor: "#334155",
        borderWidth: 1,
        titleColor: "#f8fafc",
        bodyColor: "#94a3b8",
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: "#94a3b8", font: { size: 10 } },
      },
      y: {
        grid: { color: "rgba(51, 65, 85, 0.3)" },
        ticks: { color: "#94a3b8", font: { size: 10 }, stepSize: 2 },
        beginAtZero: true,
      },
    },
  };

  // 3. Risk Distribution Donut Chart
  const distribution = managerData?.distribution || {
    critical: 1,
    high: 2,
    medium: 3,
    low: 4,
  };

  const donutData = {
    labels: ["Critical (>=75)", "High (>=50)", "Medium (>=25)", "Low (<25)"],
    datasets: [
      {
        data: [
          distribution.critical || 0,
          distribution.high || 0,
          distribution.medium || 0,
          distribution.low || 0,
        ],
        backgroundColor: ["#dc2626", "#f97316", "#fbbf24", "#10b981"],
        borderWidth: 2,
        borderColor: "#0f172a",
      },
    ],
  };

  const donutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "bottom" as const,
        labels: {
          color: "#94a3b8",
          font: { size: 10 },
          boxWidth: 12,
        },
      },
    },
    cutout: "70%",
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Anomalies Over Time */}
      <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold text-white font-mono uppercase tracking-wider flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#7a1f2b]" />
            Anomalies Over Time (SOC)
          </h3>
          <span className="text-[10px] text-slate-400 font-mono">Day 29 Spec (#7a1f2b)</span>
        </div>
        <div className="h-52 w-full">
          <Line data={lineChartData} options={lineOptions} />
        </div>
      </div>

      {/* Alerts by Severity */}
      <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold text-white font-mono uppercase tracking-wider flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400" />
            Alerts by Severity (SOC)
          </h3>
          <span className="text-[10px] text-slate-400 font-mono">5-Tier Severity</span>
        </div>
        <div className="h-52 w-full">
          <Bar data={barChartData} options={barOptions} />
        </div>
      </div>

      {/* Risk Distribution Donut */}
      <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold text-white font-mono uppercase tracking-wider flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
            Posture Distribution (Manager)
          </h3>
          <span className="text-[10px] text-slate-400 font-mono">Composite Model</span>
        </div>
        <div className="h-52 w-full">
          <Doughnut data={donutData} options={donutOptions} />
        </div>
      </div>
    </div>
  );
}

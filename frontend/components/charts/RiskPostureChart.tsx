"use client";

import { useMemo } from "react";
import { Doughnut } from "react-chartjs-2";
import "@/components/charts/ChartSetup";

interface RiskDistribution {
  low: number;
  medium: number;
  high: number;
  critical: number;
}

interface RiskPostureChartProps {
  distribution?: RiskDistribution;
  totalEmployees?: number;
}

export default function RiskPostureChart({
  distribution = { low: 0, medium: 0, high: 0, critical: 0 },
  totalEmployees = 0,
}: RiskPostureChartProps) {
  const chartData = useMemo(() => {
    return {
      labels: ["Critical Risk", "High Risk", "Medium Risk", "Low Risk"],
      datasets: [
        {
          data: [
            distribution?.critical || 0,
            distribution?.high || 0,
            distribution?.medium || 0,
            distribution?.low || 0,
          ],
          backgroundColor: [
            "rgba(239, 68, 68, 0.9)", // Critical
            "rgba(249, 115, 22, 0.85)", // High
            "rgba(245, 158, 11, 0.85)", // Medium
            "rgba(16, 185, 129, 0.85)", // Low
          ],
          borderColor: ["#ef4444", "#f97316", "#f59e0b", "#10b981"],
          borderWidth: 2,
          hoverOffset: 6,
        },
      ],
    };
  }, [distribution]);

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: "68%",
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: "rgba(15, 23, 42, 0.95)",
        titleColor: "#f8fafc",
        bodyColor: "#94a3b8",
        borderColor: "rgba(255, 255, 255, 0.1)",
        borderWidth: 1,
        padding: 10,
        cornerRadius: 8,
        callbacks: {
          label: (context: any) => {
            const val = context.parsed;
            const pct =
              totalEmployees > 0 ? Math.round((val / totalEmployees) * 100) : 0;
            return ` ${context.label}: ${val} (${pct}%)`;
          },
        },
      },
    },
  };

  return (
    <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-center sm:justify-around">
      <div className="relative h-44 w-44">
        <Doughnut data={chartData} options={options} />
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-2xl font-black tracking-tight text-[var(--foreground)]">
            {totalEmployees}
          </span>
          <span className="text-[10px] uppercase font-semibold text-[var(--muted)]">
            Employees
          </span>
        </div>
      </div>

      <div className="flex flex-col gap-2.5 text-xs">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-red-500 shadow-sm shadow-red-500/50" />
            <span className="text-[var(--foreground)] font-medium">Critical Risk</span>
          </div>
          <span className="font-bold text-red-400">{distribution?.critical || 0}</span>
        </div>

        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-orange-500 shadow-sm shadow-orange-500/50" />
            <span className="text-[var(--foreground)] font-medium">High Risk</span>
          </div>
          <span className="font-bold text-orange-400">{distribution?.high || 0}</span>
        </div>

        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-amber-500 shadow-sm shadow-amber-500/50" />
            <span className="text-[var(--foreground)] font-medium">Medium Risk</span>
          </div>
          <span className="font-bold text-amber-400">{distribution?.medium || 0}</span>
        </div>

        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 shadow-sm shadow-emerald-500/50" />
            <span className="text-[var(--foreground)] font-medium">Low Risk</span>
          </div>
          <span className="font-bold text-emerald-400">{distribution?.low || 0}</span>
        </div>
      </div>
    </div>
  );
}

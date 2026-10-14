"use client";

import { useMemo } from "react";
import { Doughnut } from "react-chartjs-2";
import "@/components/charts/ChartSetup";

interface SeverityCounts {
  critical: number;
  high: number;
  medium: number;
  low: number;
}

interface SeverityDoughnutChartProps {
  severities?: SeverityCounts;
}

export default function SeverityDoughnutChart({
  severities = { critical: 0, high: 0, medium: 0, low: 0 },
}: SeverityDoughnutChartProps) {
  const safe = severities || { critical: 0, high: 0, medium: 0, low: 0 };
  const crit = Number(safe.critical) || 0;
  const hi = Number(safe.high) || 0;
  const med = Number(safe.medium) || 0;
  const lo = Number(safe.low) || 0;
  const total = crit + hi + med + lo;

  const chartData = useMemo(() => {
    const hasData = total > 0;
    return {
      labels: ["Critical", "High", "Medium", "Low"],
      datasets: [
        {
          data: hasData
            ? [crit, hi, med, lo]
            : [1],
          backgroundColor: hasData
            ? [
                "rgba(239, 68, 68, 0.85)",
                "rgba(249, 115, 22, 0.85)",
                "rgba(245, 158, 11, 0.85)",
                "rgba(16, 185, 129, 0.85)",
              ]
            : ["rgba(100, 116, 139, 0.2)"],
          borderColor: hasData
            ? ["#ef4444", "#f97316", "#f59e0b", "#10b981"]
            : ["transparent"],
          borderWidth: 2,
          hoverOffset: 4,
        },
      ],
    };
  }, [crit, hi, med, lo, total]);

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: "70%",
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
      },
    },
  };

  return (
    <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-center sm:justify-around">
      <div className="relative h-44 w-44">
        <Doughnut data={chartData} options={options} />
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-2xl font-black tracking-tight text-[var(--foreground)]">
            {total}
          </span>
          <span className="text-[10px] uppercase font-semibold text-[var(--muted)]">
            Total Alerts
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/10 p-2">
          <span className="h-2 w-2 rounded-full bg-red-500" />
          <div>
            <div className="text-[10px] uppercase text-red-400 font-bold">Critical</div>
            <div className="font-bold text-[var(--foreground)]">{safe.critical || 0}</div>
          </div>
        </div>

        <div className="flex items-center gap-2 rounded-lg border border-orange-500/20 bg-orange-500/10 p-2">
          <span className="h-2 w-2 rounded-full bg-orange-500" />
          <div>
            <div className="text-[10px] uppercase text-orange-400 font-bold">High</div>
            <div className="font-bold text-[var(--foreground)]">{safe.high || 0}</div>
          </div>
        </div>

        <div className="flex items-center gap-2 rounded-lg border border-amber-500/20 bg-amber-500/10 p-2">
          <span className="h-2 w-2 rounded-full bg-amber-500" />
          <div>
            <div className="text-[10px] uppercase text-amber-400 font-bold">Medium</div>
            <div className="font-bold text-[var(--foreground)]">{safe.medium || 0}</div>
          </div>
        </div>

        <div className="flex items-center gap-2 rounded-lg border border-emerald-500/20 bg-emerald-500/10 p-2">
          <span className="h-2 w-2 rounded-full bg-emerald-500" />
          <div>
            <div className="text-[10px] uppercase text-emerald-400 font-bold">Low</div>
            <div className="font-bold text-[var(--foreground)]">{safe.low || 0}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

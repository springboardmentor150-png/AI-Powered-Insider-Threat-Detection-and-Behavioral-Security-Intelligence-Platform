"use client";

import { useMemo } from "react";
import { Doughnut } from "react-chartjs-2";
import "@/components/charts/ChartSetup";

interface AnomalyDoughnutChartProps {
  ruleBased?: number | null;
  machineLearning?: number | null;
}

export default function AnomalyDoughnutChart({
  ruleBased = 0,
  machineLearning = 0,
}: AnomalyDoughnutChartProps) {
  const rb = Number(ruleBased) || 0;
  const ml = Number(machineLearning) || 0;
  const total = rb + ml;

  const chartData = useMemo(() => {
    return {
      labels: ["Rule-Based UEBA", "Isolation Forest ML"],
      datasets: [
        {
          data: total > 0 ? [rb, ml] : [1, 0],
          backgroundColor:
            total > 0
              ? ["rgba(239, 68, 68, 0.85)", "rgba(59, 130, 246, 0.85)"]
              : ["rgba(100, 116, 139, 0.3)", "rgba(100, 116, 139, 0.1)"],
          borderColor:
            total > 0 ? ["#ef4444", "#3b82f6"] : ["transparent", "transparent"],
          borderWidth: 2,
          hoverOffset: 4,
        },
      ],
    };
  }, [rb, ml, total]);

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
        callbacks: {
          label: (context: any) => {
            const count = context.parsed;
            const pct = total > 0 ? Math.round((count / total) * 100) : 0;
            return ` ${context.label}: ${count} (${pct}%)`;
          },
        },
      },
    },
  };

  const rulePct = total > 0 ? Math.round((rb / total) * 100) : 0;
  const mlPct = total > 0 ? Math.round((ml / total) * 100) : 0;

  return (
    <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-center sm:justify-around">
      <div className="relative h-44 w-44">
        <Doughnut data={chartData} options={options} />
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-2xl font-black tracking-tight text-[var(--foreground)]">
            {total}
          </span>
          <span className="text-[10px] uppercase font-semibold text-[var(--muted)]">
            Anomalies
          </span>
        </div>
      </div>

      <div className="flex flex-col gap-3">
        <div className="flex items-center gap-3">
          <span className="h-3 w-3 rounded-full bg-red-500 shadow-sm shadow-red-500/50" />
          <div>
            <div className="text-xs font-semibold text-[var(--foreground)]">
              Rule-Based Deviations
            </div>
            <div className="text-xs text-[var(--muted)]">
              {rb} events ({rulePct}%)
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="h-3 w-3 rounded-full bg-blue-500 shadow-sm shadow-blue-500/50" />
          <div>
            <div className="text-xs font-semibold text-[var(--foreground)]">
              Isolation Forest ML
            </div>
            <div className="text-xs text-[var(--muted)]">
              {ml} outlier-days ({mlPct}%)
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

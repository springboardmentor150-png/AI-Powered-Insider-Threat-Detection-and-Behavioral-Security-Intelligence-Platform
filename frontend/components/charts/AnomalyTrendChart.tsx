"use client";

import { useMemo } from "react";
import { Line } from "react-chartjs-2";
import "@/components/charts/ChartSetup";

interface TrendPoint {
  date: string;
  rule_based: number;
  machine_learning: number;
  total: number;
}

interface AnomalyTrendChartProps {
  trend?: TrendPoint[];
}

export default function AnomalyTrendChart({ trend = [] }: AnomalyTrendChartProps) {
  const chartData = useMemo(() => {
    const list = Array.isArray(trend) ? trend : [];
    const labels = list.map((p) => {
      // Format as "Mon DD"
      const parts = p.date.split("-");
      if (parts.length === 3) {
        return `${parts[1]}/${parts[2]}`;
      }
      return p.date;
    });

    const ruleData = list.map((p) => Number(p.rule_based) || 0);
    const mlData = list.map((p) => Number(p.machine_learning) || 0);
    const totalData = list.map((p) => Number(p.total) || 0);

    return {
      labels,
      datasets: [
        {
          label: "Total Anomalies",
          data: totalData,
          borderColor: "#ec4899",
          backgroundColor: "rgba(236, 72, 153, 0.15)",
          borderWidth: 2.5,
          tension: 0.35,
          fill: true,
          pointBackgroundColor: "#ec4899",
          pointBorderColor: "#fff",
          pointRadius: 4,
          pointHoverRadius: 6,
        },
        {
          label: "Rule-Based",
          data: ruleData,
          borderColor: "#ef4444",
          backgroundColor: "transparent",
          borderWidth: 1.5,
          borderDash: [4, 4],
          tension: 0.35,
          pointRadius: 2,
        },
        {
          label: "ML Outliers",
          data: mlData,
          borderColor: "#3b82f6",
          backgroundColor: "transparent",
          borderWidth: 1.5,
          borderDash: [2, 2],
          tension: 0.35,
          pointRadius: 2,
        },
      ],
    };
  }, [trend]);

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: "top" as const,
        labels: {
          color: "rgba(226, 232, 240, 0.8)",
          boxWidth: 12,
          font: { size: 11 },
        },
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
    scales: {
      x: {
        grid: {
          color: "rgba(255, 255, 255, 0.05)",
        },
        ticks: {
          color: "rgba(148, 163, 184, 0.8)",
          font: { size: 11 },
        },
      },
      y: {
        beginAtZero: true,
        grid: {
          color: "rgba(255, 255, 255, 0.05)",
        },
        ticks: {
          color: "rgba(148, 163, 184, 0.8)",
          font: { size: 11 },
          stepSize: 1,
        },
      },
    },
  };

  return (
    <div className="relative h-64 w-full">
      <Line data={chartData} options={options} />
    </div>
  );
}

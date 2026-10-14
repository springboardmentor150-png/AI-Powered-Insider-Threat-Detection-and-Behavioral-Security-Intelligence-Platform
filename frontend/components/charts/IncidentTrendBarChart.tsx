"use client";

import { useMemo } from "react";
import { Bar } from "react-chartjs-2";
import "@/components/charts/ChartSetup";

interface IncidentPoint {
  date: string;
  incident_count: number;
}

interface IncidentTrendBarChartProps {
  trend: IncidentPoint[];
}

export default function IncidentTrendBarChart({
  trend,
}: IncidentTrendBarChartProps) {
  const chartData = useMemo(() => {
    const labels = trend.map((p) => {
      const parts = p.date.split("-");
      if (parts.length === 3) return `${parts[1]}/${parts[2]}`;
      return p.date;
    });

    const data = trend.map((p) => p.incident_count);

    return {
      labels,
      datasets: [
        {
          label: "Incidents Created",
          data,
          backgroundColor: "rgba(168, 85, 247, 0.75)",
          borderColor: "#a855f7",
          borderWidth: 1.5,
          borderRadius: 6,
          barThickness: 24,
        },
      ],
    };
  }, [trend]);

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
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
        grid: { color: "rgba(255, 255, 255, 0.05)" },
        ticks: { color: "rgba(148, 163, 184, 0.8)", font: { size: 11 } },
      },
      y: {
        beginAtZero: true,
        grid: { color: "rgba(255, 255, 255, 0.05)" },
        ticks: {
          color: "rgba(148, 163, 184, 0.8)",
          font: { size: 11 },
          stepSize: 1,
        },
      },
    },
  };

  return (
    <div className="relative h-60 w-full">
      <Bar data={chartData} options={options} />
    </div>
  );
}

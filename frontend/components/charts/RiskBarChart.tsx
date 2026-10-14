"use client";

import { useMemo } from "react";
import { Bar } from "react-chartjs-2";
import "@/components/charts/ChartSetup";

interface EmployeeRisk {
  employee_code: string;
  employee_name: string;
  department: string;
  risk_score: number;
  risk_level: string;
}

interface RiskBarChartProps {
  employees?: EmployeeRisk[];
}

export default function RiskBarChart({ employees = [] }: RiskBarChartProps) {
  const chartData = useMemo(() => {
    const list = Array.isArray(employees) ? employees : [];
    // Sort or take top 7 for clean visual rendering
    const sorted = [...list]
      .sort((a, b) => (Number(b.risk_score) || 0) - (Number(a.risk_score) || 0))
      .slice(0, 7);

    const labels = sorted.map(
      (e) => `${e.employee_name || e.employee_code} (${e.employee_code})`
    );
    const scores = sorted.map((e) => Number(e.risk_score) || 0);

    const backgroundColors = sorted.map((e) => {
      const score = Number(e.risk_score) || 0;
      if (score >= 75) return "rgba(239, 68, 68, 0.85)"; // Red
      if (score >= 50) return "rgba(249, 115, 22, 0.85)"; // Orange
      if (score >= 25) return "rgba(245, 158, 11, 0.85)"; // Amber
      return "rgba(16, 185, 129, 0.85)"; // Emerald
    });

    const borderColors = sorted.map((e) => {
      const score = Number(e.risk_score) || 0;
      if (score >= 75) return "#ef4444";
      if (score >= 50) return "#f97316";
      if (score >= 25) return "#f59e0b";
      return "#10b981";
    });

    return {
      labels,
      datasets: [
        {
          label: "Risk Score",
          data: scores,
          backgroundColor: backgroundColors,
          borderColor: borderColors,
          borderWidth: 1.5,
          borderRadius: 6,
          barThickness: 16,
        },
      ],
    };
  }, [employees]);

  const options = {
    indexAxis: "y" as const,
    responsive: true,
    maintainAspectRatio: false,
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
          label: (context: any) => ` Risk Score: ${context.parsed.x} / 100`,
        },
      },
    },
    scales: {
      x: {
        min: 0,
        max: 100,
        grid: {
          color: "rgba(255, 255, 255, 0.05)",
        },
        ticks: {
          color: "rgba(148, 163, 184, 0.8)",
          font: { size: 11 },
        },
      },
      y: {
        grid: {
          display: false,
        },
        ticks: {
          color: "rgba(226, 232, 240, 0.9)",
          font: { size: 11, weight: "bold" as const },
        },
      },
    },
  };

  return (
    <div className="relative h-64 w-full">
      <Bar data={chartData} options={options} />
    </div>
  );
}

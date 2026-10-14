"use client";

import { useMemo } from "react";
import { Doughnut } from "react-chartjs-2";
import "@/components/charts/ChartSetup";

interface UserRoleChartProps {
  usersByRole?: Record<string, number>;
}

export default function UserRoleChart({ usersByRole = {} }: UserRoleChartProps) {
  const safeRoles = usersByRole || {};
  const total = Object.values(safeRoles).reduce((acc, curr) => acc + (Number(curr) || 0), 0);

  const chartData = useMemo(() => {
    const labels = Object.keys(safeRoles).map((k) =>
      k
        .split("_")
        .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
        .join(" ")
    );
    const data = Object.values(safeRoles).map((v) => Number(v) || 0);

    return {
      labels,
      datasets: [
        {
          data,
          backgroundColor: [
            "rgba(168, 85, 247, 0.85)", // Purple (Analyst)
            "rgba(59, 130, 246, 0.85)", // Blue (SOC)
            "rgba(16, 185, 129, 0.85)", // Emerald (Manager)
            "rgba(245, 158, 11, 0.85)", // Amber (Admin)
          ],
          borderColor: ["#a855f7", "#3b82f6", "#10b981", "#f59e0b"],
          borderWidth: 2,
          hoverOffset: 4,
        },
      ],
    };
  }, [usersByRole]);

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: "68%",
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
            Users
          </span>
        </div>
      </div>

      <div className="flex flex-col gap-2 text-xs">
        {Object.entries(safeRoles).map(([role, count], idx) => {
          const colors = ["bg-purple-500", "bg-blue-500", "bg-emerald-500", "bg-amber-500"];
          const dot = colors[idx % colors.length];
          const label = role
            .split("_")
            .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
            .join(" ");

          return (
            <div key={role} className="flex items-center justify-between gap-6">
              <div className="flex items-center gap-2">
                <span className={`h-2.5 w-2.5 rounded-full ${dot}`} />
                <span className="text-[var(--foreground)] font-medium">{label}</span>
              </div>
              <span className="font-bold text-[var(--muted)]">{count}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

"use client";

import React from "react";

interface ThreatScoreBadgeProps {
  score: number;
  level?: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" | string;
  showLevel?: boolean;
  size?: "sm" | "md" | "lg";
}

export const ThreatScoreBadge: React.FC<ThreatScoreBadgeProps> = ({
  score,
  level,
  showLevel = true,
  size = "md",
}) => {
  // Infer level if not provided
  let computedLevel = level;
  if (!computedLevel) {
    if (score >= 80) computedLevel = "CRITICAL";
    else if (score >= 60) computedLevel = "HIGH";
    else if (score >= 35) computedLevel = "MEDIUM";
    else computedLevel = "LOW";
  }

  let colorClasses = "";
  let dotColor = "";

  switch (computedLevel?.toUpperCase()) {
    case "CRITICAL":
      colorClasses = "bg-rose-950/80 text-rose-300 border-rose-500/50 shadow-sm shadow-rose-500/20";
      dotColor = "bg-rose-400 animate-ping";
      break;
    case "HIGH":
      colorClasses = "bg-amber-950/80 text-amber-300 border-amber-500/50 shadow-sm shadow-amber-500/20";
      dotColor = "bg-amber-400";
      break;
    case "MEDIUM":
      colorClasses = "bg-yellow-950/60 text-yellow-300 border-yellow-500/40";
      dotColor = "bg-yellow-400";
      break;
    default:
      colorClasses = "bg-emerald-950/60 text-emerald-300 border-emerald-500/40";
      dotColor = "bg-emerald-400";
      break;
  }

  const sizeClasses = {
    sm: "text-[11px] px-2 py-0.5 space-x-1.5",
    md: "text-xs px-2.5 py-1 space-x-2",
    lg: "text-sm px-3.5 py-1.5 space-x-2.5 font-bold",
  }[size];

  return (
    <span
      className={`inline-flex items-center rounded-full border font-mono font-medium ${colorClasses} ${sizeClasses}`}
    >
      <span className={`w-2 h-2 rounded-full ${dotColor}`} />
      <span>{score.toFixed(1)}</span>
      {showLevel && <span className="opacity-80 uppercase text-[10px] tracking-wider">({computedLevel})</span>}
    </span>
  );
};

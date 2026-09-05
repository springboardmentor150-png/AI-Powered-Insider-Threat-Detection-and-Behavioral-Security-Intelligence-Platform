"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import {
  LayoutDashboard,
  Users,
  Activity,
  AlertTriangle,
  FolderLock,
  PlaySquare,
  ShieldCheck,
  Cpu
} from "lucide-react";

export const Sidebar: React.FC = () => {
  const pathname = usePathname();
  const { user } = useAuth();

  const navItems = [
    { label: "SOC Dashboard", href: "/", icon: LayoutDashboard },
    { label: "Employee Profiles", href: "/employees", icon: Users },
    { label: "Activity Stream", href: "/logs", icon: Activity },
    { label: "Alert Triage", href: "/alerts", icon: AlertTriangle, badge: "Live" },
    { label: "Incidents & SOC", href: "/incidents", icon: FolderLock },
    { label: "Threat Simulator", href: "/simulation", icon: PlaySquare },
  ];

  if (user?.role === "admin") {
    navItems.push({ label: "Admin & RBAC", href: "/admin", icon: ShieldCheck });
  }

  return (
    <aside className="w-64 border-r border-slate-800/80 bg-slate-900/40 backdrop-blur-md flex flex-col justify-between py-6 px-4">
      <div className="space-y-6">
        <div className="px-3">
          <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider font-mono">
            Intelligence Modules
          </p>
        </div>

        <nav className="space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-sm shadow-cyan-500/10"
                    : "text-slate-300 hover:text-white hover:bg-slate-800/60"
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Icon className={`w-4 h-4 ${isActive ? "text-cyan-400" : "text-slate-400"}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-rose-950 text-rose-400 border border-rose-800 animate-pulse">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* AI Engine Status Card */}
      <div className="p-3.5 rounded-xl bg-slate-800/50 border border-slate-700/60 space-y-2">
        <div className="flex items-center space-x-2 text-xs font-semibold text-cyan-300">
          <Cpu className="w-4 h-4 text-cyan-400 animate-spin" style={{ animationDuration: '6s' }} />
          <span>Isolation Forest Engine</span>
        </div>
        <p className="text-[11px] text-slate-400 leading-tight">
          Baseline anomaly detection & statistical Z-scoring active.
        </p>
        <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 pt-1 border-t border-slate-700/40">
          <span>Model Contamination:</span>
          <span className="text-cyan-400">12%</span>
        </div>
      </div>
    </aside>
  );
};

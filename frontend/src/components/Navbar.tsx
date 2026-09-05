"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { Shield, ShieldAlert, UserCheck, LogOut, ChevronDown, Radio } from "lucide-react";

export const Navbar: React.FC = () => {
  const { user, quickLogin, logout } = useAuth();
  const [roleDropdownOpen, setRoleDropdownOpen] = useState(false);

  const getRoleBadgeColor = (role?: string) => {
    switch (role) {
      case "admin":
        return "bg-purple-900/40 text-purple-300 border-purple-500/30";
      case "security_manager":
        return "bg-blue-900/40 text-blue-300 border-blue-500/30";
      case "security_analyst":
        return "bg-emerald-900/40 text-emerald-300 border-emerald-500/30";
      case "soc_engineer":
        return "bg-cyan-900/40 text-cyan-300 border-cyan-500/30";
      default:
        return "bg-slate-800 text-slate-300 border-slate-700";
    }
  };

  return (
    <header className="h-16 border-b border-slate-800/80 bg-slate-900/80 backdrop-blur-md sticky top-0 z-40 px-6 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <Shield className="w-5 h-5 text-white" />
        </div>
        <div>
          <span className="font-bold text-lg text-white tracking-wide flex items-center gap-2">
            ITBIS <span className="text-xs px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/50 font-mono">v1.0 AI-SOC</span>
          </span>
          <p className="text-[11px] text-slate-400 font-mono">Behavioral Insider Threat Intelligence</p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {/* Live Ingestion Indicator */}
        <div className="hidden md:flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-800/60 border border-slate-700/50 text-xs text-slate-300">
          <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
          <span className="text-slate-400">Telemetry Pipeline:</span>
          <span className="text-emerald-400 font-semibold">STREAMING</span>
        </div>

        {/* Quick Demo Role Switcher */}
        <div className="relative">
          <button
            onClick={() => setRoleDropdownOpen(!roleDropdownOpen)}
            className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700/80 border border-slate-700 text-xs font-medium text-slate-200 transition"
          >
            <UserCheck className="w-3.5 h-3.5 text-cyan-400" />
            <span>Switch Role</span>
            <ChevronDown className="w-3 h-3 text-slate-400" />
          </button>

          {roleDropdownOpen && (
            <div className="absolute right-0 mt-2 w-56 bg-slate-900 border border-slate-700/80 rounded-xl shadow-2xl py-2 z-50 text-xs">
              <div className="px-3 py-1 text-[11px] font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-800 mb-1">
                Simulate Role Identity
              </div>
              <button
                onClick={() => { quickLogin("admin"); setRoleDropdownOpen(false); }}
                className="w-full text-left px-3 py-2 hover:bg-slate-800 text-slate-200 flex items-center justify-between"
              >
                <span>Sarah Connor (Admin)</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800">Admin</span>
              </button>
              <button
                onClick={() => { quickLogin("analyst"); setRoleDropdownOpen(false); }}
                className="w-full text-left px-3 py-2 hover:bg-slate-800 text-slate-200 flex items-center justify-between"
              >
                <span>Alex Rivera (Analyst)</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">Analyst</span>
              </button>
              <button
                onClick={() => { quickLogin("manager"); setRoleDropdownOpen(false); }}
                className="w-full text-left px-3 py-2 hover:bg-slate-800 text-slate-200 flex items-center justify-between"
              >
                <span>Marcus Vance (Manager)</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">Manager</span>
              </button>
              <button
                onClick={() => { quickLogin("soc"); setRoleDropdownOpen(false); }}
                className="w-full text-left px-3 py-2 hover:bg-slate-800 text-slate-200 flex items-center justify-between"
              >
                <span>Priya Sharma (SOC)</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">SOC Eng</span>
              </button>
            </div>
          )}
        </div>

        {/* Current User Pill */}
        {user ? (
          <div className="flex items-center space-x-3 pl-2 border-l border-slate-800">
            <div className="text-right hidden sm:block">
              <p className="text-xs font-medium text-slate-200">{user.full_name || user.email}</p>
              <span className={`inline-block text-[10px] px-2 py-0.2 border rounded-full font-mono uppercase ${getRoleBadgeColor(user.role)}`}>
                {user.role}
              </span>
            </div>
            <button
              onClick={logout}
              title="Sign Out"
              className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-950/30 transition"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <Link
            href="/login"
            className="px-4 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold shadow transition"
          >
            Sign In
          </Link>
        )}
      </div>
    </header>
  );
};

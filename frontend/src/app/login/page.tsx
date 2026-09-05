"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Lock, Mail, Key, UserCheck, ArrowRight, ShieldCheck } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { login, quickLogin } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    const success = await login(email, password);
    setLoading(false);
    if (success) {
      router.push("/");
    } else {
      setError("Invalid email or password. Please verify credentials.");
    }
  };

  const handleQuickRole = async (role: "admin" | "analyst" | "manager" | "soc") => {
    setError(null);
    setLoading(true);
    const success = await quickLogin(role);
    setLoading(false);
    if (success) {
      router.push("/");
    } else {
      setError("Quick login failed.");
    }
  };

  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center py-12 px-4 animate-fade-in">
      <div className="w-full max-w-md space-y-8 p-8 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-2xl backdrop-blur-xl">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center mx-auto shadow-lg shadow-cyan-500/25">
            <ShieldCheck className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">ITBIS SOC Authentication</h2>
          <p className="text-xs text-slate-400">Sign in to access behavioral intelligence and threat monitoring</p>
        </div>

        {/* 1-Click Quick Role Switchers */}
        <div className="space-y-2.5 p-4 rounded-2xl bg-slate-950/70 border border-slate-800/80">
          <div className="flex items-center space-x-2 text-[11px] font-semibold text-slate-400 uppercase tracking-wider font-mono">
            <UserCheck className="w-3.5 h-3.5 text-cyan-400" />
            <span>1-Click Demo Profiles</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <button
              type="button"
              onClick={() => handleQuickRole("admin")}
              className="p-2.5 rounded-xl bg-purple-950/40 hover:bg-purple-900/50 border border-purple-500/30 text-purple-300 font-medium text-left transition"
            >
              <div className="font-bold">Admin</div>
              <div className="text-[10px] text-purple-400/80 font-mono">Full Privileges</div>
            </button>
            <button
              type="button"
              onClick={() => handleQuickRole("analyst")}
              className="p-2.5 rounded-xl bg-emerald-950/40 hover:bg-emerald-900/50 border border-emerald-500/30 text-emerald-300 font-medium text-left transition"
            >
              <div className="font-bold">Analyst</div>
              <div className="text-[10px] text-emerald-400/80 font-mono">Triage & Investigation</div>
            </button>
            <button
              type="button"
              onClick={() => handleQuickRole("manager")}
              className="p-2.5 rounded-xl bg-blue-950/40 hover:bg-blue-900/50 border border-blue-500/30 text-blue-300 font-medium text-left transition"
            >
              <div className="font-bold">Manager</div>
              <div className="text-[10px] text-blue-400/80 font-mono">Employees & Reports</div>
            </button>
            <button
              type="button"
              onClick={() => handleQuickRole("soc")}
              className="p-2.5 rounded-xl bg-cyan-950/40 hover:bg-cyan-900/50 border border-cyan-500/30 text-cyan-300 font-medium text-left transition"
            >
              <div className="font-bold">SOC Eng</div>
              <div className="text-[10px] text-cyan-400/80 font-mono">Telemetry & Simulation</div>
            </button>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="p-3 rounded-xl bg-rose-950/60 border border-rose-800 text-rose-300 text-xs text-center font-medium">
            {error}
          </div>
        )}

        {/* Manual Login Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-xs text-slate-300 font-medium">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="analyst@itbis.security"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 focus:border-cyan-500 text-slate-100 text-xs focus:outline-none transition font-mono"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-xs text-slate-300 font-medium">Password</label>
            <div className="relative">
              <Key className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 focus:border-cyan-500 text-slate-100 text-xs focus:outline-none transition font-mono"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center space-x-2 py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-bold shadow-lg shadow-cyan-600/25 transition disabled:opacity-50"
          >
            <span>{loading ? "Authenticating..." : "Sign In with Credentials"}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}

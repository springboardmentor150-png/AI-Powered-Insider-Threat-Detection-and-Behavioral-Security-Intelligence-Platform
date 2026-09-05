"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { authAPI } from "@/lib/api";
import {
  ShieldCheck,
  UserPlus,
  Lock,
  Mail,
  Shield,
  CheckCircle,
  AlertOctagon,
  RefreshCw
} from "lucide-react";

export default function AdminPage() {
  const { user } = useAuth();
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [newUserForm, setNewUserForm] = useState({
    email: "",
    full_name: "",
    password: "",
    role: "security_analyst",
  });
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const res = await authAPI.getUsers();
      setUsers(res.data || []);
    } catch (e) {
      console.error("RBAC Restricted:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user?.role === "admin") {
      fetchUsers();
    } else {
      setLoading(false);
    }
  }, [user]);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccessMsg(null);
    try {
      await authAPI.register(newUserForm);
      setSuccessMsg(`User ${newUserForm.email} registered successfully with role '${newUserForm.role}'!`);
      setNewUserForm({
        email: "",
        full_name: "",
        password: "",
        role: "security_analyst",
      });
      fetchUsers();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to create user.");
    }
  };

  // RBAC Enforcement Check
  if (user?.role !== "admin") {
    return (
      <div className="p-12 text-center rounded-3xl bg-slate-900/60 border border-slate-800 space-y-4 max-w-xl mx-auto my-12 animate-fade-in">
        <div className="w-12 h-12 rounded-2xl bg-rose-950/60 border border-rose-800 flex items-center justify-center mx-auto text-rose-400">
          <AlertOctagon className="w-6 h-6" />
        </div>
        <h2 className="text-lg font-bold text-white">403 Forbidden: Administrator Access Required</h2>
        <p className="text-xs text-slate-400 leading-relaxed">
          Your current authenticated role is <strong className="text-cyan-400 font-mono">'{user?.role || "anonymous"}'</strong>.
          Role-Based Access Control (RBAC) restricts user governance and permission provisioning exclusively to the Administrator.
        </p>
        <p className="text-[11px] text-slate-500 font-mono">
          Tip: Use the "Switch Role" menu at the top right to switch to "Sarah Connor (Admin)".
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-purple-400" />
            <span>Platform User Administration & RBAC Management</span>
          </h1>
          <p className="text-xs text-slate-400">
            Provision platform operator credentials, assign roles, and audit security permissions.
          </p>
        </div>

        <button
          onClick={fetchUsers}
          className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          <span>Refresh</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Create User Form */}
        <div className="lg:col-span-5 p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="flex items-center space-x-2 text-sm font-bold text-white">
            <UserPlus className="w-4 h-4 text-cyan-400" />
            <span>Provision New SOC Operator</span>
          </div>

          {successMsg && (
            <div className="p-3 rounded-xl bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-xs flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          <form onSubmit={handleCreateUser} className="space-y-3.5 text-xs">
            <div>
              <label className="text-slate-300 font-medium">Full Name</label>
              <input
                type="text"
                required
                placeholder="e.g. Jordan Reed"
                value={newUserForm.full_name}
                onChange={(e) => setNewUserForm({ ...newUserForm, full_name: e.target.value })}
                className="w-full mt-1 p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100"
              />
            </div>

            <div>
              <label className="text-slate-300 font-medium">Email Address</label>
              <input
                type="email"
                required
                placeholder="e.g. jreed@itbis.security"
                value={newUserForm.email}
                onChange={(e) => setNewUserForm({ ...newUserForm, email: e.target.value })}
                className="w-full mt-1 p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-mono"
              />
            </div>

            <div>
              <label className="text-slate-300 font-medium">Password</label>
              <input
                type="password"
                required
                placeholder="••••••••••••"
                value={newUserForm.password}
                onChange={(e) => setNewUserForm({ ...newUserForm, password: e.target.value })}
                className="w-full mt-1 p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-mono"
              />
            </div>

            <div>
              <label className="text-slate-300 font-medium">RBAC Role Assignment</label>
              <select
                value={newUserForm.role}
                onChange={(e) => setNewUserForm({ ...newUserForm, role: e.target.value })}
                className="w-full mt-1 p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-mono"
              >
                <option value="admin">admin (Full Administrator)</option>
                <option value="security_manager">security_manager (SOC Management & Baselines)</option>
                <option value="security_analyst">security_analyst (Investigation & Triage)</option>
                <option value="soc_engineer">soc_engineer (Telemetry & Threat Simulations)</option>
              </select>
            </div>

            <button
              type="submit"
              className="w-full py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold shadow-lg shadow-purple-600/20 transition"
            >
              Provision Account
            </button>
          </form>
        </div>

        {/* Existing Users Table */}
        <div className="lg:col-span-7 p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider font-mono">
            Active System Operators ({users.length})
          </h3>

          <div className="divide-y divide-slate-800/80 overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="text-slate-400 uppercase tracking-wider font-mono text-[10px]">
                  <th className="py-2.5">User</th>
                  <th className="py-2.5">Role</th>
                  <th className="py-2.5">Status</th>
                  <th className="py-2.5 text-right">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 font-medium text-slate-100">
                      <div>{u.full_name || u.email}</div>
                      <div className="text-[10px] text-slate-400 font-mono">{u.email}</div>
                    </td>
                    <td className="py-3">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700">
                        {u.role}
                      </span>
                    </td>
                    <td className="py-3">
                      <span className="text-[10px] font-mono text-emerald-400">ACTIVE</span>
                    </td>
                    <td className="py-3 text-right text-slate-400 font-mono text-[10px]">
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

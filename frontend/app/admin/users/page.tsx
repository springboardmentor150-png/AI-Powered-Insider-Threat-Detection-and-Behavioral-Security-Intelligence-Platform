"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import Navbar from "@/components/Navbar";
import api from "@/lib/api";
import { verifyAuthentication } from "@/lib/auth";

interface AdminUser {
  id: number;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string | null;
}

export default function AdminUsersPage() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState<number | null>(null);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const user = await verifyAuthentication();
      if ((user.role || "").toLowerCase() !== "admin") {
        window.location.href = "/dashboard";
        return;
      }

      const res = await api.get("/admin/users");
      setUsers(res.data?.users || []);
    } catch (err: any) {
      if (err.response?.status === 401) {
        window.location.href = "/login";
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleRoleChange = async (userId: number, newRole: string) => {
    try {
      setUpdatingId(userId);
      setMessage(null);
      await api.patch(`/admin/users/${userId}/role`, { role: newRole });
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, role: newRole } : u))
      );
      setMessage({ type: "success", text: `Role updated to ${newRole} successfully.` });
    } catch (err: any) {
      setMessage({ type: "error", text: err.response?.data?.detail || "Failed to update role." });
    } finally {
      setUpdatingId(null);
    }
  };

  const handleStatusToggle = async (userId: number, currentStatus: boolean) => {
    try {
      setUpdatingId(userId);
      setMessage(null);
      const nextStatus = !currentStatus;
      await api.patch(`/admin/users/${userId}/status`, { is_active: nextStatus });
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, is_active: nextStatus } : u))
      );
      setMessage({
        type: "success",
        text: `User ${nextStatus ? "activated" : "deactivated"} successfully.`,
      });
    } catch (err: any) {
      setMessage({ type: "error", text: err.response?.data?.detail || "Failed to update status." });
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <div className="flex h-screen bg-[var(--background)] text-[var(--foreground)]">
      <Sidebar />

      <div className="flex flex-1 flex-col overflow-hidden">
        <Navbar />

        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="mx-auto max-w-6xl space-y-6">
            <div className="border-b border-[var(--border)] pb-5">
              <h1 className="text-2xl font-bold tracking-tight">Platform User Management</h1>
              <p className="text-sm text-[var(--muted)]">
                Admin control center for user access credentials, role privileges, and account status
              </p>
            </div>

            {message && (
              <div
                className={`rounded-xl border p-4 text-xs font-semibold ${
                  message.type === "success"
                    ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
                    : "border-red-500/30 bg-red-500/10 text-red-400"
                }`}
              >
                {message.text}
              </div>
            )}

            <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-[var(--border)] bg-[var(--background)]/50 text-[11px] font-semibold uppercase tracking-wider text-[var(--muted)]">
                      <th className="p-4">User ID</th>
                      <th className="p-4">Email</th>
                      <th className="p-4">Assigned Role</th>
                      <th className="p-4">Access Status</th>
                      <th className="p-4">Registered Date</th>
                      <th className="p-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[var(--border)]">
                    {loading ? (
                      <tr>
                        <td colSpan={6} className="p-8 text-center text-xs text-[var(--muted)]">
                          Loading user directory...
                        </td>
                      </tr>
                    ) : (
                      users.map((u) => (
                        <tr key={u.id} className="hover:bg-[var(--card-hover)] transition text-xs">
                          <td className="p-4 font-mono font-bold text-[var(--primary)]">#{u.id}</td>
                          <td className="p-4 font-medium text-[var(--foreground)]">{u.email}</td>
                          <td className="p-4">
                            <select
                              value={u.role}
                              disabled={updatingId === u.id}
                              onChange={(e) => handleRoleChange(u.id, e.target.value)}
                              className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-2.5 py-1 text-xs outline-none focus:border-[var(--primary)] font-medium capitalize"
                            >
                              <option value="security_analyst">Security Analyst</option>
                              <option value="soc_engineer">SOC Engineer</option>
                              <option value="security_manager">Security Manager</option>
                              <option value="admin">Administrator</option>
                            </select>
                          </td>
                          <td className="p-4">
                            <span
                              className={`rounded-md border px-2 py-0.5 text-[10px] font-bold uppercase ${
                                u.is_active
                                  ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                                  : "bg-red-500/20 text-red-400 border-red-500/30"
                              }`}
                            >
                              {u.is_active ? "Active" : "Disabled"}
                            </span>
                          </td>
                          <td className="p-4 font-mono text-[var(--muted)]">
                            {u.created_at ? new Date(u.created_at).toLocaleDateString() : "-"}
                          </td>
                          <td className="p-4 text-right">
                            <button
                              onClick={() => handleStatusToggle(u.id, u.is_active)}
                              disabled={updatingId === u.id}
                              className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                                u.is_active
                                  ? "bg-red-500/10 text-red-400 hover:bg-red-500/20"
                                  : "bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20"
                              }`}
                            >
                              {u.is_active ? "Deactivate" : "Activate"}
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

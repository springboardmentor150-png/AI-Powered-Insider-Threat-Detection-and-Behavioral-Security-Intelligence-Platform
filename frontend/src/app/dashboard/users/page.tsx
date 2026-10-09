"use client";
import { useEffect, useState } from "react";
import { api, getDecodedRole } from "@/lib/api";

type User = {
  id: number;
  email: string;
  role: string;
};

export default function UserManagementPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ email: "", password: "", role: "security_analyst" });
  
  const fetchUsers = async () => {
    try {
      const res = await api.get("/users");
      setUsers(res.data);
      setError("");
    } catch (e: any) {
      setError("Access Denied. Only Administrators can manage users.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/users", formData);
      setShowForm(false);
      setFormData({ email: "", password: "", role: "security_analyst" });
      fetchUsers();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Error provisioning user.");
    }
  };

  if (loading) return (
    <div style={{ padding: "2rem", display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      <div style={{ width: "250px", height: "32px", background: "var(--bg-input)", borderRadius: "6px", animation: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite" }}></div>
      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr><th style={{ padding: "1rem", borderBottom: "1px solid var(--border)" }}><div style={{ width: "100px", height: "16px", background: "var(--bg-dark)", borderRadius: "4px" }}></div></th></tr>
          </thead>
          <tbody>
            {[1,2,3].map(i => (
              <tr key={i}><td style={{ padding: "1.25rem 1rem", borderBottom: "1px solid var(--border)" }}><div style={{ width: "100%", height: "20px", background: "var(--bg-input)", borderRadius: "4px", animation: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite" }}></div></td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: "2rem" }}>
        <div>
          <h2 className="title-h1">Platform Identity Management</h2>
          <p className="text-caption">Centralized control for administrative personnel and analysts.</p>
        </div>
        <button className={showForm ? "btn-outline" : "btn-primary"} onClick={() => setShowForm(!showForm)} style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          {showForm ? "Cancel" : "Provision User"}
        </button>
      </div>

      {error ? (
        <div style={{ padding: "1rem", color: "var(--danger)", border: "1px solid var(--danger)", background: "rgba(239, 68, 68, 0.1)" }}>{error}</div>
      ) : (
        <>
          {showForm && (
            <div className="card" style={{ marginBottom: "2rem" }}>
              <h3>New User Provisioning</h3>
              <form onSubmit={handleCreate} style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginTop: "1rem" }}>
                 <input className="input-field" placeholder="Email Address" required type="email" value={formData.email} onChange={e=>setFormData({...formData, email: e.target.value})} />
                 <input className="input-field" placeholder="Password" required type="password" value={formData.password} onChange={e=>setFormData({...formData, password: e.target.value})} />
                 <select className="input-field" value={formData.role} onChange={e=>setFormData({...formData, role: e.target.value})}>
                    <option value="admin">Administrator</option>
                    <option value="security_manager">Security Manager</option>
                    <option value="soc_engineer">SOC Engineer</option>
                    <option value="security_analyst">Security Analyst</option>
                 </select>
                 <button className="btn-primary" type="submit">Create User</button>
              </form>
            </div>
          )}
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>User ID</th>
                  <th>Email Address</th>
                  <th>Clearance Role</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id}>
                    <td>#{u.id}</td>
                    <td>{u.email}</td>
                    <td><span className="badge badge-neutral">{u.role.replace('_', ' ')}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

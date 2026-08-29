"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import Link from "next/link";

export default function Signup() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("security_analyst");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);
    try {
      await api.post("/auth/signup", { email, password, role });
      setSuccess("Clearance granted. Security profile created.");
      setTimeout(() => router.push("/login"), 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Registration failed");
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh", background: "radial-gradient(circle at top right, #152238, var(--bg-dark))" }}>
      <div style={{ width: "100%", maxWidth: "420px", padding: "1.5rem" }}>
        <div style={{ textAlign: "center", marginBottom: "2.5rem" }}>
          <div style={{ width: "48px", height: "48px", background: "var(--bg-input)", border: "1px solid var(--border)", borderRadius: "12px", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 1rem auto" }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--text-main)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><line x1="19" y1="8" x2="19" y2="14"></line><line x1="22" y1="11" x2="16" y2="11"></line>
            </svg>
          </div>
          <h1 style={{ fontSize: "1.75rem", fontWeight: "600", color: "#fff", letterSpacing: "-0.025em" }}>Profile Provisioning</h1>
          <p className="text-caption" style={{ marginTop: "0.5rem" }}>Register a new operative for ITBIS</p>
        </div>

        <form onSubmit={handleSignup} className="card" style={{ padding: "2rem" }}>
          {error && (
            <div style={{ padding: "0.75rem", background: "rgba(239, 68, 68, 0.1)", border: "1px solid rgba(239, 68, 68, 0.2)", borderRadius: "6px", color: "var(--danger)", fontSize: "0.875rem", marginBottom: "1.5rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
              {error}
            </div>
          )}
          {success && (
            <div style={{ padding: "0.75rem", background: "rgba(16, 185, 129, 0.1)", border: "1px solid rgba(16, 185, 129, 0.2)", borderRadius: "6px", color: "var(--success)", fontSize: "0.875rem", marginBottom: "1.5rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
              {success}
            </div>
          )}
          
          <div style={{ marginBottom: "1.25rem" }}>
            <label className="input-label">Corporate Email</label>
            <input type="email" required value={email} onChange={e => setEmail(e.target.value)} className="input-field" placeholder="new.analyst@itbis.local" />
          </div>
          
          <div style={{ marginBottom: "1.25rem" }}>
            <label className="input-label">Access Role</label>
            <select value={role} onChange={e => setRole(e.target.value)} className="input-field">
              <option value="security_analyst">Security Analyst</option>
              <option value="soc_engineer">SOC Engineer</option>
              <option value="security_manager">Security Manager</option>
              <option value="admin">Administrator</option>
            </select>
          </div>
          
          <div style={{ marginBottom: "1.5rem" }}>
            <label className="input-label">Secure Password</label>
            <input type="password" required value={password} onChange={e => setPassword(e.target.value)} className="input-field" placeholder="••••••••" />
          </div>
          
          <button type="submit" className="btn-primary" style={{ width: "100%", display: "flex", justifyContent: "center" }} disabled={loading}>
            {loading ? <div className="loader" style={{ width: "1.25rem", height: "1.25rem", borderWidth: "2px", borderTopColor: "#0B0F19", borderColor: "rgba(0,0,0,0.2)" }}></div> : "Provision Profile"}
          </button>
        </form>
        
        <p style={{ textAlign: "center", marginTop: "2rem", fontSize: "0.875rem", color: "var(--text-muted)" }}>
          Already cleared? <Link href="/login" style={{ color: "var(--text-main)", fontWeight: "500", borderBottom: "1px solid var(--text-muted)", paddingBottom: "1px" }}>Secure Login</Link>
        </p>
      </div>
    </div>
  );
}

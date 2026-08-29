"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import Link from "next/link";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await api.post("/auth/login", { email, password });
      localStorage.setItem("token", res.data.access_token);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Invalid credentials");
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh", background: "url('/noise.png'), radial-gradient(circle at top right, #152238, var(--bg-dark))" }}>
      <div style={{ width: "100%", maxWidth: "420px", padding: "1.5rem" }}>
        <div style={{ textAlign: "center", marginBottom: "2.5rem" }}>
          <div style={{ width: "48px", height: "48px", background: "var(--accent-light)", border: "1px solid var(--accent)", borderRadius: "12px", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 1rem auto" }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            </svg>
          </div>
          <h1 style={{ fontSize: "1.75rem", fontWeight: "600", color: "#fff", letterSpacing: "-0.025em" }}>Welcome back</h1>
          <p className="text-caption" style={{ marginTop: "0.5rem" }}>Sign in to the ITBIS Operations Center</p>
        </div>

        <form onSubmit={handleLogin} className="card" style={{ padding: "2rem" }}>
          {error && (
            <div style={{ padding: "0.75rem", background: "rgba(239, 68, 68, 0.1)", border: "1px solid rgba(239, 68, 68, 0.2)", borderRadius: "6px", color: "var(--danger)", fontSize: "0.875rem", marginBottom: "1.5rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
              {error}
            </div>
          )}
          
          <div style={{ marginBottom: "1.25rem" }}>
            <label className="input-label">Corporate Email</label>
            <input type="email" required value={email} onChange={e => setEmail(e.target.value)} className="input-field" placeholder="analyst@itbis.local" />
          </div>
          
          <div style={{ marginBottom: "1.5rem" }}>
            <label className="input-label">Password</label>
            <input type="password" required value={password} onChange={e => setPassword(e.target.value)} className="input-field" placeholder="••••••••" />
          </div>
          
          <button type="submit" className="btn-primary" style={{ width: "100%", display: "flex", justifyContent: "center" }} disabled={loading}>
            {loading ? <div className="loader" style={{ width: "1.25rem", height: "1.25rem", borderWidth: "2px" }}></div> : "Authenticate Access"}
          </button>

        </form>
        
        <p style={{ textAlign: "center", marginTop: "2rem", fontSize: "0.875rem", color: "var(--text-muted)" }}>
          Don't have an operating account? <Link href="/signup" style={{ color: "var(--text-main)", fontWeight: "500", borderBottom: "1px solid var(--text-muted)", paddingBottom: "1px" }}>Request access</Link>
        </p>
      </div>
    </div>
  );
}

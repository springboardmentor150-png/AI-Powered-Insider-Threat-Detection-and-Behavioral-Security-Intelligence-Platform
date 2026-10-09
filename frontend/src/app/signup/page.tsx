"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import Link from "next/link";

import Image from "next/image";

export default function Signup() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    
    setLoading(true);
    try {
      await api.post("/auth/signup", { email, password });
      setSuccess("Clearance granted. Security profile created.");
      setTimeout(() => router.push("/login"), 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Registration failed");
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh", background: "url('/noise.png'), radial-gradient(circle at top right, var(--bg-sidebar), var(--bg-dark))" }}>
      <div style={{ width: "100%", maxWidth: "420px", padding: "1.5rem" }}>
        <div style={{ textAlign: "center", marginBottom: "2.5rem" }}>
          <div style={{ width: "80px", height: "80px", position: "relative", margin: "0 auto 1rem auto" }}>
             <Image src="/logo.png" alt="Insider Threat Detection Logo" fill style={{ objectFit: "contain", filter: "drop-shadow(0 0 10px rgba(0, 229, 255, 0.4))" }} priority />
          </div>
          <h1 style={{ fontSize: "1.75rem", fontWeight: "600", color: "#F1F5F9", letterSpacing: "-0.025em" }}>Profile Provisioning</h1>
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
            <input type="email" required value={email} onChange={e => setEmail(e.target.value)} className="input-field" placeholder="employee@itbis.local" />
          </div>
          
          <div style={{ marginBottom: "1.25rem" }}>
            <label className="input-label">Secure Password</label>
            <input type="password" required value={password} onChange={e => setPassword(e.target.value)} className="input-field" placeholder="••••••••" />
          </div>

          <div style={{ marginBottom: "1.5rem" }}>
            <label className="input-label">Confirm Password</label>
            <input type="password" required value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} className="input-field" placeholder="••••••••" />
          </div>
          
          <button type="submit" className="btn-primary" style={{ width: "100%", display: "flex", justifyContent: "center" }} disabled={loading}>
            {loading ? <div className="loader" style={{ width: "1.25rem", height: "1.25rem", borderWidth: "2px", borderTopColor: "#0B0F19", borderColor: "rgba(0,0,0,0.2)" }}></div> : "SIGN UP"}
          </button>
        </form>
        
        <p style={{ textAlign: "center", marginTop: "2rem", fontSize: "0.875rem", color: "var(--text-muted)", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
          <span>Already cleared? <Link href="/login" style={{ color: "var(--text-main)", fontWeight: "500", borderBottom: "1px solid var(--text-muted)", paddingBottom: "1px" }}>Secure Login</Link></span>
          <span><Link href="/" style={{ color: "var(--text-main)", fontWeight: "500", borderBottom: "1px solid var(--text-muted)", paddingBottom: "1px", marginTop: "1rem", display: "inline-block" }}>Back to Portal Selection</Link></span>
        </p>
      </div>
    </div>
  );
}

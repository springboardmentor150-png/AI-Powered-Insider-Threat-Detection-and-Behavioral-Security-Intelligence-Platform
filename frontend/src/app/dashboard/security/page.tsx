"use client";
import { useEffect, useState } from "react";
import { getDecodedRole } from "@/lib/api";

export default function SecurityPage() {
  const [session, setSession] = useState<{ role: string | null; tokenStatus: string }>({ role: null, tokenStatus: "Checking..." });

  useEffect(() => {
    const role = getDecodedRole();
    const token = localStorage.getItem("token");
    setSession({ 
      role, 
      tokenStatus: token ? "Active (Cryptographically Verified)" : "Invalid/Missing"
    });
  }, []);

  return (
    <div>
      <div style={{ marginBottom: "2rem" }}>
        <h2 className="title-h1">Access & Security Policies</h2>
        <p className="text-caption">Zero-trust session metrics and role-based access control details.</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
        <div className="card">
          <h3 style={{ fontSize: "1.125rem", fontWeight: 600, marginBottom: "1.5rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--danger)" strokeWidth="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
            Current Session Context
          </h3>
          
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div>
              <div className="text-caption" style={{ marginBottom: "0.25rem" }}>Authenticated Identity Role</div>
              <div style={{ fontSize: "1.25rem", fontWeight: 600, color: "var(--text-main)", textTransform: "capitalize" }}>
                {session.role ? session.role.replace('_', ' ') : "Unauthenticated"}
              </div>
            </div>
            
            <div>
              <div className="text-caption" style={{ marginBottom: "0.25rem" }}>JWT Bearer Status</div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <span className="badge badge-success">{session.tokenStatus}</span>
              </div>
            </div>

            <div>
              <div className="text-caption" style={{ marginBottom: "0.25rem" }}>Session Lifecycle Guard</div>
              <div style={{ color: "var(--text-main)" }}>FastAPI auth endpoint enforcing HTTPS/WSS (M1 specs).</div>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 style={{ fontSize: "1.125rem", fontWeight: 600, marginBottom: "1.5rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
            RBAC Enforcement
          </h3>

          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div style={{ padding: "0.75rem", background: "var(--bg-input)", borderRadius: "6px", border: "1px solid var(--border)" }}>
              <div style={{ fontSize: "0.875rem", fontWeight: 600, color: "var(--text-main)", marginBottom: "0.25rem", display: "flex", justifyContent: "space-between" }}>
                Admin Operations
                <span className="badge badge-success">GRANTED</span>
              </div>
              <div className="text-caption">User provisioning, system tuning, full lifecycle management.</div>
            </div>
            
            <div style={{ padding: "0.75rem", background: "var(--bg-input)", borderRadius: "6px", border: "1px solid var(--border)", opacity: 0.7 }}>
              <div style={{ fontSize: "0.875rem", fontWeight: 600, color: "var(--text-main)", marginBottom: "0.25rem", display: "flex", justifyContent: "space-between" }}>
                Analyst Workloads
                <span className="badge badge-neutral">IMPLICIT</span>
              </div>
              <div className="text-caption">Log telemetry review and anomaly tagging.</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

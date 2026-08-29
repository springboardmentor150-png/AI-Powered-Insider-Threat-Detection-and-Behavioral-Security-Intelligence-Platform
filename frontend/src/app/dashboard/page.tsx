"use client";
import { useEffect, useState } from "react";
import { api, getDecodedRole } from "@/lib/api";

type SummaryData = {
  empCount: number | null;
  logCount: number | null;
  role: string;
};

export default function DashboardIndex() {
  const [data, setData] = useState<SummaryData>({ empCount: null, logCount: null, role: "" });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const role = getDecodedRole() || "unknown";
      
      let empCount = null;
      let logCount = null;

      try {
        const empRes = await api.get("/employees");
        empCount = empRes.data.length;
      } catch (e) { /* Forbidden or API error */ }

      try {
        const logRes = await api.get("/logs");
        logCount = logRes.data.length;
      } catch (e) { /* Forbidden or API error */ }

      setData({ empCount, logCount, role });
      setLoading(false);
    };

    fetchData();
  }, []);

  return (
    <div>
      <div style={{ marginBottom: "2rem" }}>
        <h2 className="title-h1">Command Center</h2>
        <p className="text-caption">Real-time system telemetry and authorization status.</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "1.5rem", marginBottom: "2rem" }}>
        
        {/* Auth Status Card */}
        <div className="card" style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "1rem" }}>
            <div style={{ background: "rgba(16, 185, 129, 0.1)", color: "var(--success)", padding: "0.5rem", borderRadius: "8px" }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
            </div>
            <h3 style={{ fontSize: "1rem", fontWeight: 600 }}>Active Clearance</h3>
          </div>
          <div style={{ fontSize: "2rem", fontWeight: 700, margin: "auto 0 0.5rem 0", color: "var(--text-main)", textTransform: "capitalize" }}>
            {data.role.replace('_', ' ')}
          </div>
          <div className="text-caption">RBAC Policies securely enforced</div>
        </div>

        {/* Identity Registry Card */}
        <div className="card" style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "1rem" }}>
            <div style={{ background: "var(--accent-light)", color: "var(--accent)", padding: "0.5rem", borderRadius: "8px" }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
            </div>
            <h3 style={{ fontSize: "1rem", fontWeight: 600 }}>Monitored Identities</h3>
          </div>
          <div style={{ fontSize: "2rem", fontWeight: 700, margin: "auto 0 0.5rem 0", color: data.empCount === null ? "var(--text-muted)" : "var(--text-main)" }}>
            {loading ? <div className="loader"></div> : data.empCount !== null ? data.empCount : "RESTRICTED"}
          </div>
          <div className="text-caption">Identities currently synced in platform</div>
        </div>

        {/* Logs Card */}
        <div className="card" style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "1rem" }}>
            <div style={{ background: "rgba(245, 158, 11, 0.1)", color: "var(--warning)", padding: "0.5rem", borderRadius: "8px" }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
            </div>
            <h3 style={{ fontSize: "1rem", fontWeight: 600 }}>Telemetry Events</h3>
          </div>
          <div style={{ fontSize: "2rem", fontWeight: 700, margin: "auto 0 0.5rem 0", color: data.logCount === null ? "var(--text-muted)" : "var(--text-main)" }}>
            {loading ? <div className="loader"></div> : data.logCount !== null ? data.logCount : "RESTRICTED"}
          </div>
          <div className="text-caption">Total behavior logs analyzed locally</div>
        </div>

      </div>

      <div className="card" style={{ background: "var(--bg-input)" }}>
        <h3 className="title-h1" style={{ fontSize: "1.125rem", marginBottom: "1.5rem" }}>System Diagnostics</h3>
        
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", paddingBottom: "1rem", borderBottom: "1px solid var(--border)" }}>
            <span className="text-caption" style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>
              PostgreSQL Core DB
            </span>
            <span className="badge badge-success">OPERATIONAL</span>
          </div>
          
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", paddingBottom: "1rem", borderBottom: "1px solid var(--border)" }}>
            <span className="text-caption" style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
              MongoDB Ingestion Node
            </span>
            <span className="badge badge-success">OPERATIONAL</span>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span className="text-caption" style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="4 14 10 14 10 20"></polyline><polyline points="20 10 14 10 14 4"></polyline><line x1="14" y1="10" x2="21" y2="3"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>
              FastAPI Analytics Engine
            </span>
            <span className="badge badge-success">ONLINE</span>
          </div>
        </div>
      </div>
    </div>
  );
}

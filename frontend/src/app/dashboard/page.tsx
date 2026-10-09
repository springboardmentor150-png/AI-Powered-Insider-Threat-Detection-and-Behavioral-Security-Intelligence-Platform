"use client";
import { useEffect, useState } from "react";
import { api, getDecodedRole } from "@/lib/api";
import Link from "next/link";
import AdminDashboard from "@/components/AdminDashboard";
import ManagerDashboard from "@/components/ManagerDashboard";
import AnalystDashboard from "@/components/AnalystDashboard";
import SocDashboard from "@/components/SocDashboard";

export default function DashboardIndex() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [role, setRole] = useState("unknown");
  const [apiError, setApiError] = useState(false);

  useEffect(() => {
    const fetchSummary = async () => {
      const decodedRole = getDecodedRole() || "unknown";
      setRole(decodedRole);
      
      try {
        const res = await api.get("/dashboard/summary");
        setStats(res.data);
      } catch (e) {
        setApiError(true);
      } finally {
        setLoading(false);
      }
    };
    
    fetchSummary();
  }, []);

  if (loading) return (
    <div style={{ padding: "2rem", display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      <div style={{ width: "300px", height: "32px", background: "var(--bg-input)", borderRadius: "6px", animation: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite" }}></div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "1.5rem" }}>
        {[1,2,3,4].map(i => (
           <div key={i} className="card" style={{ height: "140px", animation: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite", background: "var(--bg-card)" }}></div>
        ))}
      </div>
    </div>
  );

  if (apiError) {
    return (
      <div style={{ padding: "3rem", textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center" }}>
        <h3 className="title-h1" style={{ fontSize: "1.25rem", color: "var(--danger)" }}>Unable to load dashboard data.</h3>
        <button onClick={() => window.location.reload()} className="btn-primary" style={{marginTop: "1rem"}}>Retry Connection</button>
      </div>
    );
  }

  const roleUpper = role.toUpperCase();
  
  if (roleUpper === "ADMIN") return <AdminDashboard stats={stats} role={roleUpper} />;
  if (roleUpper === "SECURITY_MANAGER") return <ManagerDashboard stats={stats} role={roleUpper} />;
  if (roleUpper === "SECURITY_ANALYST") return <AnalystDashboard stats={stats} role={roleUpper} />;
  if (roleUpper === "SOC_ENGINEER") return <SocDashboard stats={stats} role={roleUpper} />;

  return (
    <div className="card">
        <h3>Dashboard Component Loading (Role unmapped: {roleUpper})</h3>
    </div>
  );
}

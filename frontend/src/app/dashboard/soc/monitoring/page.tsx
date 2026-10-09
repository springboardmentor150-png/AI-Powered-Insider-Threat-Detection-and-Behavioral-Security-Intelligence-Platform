"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function SecurityMonitoring() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.get("/analytics/dashboard-stats");
        setStats(res.data);
      } catch (err) {
        setStats(null);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  return (
    <div className="soc-subpage">
      <h2 style={{ fontSize: "1.25rem", color: "#f1f5f9", marginBottom: "0.25rem", letterSpacing: "1px" }}>SECURITY MONITORING</h2>
      <p style={{ color: "#00e5ff", fontSize: "0.85rem", marginBottom: "1.5rem" }}>Operational security analytics and detection trends.</p>

      {loading ? (
        <div style={{ color: "rgba(255,255,255,0.4)" }}>Building risk profiles...</div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
           <div style={{ background: "rgba(10,16,30,0.8)", padding: "1.5rem", borderRadius: "8px", border: "1px solid rgba(255,255,255,0.05)" }}>
              <div style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 700, marginBottom: "1rem" }}>ENDPOINT ACTIVITY</div>
              <div style={{ fontSize: "2rem", color: "#f1f5f9", fontWeight: 700 }}>{stats?.recent_activities || "0"}</div>
              <div style={{ fontSize: "0.75rem", color: "#00e5ff", marginTop: "0.5rem" }}>Events recorded across all sensors.</div>
           </div>
           
           <div style={{ background: "rgba(10,16,30,0.8)", padding: "1.5rem", borderRadius: "8px", border: "1px solid rgba(255,255,255,0.05)" }}>
              <div style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 700, marginBottom: "1rem" }}>CRITICAL DETECTIONS</div>
              <div style={{ fontSize: "2rem", color: "#ef4444", fontWeight: 700 }}>{stats?.high_critical_risks || "0"}</div>
              <div style={{ fontSize: "0.75rem", color: "#ef4444", marginTop: "0.5rem" }}>High severity markers requiring triage.</div>
           </div>

           <div style={{ gridColumn: "1 / -1", background: "rgba(10,16,30,0.8)", padding: "3rem 1rem", borderRadius: "8px", border: "1px solid rgba(255,255,255,0.05)", textAlign: "center", color: "#64748b", fontSize: "0.85rem" }}>
              Insufficient historical telemetry data to generate confidence curves.
           </div>
        </div>
      )}
    </div>
  );
}

"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function SecurityAlertQueue() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await api.get("/alerts");
        setAlerts(res.data || []);
      } catch (err) {
        setAlerts([]);
      } finally {
        setLoading(false);
      }
    };
    fetchAlerts();
  }, []);

  return (
    <div className="soc-subpage">
      <h2 style={{ fontSize: "1.25rem", color: "#f1f5f9", marginBottom: "0.25rem", letterSpacing: "1px" }}>SECURITY ALERT QUEUE</h2>
      <p style={{ color: "#00e5ff", fontSize: "0.85rem", marginBottom: "1.5rem" }}>Operational alert management and triage interface.</p>

      {loading ? (
        <div style={{ color: "rgba(255,255,255,0.4)" }}>Synchronizing alerts...</div>
      ) : (
        <div style={{ display: "grid", gap: "1rem" }}>
          {alerts.map((alt, i) => (
            <div key={alt.id || i} style={{ background: "rgba(10,16,30,0.8)", padding: "1.25rem", borderRadius: "8px", border: "1px solid rgba(255,255,255,0.05)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
               <div>
                  <div style={{ fontSize: "0.75rem", color: "#64748b", marginBottom: "0.25rem" }}>ALERT ID: {alt.id || 'SYS-ALT'} • {new Date(alt.created_at || alt.timestamp).toLocaleString()}</div>
                  <div style={{ fontSize: "1rem", color: "#f1f5f9", fontWeight: 700 }}>{alt.detection_type}</div>
                  <div style={{ fontSize: "0.85rem", color: "#94a3b8", marginTop: "0.25rem" }}>Entity: {alt.employee_id} • Status: {alt.status || 'UNASSIGNED'}</div>
               </div>
               <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
                  <span style={{ fontSize: "0.8rem", fontWeight: 700, padding: "4px 10px", borderRadius: "4px", background: alt.severity === 'critical' || alt.severity === 'high' ? "rgba(239, 68, 68, 0.2)" : "rgba(245, 158, 11, 0.2)", color: alt.severity === 'critical' || alt.severity === 'high' ? "#ef4444" : "#f59e0b" }}>
                    {alt.severity?.toUpperCase()}
                  </span>
                  <button style={{ background: "transparent", border: "1px solid rgba(0,229,255,0.3)", color: "#00e5ff", padding: "0.5rem 1rem", borderRadius: "4px", fontSize: "0.75rem", fontWeight: 600, cursor: "pointer" }}>INVESTIGATE</button>
               </div>
            </div>
          ))}
          {alerts.length === 0 && <div style={{ padding: "2rem", textAlign: "center", color: "#64748b" }}>Queue is empty.</div>}
        </div>
      )}
    </div>
  );
}

"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function IncidentResponseCenter() {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchIncidents = async () => {
      try {
        const res = await api.get("/incidents");
        setIncidents(res.data || []);
      } catch (err) {
        setIncidents([]);
      } finally {
        setLoading(false);
      }
    };
    fetchIncidents();
  }, []);

  return (
    <div className="soc-subpage">
      <h2 style={{ fontSize: "1.25rem", color: "#f1f5f9", marginBottom: "0.25rem", letterSpacing: "1px" }}>INCIDENT RESPONSE CENTER</h2>
      <p style={{ color: "#00e5ff", fontSize: "0.85rem", marginBottom: "1.5rem" }}>Active security incident tracking and mitigation workflows.</p>

      {loading ? (
        <div style={{ color: "rgba(255,255,255,0.4)" }}>Loading response center...</div>
      ) : (
        <div style={{ background: "rgba(10, 16, 30, 0.6)", borderRadius: "8px", border: "1px solid rgba(0,229,255,0.1)", overflow: "hidden" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.8rem", textAlign: "left" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                <th style={{ padding: "1rem", color: "#64748b" }}>INCIDENT ID</th>
                <th style={{ padding: "1rem", color: "#64748b" }}>AFFECTED ENTITY</th>
                <th style={{ padding: "1rem", color: "#64748b" }}>SEVERITY</th>
                <th style={{ padding: "1rem", color: "#64748b" }}>STATUS</th>
                <th style={{ padding: "1rem", color: "#64748b" }}>CREATED</th>
                <th style={{ padding: "1rem", color: "#64748b" }}>ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              {incidents.map((inc, i) => (
                <tr key={inc.id || i} style={{ borderBottom: "1px solid rgba(255,255,255,0.02)" }}>
                  <td style={{ padding: "1rem", color: "#f1f5f9", fontWeight: 600 }}>INC-{inc.id}</td>
                  <td style={{ padding: "1rem", color: "#94a3b8" }}>{inc.employee_id}</td>
                  <td style={{ padding: "1rem", color: "#ef4444", fontWeight: 700 }}>{inc.severity?.toUpperCase() || 'CRITICAL'}</td>
                  <td style={{ padding: "1rem", color: inc.status === 'open' ? '#f59e0b' : '#10b981' }}>{inc.status?.toUpperCase() || 'OPEN'}</td>
                  <td style={{ padding: "1rem", color: "#64748b" }}>{new Date(inc.created_at).toLocaleString()}</td>
                  <td style={{ padding: "1rem" }}><button style={{ background: "rgba(255,255,255,0.1)", color: "#f1f5f9", border: "none", padding: "4px 8px", borderRadius: "4px", fontSize: "0.7rem", cursor: "pointer" }}>VIEW</button></td>
                </tr>
              ))}
              {incidents.length === 0 && (
                <tr><td colSpan={6} style={{ padding: "2rem", textAlign: "center", color: "#64748b" }}>No active incidents at this time.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

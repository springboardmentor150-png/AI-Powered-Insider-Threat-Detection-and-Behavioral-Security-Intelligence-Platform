"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function TelemetryStream() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await api.get("/logs");
        setLogs(res.data || []);
      } catch (err) {
        setLogs([]);
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, []);

  return (
    <div className="soc-subpage">
      <h2 style={{ fontSize: "1.25rem", color: "#f1f5f9", marginBottom: "0.25rem", letterSpacing: "1px" }}>LIVE SECURITY TELEMETRY</h2>
      <p style={{ color: "#00e5ff", fontSize: "0.85rem", marginBottom: "1.5rem" }}>Continuous monitoring stream of organizational events.</p>

      {loading ? (
        <div style={{ color: "rgba(255,255,255,0.4)" }}>Initializing telemetry stream...</div>
      ) : (
        <div style={{ background: "rgba(10, 16, 30, 0.6)", borderRadius: "8px", border: "1px solid rgba(0,229,255,0.1)", overflow: "hidden" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.8rem", textAlign: "left" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                <th style={{ padding: "1rem", color: "#64748b" }}>TIMESTAMP</th>
                <th style={{ padding: "1rem", color: "#64748b" }}>ENTITY</th>
                <th style={{ padding: "1rem", color: "#64748b" }}>EVENT TYPE</th>
                <th style={{ padding: "1rem", color: "#64748b" }}>DEVICE</th>
                <th style={{ padding: "1rem", color: "#64748b" }}>RISK/SEVERITY</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log, i) => (
                <tr key={log.id || i} style={{ borderBottom: "1px solid rgba(255,255,255,0.02)" }}>
                  <td style={{ padding: "1rem", color: "#94a3b8" }}>{new Date(log.timestamp).toLocaleString()}</td>
                  <td style={{ padding: "1rem", color: "#f1f5f9", fontWeight: 600 }}>{log.employee_id}</td>
                  <td style={{ padding: "1rem", color: "#cbd5e1" }}>{log.event_type}</td>
                  <td style={{ padding: "1rem" }}><span style={{ padding: "2px 6px", background: "rgba(255,255,255,0.05)", borderRadius: "4px" }}>{log.device_id || 'SYS'}</span></td>
                  <td style={{ padding: "1rem", color: log.severity === 'high' ? '#ef4444' : '#00e5ff', fontWeight: 700 }}>{log.severity?.toUpperCase() || 'LOW'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

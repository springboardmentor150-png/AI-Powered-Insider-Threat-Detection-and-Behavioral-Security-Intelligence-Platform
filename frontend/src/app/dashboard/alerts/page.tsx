"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import Link from "next/link";

type Alert = {
  id: number;
  employee_id: string;
  severity: string;
  message: string;
  anomaly_type: string;
  status: string;
  created_at: string;
};

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchAlerts = async () => {
    try {
      const res = await api.get("/alerts");
      setAlerts(res.data);
      setError("");
    } catch (e: any) {
      setError("Failed to fetch alerts. You may lack sufficient clearance.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  const createIncident = async (alertId: number) => {
    try {
      await api.post("/incidents", { alert_id: alertId, status: "open" });
      alert("Incident Workflow initiated successfully.");
    } catch (e) {
      alert("Failed to create incident");
    }
  };

  const updateStatus = async (alertId: number, status: string) => {
    try {
      await api.put(`/alerts/${alertId}/status?status=${status}`);
      fetchAlerts();
    } catch (e) {
      alert("Update failed");
    }
  };

  if (loading) return <div style={{ padding: "3rem" }}>Loading Alerts...</div>;

  return (
    <div>
      <div style={{ marginBottom: "2rem" }}>
        <h2 className="title-h1">Security Alerts Center</h2>
        <p className="text-caption">Review and triage detected behavioral anomalies.</p>
      </div>

      {error ? (
        <div style={{ padding: "1rem", color: "var(--danger)", border: "1px solid var(--danger)", background: "rgba(239, 68, 68, 0.1)" }}>{error}</div>
      ) : (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Time (UTC)</th>
                <th>Employee / Entity</th>
                <th>Anomaly Type</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {alerts.length === 0 ? (
                 <tr><td colSpan={6} style={{ textAlign: "center", padding: "2rem" }}>No alerts fired.</td></tr>
              ) : alerts.map(a => (
                <tr key={a.id}>
                  <td>{new Date(a.created_at).toISOString().substring(0, 19).replace('T', ' ')}</td>
                  <td><span className="badge badge-neutral">{a.employee_id}</span></td>
                  <td>{a.anomaly_type}</td>
                  <td>
                    <span className={`badge ${a.severity === 'critical' ? 'badge-danger' : a.severity === 'high' ? 'badge-warning' : 'badge-info'}`}>
                      {a.severity.toUpperCase()}
                    </span>
                  </td>
                  <td>{a.status.toUpperCase()}</td>
                  <td>
                    <div style={{ display: "flex", gap: "0.5rem" }}>
                       <Link href={`/dashboard/alerts/${a.id}`} className="btn-primary" style={{ padding: "0.25rem 0.5rem", fontSize: "0.75rem" }}>Investigate Alert</Link>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

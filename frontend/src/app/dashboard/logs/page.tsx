"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type ActivityLog = {
  _id: string;
  employee_id: string;
  event_type: string;
  timestamp: string;
  details: any;
};

export default function LogsPage() {
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");

  const fetchLogs = async () => {
    try {
      const res = await api.get("/logs/");
      setLogs(res.data);
      setError("");
    } catch (err: any) {
      if (err.response?.status === 403) {
        setError("RESTRICTED: You lack the clearance protocol to view internal telemetry.");
      } else {
        setError("System failure: Unable to fetch telemetry.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const getBadgeClass = (type: string) => {
    const t = type.toLowerCase();
    if (t.includes('login') || t.includes('auth')) return 'badge-success';
    if (t.includes('download') || t.includes('usb')) return 'badge-warning';
    if (t.includes('delete') || t.includes('drop')) return 'badge-danger';
    return 'badge-info';
  };

  const filteredLogs = logs.filter(log => 
    log.employee_id.toLowerCase().includes(searchTerm.toLowerCase()) || 
    log.event_type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: "2rem", flexWrap: "wrap", gap: "1rem" }}>
        <div>
          <h2 className="title-h1">Activity Telemetry</h2>
          <p className="text-caption">Unfiltered raw MongoDB endpoint events stream.</p>
        </div>
        
        <div style={{ position: "relative" }}>
          <svg style={{ position: "absolute", left: "10px", top: "10px", color: "var(--text-placeholder)" }} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <input 
            type="text" 
            placeholder="Filter by ID or Event..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input-field"
            style={{ paddingLeft: "2.5rem", width: "300px" }}
          />
        </div>
      </div>

      {error ? (
        <div style={{ padding: "1rem", background: "rgba(239, 68, 68, 0.1)", border: "1px solid rgba(239, 68, 68, 0.2)", borderRadius: "8px", color: "var(--danger)", display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
          {error}
        </div>
      ) : (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Timestamp (UTC)</th>
                <th>Identity Node</th>
                <th>Telemetry Protocol</th>
                <th>Payload Matrix</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={4} style={{ textAlign: "center", padding: "3rem" }}><div className="loader"></div></td></tr>
              ) : filteredLogs.length === 0 ? (
                 <tr><td colSpan={4} style={{ textAlign: "center", padding: "3rem", color: "var(--text-muted)" }}>No telemetry packets resolved.</td></tr>
              ) : filteredLogs.map(log => (
                <tr key={log._id}>
                  <td style={{ color: "var(--text-muted)", fontSize: "0.80rem", whiteSpace: "nowrap" }}>
                    {new Date(log.timestamp).toISOString().replace('T', ' ').substring(0, 19)}
                  </td>
                  <td>
                    <span className="badge badge-neutral" style={{ letterSpacing: "1px" }}>{log.employee_id}</span>
                  </td>
                  <td>
                    <span className={`badge ${getBadgeClass(log.event_type)}`}>
                      {log.event_type}
                    </span>
                  </td>
                  <td>
                    <pre style={{ margin: 0, fontSize: "0.75rem", color: "var(--accent)", background: "rgba(0,0,0,0.4)", border: "1px solid var(--border)", padding: "0.5rem 0.75rem", borderRadius: "6px", overflowX: "auto", maxWidth: "400px" }}>
                      {JSON.stringify(log.details, null, 2)}
                    </pre>
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

import Link from "next/link";

export default function ManagerDashboard({ stats, role }: { stats: any, role: string }) {
  return (
    <div>
      <div style={{ marginBottom: "2rem" }}>
        <h2 className="title-h1">Security Management Overview</h2>
        <p className="text-caption">Overview of organizational security posture and employee risk.</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1.5rem", marginBottom: "2rem" }}>
        <div className="card">
          <h3 style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>Employees Monitored</h3>
          <div style={{ fontSize: "2rem", fontWeight: "bold" }}>{stats.monitored_employees || 0}</div>
        </div>
        <div className="card" style={{ borderLeft: "4px solid var(--accent)" }}>
          <h3 style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>High-Risk Employees</h3>
          <div style={{ fontSize: "2rem", fontWeight: "bold", color: "var(--accent)" }}>{stats.high_risk_employees || 0}</div>
        </div>
        <div className="card" style={{ borderLeft: "4px solid var(--warning)" }}>
          <h3 style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>Open Incidents</h3>
          <div style={{ fontSize: "2rem", fontWeight: "bold", color: "var(--warning)" }}>{stats.open_incidents || 0}</div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: "2rem" }}>
          <h3 style={{ marginBottom: "1rem" }}>Recent Alerts & Behavioral Findings</h3>
          {stats.recent_alerts && stats.recent_alerts.length > 0 ? (
            <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "1rem" }}>
                {stats.recent_alerts.slice(0, 5).map((a: any) => (
                    <li key={a.id} style={{ display: "flex", justifyContent: "space-between", padding: "1rem", background: "var(--bg-input)", borderRadius: "6px" }}>
                        <div>
                            <strong>{a.employee_id}</strong> - {a.message}
                        </div>
                        <span className={`badge ${a.severity.toLowerCase() === 'high' ? 'badge-danger' : 'badge-warning'}`}>{a.severity}</span>
                    </li>
                ))}
            </ul>
          ) : (
             <div className="text-caption">No recent alerts.</div>
          )}
      </div>

      <div style={{ display: "flex", gap: "1rem" }}>
        <Link href="/dashboard/employees" className="btn-primary">Employee Directory</Link>
        <Link href="/dashboard/alerts" className="btn-outline">Open Alerts</Link>
        <Link href="/dashboard/incidents" className="btn-outline">Incident Reports</Link>
      </div>
    </div>
  );
}

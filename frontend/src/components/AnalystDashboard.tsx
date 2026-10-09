import Link from "next/link";

export default function AnalystDashboard({ stats, role }: { stats: any, role: string }) {
  return (
    <div>
      <div style={{ marginBottom: "2rem" }}>
        <h2 className="title-h1">Security Analyst Operations Center</h2>
        <p className="text-caption">Investigate individual security alerts and behavioral deviations.</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "1.5rem", marginBottom: "2rem" }}>
        <div className="card" style={{ borderLeft: "4px solid var(--danger)" }}>
          <h3 style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>Open Alerts</h3>
          <div style={{ fontSize: "2rem", fontWeight: "bold", color: "var(--danger)" }}>{stats.active_alerts || 0}</div>
        </div>
        <div className="card" style={{ borderLeft: "4px solid var(--warning)" }}>
          <h3 style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>Active Incidents</h3>
          <div style={{ fontSize: "2rem", fontWeight: "bold", color: "var(--warning)" }}>{stats.open_incidents || 0}</div>
        </div>
        <div className="card">
          <h3 style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>Under Investigation</h3>
          <div style={{ fontSize: "2rem", fontWeight: "bold" }}>{stats.high_risk_employees || 0}</div>
        </div>
        <div className="card">
          <h3 style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>Events Today</h3>
          <div style={{ fontSize: "2rem", fontWeight: "bold" }}>{stats.events_today || 0}</div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: "2rem" }}>
        <h3 style={{ marginBottom: "1rem" }}>Priority Investigation Queue</h3>
        {stats.recent_alerts && stats.recent_alerts.length > 0 ? (
           <table style={{ width: "100%", textAlign: "left", borderCollapse: "collapse" }}>
               <thead>
                   <tr style={{ borderBottom: "1px solid var(--border)", color: 'var(--text-muted)' }}>
                       <th style={{ padding: "0.5rem" }}>Alert ID</th>
                       <th style={{ padding: "0.5rem" }}>Employee</th>
                       <th style={{ padding: "0.5rem" }}>Anomaly Message</th>
                       <th style={{ padding: "0.5rem" }}>Severity</th>
                       <th style={{ padding: "0.5rem" }}>Status</th>
                       <th style={{ padding: "0.5rem" }}>Action</th>
                   </tr>
               </thead>
               <tbody>
                   {stats.recent_alerts.filter((a:any) => a.status !== 'resolved').slice(0, 10).map((a: any) => (
                       <tr key={a.id} style={{ borderBottom: "1px solid var(--border)" }}>
                           <td style={{ padding: "0.75rem 0.5rem" }}>ALT-{a.id}</td>
                           <td style={{ padding: "0.75rem 0.5rem" }}>{a.employee_id}</td>
                           <td style={{ padding: "0.75rem 0.5rem" }}>{a.message}</td>
                           <td style={{ padding: "0.75rem 0.5rem" }}>
                               <span className={`badge ${a.severity.toLowerCase() === 'high' ? 'badge-danger' : 'badge-warning'}`}>{a.severity}</span>
                           </td>
                           <td style={{ padding: "0.75rem 0.5rem" }}>{a.status}</td>
                           <td style={{ padding: "0.75rem 0.5rem" }}>
                               <Link href={`/dashboard/alerts/${a.id}`} className="btn-outline" style={{ padding: "0.25rem 0.5rem", fontSize: "0.75rem" }}>Investigate</Link>
                           </td>
                       </tr>
                   ))}
               </tbody>
           </table>
        ) : (
            <div className="text-caption">No pending alerts requiring investigation.</div>
        )}
      </div>

      <div style={{ display: "flex", gap: "1rem" }}>
        <Link href="/dashboard/alerts" className="btn-primary">View All Alerts</Link>
        <Link href="/dashboard/employees" className="btn-outline">Analyze Behaviors</Link>
        <Link href="/dashboard/logs" className="btn-outline">View Activity Logs</Link>
      </div>
    </div>
  );
}

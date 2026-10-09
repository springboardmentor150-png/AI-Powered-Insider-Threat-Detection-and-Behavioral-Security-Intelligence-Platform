import Link from "next/link";

export default function AdminDashboard({ stats, role }: { stats: any, role: string }) {
  return (
    <div>
      <div style={{ marginBottom: "2rem", display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
        <div>
          <h2 className="title-h1">Platform Command Center</h2>
          <p className="text-caption">Administrative oversight and global platform telemetry.</p>
        </div>
        <div className="badge badge-success">System Health: {stats.system_health || 'Stable'}</div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "1.5rem", marginBottom: "1.5rem" }}>
        <div className="card">
          <h3 style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>Platform Users</h3>
          <div style={{ fontSize: "2rem", fontWeight: "bold" }}>{stats.total_users || 0}</div>
        </div>
        <div className="card">
          <h3 style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>Monitored Employees</h3>
          <div style={{ fontSize: "2rem", fontWeight: "bold" }}>{stats.monitored_employees || 0}</div>
        </div>
        <div className="card">
          <h3 style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>Telemetry Events</h3>
          <div style={{ fontSize: "2rem", fontWeight: "bold" }}>{stats.telemetry_events || 0}</div>
        </div>
        <div className="card">
          <h3 style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>Events Today</h3>
          <div style={{ fontSize: "2rem", fontWeight: "bold" }}>{stats.events_today || 0}</div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1.5rem", marginBottom: "2rem" }}>
        <div className="card" style={{ borderLeft: "4px solid var(--danger)" }}>
          <h3 style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>Active Alerts</h3>
          <div style={{ fontSize: "2rem", fontWeight: "bold", color: "var(--danger)" }}>{stats.active_alerts || 0}</div>
        </div>
        <div className="card" style={{ borderLeft: "4px solid var(--warning)" }}>
          <h3 style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>Open Incidents</h3>
          <div style={{ fontSize: "2rem", fontWeight: "bold", color: "var(--warning)" }}>{stats.open_incidents || 0}</div>
        </div>
        <div className="card" style={{ borderLeft: "4px solid var(--accent)" }}>
          <h3 style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>High-Risk Employees</h3>
          <div style={{ fontSize: "2rem", fontWeight: "bold", color: "var(--accent)" }}>{stats.high_risk_employees || 0}</div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "1.5rem", marginBottom: "2rem" }}>
         <div className="card">
             <h3 style={{ marginBottom: "1rem" }}>Risk Distribution</h3>
             <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                 <li style={{ display: "flex", justifyContent: "space-between" }}><span>Low Risk</span> <span className="badge badge-success">{stats.risk_distribution?.low || 0}</span></li>
                 <li style={{ display: "flex", justifyContent: "space-between" }}><span>Medium Risk</span> <span className="badge badge-warning">{stats.risk_distribution?.medium || 0}</span></li>
                 <li style={{ display: "flex", justifyContent: "space-between" }}><span>High Risk</span> <span className="badge badge-danger" style={{background: 'orange'}}>{stats.risk_distribution?.high || 0}</span></li>
                 <li style={{ display: "flex", justifyContent: "space-between" }}><span>Critical Risk</span> <span className="badge badge-danger">{stats.risk_distribution?.critical || 0}</span></li>
             </ul>
         </div>
      </div>

      <div className="card" style={{ marginBottom: "2rem" }}>
        <h3 style={{ marginBottom: "1rem" }}>Recent Security Alerts</h3>
        {stats.recent_alerts && stats.recent_alerts.length > 0 ? (
           <table style={{ width: "100%", textAlign: "left", borderCollapse: "collapse" }}>
               <thead>
                   <tr style={{ borderBottom: "1px solid var(--border)" }}>
                       <th style={{ padding: "0.5rem" }}>ID</th>
                       <th style={{ padding: "0.5rem" }}>Employee</th>
                       <th style={{ padding: "0.5rem" }}>Severity</th>
                       <th style={{ padding: "0.5rem" }}>Status</th>
                   </tr>
               </thead>
               <tbody>
                   {stats.recent_alerts.slice(0, 5).map((a: any) => (
                       <tr key={a.id} style={{ borderBottom: "1px solid var(--border)" }}>
                           <td style={{ padding: "0.75rem 0.5rem" }}>ALT-{a.id}</td>
                           <td style={{ padding: "0.75rem 0.5rem" }}>{a.employee_id}</td>
                           <td style={{ padding: "0.75rem 0.5rem" }}>
                               <span className={`badge ${a.severity.toLowerCase() === 'high' ? 'badge-danger' : 'badge-warning'}`}>{a.severity}</span>
                           </td>
                           <td style={{ padding: "0.75rem 0.5rem" }}>{a.status}</td>
                       </tr>
                   ))}
               </tbody>
           </table>
        ) : (
            <div className="text-caption">No recent alerts.</div>
        )}
      </div>

      <div style={{ display: "flex", gap: "1rem" }}>
        <Link href="/dashboard/users" className="btn-primary">Manage Users</Link>
        <Link href="/dashboard/employees" className="btn-outline">Manage Employees</Link>
        <Link href="/dashboard/simulator" className="btn-outline">Launch Simulator</Link>
      </div>
    </div>
  );
}

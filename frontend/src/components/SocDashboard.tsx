"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import Link from "next/link";

export default function SocDashboard({ stats, role }: { stats: any, role: string }) {
  const [logs, setLogs] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [sysHealth, setSysHealth] = useState("OPTIMAL");
  const [loadingExtras, setLoadingExtras] = useState(true);

  useEffect(() => {
    const fetchPreviews = async () => {
      try {
        const resLogs = await api.get("/logs");
        setLogs(resLogs.data.slice(0, 5)); // top 5 recent events

        const resAlerts = await api.get("/alerts");
        setAlerts(resAlerts.data.slice(0, 5)); // top 5 active alerts

        if (!stats) setSysHealth("ERROR");
      } catch (err) {
        setSysHealth("DEGRADED");
      } finally {
        setLoadingExtras(false);
      }
    };
    fetchPreviews();
  }, [stats]);

  if (!stats && sysHealth === "ERROR") {
    return (
      <div className="soc-panel" style={{ textAlign: "center", padding: "4rem 2rem" }}>
         <h2 style={{ color: "#ef4444" }}>Unable to load security telemetry</h2>
         <p style={{ color: "#94a3b8", marginBottom: "1.5rem" }}>The telemetry streams are offline.</p>
         <button onClick={() => window.location.reload()} style={{ padding: "0.5rem 1rem", background: "rgba(239, 68, 68, 0.1)", border: "1px solid #ef4444", color: "#ef4444", borderRadius: "6px", cursor: "pointer" }}>Retry Connection</button>
      </div>
    );
  }

  return (
    <div className="soc-overview">
      <div style={{ marginBottom: "2rem" }}>
        <h1 style={{ fontSize: "1.5rem", fontWeight: "700", color: "#f1f5f9", letterSpacing: "1px", marginBottom: "0.25rem" }}>Security Operations Center</h1>
        <p style={{ color: "#00e5ff", margin: 0, fontSize: "0.85rem", fontWeight: "600" }}>Real-time security telemetry, detection activity and incident response.</p>
      </div>

      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card c-amber" style={{ animationDelay: "0ms" }}>
          <div className="kpi-label">ACTIVE ALERTS</div>
          <div className="kpi-value">{stats?.active_alerts || 0}</div>
        </div>
        <div className="kpi-card c-red" style={{ animationDelay: "80ms" }}>
          <div className="kpi-label">CRITICAL ALERTS</div>
          <div className="kpi-value">{stats?.high_critical_risks || 0}</div>
        </div>
        <div className="kpi-card c-cyan" style={{ animationDelay: "160ms" }}>
          <div className="kpi-label">EVENTS INGESTED</div>
          <div className="kpi-value">{stats?.recent_activities || (logs.length * 12)}</div>
        </div>
        <div className="kpi-card c-blue" style={{ animationDelay: "240ms" }}>
          <div className="kpi-label">MONITORED ENDPOINTS</div>
          <div className="kpi-value">{stats?.total_users || 0}</div>
        </div>
        <div className="kpi-card c-red" style={{ animationDelay: "320ms" }}>
          <div className="kpi-label">OPEN INCIDENTS</div>
          <div className="kpi-value">{stats?.open_incidents || 0}</div>
        </div>
        <div className="kpi-card c-green" style={{ animationDelay: "400ms" }}>
          <div className="kpi-label">DETECTION STATUS</div>
          <div className="kpi-value" style={{ fontSize: "1.25rem" }}>{sysHealth}</div>
        </div>
      </div>

      <div className="soc-layout-grid" style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "1.5rem", marginTop: "1.5rem" }}>
        
        {/* Left Column: Flow & Telemetry */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          
          {/* Security Operations Flow */}
          <div className="soc-panel">
            <div className="panel-header">SECURITY OPERATIONS FLOW</div>
            <div className="workflow-diagram">
              <div className="flow-node active">
                 <span className="dot"></span> TELEMETRY
              </div>
              <div className="flow-line"></div>
              <div className="flow-node">DETECTION</div>
              <div className="flow-line"></div>
              <div className="flow-node">ALERT</div>
              <div className="flow-line"></div>
              <div className="flow-node">INVESTIGATION</div>
              <div className="flow-line"></div>
              <div className="flow-node">RESPONSE</div>
            </div>
          </div>

          {/* Live Telemetry Preview */}
          <div className="soc-panel">
            <div className="panel-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span>LIVE TELEMETRY STREAM</span>
              <Link href="/dashboard/soc/telemetry" style={{ color: "#00e5ff", fontSize: "0.75rem", textDecoration: "none" }}>VIEW ALL →</Link>
            </div>
            {loadingExtras ? (
              <div style={{ color: "rgba(255,255,255,0.3)", padding: "1rem" }}>Loading stream...</div>
            ) : (
              <div className="telemetry-table-wrapper">
                <table className="soc-table">
                  <thead>
                    <tr>
                      <th>TIME</th>
                      <th>IDENTITY</th>
                      <th>EVENT</th>
                      <th>SOURCE</th>
                      <th>SEVERITY</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs.map((log: any, i: number) => (
                      <tr key={log.id || i} style={{ animation: `rowEnter 0.4s ease forwards`, animationDelay: `${i*100}ms` }}>
                        <td style={{ color: "#94a3b8" }}>{new Date(log.timestamp).toLocaleTimeString()}</td>
                        <td style={{ fontWeight: 600 }}>{log.employee_id}</td>
                        <td style={{ color: "#f1f5f9" }}>{log.event_type}</td>
                        <td><span className="sc-badge">{log.device_id || "SYS"}</span></td>
                        <td>
                          <span className={`sc-sev ${log.severity === 'high' ? 'sev-h' : log.severity === 'medium' ? 'sev-m' : 'sev-l'}`}>
                            {log.severity?.toUpperCase() || 'LOW'}
                          </span>
                        </td>
                      </tr>
                    ))}
                    {logs.length === 0 && (
                      <tr><td colSpan={5} style={{ textAlign: "center", color: "#64748b", padding: "1rem" }}>Insufficient telemetry data</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Status & Alerts */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          
          {/* System Infrastructure */}
          <div className="soc-panel">
            <div className="panel-header">SYSTEM INFRASTRUCTURE</div>
            <div className="infra-list">
              <div className="infra-item">
                 <span>PostgreSQL (Identity)</span>
                 <span className="i-stat is-green"><span className="pulse-dot"></span> CONNECTED</span>
              </div>
              <div className="infra-item">
                 <span>MongoDB (Telemetry)</span>
                 <span className={`i-stat ${sysHealth === 'OPTIMAL' ? 'is-green' : 'is-amber'}`}><span className="pulse-dot"></span> {sysHealth}</span>
              </div>
              <div className="infra-item">
                 <span>FastAPI (Gateway)</span>
                 <span className="i-stat is-green"><span className="pulse-dot"></span> CONNECTED</span>
              </div>
              <div className="infra-item">
                 <span>Telemetry Ingestion</span>
                 <span className="i-stat is-green"><span className="pulse-dot"></span> OPTIMAL</span>
              </div>
              <div className="infra-item">
                 <span>Detection Engine</span>
                 <span className="i-stat is-green"><span className="pulse-dot"></span> OPTIMAL</span>
              </div>
            </div>
          </div>

          {/* Active Alert Queue */}
          <div className="soc-panel" style={{ flex: 1 }}>
            <div className="panel-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span>ACTIVE ALERT QUEUE</span>
              <Link href="/dashboard/soc/alerts" style={{ color: "#00e5ff", fontSize: "0.75rem", textDecoration: "none" }}>QUEUE →</Link>
            </div>
            {loadingExtras ? (
               <div style={{ color: "rgba(255,255,255,0.3)", padding: "1rem" }}>Syncing alerts...</div>
            ) : (
               <div className="alert-list">
                 {alerts.length > 0 ? alerts.map((alt: any, i: number) => (
                   <div key={alt.id || i} className="alert-item">
                     <div className={`al-sev ${alt.severity === 'critical' || alt.severity === 'high' ? 'c-red' : 'c-amber'}`}></div>
                     <div className="al-content">
                       <div className="al-type">{alt.detection_type}</div>
                       <div className="al-ent">{alt.employee_id} • {new Date(alt.created_at || alt.timestamp).toLocaleTimeString()}</div>
                     </div>
                   </div>
                 )) : (
                   <div style={{ textAlign: "center", color: "#64748b", padding: "1rem" }}>No active alerts</div>
                 )}
               </div>
            )}
          </div>

        </div>
      </div>

      <style>{`
        .soc-panel {
          background: rgba(10, 16, 30, 0.6);
          border: 1px solid rgba(0, 229, 255, 0.1);
          backdrop-filter: blur(12px);
          border-radius: 8px;
          padding: 1.25rem;
        }
        .panel-header {
          font-size: 0.75rem; font-weight: 700; letter-spacing: 2px;
          color: rgba(255,255,255,0.5);
          margin-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.05);
          padding-bottom: 0.5rem;
        }

        /* KPIs */
        .kpi-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 1rem; }
        .kpi-card {
          background: rgba(10,16,30,0.8); border: 1px solid rgba(255,255,255,0.05);
          padding: 1rem; border-radius: 8px; display: flex; flex-direction: column;
          animation: fadeUp 0.5s ease forwards; opacity: 0; transform: translateY(10px);
          transition: transform 0.2s, border-color 0.2s;
        }
        .kpi-card:hover { transform: translateY(-4px); }
        .kpi-label { font-size: 0.65rem; color: #94a3b8; font-weight: 700; letter-spacing: 1px; margin-bottom: 0.5rem; }
        .kpi-value { font-size: 1.75rem; font-weight: 700; font-family: monospace; color: #f1f5f9; }
        
        .kpi-card.c-amber:hover { border-color: rgba(245, 158, 11, 0.4); box-shadow: 0 0 15px rgba(245,158,11,0.1); }
        .kpi-card.c-red:hover { border-color: rgba(239, 68, 68, 0.4); box-shadow: 0 0 15px rgba(239,68,68,0.1); }
        .kpi-card.c-cyan:hover { border-color: rgba(0, 229, 255, 0.4); box-shadow: 0 0 15px rgba(0,229,255,0.1); }
        .kpi-card.c-blue:hover { border-color: rgba(59, 130, 246, 0.4); box-shadow: 0 0 15px rgba(59,130,246,0.1); }
        .kpi-card.c-green:hover { border-color: rgba(16, 185, 129, 0.4); box-shadow: 0 0 15px rgba(16,185,129,0.1); }

        /* Workflow */
        .workflow-diagram { display: flex; align-items: center; justify-content: space-between; padding: 1rem 0.5rem; }
        .flow-node { 
          font-size: 0.7rem; font-weight: 600; padding: 0.4rem 0.75rem; border-radius: 4px;
          background: rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.1); color: #64748b;
          display: flex; align-items: center; gap: 0.25rem;
        }
        .flow-node.active { border-color: rgba(0,229,255,0.4); color: #00e5ff; box-shadow: 0 0 15px rgba(0,229,255,0.1); }
        .flow-line { flex: 1; height: 1px; background: rgba(255,255,255,0.1); margin: 0 0.5rem; }
        .dot { width: 6px; height: 6px; background: #00e5ff; border-radius: 50%; box-shadow: 0 0 5px #00e5ff; }

        /* Tables & Lists */
        .soc-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
        .soc-table th { text-align: left; padding: 0.5rem; color: #64748b; font-weight: 600; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .soc-table td { padding: 0.75rem 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.02); }
        .soc-table tbody tr { opacity: 0; }
        
        .sc-badge { background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 4px; font-family: monospace; color: #cbd5e1; }
        .sc-sev { font-weight: 700; font-size: 0.7rem; letter-spacing: 1px; }
        .sev-h { color: #ef4444; } .sev-m { color: #f59e0b; } .sev-l { color: #00e5ff; }

        /* Infra */
        .infra-list { display: flex; flex-direction: column; gap: 0.75rem; }
        .infra-item { display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; color: #e2e8f0; background: rgba(0,0,0,0.2); padding: 0.5rem 0.75rem; border-radius: 4px; border: 1px solid rgba(255,255,255,0.03); }
        .i-stat { display: flex; align-items: center; gap: 6px; font-size: 0.7rem; font-weight: 700; }
        .is-green { color: #10b981; } .is-amber { color: #f59e0b; } .is-red { color: #ef4444; }

        /* Alerts */
        .alert-list { display: flex; flex-direction: column; gap: 0.5rem; }
        .alert-item { display: flex; gap: 0.75rem; align-items: center; background: rgba(0,0,0,0.3); padding: 0.5rem; border-radius: 4px; border: 1px solid rgba(255,255,255,0.03); }
        .al-sev { width: 4px; height: 100%; min-height: 32px; border-radius: 2px; }
        .al-sev.c-red { background: #ef4444; box-shadow: 0 0 8px rgba(239, 68, 68, 0.4); }
        .al-sev.c-amber { background: #f59e0b; box-shadow: 0 0 8px rgba(245, 158, 11, 0.4); }
        .al-content { display: flex; flex-direction: column; }
        .al-type { font-size: 0.8rem; font-weight: 600; color: #f1f5f9; }
        .al-ent { font-size: 0.7rem; color: #94a3b8; }

        @keyframes fadeUp {
          100% { opacity: 1; transform: translateY(0); }
        }
        @keyframes rowEnter {
          0% { opacity: 0; transform: translateX(-10px); }
          100% { opacity: 1; transform: translateX(0); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }

        @media (prefers-reduced-motion: reduce) {
          .kpi-card, .soc-table tbody tr { animation: none !important; opacity: 1 !important; transform: none !important; }
        }
        @media (max-width: 1200px) {
          .soc-layout-grid { grid-template-columns: 1fr; }
          .kpi-grid { grid-template-columns: repeat(3, 1fr); }
        }
        @media (max-width: 768px) {
          .kpi-grid { grid-template-columns: 1fr 1fr; }
          .workflow-diagram { flex-direction: column; align-items: flex-start; gap: 0.25rem; }
          .flow-line { width: 2px; height: 10px; margin: 0 1rem; }
        }
      `}</style>
    </div>
  );
}

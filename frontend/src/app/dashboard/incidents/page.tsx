"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import Link from "next/link";
import { getDecodedRole } from "@/lib/api";

export default function IncidentsDashboard() {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [role, setRole] = useState("unknown");

  useEffect(() => {
    const r = getDecodedRole();
    setRole(r || "unknown");

    const fetchIncidents = async () => {
      try {
        const res = await api.get("/incidents");
        setIncidents(res.data);
      } catch (e) {
        console.error("Failed to load incidents");
      }
      setLoading(false);
    };
    fetchIncidents();
  }, []);

  const handleUpdateStatus = async (id: number, currentStatus: string) => {
      const newStatus = currentStatus === "open" ? "investigating" : "resolved";
      try {
          await api.put(`/incidents/${id}?status=${newStatus}`);
          setIncidents(incidents.map(i => i.id === id ? { ...i, status: newStatus } : i));
      } catch (e) {
          alert("Failed to update status");
      }
  };

  if (loading) return <div>Loading Incidents...</div>;

  return (
    <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
         <div>
            <h2 className="title-h1">Incident Workflows</h2>
            <div className="text-caption">Manage and track security investigations.</div>
         </div>
      </div>

      <div className="card">
        {incidents.length > 0 ? (
           <table style={{ width: "100%", textAlign: "left", borderCollapse: "collapse" }}>
               <thead>
                   <tr style={{ borderBottom: "1px solid var(--border)", color: 'var(--text-muted)' }}>
                       <th style={{ padding: "0.75rem", paddingLeft: 0 }}>Incident ID</th>
                       <th style={{ padding: "0.75rem" }}>Alert Ref</th>
                       <th style={{ padding: "0.75rem" }}>Assigned To</th>
                       <th style={{ padding: "0.75rem" }}>Status</th>
                       <th style={{ padding: "0.75rem" }}>Created At</th>
                       <th style={{ padding: "0.75rem" }}>Actions</th>
                   </tr>
               </thead>
               <tbody>
                   {incidents.map((i: any) => (
                       <tr key={i.id} style={{ borderBottom: "1px solid var(--border)" }}>
                           <td style={{ padding: "1rem", paddingLeft: 0 }}><strong>INC-{i.id}</strong></td>
                           <td style={{ padding: "1rem" }}>
                               <Link href={`/dashboard/alerts/${i.alert_id}`} className="text-caption" style={{ textDecoration: "underline", color: "var(--accent)" }}>
                                   ALT-{i.alert_id}
                               </Link>
                           </td>
                           <td style={{ padding: "1rem" }}>UID: {i.assigned_to || "Unassigned"}</td>
                           <td style={{ padding: "1rem" }}>
                               <span className={`badge ${i.status === 'resolved' ? 'badge-success' : (i.status === 'investigating' ? 'badge-warning' : 'badge-danger')}`}>
                                   {i.status.toUpperCase()}
                               </span>
                           </td>
                           <td style={{ padding: "1rem" }} className="text-caption">
                               {new Date(i.created_at).toLocaleString()}
                           </td>
                           <td style={{ padding: "1rem" }}>
                               {i.status !== "resolved" && (
                                   <button onClick={() => handleUpdateStatus(i.id, i.status)} className="btn-outline" style={{ padding: "0.25rem 0.5rem", fontSize: "0.75rem" }}>
                                       {i.status === "open" ? "Start Investigation" : "Mark Resolved"}
                                   </button>
                               )}
                           </td>
                       </tr>
                   ))}
               </tbody>
           </table>
        ) : (
            <div style={{ textAlign: "center", padding: "3rem 1rem", color: "var(--text-muted)" }}>
               <svg style={{ margin: "0 auto 1rem auto" }} width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1"><path d="M12 22L12 16"></path><path d="M12 8L12 12"></path><circle cx="12" cy="12" r="10"></circle></svg>
               <h3 style={{ fontSize: "1.125rem", marginBottom: "0.5rem" }}>No Incidents Found</h3>
               <p style={{ maxWidth: "400px", margin: "0 auto" }}>There are currently no active incidents mapped to your role context.</p>
            </div>
        )}
      </div>
    </div>
  );
}

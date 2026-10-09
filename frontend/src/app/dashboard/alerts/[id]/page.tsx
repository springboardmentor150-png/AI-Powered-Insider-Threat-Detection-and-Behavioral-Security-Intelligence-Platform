"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useParams, useRouter } from "next/navigation";

export default function AlertInvestigation() {
  const router = useRouter();
  const { id } = useParams();
  const [alert, setAlert] = useState<any>(null);
  const [employee, setEmployee] = useState<any>(null);
  const [evidence, setEvidence] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [escalating, setEscalating] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const alertsResp = await api.get("/alerts");
        const foundAlert = alertsResp.data.find((a:any) => a.id.toString() === id);
        if (foundAlert) {
            setAlert(foundAlert);
            
            const empRes = await api.get("/employees");
            setEmployee(empRes.data.find((e:any) => e.employee_id === foundAlert.employee_id));

            const evidenceRes = await api.get(`/analytics/anomalies/${foundAlert.employee_id}`);
            setEvidence(evidenceRes.data.filter((e:any) => e.type === foundAlert.anomaly_type));
        }
      } catch (err) {}
      setLoading(false);
    };
    fetchData();
  }, [id]);

  const handleEscalate = async () => {
      setEscalating(true);
      try {
          await api.post("/incidents", { alert_id: alert.id, status: "open", notes: "Escalated from manual review" });
          window.alert("Incident Created successfully! Check the Incidents dashboard.");
          router.push("/dashboard/incidents");
      } catch (e) {
          window.alert("Failed to escalate: Incident may already exist or backend error.");
      } finally {
          setEscalating(false);
      }
  };

  if (loading) return <div>Loading Alert Data...</div>;
  if (!alert) return <div>Alert not found or access denied.</div>;

  return (
    <div style={{ maxWidth: "1000px", margin: "0 auto" }}>
      <button onClick={() => router.back()} className="btn-outline" style={{ marginBottom: "1.5rem" }}>&larr; Back</button>
      
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
         <div>
            <h2 className="title-h1">Alert Investigation: ALT-{alert.id}</h2>
            <div className="text-caption">Review evidence and determine escalation path.</div>
         </div>
         <div className={`badge ${alert.severity.toLowerCase() === 'high' ? 'badge-danger' : 'badge-warning'}`} style={{ fontSize: "1rem" }}>
             {alert.severity} SEVERITY
         </div>
      </div>

      <div className="card" style={{ marginBottom: "2rem" }}>
         <h3 style={{ marginBottom: "1rem" }}>Flagged Subject: {alert.employee_id}</h3>
         {employee && (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1.5rem", padding: "1rem", background: "var(--bg-input)", borderRadius: "6px" }}>
              <div><strong>Name:</strong> {employee.name}</div>
              <div><strong>Department:</strong> {employee.department}</div>
              <div><strong>Designation:</strong> {employee.designation}</div>
              <div><strong>Access Level:</strong> {employee.access_privileges}</div>
            </div>
         )}
         <button onClick={() => router.push(`/dashboard/employees/${alert.employee_id}`)} className="btn-outline">View Full Behavioral Profile</button>
      </div>

      <div className="card" style={{ marginBottom: "2rem", borderLeft: "4px solid var(--danger)" }}>
         <h3 style={{ color: "var(--danger)", marginBottom: "1rem" }}>Security Detection Evidence</h3>
         <div style={{ fontWeight: 600, fontSize: "1.125rem", marginBottom: "0.5rem" }}>{alert.anomaly_type || alert.message}</div>
         <div className="text-caption" style={{ marginBottom: "1.5rem" }}>{alert.message}</div>
         
         <h4 style={{ marginBottom: "0.5rem" }}>Why was this flagged?</h4>
         <div style={{ background: "var(--bg-input)", padding: "1rem", borderRadius: "6px", fontFamily: "monospace" }}>
             {evidence.length > 0 ? (
                 evidence.map((ev, i) => <div key={i}>[{new Date(ev.detected_at).toISOString()}] {ev.message}</div>)
             ) : (
                 <div>Standard deviation exceeded on base metrics. Refer to raw logs.</div>
             )}
         </div>
      </div>

      <div style={{ display: "flex", gap: "1rem", justifyContent: "flex-end" }}>
          <button className="btn-outline">Mark as False Positive (Resolve)</button>
          <button className="btn-primary" onClick={handleEscalate} disabled={escalating}>
              {escalating ? 'Escalating...' : 'ESCALATE TO INCIDENT'}
          </button>
      </div>
    </div>
  );
}

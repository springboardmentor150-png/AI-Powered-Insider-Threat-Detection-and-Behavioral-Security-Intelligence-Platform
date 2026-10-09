"use client";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";

export default function SecurityEventSimulator() {
  const [employees, setEmployees] = useState<any[]>([]);
  const [employeeId, setEmployeeId] = useState("");
  const [eventType, setEventType] = useState("login");
  const [detailsStr, setDetailsStr] = useState('{\n  "device": "Macbook",\n  "ip": "192.168.1.10"\n}');
  
  const [status, setStatus] = useState({ type: "", message: "" });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Fetch employees for dropdown
    api.get("/employees").then(res => {
      setEmployees(res.data);
      if (res.data.length > 0) setEmployeeId(res.data[0].employee_id);
    }).catch(() => {
        // Fallback for demo if users aren't loaded or permission denied
        setEmployees([{ employee_id: "EMP-RISK-999", name: "Charlie Risk" }, {employee_id: "EMP-001", name: "Alice Smith"}]);
        setEmployeeId("EMP-RISK-999");
    });
  }, []);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus({ type: "", message: "" });
    setLoading(true);

    try {
      let parsedDetails = {};
      try {
        parsedDetails = JSON.parse(detailsStr);
      } catch (err) {
        throw new Error("Invalid JSON in Details field");
      }

      await api.post("/logs/ingest", {
        employee_id: employeeId,
        event_type: eventType,
        details: parsedDetails
      });
      
      // Also optionally trigger anomaly detection immediately for demo purposes
      await api.post(`/analytics/anomalies/${employeeId}`);
      await api.post(`/analytics/risk-score/${employeeId}`);

      setStatus({ type: "success", message: `Generated ${eventType} event successfully and triggered pipeline.` });
    } catch (error: any) {
      const apiDetail = error.response?.data?.detail || error.message || "Failed to generate event";
      setStatus({ type: "error", message: apiDetail });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card" style={{ maxWidth: "800px", margin: "0 auto" }}>
      <h2 style={{ marginBottom: "0.5rem", color: "var(--accent)" }}>Security Event Simulator</h2>
      <p style={{ color: "var(--text-muted)", marginBottom: "2rem", fontSize: "0.875rem" }}>
        Inject artificial activity telemetry into the platform for demonstration purposes. This simulates agent endpoints sending data.
      </p>

      {status.message && (
        <div className={`badge ${status.type === 'error' ? 'badge-danger' : 'badge-success'}`} style={{ marginBottom: "1.5rem", display: "block", textAlign: "center", padding: "1rem" }}>
          {status.message}
        </div>
      )}

      <form onSubmit={handleGenerate} style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
        <div style={{ display: "flex", gap: "1.5rem" }}>
          <div className="form-group" style={{ flex: 1 }}>
            <label>Target Employee Entity</label>
            <select value={employeeId} onChange={e => setEmployeeId(e.target.value)} className="input-field" required>
              {employees.map(emp => (
                <option key={emp.employee_id} value={emp.employee_id}>{emp.name} ({emp.employee_id})</option>
              ))}
            </select>
          </div>
          
          <div className="form-group" style={{ flex: 1 }}>
            <label>Event Classification</label>
            <select value={eventType} onChange={e => setEventType(e.target.value)} className="input-field" required>
              <option value="login">Login / Authentication</option>
              <option value="file_download">File Download (Mass)</option>
              <option value="usb_activity">USB / Peripheral Connect</option>
              <option value="file_access">Resource Access</option>
              <option value="application_usage">Suspicious Application</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label>Event Details Payload (JSON)</label>
          <textarea 
            value={detailsStr} 
            onChange={e => setDetailsStr(e.target.value)} 
            className="input-field" 
            style={{ height: "150px", fontFamily: "monospace" }} 
            required
          />
        </div>

        <button type="submit" className="btn-primary" disabled={loading} style={{ alignSelf: "flex-end" }}>
          {loading ? "Generating..." : "Inject Security Event"}
        </button>
      </form>
    </div>
  );
}

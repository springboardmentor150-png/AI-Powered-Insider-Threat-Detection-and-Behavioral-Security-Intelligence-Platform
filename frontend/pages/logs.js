import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import axios from "axios";

export default function Logs() {
  const router = useRouter();
  const [role, setRole] = useState("");
  const [form, setForm] = useState({
    employee_id: "EMP1001",
    event_type: "login",
    details: '{\n  "ip_address": "192.168.1.10",\n  "device": "laptop-01"\n}',
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [logs, setLogs] = useState([]);

  const getAuth = () => ({
    headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
  });

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) { router.push("/login"); return; }
    setRole(localStorage.getItem("role"));
  }, []);

  const handleIngest = async (e) => {
    e.preventDefault();
    setError(""); setSuccess("");
    try {
      const parsedDetails = JSON.parse(form.details);
      const res = await axios.post(
        "http://localhost:8000/logs/ingest",
        { employee_id: form.employee_id, event_type: form.event_type, details: parsedDetails },
        getAuth()
      );
      setSuccess(`Log ingested (ID: ${res.data.log_id})`);
      setLogs([...logs, { employee_id: form.employee_id, event_type: form.event_type, details: parsedDetails }]);
    } catch (err) {
      if (err instanceof SyntaxError) {
        setError("Invalid JSON in details field");
      } else {
        setError(err.response?.data?.detail || "Failed to ingest log");
      }
    }
  };

  const templates = {
    login: '{\n  "ip_address": "192.168.1.10",\n  "device": "laptop-01",\n  "location": "Bengaluru Office"\n}',
    file_download: '{\n  "file_name": "confidential_report.pdf",\n  "size_mb": 4.2,\n  "source_system": "SharePoint"\n}',
    usb_connect: '{\n  "device_name": "USB Drive",\n  "device_id": "USB-12345"\n}',
    email_sent: '{\n  "recipient": "external@example.com",\n  "subject": "Project Files",\n  "attachment_count": 2\n}',
  };

  return (
    <>
      <nav className="nav">
        <strong>ITBIS</strong>
        <a href="/dashboard">Dashboard</a>
        {(role === "admin" || role === "security_analyst" || role === "soc_engineer") && (
          <a href="/employees">Employees</a>
        )}
        <a href="/logs">Activity Logs</a>
        <span className="spacer" />
        <span style={{ fontSize: "13px", color: "#666" }}>Role: {role}</span>
      </nav>
      <div className="container">
        <h1>Activity Log Ingestion</h1>
        {error && <p className="error">{error}</p>}
        {success && <p className="success">{success}</p>}

        <div className="card">
          <h2>Ingest a Log</h2>
          <form onSubmit={handleIngest}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
              <div className="form-group">
                <label>Employee ID</label>
                <input value={form.employee_id} onChange={(e) => setForm({ ...form, employee_id: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Event Type</label>
                <select
                  value={form.event_type}
                  onChange={(e) => setForm({ ...form, event_type: e.target.value, details: templates[e.target.value] })}
                >
                  <option value="login">login</option>
                  <option value="file_download">file_download</option>
                  <option value="usb_connect">usb_connect</option>
                  <option value="email_sent">email_sent</option>
                </select>
              </div>
            </div>
            <div className="form-group">
              <label>Details (JSON)</label>
              <textarea
                value={form.details}
                onChange={(e) => setForm({ ...form, details: e.target.value })}
                rows={6}
                style={{ width: "100%", fontFamily: "monospace", fontSize: "13px", padding: "8px", border: "1px solid #dadce0", borderRadius: "4px" }}
              />
            </div>
            <button className="btn btn-primary" type="submit">Ingest Log</button>
          </form>
        </div>

        {logs.length > 0 && (
          <div className="card">
            <h2>Ingested Logs (this session)</h2>
            <table>
              <thead>
                <tr><th>Employee</th><th>Event</th><th>Details</th></tr>
              </thead>
              <tbody>
                {logs.map((log, i) => (
                  <tr key={i}>
                    <td>{log.employee_id}</td>
                    <td>{log.event_type}</td>
                    <td><code>{JSON.stringify(log.details)}</code></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
}

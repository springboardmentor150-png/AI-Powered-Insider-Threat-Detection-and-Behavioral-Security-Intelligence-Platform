import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import axios from "axios";

export default function Dashboard() {
  const router = useRouter();
  const [role, setRole] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }
    setRole(localStorage.getItem("role"));
  }, []);

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    router.push("/login");
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
        <button className="btn btn-danger" onClick={logout} style={{ fontSize: "12px", padding: "4px 12px" }}>
          Logout
        </button>
      </nav>
      <div className="container">
        <div className="card">
          <h1>Dashboard</h1>
          <p>Welcome to the AI-Powered Insider Threat Detection Platform.</p>
          <p style={{ marginTop: "8px", fontSize: "14px", color: "#666" }}>
            You are logged in as: <strong>{role}</strong>
          </p>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
          <div className="card">
            <h2>Employees</h2>
            <p>Manage monitored employee profiles.</p>
            <a href="/employees" className="btn btn-primary" style={{ marginTop: "8px", display: "inline-block" }}>
              View Employees
            </a>
          </div>
          <div className="card">
            <h2>Activity Logs</h2>
            <p>Ingest and view employee activity logs.</p>
            <a href="/logs" className="btn btn-primary" style={{ marginTop: "8px", display: "inline-block" }}>
              View Logs
            </a>
          </div>
        </div>
      </div>
    </>
  );
}

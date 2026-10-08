"use client";

import { useRouter } from "next/navigation";

export default function DashboardPage() {
  const router = useRouter();

  const role =
    typeof window !== "undefined"
      ? localStorage.getItem("role")
      : "";

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("role");
    router.push("/");
  };

  return (
    <main className="dashboard-page">
      <header className="dashboard-header">
        <div>
          <h1>ITBIS Dashboard</h1>
          <p>Insider Threat Detection & Behavioral Security Intelligence</p>
        </div>

        <button onClick={logout}>Logout</button>
      </header>

      <section className="dashboard-content">
        <div className="welcome-card">
          <h2>Welcome to ITBIS</h2>
          <p>
            You are successfully logged in to the Insider Threat Detection
            and Behavioral Security Intelligence Platform.
          </p>
          <p>
            <strong>Role:</strong> {role || "User"}
          </p>
        </div>

        <div className="dashboard-grid">
          <div className="dashboard-card">
            <h3>Employees</h3>
            <p>Manage and view employee profiles.</p>
            <button onClick={() => router.push("/employees")}>
              Open Employees
            </button>
          </div>

          <div className="dashboard-card">
            <h3>Activity Logs</h3>
            <p>View employee activity and security logs.</p>
            <button onClick={() => router.push("/activity-logs")}>
              View Logs
            </button>
          </div>

          <div className="dashboard-card">
            <h3>Alerts</h3>
            <p>Monitor security alerts.</p>
            <button onClick={() => router.push("/alerts")}>
              View Alerts
            </button>
          </div>

          <div className="dashboard-card">
            <h3>Incidents</h3>
            <p>Track security incidents.</p>
            <button onClick={() => router.push("/incidents")}>
              View Incidents
            </button>
          </div>

          <div className="dashboard-card">
            <h3>Reports</h3>
            <p>View security reports.</p>
            <button onClick={() => router.push("/reports")}>
              View Reports
            </button>
          </div>

          <div className="dashboard-card">
            <h3>Settings</h3>
            <p>Manage platform settings.</p>
            <button onClick={() => router.push("/settings")}>
              Open Settings
            </button>
          </div>
        </div>
      </section>
    </main>
  );
}

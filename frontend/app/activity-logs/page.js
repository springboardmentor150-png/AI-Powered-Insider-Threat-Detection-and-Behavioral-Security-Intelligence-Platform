"use client";

import { useEffect, useState } from "react";

export default function ActivityLogsPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchLogs = async () => {
    try {
      setLoading(true);
      setError("");

      const token = localStorage.getItem("access_token");

      if (!token) {
        setError("Please login first.");
        return;
      }

      const response = await fetch(
        "http://127.0.0.1:8000/logs/",
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to fetch activity logs"
        );
      }

      setLogs(data);
    } catch (err) {
      console.error("Activity logs error:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  return (
    <main className="activity-page">
      <div className="activity-header">
        <div>
          <h1>Activity Logs</h1>
          <p>
            Monitor employee activities and system events
          </p>
        </div>

        <button
          className="refresh-btn"
          onClick={fetchLogs}
        >
          ↻ Refresh
        </button>
      </div>

      <div className="activity-card">
        <div className="activity-card-header">
          <div>
            <h2>Recent Activity</h2>
            <p>
              Real-time activity logs from the security system
            </p>
          </div>

          <span className="log-count">
            {logs.length} Logs
          </span>
        </div>

        {loading && (
          <div className="activity-message">
            Loading activity logs...
          </div>
        )}

        {error && (
          <div className="activity-error">
            {error}
          </div>
        )}

        {!loading && !error && logs.length === 0 && (
          <div className="activity-message">
            No activity logs found.
          </div>
        )}

        {!loading && !error && logs.length > 0 && (
          <div className="table-wrapper">
            <table className="activity-table">
              <thead>
                <tr>
                  <th>Employee ID</th>
                  <th>Activity</th>
                  <th>Timestamp</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                {logs.map((log, index) => (
                  <tr key={index}>
                    <td>
                      <strong>
                        {log.employee_id || "N/A"}
                      </strong>
                    </td>

                    <td>
                      {log.activity || "N/A"}
                    </td>

                    <td>
                      {log.timestamp || "N/A"}
                    </td>

                    <td>
                      <span
                        className={`status-badge ${
                          log.status === "Normal"
                            ? "status-normal"
                            : "status-warning"
                        }`}
                      >
                        {log.status || "Unknown"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </main>
  );
}
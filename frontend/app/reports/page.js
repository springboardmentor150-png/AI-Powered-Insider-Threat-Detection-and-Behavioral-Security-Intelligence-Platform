"use client";

const reports = [
  {
    id: "weekly",
    icon: "📊",
    title: "Weekly Security Report",
    description: "Summary of security activity and events for the week.",
  },
  {
    id: "employee",
    icon: "👥",
    title: "Employee Risk Report",
    description: "Employee activity and security risk summary.",
  },
  {
    id: "alerts",
    icon: "🚨",
    title: "Security Alert Report",
    description: "Summary of detected security alerts and severity.",
  },
];

function generateReport(type) {
  let title = "";
  let content = "";

  if (type === "weekly") {
    title = "ITBIS - Weekly Security Report";

    content = `
ITBIS - WEEKLY SECURITY REPORT
================================

Report Type: Weekly Security Report

SECURITY SUMMARY
----------------
Total Events : 12,540
Total Alerts : 18
Incidents    : 5

RECENT SECURITY ACTIVITY
------------------------
Unusual Login Activity
Employee : EMP-1024
Severity : High
Status   : Investigating

Large File Transfer
Employee : EMP-1018
Severity : Medium
Status   : Under Review

After Hours Access
Employee : EMP-1032
Severity : Low
Status   : Monitoring

REPORT STATUS
-------------
Generated successfully by ITBIS Security Platform.
`;
  }

  if (type === "employee") {
    title = "ITBIS - Employee Risk Report";

    content = `
ITBIS - EMPLOYEE RISK REPORT
============================

Report Type: Employee Risk Report

EMPLOYEE RISK SUMMARY
---------------------
Employee ID : EMP-1024
Risk Event  : Unusual Login Activity
Severity    : High
Status      : Investigating

Employee ID : EMP-1018
Risk Event  : Large File Transfer
Severity    : Medium
Status      : Under Review

Employee ID : EMP-1032
Risk Event  : After Hours Access
Severity    : Low
Status      : Monitoring

REPORT STATUS
-------------
Generated successfully by ITBIS Security Platform.
`;
  }

  if (type === "alerts") {
    title = "ITBIS - Security Alert Report";

    content = `
ITBIS - SECURITY ALERT REPORT
=============================

Report Type: Security Alert Report

ALERT SUMMARY
-------------
Total Alerts   : 18
High Severity  : 1
Medium Severity: 1
Low Severity   : 1

ACTIVE SECURITY ALERTS
----------------------
1. Unusual Login Activity
   Employee : EMP-1024
   Severity : High
   Status   : Investigating

2. Large File Transfer
   Employee : EMP-1018
   Severity : Medium
   Status   : Under Review

3. After Hours Access
   Employee : EMP-1032
   Severity : Low
   Status   : Monitoring

REPORT STATUS
-------------
Generated successfully by ITBIS Security Platform.
`;
  }

  const blob = new Blob([content], {
    type: "text/plain",
  });

  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = `${type}-security-report.txt`;

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  URL.revokeObjectURL(url);
}

export default function ReportsPage() {
  return (
    <main className="reports-page">

      <div className="reports-header">
        <div>
          <h1>Security Intelligence Reports</h1>
          <p>
            Generate security reports and analyze platform activity
          </p>
        </div>

        <div className="report-status">
          <span></span>
          Reporting System Active
        </div>
      </div>

      <div className="report-stats">

        <div className="report-stat-card">
          <span>Total Events</span>
          <strong>12,540</strong>
          <small>Recorded security events</small>
        </div>

        <div className="report-stat-card">
          <span>Total Alerts</span>
          <strong>18</strong>
          <small>Detected security alerts</small>
        </div>

        <div className="report-stat-card">
          <span>Incidents</span>
          <strong>5</strong>
          <small>Security incidents</small>
        </div>

      </div>

      <section className="reports-container">

        <div className="reports-section-header">
          <div>
            <h2>Available Reports</h2>
            <p>
              Generate downloadable security intelligence reports
            </p>
          </div>
        </div>

        <div className="reports-list">

          {reports.map((report) => (

            <div className="report-card" key={report.id}>

              <div className="report-icon">
                {report.icon}
              </div>

              <div className="report-info">
                <h3>{report.title}</h3>
                <p>{report.description}</p>
              </div>

              <button
                className="generate-report-btn"
                onClick={() => generateReport(report.id)}
              >
                Generate
              </button>

            </div>

          ))}

        </div>

      </section>

    </main>
  );
}
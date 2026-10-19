"use client";

import { useState } from "react";

const alerts = [
  {
    title: "Unusual Login Activity",
    employee: "EMP-1024",
    description:
      "Multiple login attempts detected from an unusual location.",
    time: "10 minutes ago",
    severity: "High",
    status: "Investigating",
  },
  {
    title: "Large File Transfer",
    employee: "EMP-1018",
    description:
      "Large volume of files transferred outside normal working patterns.",
    time: "25 minutes ago",
    severity: "Medium",
    status: "Under Review",
  },
  {
    title: "After Hours Access",
    employee: "EMP-1032",
    description:
      "System resources accessed outside the employee's normal working hours.",
    time: "1 hour ago",
    severity: "Low",
    status: "Monitoring",
  },
];

export default function AlertsPage() {
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [investigationStarted, setInvestigationStarted] = useState(false);

  const handleInvestigation = () => {
    setInvestigationStarted(true);
    setSelectedAlert(null);

    setTimeout(() => {
      setInvestigationStarted(false);
    }, 3000);
  };

  return (
    <main className="alerts-page">

      {/* Header */}
      <div className="alerts-header">

        <div>
          <h1>Security Alerts</h1>

          <p>
            Monitor and investigate suspicious security events
          </p>
        </div>

        <div className="alert-summary">
          <span className="summary-dot"></span>
          3 Active Alerts
        </div>

      </div>


      {/* Success Message */}
      {investigationStarted && (
        <div className="investigation-success">
          ✓ Investigation started successfully
        </div>
      )}


      {/* Statistics */}
      <div className="alerts-stats">

        <div className="alert-stat-card">

          <span className="stat-label">
            Total Alerts
          </span>

          <strong>3</strong>

          <small>
            Active security events
          </small>

        </div>


        <div className="alert-stat-card high-stat">

          <span className="stat-label">
            High Severity
          </span>

          <strong>1</strong>

          <small>
            Requires immediate review
          </small>

        </div>


        <div className="alert-stat-card medium-stat">

          <span className="stat-label">
            Medium Severity
          </span>

          <strong>1</strong>

          <small>
            Requires investigation
          </small>

        </div>


        <div className="alert-stat-card low-stat">

          <span className="stat-label">
            Low Severity
          </span>

          <strong>1</strong>

          <small>
            Under monitoring
          </small>

        </div>

      </div>


      {/* Alerts Section */}
      <div className="alerts-section">

        <div className="section-title">

          <div>

            <h2>
              Recent Security Events
            </h2>

            <p>
              Latest suspicious activities detected by ITBIS
            </p>

          </div>


          <button
            type="button"
            className="filter-btn"
          >
            Filter Alerts
          </button>

        </div>


        {/* Alerts List */}
        <div className="alerts-list">

          {alerts.map((alert, index) => (

            <div
              className="professional-alert-card"
              key={index}
            >

              {/* Alert Icon */}
              <div className="alert-icon">
                !
              </div>


              {/* Alert Information */}
              <div className="alert-main">

                <div className="alert-title-row">

                  <h3>
                    {alert.title}
                  </h3>


                  <span
                    className={`severity-badge ${alert.severity.toLowerCase()}`}
                  >
                    {alert.severity}
                  </span>

                </div>


                <p className="alert-description">
                  {alert.description}
                </p>


                <div className="alert-details">

                  <span>
                    <strong>
                      Employee:
                    </strong>{" "}
                    {alert.employee}
                  </span>


                  <span>
                    <strong>
                      Detected:
                    </strong>{" "}
                    {alert.time}
                  </span>


                  <span>
                    <strong>
                      Status:
                    </strong>{" "}
                    {alert.status}
                  </span>

                </div>

              </div>


              {/* View Details Button */}
              <button
                type="button"
                className="view-alert-btn"
                onClick={() =>
                  setSelectedAlert(alert)
                }
              >
                View Details
              </button>

            </div>

          ))}

        </div>

      </div>


      {/* Alert Details Modal */}
      {selectedAlert && (

        <div
          className="alert-modal-overlay"
          onClick={() =>
            setSelectedAlert(null)
          }
        >

          <div
            className="alert-modal"
            onClick={(e) =>
              e.stopPropagation()
            }
          >

            {/* Modal Header */}
            <div className="alert-modal-header">

              <div>

                <span className="modal-label">
                  SECURITY ALERT
                </span>

                <h2>
                  {selectedAlert.title}
                </h2>

              </div>


              {/* X Close Button */}
              <button
                type="button"
                className="modal-close-btn"
                onClick={() =>
                  setSelectedAlert(null)
                }
                aria-label="Close"
              >
                ×
              </button>

            </div>


            {/* Status */}
            <div className="modal-alert-status">

              <span
                className={`severity-badge ${selectedAlert.severity.toLowerCase()}`}
              >
                {selectedAlert.severity}
              </span>


              <span className="modal-status">
                {selectedAlert.status}
              </span>

            </div>


            {/* Details */}
            <div className="modal-details">

              <div className="modal-detail-item">

                <span>
                  Employee
                </span>

                <strong>
                  {selectedAlert.employee}
                </strong>

              </div>


              <div className="modal-detail-item">

                <span>
                  Detected
                </span>

                <strong>
                  {selectedAlert.time}
                </strong>

              </div>


              <div className="modal-detail-item full">

                <span>
                  Description
                </span>

                <p>
                  {selectedAlert.description}
                </p>

              </div>

            </div>


            {/* Modal Buttons */}
            <div className="modal-actions">

              {/* Close */}
              <button
                type="button"
                className="modal-secondary-btn"
                onClick={() =>
                  setSelectedAlert(null)
                }
              >
                Close
              </button>


              {/* Start Investigation */}
              <button
                type="button"
                className="investigate-btn"
                onClick={handleInvestigation}
              >
                Start Investigation
              </button>

            </div>

          </div>

        </div>

      )}

    </main>
  );
}
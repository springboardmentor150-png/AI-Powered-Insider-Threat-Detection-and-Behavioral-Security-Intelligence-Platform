"use client";

import { useState } from "react";

const incidents = [
  {
    id: "INC-001",
    employee: "EMP-1024",
    description: "Suspicious Login",
    details:
      "Unusual login activity detected from an unexpected location.",
    severity: "High",
    status: "Open",
    time: "10 minutes ago",
  },
  {
    id: "INC-002",
    employee: "EMP-1018",
    description: "Large Data Transfer",
    details:
      "Large volume of data transferred outside normal activity patterns.",
    severity: "Medium",
    status: "Investigating",
    time: "25 minutes ago",
  },
  {
    id: "INC-003",
    employee: "EMP-1032",
    description: "After Hours Access",
    details:
      "Employee accessed protected resources outside normal working hours.",
    severity: "High",
    status: "Open",
    time: "1 hour ago",
  },
];

export default function IncidentsPage() {
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [investigationStarted, setInvestigationStarted] =
    useState(false);

  const handleInvestigation = () => {
    setInvestigationStarted(true);
    setSelectedIncident(null);

    setTimeout(() => {
      setInvestigationStarted(false);
    }, 3000);
  };

  return (
    <main className="incidents-page">

      {/* Header */}
      <div className="incidents-header">

        <div>
          <h1>Security Incidents</h1>

          <p>
            Investigate and manage detected security incidents
          </p>
        </div>

        <button
          type="button"
          className="new-incident-btn"
          onClick={() =>
            alert("New Incident feature is ready for implementation.")
          }
        >
          + New Incident
        </button>

      </div>


      {/* Success Message */}
      {investigationStarted && (
        <div className="incident-success-message">
          ✓ Investigation started successfully
        </div>
      )}


      {/* Statistics */}
      <div className="incident-stats">

        <div className="incident-stat-card">

          <span>Total Incidents</span>

          <strong>3</strong>

          <small>
            Detected security incidents
          </small>

        </div>


        <div className="incident-stat-card open-card">

          <span>Open</span>

          <strong>2</strong>

          <small>
            Requires investigation
          </small>

        </div>


        <div className="incident-stat-card investigating-card">

          <span>Investigating</span>

          <strong>1</strong>

          <small>
            Currently under review
          </small>

        </div>


        <div className="incident-stat-card high-card">

          <span>High Severity</span>

          <strong>2</strong>

          <small>
            Priority incidents
          </small>

        </div>

      </div>


      {/* Incident Section */}
      <section className="incidents-container">

        <div className="incidents-section-header">

          <div>

            <h2>
              Incident Investigation
            </h2>

            <p>
              Review and track security incidents detected by ITBIS
            </p>

          </div>


          <button
            type="button"
            className="filter-incident-btn"
            onClick={() =>
              alert("Incident filter is ready for implementation.")
            }
          >
            Filter
          </button>

        </div>


        {/* Table */}
        <div className="incident-table-wrapper">

          <table className="incident-table">

            <thead>

              <tr>

                <th>INCIDENT ID</th>

                <th>EMPLOYEE</th>

                <th>DESCRIPTION</th>

                <th>SEVERITY</th>

                <th>STATUS</th>

                <th>DETECTED</th>

                <th>ACTION</th>

              </tr>

            </thead>


            <tbody>

              {incidents.map((incident) => (

                <tr key={incident.id}>

                  {/* Incident ID */}
                  <td>

                    <strong className="incident-id">
                      {incident.id}
                    </strong>

                  </td>


                  {/* Employee */}
                  <td>

                    <span className="employee-badge">
                      {incident.employee}
                    </span>

                  </td>


                  {/* Description */}
                  <td>

                    <div className="incident-description">

                      <strong>
                        {incident.description}
                      </strong>

                      <span>
                        {incident.details}
                      </span>

                    </div>

                  </td>


                  {/* Severity */}
                  <td>

                    <span
                      className={`incident-severity ${incident.severity.toLowerCase()}`}
                    >
                      {incident.severity}
                    </span>

                  </td>


                  {/* Status */}
                  <td>

                    <span
                      className={`incident-status ${incident.status
                        .toLowerCase()
                        .replace(" ", "-")}`}
                    >

                      <span className="status-dot"></span>

                      {incident.status}

                    </span>

                  </td>


                  {/* Time */}
                  <td>

                    <span className="incident-time">
                      {incident.time}
                    </span>

                  </td>


                  {/* View Button */}
                  <td>

                    <button
                      type="button"
                      className="view-incident-btn"
                      onClick={() =>
                        setSelectedIncident(incident)
                      }
                    >
                      View
                    </button>

                  </td>

                </tr>

              ))}

            </tbody>

          </table>

        </div>

      </section>


      {/* Incident Details Modal */}
      {selectedIncident && (

        <div
          className="incident-modal-overlay"
          onClick={() =>
            setSelectedIncident(null)
          }
        >

          <div
            className="incident-modal"
            onClick={(e) =>
              e.stopPropagation()
            }
          >

            {/* Modal Header */}
            <div className="incident-modal-header">

              <div>

                <span className="incident-modal-label">
                  SECURITY INCIDENT
                </span>

                <h2>
                  {selectedIncident.description}
                </h2>

                <span className="incident-number">
                  {selectedIncident.id}
                </span>

              </div>


              {/* Close X */}
              <button
                type="button"
                className="incident-modal-close"
                onClick={() =>
                  setSelectedIncident(null)
                }
              >
                ×
              </button>

            </div>


            {/* Status */}
            <div className="incident-modal-status">

              <span
                className={`incident-severity ${selectedIncident.severity.toLowerCase()}`}
              >
                {selectedIncident.severity}
              </span>


              <span
                className={`incident-status ${selectedIncident.status
                  .toLowerCase()
                  .replace(" ", "-")}`}
              >
                <span className="status-dot"></span>
                {selectedIncident.status}
              </span>

            </div>


            {/* Details */}
            <div className="incident-modal-details">

              <div className="incident-modal-detail">

                <span>
                  Incident ID
                </span>

                <strong>
                  {selectedIncident.id}
                </strong>

              </div>


              <div className="incident-modal-detail">

                <span>
                  Employee
                </span>

                <strong>
                  {selectedIncident.employee}
                </strong>

              </div>


              <div className="incident-modal-detail">

                <span>
                  Detected
                </span>

                <strong>
                  {selectedIncident.time}
                </strong>

              </div>


              <div className="incident-modal-detail full">

                <span>
                  Description
                </span>

                <p>
                  {selectedIncident.details}
                </p>

              </div>

            </div>


            {/* Buttons */}
            <div className="incident-modal-actions">

              <button
                type="button"
                className="incident-close-btn"
                onClick={() =>
                  setSelectedIncident(null)
                }
              >
                Close
              </button>


              <button
                type="button"
                className="incident-investigate-btn"
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
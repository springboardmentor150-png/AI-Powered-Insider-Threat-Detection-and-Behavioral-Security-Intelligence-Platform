"use client";

import { useState } from "react";

const users = [
  {
    email: "admin@itbis.com",
    role: "Admin",
    description: "Full platform administration access",
    status: "Active",
  },
  {
    email: "analyst@itbis.com",
    role: "Security Analyst",
    description: "Security monitoring and alert analysis",
    status: "Active",
  },
  {
    email: "soc@itbis.com",
    role: "SOC Engineer",
    description: "Security operations and incident response",
    status: "Active",
  },
  {
    email: "manager@itbis.com",
    role: "Security Manager",
    description: "Security oversight and management",
    status: "Active",
  },
];

export default function UsersPage() {
  const [selectedUser, setSelectedUser] = useState(null);
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);

    setTimeout(() => {
      setSaved(false);
      setSelectedUser(null);
    }, 2000);
  };

  return (
    <main className="users-page">

      {/* Header */}
      <div className="users-header">

        <div>
          <h1>Platform Users</h1>

          <p>
            Manage platform users and role-based access
          </p>
        </div>

        <button
          type="button"
          className="add-user-btn"
          onClick={() =>
            alert("Add User feature is ready for implementation.")
          }
        >
          + Add User
        </button>

      </div>


      {/* Statistics */}
      <div className="users-stats">

        <div className="user-stat-card">
          <span>Total Users</span>
          <strong>4</strong>
          <small>Registered platform users</small>
        </div>

        <div className="user-stat-card">
          <span>Administrators</span>
          <strong>1</strong>
          <small>Full system access</small>
        </div>

        <div className="user-stat-card">
          <span>Security Team</span>
          <strong>3</strong>
          <small>Security operations users</small>
        </div>

        <div className="user-stat-card">
          <span>Active Users</span>
          <strong>4</strong>
          <small>Currently enabled</small>
        </div>

      </div>


      {/* User Management */}
      <section className="users-container">

        <div className="users-section-header">

          <div>
            <h2>User Access Management</h2>

            <p>
              Review users and their assigned security roles
            </p>
          </div>

          <button
            type="button"
            className="role-filter-btn"
            onClick={() =>
              alert("Role filter is ready for implementation.")
            }
          >
            Filter by Role
          </button>

        </div>


        {/* Table */}
        <div className="users-table-wrapper">

          <table className="users-table">

            <thead>

              <tr>
                <th>USER</th>
                <th>ROLE</th>
                <th>ACCESS DESCRIPTION</th>
                <th>STATUS</th>
                <th>ACTION</th>
              </tr>

            </thead>


            <tbody>

              {users.map((user, index) => (

                <tr key={index}>

                  {/* User */}
                  <td>

                    <div className="user-info">

                      <div className="user-avatar">
                        {user.email.charAt(0).toUpperCase()}
                      </div>

                      <div>
                        <strong>{user.email}</strong>

                        <span>
                          Platform User
                        </span>
                      </div>

                    </div>

                  </td>


                  {/* Role */}
                  <td>

                    <span
                      className={`role-badge ${user.role
                        .toLowerCase()
                        .replace(" ", "-")}`}
                    >
                      {user.role}
                    </span>

                  </td>


                  {/* Description */}
                  <td>

                    <span className="access-description">
                      {user.description}
                    </span>

                  </td>


                  {/* Status */}
                  <td>

                    <span className="active-status">

                      <span className="active-dot"></span>

                      {user.status}

                    </span>

                  </td>


                  {/* Manage */}
                  <td>

                    <button
                      type="button"
                      className="manage-user-btn"
                      onClick={() =>
                        setSelectedUser(user)
                      }
                    >
                      Manage
                    </button>

                  </td>

                </tr>

              ))}

            </tbody>

          </table>

        </div>

      </section>


      {/* Manage User Modal */}
      {selectedUser && (

        <div
          className="user-modal-overlay"
          onClick={() =>
            setSelectedUser(null)
          }
        >

          <div
            className="user-modal"
            onClick={(e) =>
              e.stopPropagation()
            }
          >

            {/* Modal Header */}
            <div className="user-modal-header">

              <div>

                <span className="user-modal-label">
                  USER MANAGEMENT
                </span>

                <h2>
                  Manage User
                </h2>

              </div>


              <button
                type="button"
                className="user-modal-close"
                onClick={() =>
                  setSelectedUser(null)
                }
              >
                ×
              </button>

            </div>


            {/* User Profile */}
            <div className="user-modal-profile">

              <div className="large-user-avatar">
                {selectedUser.email.charAt(0).toUpperCase()}
              </div>

              <div>

                <h3>
                  {selectedUser.email}
                </h3>

                <p>
                  Platform User
                </p>

              </div>

            </div>


            {/* User Details */}
            <div className="user-modal-details">

              <div className="user-detail-item">

                <span>Email</span>

                <strong>
                  {selectedUser.email}
                </strong>

              </div>


              <div className="user-detail-item">

                <span>Current Role</span>

                <strong>
                  {selectedUser.role}
                </strong>

              </div>


              <div className="user-detail-item full">

                <span>Access Description</span>

                <p>
                  {selectedUser.description}
                </p>

              </div>


              <div className="user-detail-item">

                <span>Status</span>

                <strong className="modal-active-status">
                  ● {selectedUser.status}
                </strong>

              </div>


              <div className="user-detail-item">

                <span>Access Level</span>

                <strong>
                  Role Based
                </strong>

              </div>

            </div>


            {/* Role Selection */}
            <div className="user-role-section">

              <label>
                User Role
              </label>

              <select
                value={selectedUser.role}
                onChange={(e) =>
                  setSelectedUser({
                    ...selectedUser,
                    role: e.target.value,
                  })
                }
              >
                <option>Admin</option>
                <option>Security Analyst</option>
                <option>SOC Engineer</option>
                <option>Security Manager</option>
              </select>

            </div>


            {/* Actions */}
            <div className="user-modal-actions">

              <button
                type="button"
                className="user-cancel-btn"
                onClick={() =>
                  setSelectedUser(null)
                }
              >
                Cancel
              </button>


              <button
                type="button"
                className="user-save-btn"
                onClick={handleSave}
              >
                Save Changes
              </button>

            </div>


            {/* Save Message */}
            {saved && (

              <div className="user-save-message">
                ✓ User details updated successfully
              </div>

            )}

          </div>

        </div>

      )}

    </main>
  );
}
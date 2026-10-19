"use client";

import { useEffect, useState } from "react";

export default function EmployeesPage() {
  const [employees, setEmployees] = useState([]);
  const [showForm, setShowForm] = useState(false);

  const [employeeId, setEmployeeId] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [department, setDepartment] = useState("");
  const [role, setRole] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadEmployees = async () => {
    try {
      const token = localStorage.getItem("access_token");

      const response = await fetch(
        "http://127.0.0.1:8000/employees/",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Unable to load employees"
        );
      }

      setEmployees(data.employees || []);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    loadEmployees();
  }, []);

  const handleAddEmployee = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError("");

    try {
      const token = localStorage.getItem("access_token");

      const params = new URLSearchParams({
        employee_id: employeeId,
        name: name,
        email: email,
        department: department,
        role: role,
      });

      const response = await fetch(
        `http://127.0.0.1:8000/employees/?${params.toString()}`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Failed to add employee"
        );
      }

      setEmployeeId("");
      setName("");
      setEmail("");
      setDepartment("");
      setRole("");

      setShowForm(false);

      await loadEmployees();

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="employee-page">

      <div className="employee-header">
        <div>
          <h1>Employees</h1>
          <p>Manage monitored employee profiles</p>
        </div>

        <button
          className="add-employee-btn"
          onClick={() => {
            setShowForm(true);
            setError("");
          }}
        >
          + Add Employee
        </button>
      </div>

      {error && (
        <div className="employee-error">
          {error}
        </div>
      )}

      {showForm && (
        <div className="employee-form-card">

          <div className="form-header">
            <div>
              <h2>Add Employee</h2>
              <p>Enter employee profile details</p>
            </div>

            <button
              className="close-btn"
              onClick={() => setShowForm(false)}
            >
              ×
            </button>
          </div>

          <form onSubmit={handleAddEmployee}>

            <div className="form-grid">

              <div>
                <label>Employee ID</label>
                <input
                  type="text"
                  placeholder="EMP-1001"
                  value={employeeId}
                  onChange={(e) =>
                    setEmployeeId(e.target.value)
                  }
                  required
                />
              </div>

              <div>
                <label>Employee Name</label>
                <input
                  type="text"
                  placeholder="Enter employee name"
                  value={name}
                  onChange={(e) =>
                    setName(e.target.value)
                  }
                  required
                />
              </div>

              <div>
                <label>Email</label>
                <input
                  type="email"
                  placeholder="employee@example.com"
                  value={email}
                  onChange={(e) =>
                    setEmail(e.target.value)
                  }
                  required
                />
              </div>

              <div>
                <label>Department</label>
                <input
                  type="text"
                  placeholder="IT / HR / Finance"
                  value={department}
                  onChange={(e) =>
                    setDepartment(e.target.value)
                  }
                />
              </div>

              <div>
                <label>Role</label>
                <input
                  type="text"
                  placeholder="Software Engineer"
                  value={role}
                  onChange={(e) =>
                    setRole(e.target.value)
                  }
                />
              </div>

            </div>

            <div className="form-actions">

              <button
                type="button"
                className="cancel-btn"
                onClick={() => setShowForm(false)}
              >
                Cancel
              </button>

              <button
                type="submit"
                className="save-employee-btn"
                disabled={loading}
              >
                {loading ? "Saving..." : "Save Employee"}
              </button>

            </div>

          </form>
        </div>
      )}

      <div className="employee-card">

        {employees.length === 0 ? (
          <div className="empty-employees">
            <div className="empty-icon">👥</div>

            <h2>No employees found.</h2>

            <p>
              Add an employee to start monitoring
              their activities.
            </p>
          </div>
        ) : (
          <table className="employee-table">

            <thead>
              <tr>
                <th>EMPLOYEE ID</th>
                <th>NAME</th>
                <th>EMAIL</th>
                <th>DEPARTMENT</th>
                <th>ROLE</th>
                <th>STATUS</th>
              </tr>
            </thead>

            <tbody>
              {employees.map((employee) => (
                <tr key={employee.id}>

                  <td>
                    <strong>
                      {employee.employee_id}
                    </strong>
                  </td>

                  <td>{employee.name}</td>

                  <td>{employee.email}</td>

                  <td>
                    {employee.department || "-"}
                  </td>

                  <td>
                    {employee.role || "-"}
                  </td>

                  <td>
                    {employee.status || "Active"}
                  </td>

                </tr>
              ))}
            </tbody>

          </table>
        )}

      </div>

    </main>
  );
}
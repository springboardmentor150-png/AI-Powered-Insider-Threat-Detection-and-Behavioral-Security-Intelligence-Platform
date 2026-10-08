"use client";

import { useEffect, useState } from "react";

export default function EmployeesPage() {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchEmployees = async () => {
    try {
      const token = localStorage.getItem("access_token");

      const response = await fetch(
        "http://127.0.0.1:8000/employees",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Unable to fetch employees");
      }

      const data = await response.json();

      setEmployees(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmployees();
  }, []);

  return (
    <main className="employees-page">
      <header className="employees-header">
        <div>
          <h1>Employees</h1>
          <p>Employee Profile Management</p>
        </div>

        <button onClick={() => window.location.href = "/dashboard"}>
          Back to Dashboard
        </button>
      </header>

      <section className="employees-content">
        <div className="employees-card">
          <h2>Employee Profiles</h2>

          {loading && <p>Loading employees...</p>}

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {!loading && !error && employees.length === 0 && (
            <p>No employees found.</p>
          )}

          {!loading && !error && employees.length > 0 && (
            <div className="employee-table-container">
              <table className="employee-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Employee ID</th>
                    <th>Name</th>
                    <th>Department</th>
                    <th>Designation</th>
                  </tr>
                </thead>

                <tbody>
                  {employees.map((employee) => (
                    <tr key={employee.id}>
                      <td>{employee.id}</td>
                      <td>{employee.employee_id}</td>
                      <td>{employee.name}</td>
                      <td>{employee.department}</td>
                      <td>{employee.designation}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}

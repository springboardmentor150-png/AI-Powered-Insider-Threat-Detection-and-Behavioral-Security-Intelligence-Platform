import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import axios from "axios";

export default function Employees() {
  const router = useRouter();
  const [employees, setEmployees] = useState([]);
  const [form, setForm] = useState({ employee_id: "", name: "", department: "", designation: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [role, setRole] = useState("");

  const getAuth = () => ({
    headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
  });

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) { router.push("/login"); return; }
    setRole(localStorage.getItem("role"));
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      const res = await axios.get("http://localhost:8000/employees", getAuth());
      setEmployees(res.data.employees);
    } catch (err) {
      setError("Failed to load employees");
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setError(""); setSuccess("");
    try {
      await axios.post("http://localhost:8000/employees", form, getAuth());
      setSuccess("Employee created");
      setForm({ employee_id: "", name: "", department: "", designation: "" });
      fetchEmployees();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create employee");
    }
  };

  const handleDelete = async (empId) => {
    if (!confirm("Delete this employee?")) return;
    try {
      await axios.delete(`http://localhost:8000/employees/${empId}`, getAuth());
      fetchEmployees();
    } catch (err) {
      setError("Failed to delete");
    }
  };

  const canCreate = role === "admin" || role === "security_manager";

  return (
    <>
      <nav className="nav">
        <strong>ITBIS</strong>
        <a href="/dashboard">Dashboard</a>
        <a href="/employees">Employees</a>
        <a href="/logs">Activity Logs</a>
        <span className="spacer" />
        <span style={{ fontSize: "13px", color: "#666" }}>Role: {role}</span>
      </nav>
      <div className="container">
        <h1>Employee Management</h1>
        {error && <p className="error">{error}</p>}
        {success && <p className="success">{success}</p>}

        {canCreate && (
          <div className="card">
            <h2>Add Employee</h2>
            <form onSubmit={handleCreate} style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
              <div className="form-group">
                <label>Employee ID</label>
                <input value={form.employee_id} onChange={(e) => setForm({ ...form, employee_id: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Name</label>
                <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Department</label>
                <input value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Designation</label>
                <input value={form.designation} onChange={(e) => setForm({ ...form, designation: e.target.value })} />
              </div>
              <div>
                <button className="btn btn-primary" type="submit">Add Employee</button>
              </div>
            </form>
          </div>
        )}

        <div className="card">
          <h2>Employees ({employees.length})</h2>
          <table>
            <thead>
              <tr>
                <th>Employee ID</th>
                <th>Name</th>
                <th>Department</th>
                <th>Designation</th>
                {canCreate && <th>Actions</th>}
              </tr>
            </thead>
            <tbody>
              {employees.map((emp) => (
                <tr key={emp.employee_id}>
                  <td>{emp.employee_id}</td>
                  <td>{emp.name}</td>
                  <td>{emp.department || "-"}</td>
                  <td>{emp.designation || "-"}</td>
                  {canCreate && (
                    <td>
                      <button className="btn btn-danger" onClick={() => handleDelete(emp.employee_id)} style={{ fontSize: "12px", padding: "4px 8px" }}>
                        Delete
                      </button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}

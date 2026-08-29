"use client";
import { useEffect, useState } from "react";
import { api, getDecodedRole } from "@/lib/api";

type Employee = {
  id: number;
  employee_id: string;
  name: string;
  department: string;
  designation: string;
};

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [role, setRole] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [adding, setAdding] = useState(false);
  
  const [formData, setFormData] = useState({
    employee_id: "",
    name: "",
    department: "",
    designation: ""
  });

  const fetchEmployees = async () => {
    try {
      const res = await api.get("/employees");
      setEmployees(res.data);
      setError("");
    } catch (err: any) {
      if (err.response?.status === 403) {
        setError("RESTRICTED: You do not possess the required clearance to access the Identity Registry.");
      } else {
        setError("Error connecting to Identity Store.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setRole(getDecodedRole() || "");
    fetchEmployees();
  }, []);

  const canCreate = ["admin", "security_manager"].includes(role);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setAdding(true);
    try {
      await api.post("/employees", formData);
      setShowForm(false);
      setFormData({ employee_id: "", name: "", department: "", designation: "" });
      fetchEmployees();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Error provisioning identity.");
    } finally {
      setAdding(false);
    }
  };

  const filteredEmployees = employees.filter(emp => 
    emp.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    emp.employee_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    emp.department.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: "2rem", flexWrap: "wrap", gap: "1rem" }}>
        <div>
          <h2 className="title-h1">Identity Registry</h2>
          <p className="text-caption">Monitored corporate personnel and endpoints.</p>
        </div>
        
        <div style={{ display: "flex", gap: "1rem" }}>
          <div style={{ position: "relative" }}>
            <svg style={{ position: "absolute", left: "10px", top: "10px", color: "var(--text-placeholder)" }} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            <input 
              type="text" 
              placeholder="Search identities..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-field"
              style={{ paddingLeft: "2.5rem", width: "300px" }}
            />
          </div>
          {canCreate && (
            <button className={showForm ? "btn-outline" : "btn-primary"} onClick={() => setShowForm(!showForm)}>
              {showForm ? "Cancel Provisioning" : "+ Provision Identity"}
            </button>
          )}
        </div>
      </div>

      {error && (
        <div style={{ padding: "1rem", background: "rgba(239, 68, 68, 0.1)", border: "1px solid rgba(239, 68, 68, 0.2)", borderRadius: "8px", color: "var(--danger)", display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "2rem" }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
          {error}
        </div>
      )}

      {showForm && canCreate && (
        <div className="card" style={{ marginBottom: "2rem", border: "1px solid var(--accent)", background: "var(--bg-input)" }}>
          <h3 style={{ marginBottom: "1.5rem", fontSize: "1.125rem", color: "var(--accent)" }}>New Identity Provisioning</h3>
          <form onSubmit={handleCreate} style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.25rem" }}>
             <div>
                <label className="input-label">Corporate Employee ID</label>
                <input className="input-field" required value={formData.employee_id} onChange={e=>setFormData({...formData, employee_id: e.target.value})} placeholder="EMP-001" />
             </div>
             <div>
                <label className="input-label">Full Legal Name</label>
                <input className="input-field" required value={formData.name} onChange={e=>setFormData({...formData, name: e.target.value})} placeholder="Jane Doe" />
             </div>
             <div>
                <label className="input-label">Department / Unit</label>
                <input className="input-field" required value={formData.department} onChange={e=>setFormData({...formData, department: e.target.value})} placeholder="Engineering" />
             </div>
             <div>
                <label className="input-label">Corporate Designation</label>
                <input className="input-field" required value={formData.designation} onChange={e=>setFormData({...formData, designation: e.target.value})} placeholder="Senior Architect" />
             </div>
             <div style={{ gridColumn: "span 2", display: "flex", justifyContent: "flex-end", marginTop: "0.5rem" }}>
                <button type="submit" className="btn-primary" disabled={adding}>
                  {adding ? "Provisioning..." : "Submit to Active Registry"}
                </button>
             </div>
          </form>
        </div>
      )}

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>DB-ID</th>
              <th>Employee ID</th>
              <th>Identity Name</th>
              <th>Department</th>
              <th>Designation</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={5} style={{ textAlign: "center", padding: "3rem" }}><div className="loader"></div></td></tr>
            ) : filteredEmployees.length === 0 && !error ? (
              <tr><td colSpan={5} style={{ textAlign: "center", padding: "3rem", color: "var(--text-muted)" }}>No identity records resolved matching parameters.</td></tr>
            ) : filteredEmployees.map(emp => (
              <tr key={emp.id}>
                <td style={{ color: "var(--text-placeholder)" }}>#{emp.id}</td>
                <td><span className="badge badge-neutral">{emp.employee_id}</span></td>
                <td style={{ fontWeight: 500 }}>{emp.name}</td>
                <td>{emp.department}</td>
                <td style={{ color: "var(--text-muted)" }}>{emp.designation}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

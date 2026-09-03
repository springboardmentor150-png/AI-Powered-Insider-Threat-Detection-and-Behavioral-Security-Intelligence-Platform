"use client";

import { FormEvent, useEffect, useState } from "react";

import Sidebar from "@/components/Sidebar";
import Navbar from "@/components/Navbar";
import EmployeeForm from "@/components/EmployeeForm";
import api from "@/lib/api";
import { verifyAuthentication } from "@/lib/auth";

type Employee = {
  id: number;
  employee_code: string;
  name: string;
  email: string;
  department: string;
  role: string;
  created_at?: string;
};

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [showForm, setShowForm] = useState(false);

  // Edit state
  const [editingEmployee, setEditingEmployee] =
    useState<Employee | null>(null);

  const [editName, setEditName] = useState("");
  const [editEmail, setEditEmail] = useState("");
  const [editDepartment, setEditDepartment] = useState("");
  const [editRole, setEditRole] = useState("");

  const [editLoading, setEditLoading] = useState(false);
  const [editError, setEditError] = useState("");
  const [editSuccess, setEditSuccess] = useState("");

  // Delete state
  const [deletingEmployee, setDeletingEmployee] =
    useState<Employee | null>(null);

  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteError, setDeleteError] = useState("");

  const loadEmployees = async () => {
    try {
      setLoading(true);
      setError("");

      // Verify JWT first
      await verifyAuthentication();

      // Fetch real employees from FastAPI
      const response = await api.get("/employees");

      const data = response.data;

      if (Array.isArray(data)) {
        setEmployees(data);
      } else if (Array.isArray(data.employees)) {
        setEmployees(data.employees);
      } else {
        setEmployees([]);
        setError(
          "Unexpected employee data received from backend."
        );
      }
    } catch (error: any) {
      if (error.response?.status === 401) {
        localStorage.removeItem("itbis-token");
        localStorage.removeItem("itbis-user");

        window.location.href = "/login";
        return;
      }

      setError(
        error.response?.data?.detail ||
          "Unable to load employee data."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEmployees();
  }, []);

  const handleEmployeeCreated = async () => {
    setShowForm(false);

    await loadEmployees();
  };

  // -------------------------
  // EDIT EMPLOYEE
  // -------------------------

  const handleEditClick = (employee: Employee) => {
    setEditingEmployee(employee);

    setEditName(employee.name);
    setEditEmail(employee.email);
    setEditDepartment(employee.department);
    setEditRole(employee.role);

    setEditError("");
    setEditSuccess("");

    setShowForm(false);
    setDeletingEmployee(null);
  };

  const handleEditCancel = () => {
    setEditingEmployee(null);

    setEditName("");
    setEditEmail("");
    setEditDepartment("");
    setEditRole("");

    setEditError("");
    setEditSuccess("");
  };

  const handleEmployeeUpdate = async (
    event: FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    if (!editingEmployee) {
      return;
    }

    setEditLoading(true);
    setEditError("");
    setEditSuccess("");

    try {
      await api.put(
        `/employees/${editingEmployee.employee_code}`,
        {
          name: editName,
          email: editEmail,
          department: editDepartment,
          role: editRole,
        }
      );

      setEditSuccess("Employee updated successfully.");

      await loadEmployees();

      setTimeout(() => {
        setEditingEmployee(null);
        setEditSuccess("");
      }, 800);
    } catch (error: any) {
      if (error.response?.status === 401) {
        localStorage.removeItem("itbis-token");
        localStorage.removeItem("itbis-user");

        window.location.href = "/login";
        return;
      }

      setEditError(
        error.response?.data?.detail ||
          "Unable to update employee."
      );
    } finally {
      setEditLoading(false);
    }
  };

  // -------------------------
  // DELETE EMPLOYEE
  // -------------------------

  const handleDeleteClick = (employee: Employee) => {
    setDeletingEmployee(employee);

    setDeleteError("");

    setEditingEmployee(null);
    setShowForm(false);
  };

  const handleDeleteCancel = () => {
    if (deleteLoading) {
      return;
    }

    setDeletingEmployee(null);
    setDeleteError("");
  };

  const handleEmployeeDelete = async () => {
    if (!deletingEmployee) {
      return;
    }

    setDeleteLoading(true);
    setDeleteError("");

    try {
      await api.delete(
        `/employees/${deletingEmployee.employee_code}`
      );

      setDeletingEmployee(null);

      await loadEmployees();
    } catch (error: any) {
      if (error.response?.status === 401) {
        localStorage.removeItem("itbis-token");
        localStorage.removeItem("itbis-user");

        window.location.href = "/login";
        return;
      }

      setDeleteError(
        error.response?.data?.detail ||
          "Unable to delete employee."
      );
    } finally {
      setDeleteLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen bg-[var(--background)] text-[var(--foreground)]">
      <Sidebar />

      <div className="flex min-w-0 flex-1 flex-col">
        <Navbar />

        <section className="flex-1 p-6">
          {/* Page Header */}
          <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-sm text-[var(--accent)]">
                Workforce Monitoring
              </p>

              <h2 className="mt-1 text-3xl font-bold tracking-tight">
                Employees
              </h2>

              <p className="mt-2 text-sm text-[var(--muted)]">
                View and manage employees registered in the ITBIS
                security system.
              </p>
            </div>

            {/* Add Employee Button */}
            <button
              type="button"
              onClick={() => {
                setShowForm(true);
                handleEditCancel();
                setDeletingEmployee(null);
              }}
              className="rounded-xl bg-[var(--primary)] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[var(--primary-hover)]"
            >
              + Add Employee
            </button>
          </div>

          {/* Create Employee Form */}
          {showForm && (
            <EmployeeForm
              onCreated={handleEmployeeCreated}
              onCancel={() => setShowForm(false)}
            />
          )}

          {/* Edit Employee Form */}
          {editingEmployee && (
            <div className="mb-6 rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6">
              <div className="mb-6 flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm text-[var(--accent)]">
                    Employee Management
                  </p>

                  <h3 className="mt-1 text-xl font-semibold">
                    Edit Employee
                  </h3>

                  <p className="mt-1 text-sm text-[var(--muted)]">
                    Update the profile information for{" "}
                    <span className="font-medium text-[var(--foreground)]">
                      {editingEmployee.employee_code}
                    </span>
                    .
                  </p>
                </div>

                <button
                  type="button"
                  onClick={handleEditCancel}
                  className="rounded-lg border border-[var(--border)] px-3 py-2 text-sm text-[var(--muted)] transition hover:bg-[var(--card-hover)] hover:text-[var(--foreground)]"
                >
                  Cancel
                </button>
              </div>

              <form
                onSubmit={handleEmployeeUpdate}
                className="grid gap-5 md:grid-cols-2"
              >
                {/* Employee Code */}
                <div>
                  <label
                    htmlFor="edit-employee-code"
                    className="mb-2 block text-sm font-medium"
                  >
                    Employee Code
                  </label>

                  <input
                    id="edit-employee-code"
                    type="text"
                    value={editingEmployee.employee_code}
                    disabled
                    className="w-full cursor-not-allowed rounded-xl border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-sm opacity-60 outline-none"
                  />

                  <p className="mt-1 text-xs text-[var(--muted)]">
                    Employee code cannot be changed.
                  </p>
                </div>

                {/* Name */}
                <div>
                  <label
                    htmlFor="edit-employee-name"
                    className="mb-2 block text-sm font-medium"
                  >
                    Full Name
                  </label>

                  <input
                    id="edit-employee-name"
                    type="text"
                    value={editName}
                    onChange={(event) =>
                      setEditName(event.target.value)
                    }
                    required
                    className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-sm outline-none transition focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20"
                  />
                </div>

                {/* Email */}
                <div>
                  <label
                    htmlFor="edit-employee-email"
                    className="mb-2 block text-sm font-medium"
                  >
                    Email
                  </label>

                  <input
                    id="edit-employee-email"
                    type="email"
                    value={editEmail}
                    onChange={(event) =>
                      setEditEmail(event.target.value)
                    }
                    required
                    className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-sm outline-none transition focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20"
                  />
                </div>

                {/* Department */}
                <div>
                  <label
                    htmlFor="edit-employee-department"
                    className="mb-2 block text-sm font-medium"
                  >
                    Department
                  </label>

                  <input
                    id="edit-employee-department"
                    type="text"
                    value={editDepartment}
                    onChange={(event) =>
                      setEditDepartment(event.target.value)
                    }
                    required
                    className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-sm outline-none transition focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20"
                  />
                </div>

                {/* Role */}
                <div className="md:col-span-2">
                  <label
                    htmlFor="edit-employee-role"
                    className="mb-2 block text-sm font-medium"
                  >
                    Job Role
                  </label>

                  <input
                    id="edit-employee-role"
                    type="text"
                    value={editRole}
                    onChange={(event) =>
                      setEditRole(event.target.value)
                    }
                    required
                    className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-sm outline-none transition focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20"
                  />
                </div>

                {/* Error */}
                {editError && (
                  <div className="md:col-span-2 rounded-xl border border-[var(--danger)]/30 bg-[var(--danger)]/10 px-4 py-3 text-sm text-[var(--danger)]">
                    {editError}
                  </div>
                )}

                {/* Success */}
                {editSuccess && (
                  <div className="md:col-span-2 rounded-xl border border-[var(--success)]/30 bg-[var(--success)]/10 px-4 py-3 text-sm text-[var(--success)]">
                    {editSuccess}
                  </div>
                )}

                {/* Buttons */}
                <div className="flex gap-3 md:col-span-2">
                  <button
                    type="submit"
                    disabled={editLoading}
                    className="rounded-xl bg-[var(--primary)] px-6 py-3 text-sm font-semibold text-white transition hover:bg-[var(--primary-hover)] disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {editLoading
                      ? "Saving Changes..."
                      : "Save Changes"}
                  </button>

                  <button
                    type="button"
                    onClick={handleEditCancel}
                    disabled={editLoading}
                    className="rounded-xl border border-[var(--border)] px-6 py-3 text-sm font-medium text-[var(--muted)] transition hover:bg-[var(--card-hover)] hover:text-[var(--foreground)] disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Delete Confirmation */}
          {deletingEmployee && (
            <div className="mb-6 rounded-2xl border border-[var(--danger)]/30 bg-[var(--card)] p-6">
              <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p className="text-sm font-medium text-[var(--danger)]">
                    Security Action
                  </p>

                  <h3 className="mt-1 text-xl font-semibold">
                    Delete Employee?
                  </h3>

                  <p className="mt-2 text-sm leading-6 text-[var(--muted)]">
                    Are you sure you want to delete{" "}
                    <span className="font-semibold text-[var(--foreground)]">
                      {deletingEmployee.name}
                    </span>{" "}
                    (
                    <span className="font-medium text-[var(--foreground)]">
                      {deletingEmployee.employee_code}
                    </span>
                    ) from the employee registry?
                  </p>

                  <p className="mt-2 text-xs text-[var(--danger)]">
                    This action cannot be undone.
                  </p>
                </div>

                <div className="flex shrink-0 gap-3">
                  <button
                    type="button"
                    onClick={handleDeleteCancel}
                    disabled={deleteLoading}
                    className="rounded-xl border border-[var(--border)] px-5 py-3 text-sm font-medium text-[var(--muted)] transition hover:bg-[var(--card-hover)] hover:text-[var(--foreground)] disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    Cancel
                  </button>

                  <button
                    type="button"
                    onClick={handleEmployeeDelete}
                    disabled={deleteLoading}
                    className="rounded-xl bg-[var(--danger)] px-5 py-3 text-sm font-semibold text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {deleteLoading
                      ? "Deleting..."
                      : "Delete Employee"}
                  </button>
                </div>
              </div>

              {deleteError && (
                <div className="mt-5 rounded-xl border border-[var(--danger)]/30 bg-[var(--danger)]/10 px-4 py-3 text-sm text-[var(--danger)]">
                  {deleteError}
                </div>
              )}
            </div>
          )}

          {/* Employee Summary */}
          <div className="mb-6 grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5">
              <p className="text-sm text-[var(--muted)]">
                Total Employees
              </p>

              <p className="mt-3 text-3xl font-bold">
                {loading ? "—" : employees.length}
              </p>

              <p className="mt-2 text-xs text-[var(--muted)]">
                Registered employee records
              </p>
            </div>

            <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5">
              <p className="text-sm text-[var(--muted)]">
                Registry Status
              </p>

              <p className="mt-3 text-xl font-semibold text-[var(--success)]">
                {loading ? "Checking..." : "Connected"}
              </p>

              <p className="mt-2 text-xs text-[var(--muted)]">
                PostgreSQL employee registry
              </p>
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="mb-6 rounded-xl border border-[var(--danger)]/30 bg-[var(--danger)]/10 px-4 py-3 text-sm text-[var(--danger)]">
              {error}
            </div>
          )}

          {/* Employee Table */}
          <div className="overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--card)]">
            <div className="border-b border-[var(--border)] px-6 py-4">
              <h3 className="font-semibold">
                Employee Registry
              </h3>

              <p className="mt-1 text-xs text-[var(--muted)]">
                Employee records retrieved from the ITBIS backend.
              </p>
            </div>

            {loading ? (
              <div className="flex items-center justify-center px-6 py-16">
                <div className="text-center">
                  <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--primary)]" />

                  <p className="text-sm text-[var(--muted)]">
                    Loading employees...
                  </p>
                </div>
              </div>
            ) : employees.length === 0 ? (
              <div className="px-6 py-16 text-center">
                <p className="font-medium">
                  No employees found
                </p>

                <p className="mt-2 text-sm text-[var(--muted)]">
                  There are currently no employee records in the
                  registry.
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[1050px] text-left">
                  <thead>
                    <tr className="border-b border-[var(--border)] text-xs uppercase tracking-wider text-[var(--muted)]">
                      <th className="px-6 py-4 font-medium">
                        Employee ID
                      </th>

                      <th className="px-6 py-4 font-medium">
                        Name
                      </th>

                      <th className="px-6 py-4 font-medium">
                        Email
                      </th>

                      <th className="px-6 py-4 font-medium">
                        Department
                      </th>

                      <th className="px-6 py-4 font-medium">
                        Role
                      </th>

                      <th className="px-6 py-4 text-right font-medium">
                        Actions
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {employees.map((employee) => (
                      <tr
                        key={employee.id}
                        className="border-b border-[var(--border)] last:border-0 transition hover:bg-[var(--card-hover)]"
                      >
                        <td className="px-6 py-4">
                          <span className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-2.5 py-1 text-xs font-medium">
                            {employee.employee_code}
                          </span>
                        </td>

                        <td className="px-6 py-4">
                          <p className="font-medium">
                            {employee.name}
                          </p>
                        </td>

                        <td className="px-6 py-4 text-sm text-[var(--muted)]">
                          {employee.email}
                        </td>

                        <td className="px-6 py-4 text-sm">
                          {employee.department}
                        </td>

                        <td className="px-6 py-4">
                          <span className="rounded-lg bg-[var(--primary)]/10 px-2.5 py-1 text-xs font-medium text-[var(--primary)]">
                            {employee.role}
                          </span>
                        </td>

                        <td className="px-6 py-4">
                          <div className="flex justify-end gap-2">
                            <button
                              type="button"
                              onClick={() =>
                                handleEditClick(employee)
                              }
                              className="rounded-lg border border-[var(--border)] px-3 py-2 text-xs font-semibold text-[var(--foreground)] transition hover:border-[var(--primary)] hover:bg-[var(--primary)]/10 hover:text-[var(--primary)]"
                            >
                              Edit
                            </button>

                            <button
                              type="button"
                              onClick={() =>
                                handleDeleteClick(employee)
                              }
                              className="rounded-lg border border-[var(--danger)]/30 px-3 py-2 text-xs font-semibold text-[var(--danger)] transition hover:bg-[var(--danger)]/10"
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}
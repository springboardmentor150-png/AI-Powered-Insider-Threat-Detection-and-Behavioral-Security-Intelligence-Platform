"use client";

import { FormEvent, useState } from "react";
import api from "@/lib/api";

type EmployeeFormProps = {
  onCreated: () => void;
  onCancel: () => void;
};

export default function EmployeeForm({
  onCreated,
  onCancel,
}: EmployeeFormProps) {
  const [employeeCode, setEmployeeCode] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [department, setDepartment] = useState("");
  const [role, setRole] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    setError("");
    setSuccess("");
    setLoading(true);

    try {
      await api.post("/employees", {
        employee_code: employeeCode,
        name,
        email,
        department,
        role,
      });

      setSuccess("Employee created successfully.");

      setEmployeeCode("");
      setName("");
      setEmail("");
      setDepartment("");
      setRole("");

      onCreated();
    } catch (error: any) {
      setError(
        error.response?.data?.detail ||
          "Unable to create employee."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mb-6 rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">
            Add Employee
          </h3>

          <p className="mt-1 text-sm text-[var(--muted)]">
            Register a new employee in the ITBIS system.
          </p>
        </div>

        <button
          type="button"
          onClick={onCancel}
          className="rounded-lg border border-[var(--border)] px-3 py-2 text-sm text-[var(--muted)] transition hover:bg-[var(--card-hover)] hover:text-[var(--foreground)]"
        >
          Cancel
        </button>
      </div>

      <form
        onSubmit={handleSubmit}
        className="grid gap-5 md:grid-cols-2"
      >
        {/* Employee Code */}
        <div>
          <label
            htmlFor="employee-code"
            className="mb-2 block text-sm font-medium"
          >
            Employee Code
          </label>

          <input
            id="employee-code"
            type="text"
            value={employeeCode}
            onChange={(event) =>
              setEmployeeCode(event.target.value)
            }
            placeholder="EMP002"
            required
            className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-sm outline-none transition focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20"
          />
        </div>

        {/* Name */}
        <div>
          <label
            htmlFor="employee-name"
            className="mb-2 block text-sm font-medium"
          >
            Full Name
          </label>

          <input
            id="employee-name"
            type="text"
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="Amit Kumar"
            required
            className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-sm outline-none transition focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20"
          />
        </div>

        {/* Email */}
        <div>
          <label
            htmlFor="employee-email"
            className="mb-2 block text-sm font-medium"
          >
            Email
          </label>

          <input
            id="employee-email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="amit.kumar@example.com"
            required
            className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-sm outline-none transition focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20"
          />
        </div>

        {/* Department */}
        <div>
          <label
            htmlFor="employee-department"
            className="mb-2 block text-sm font-medium"
          >
            Department
          </label>

          <input
            id="employee-department"
            type="text"
            value={department}
            onChange={(event) =>
              setDepartment(event.target.value)
            }
            placeholder="IT"
            required
            className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-sm outline-none transition focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20"
          />
        </div>

        {/* Role */}
        <div className="md:col-span-2">
          <label
            htmlFor="employee-role"
            className="mb-2 block text-sm font-medium"
          >
            Job Role
          </label>

          <input
            id="employee-role"
            type="text"
            value={role}
            onChange={(event) => setRole(event.target.value)}
            placeholder="Software Engineer"
            required
            className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-sm outline-none transition focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20"
          />
        </div>

        {/* Error */}
        {error && (
          <div className="md:col-span-2 rounded-xl border border-[var(--danger)]/30 bg-[var(--danger)]/10 px-4 py-3 text-sm text-[var(--danger)]">
            {error}
          </div>
        )}

        {/* Success */}
        {success && (
          <div className="md:col-span-2 rounded-xl border border-[var(--success)]/30 bg-[var(--success)]/10 px-4 py-3 text-sm text-[var(--success)]">
            {success}
          </div>
        )}

        {/* Buttons */}
        <div className="flex gap-3 md:col-span-2">
          <button
            type="submit"
            disabled={loading}
            className="rounded-xl bg-[var(--primary)] px-6 py-3 text-sm font-semibold text-white transition hover:bg-[var(--primary-hover)] disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Creating..." : "Create Employee"}
          </button>

          <button
            type="button"
            onClick={onCancel}
            className="rounded-xl border border-[var(--border)] px-6 py-3 text-sm font-medium text-[var(--muted)] transition hover:bg-[var(--card-hover)] hover:text-[var(--foreground)]"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
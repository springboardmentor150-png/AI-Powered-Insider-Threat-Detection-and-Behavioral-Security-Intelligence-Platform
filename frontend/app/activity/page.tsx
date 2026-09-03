"use client";

import { useEffect, useState } from "react";

import Sidebar from "@/components/Sidebar";
import Navbar from "@/components/Navbar";
import api from "@/lib/api";
import { verifyAuthentication } from "@/lib/auth";

type Employee = {
  id: number;
  employee_code: string;
  name: string;
  email: string;
  department: string;
  role: string;
};

type Activity = {
  id: string;
  employee_code: string;
  event_type: string;
  source: string;
  ip_address?: string | null;
  risk_score: number;
  timestamp: string;
};

export default function ActivityPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);

  const [selectedEmployee, setSelectedEmployee] = useState("");

  const [loadingEmployees, setLoadingEmployees] = useState(true);
  const [loadingActivities, setLoadingActivities] = useState(false);

  const [error, setError] = useState("");

  const loadEmployees = async () => {
    try {
      setLoadingEmployees(true);
      setError("");

      await verifyAuthentication();

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
      setLoadingEmployees(false);
    }
  };

  const loadActivities = async (employeeCode: string) => {
    if (!employeeCode) {
      setActivities([]);
      return;
    }

    try {
      setLoadingActivities(true);
      setError("");

      const response = await api.get(
        `/activity/${employeeCode}`
      );

      const data = response.data;

      if (Array.isArray(data.activities)) {
        setActivities(data.activities);
      } else {
        setActivities([]);
        setError(
          "Unexpected activity data received from backend."
        );
      }
    } catch (error: any) {
      if (error.response?.status === 401) {
        localStorage.removeItem("itbis-token");
        localStorage.removeItem("itbis-user");

        window.location.href = "/login";
        return;
      }

      setActivities([]);

      setError(
        error.response?.data?.detail ||
          "Unable to load activity logs."
      );
    } finally {
      setLoadingActivities(false);
    }
  };

  useEffect(() => {
    loadEmployees();
  }, []);

  useEffect(() => {
    loadActivities(selectedEmployee);
  }, [selectedEmployee]);

  const selectedEmployeeData = employees.find(
    (employee) =>
      employee.employee_code === selectedEmployee
  );

  const getRiskLabel = (score: number) => {
    if (score >= 70) {
      return "High";
    }

    if (score >= 40) {
      return "Medium";
    }

    return "Low";
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <main className="flex min-h-screen bg-[var(--background)] text-[var(--foreground)]">
      <Sidebar />

      <div className="flex min-w-0 flex-1 flex-col">
        <Navbar />

        <section className="flex-1 p-6">
          {/* Page Header */}
          <div className="mb-8">
            <p className="text-sm text-[var(--accent)]">
              Security Monitoring
            </p>

            <h2 className="mt-1 text-3xl font-bold tracking-tight">
              Activity Logs
            </h2>

            <p className="mt-2 text-sm text-[var(--muted)]">
              Monitor employee activity events recorded by the
              ITBIS platform.
            </p>
          </div>

          {/* Employee Selector */}
          <div className="mb-6 rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6">
            <div className="grid gap-5 md:grid-cols-[1fr_auto] md:items-end">
              <div>
                <label
                  htmlFor="employee-select"
                  className="mb-2 block text-sm font-medium"
                >
                  Select Employee
                </label>

                <select
                  id="employee-select"
                  value={selectedEmployee}
                  onChange={(event) =>
                    setSelectedEmployee(event.target.value)
                  }
                  disabled={
                    loadingEmployees ||
                    employees.length === 0
                  }
                  className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-sm outline-none transition focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20"
                >
                  <option value="">
                    {loadingEmployees
                      ? "Loading employees..."
                      : "Select an employee"}
                  </option>

                  {employees.map((employee) => (
                    <option
                      key={employee.id}
                      value={employee.employee_code}
                    >
                      {employee.employee_code} —{" "}
                      {employee.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="rounded-xl border border-[var(--border)] bg-[var(--background)] px-5 py-3">
                <p className="text-xs text-[var(--muted)]">
                  Logs Available
                </p>

                <p className="mt-1 text-xl font-bold">
                  {selectedEmployee
                    ? activities.length
                    : "—"}
                </p>
              </div>
            </div>

            {selectedEmployeeData && (
              <div className="mt-5 flex flex-wrap gap-3 border-t border-[var(--border)] pt-5">
                <span className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-1.5 text-xs font-medium">
                  {selectedEmployeeData.employee_code}
                </span>

                <span className="rounded-lg bg-[var(--primary)]/10 px-3 py-1.5 text-xs font-medium text-[var(--primary)]">
                  {selectedEmployeeData.name}
                </span>

                <span className="rounded-lg bg-[var(--accent)]/10 px-3 py-1.5 text-xs font-medium text-[var(--accent)]">
                  {selectedEmployeeData.department}
                </span>
              </div>
            )}
          </div>

          {/* Error */}
          {error && (
            <div className="mb-6 rounded-xl border border-[var(--danger)]/30 bg-[var(--danger)]/10 px-4 py-3 text-sm text-[var(--danger)]">
              {error}
            </div>
          )}

          {/* Activity Summary */}
          {selectedEmployee && (
            <div className="mb-6 grid gap-4 sm:grid-cols-3">
              <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5">
                <p className="text-sm text-[var(--muted)]">
                  Total Activities
                </p>

                <p className="mt-3 text-3xl font-bold">
                  {loadingActivities
                    ? "—"
                    : activities.length}
                </p>

                <p className="mt-2 text-xs text-[var(--muted)]">
                  Recorded activity events
                </p>
              </div>

              <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5">
                <p className="text-sm text-[var(--muted)]">
                  High Risk Events
                </p>

                <p className="mt-3 text-3xl font-bold text-[var(--danger)]">
                  {loadingActivities
                    ? "—"
                    : activities.filter(
                        (activity) =>
                          activity.risk_score >= 70
                      ).length}
                </p>

                <p className="mt-2 text-xs text-[var(--muted)]">
                  Risk score ≥ 70
                </p>
              </div>

              <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5">
                <p className="text-sm text-[var(--muted)]">
                  Average Risk
                </p>

                <p className="mt-3 text-3xl font-bold">
                  {loadingActivities ||
                  activities.length === 0
                    ? "—"
                    : Math.round(
                        activities.reduce(
                          (total, activity) =>
                            total +
                            activity.risk_score,
                          0
                        ) / activities.length
                      )}
                </p>

                <p className="mt-2 text-xs text-[var(--muted)]">
                  Across recorded activities
                </p>
              </div>
            </div>
          )}

          {/* Activity Table */}
          <div className="overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--card)]">
            <div className="border-b border-[var(--border)] px-6 py-4">
              <h3 className="font-semibold">
                Activity Event Stream
              </h3>

              <p className="mt-1 text-xs text-[var(--muted)]">
                Activity records retrieved from MongoDB.
              </p>
            </div>

            {!selectedEmployee ? (
              <div className="px-6 py-16 text-center">
                <p className="font-medium">
                  Select an employee
                </p>

                <p className="mt-2 text-sm text-[var(--muted)]">
                  Choose an employee above to view their
                  activity logs.
                </p>
              </div>
            ) : loadingActivities ? (
              <div className="flex items-center justify-center px-6 py-16">
                <div className="text-center">
                  <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--primary)]" />

                  <p className="text-sm text-[var(--muted)]">
                    Loading activity logs...
                  </p>
                </div>
              </div>
            ) : activities.length === 0 ? (
              <div className="px-6 py-16 text-center">
                <p className="font-medium">
                  No activity logs found
                </p>

                <p className="mt-2 text-sm text-[var(--muted)]">
                  No recorded activity events exist for this
                  employee.
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[950px] text-left">
                  <thead>
                    <tr className="border-b border-[var(--border)] text-xs uppercase tracking-wider text-[var(--muted)]">
                      <th className="px-6 py-4 font-medium">
                        Event
                      </th>

                      <th className="px-6 py-4 font-medium">
                        Source
                      </th>

                      <th className="px-6 py-4 font-medium">
                        IP Address
                      </th>

                      <th className="px-6 py-4 font-medium">
                        Risk
                      </th>

                      <th className="px-6 py-4 font-medium">
                        Timestamp
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {activities.map((activity) => {
                      const riskLabel = getRiskLabel(
                        activity.risk_score
                      );

                      return (
                        <tr
                          key={activity.id}
                          className="border-b border-[var(--border)] last:border-0 transition hover:bg-[var(--card-hover)]"
                        >
                          <td className="px-6 py-4">
                            <span className="rounded-lg bg-[var(--primary)]/10 px-3 py-1.5 text-xs font-medium capitalize text-[var(--primary)]">
                              {activity.event_type}
                            </span>
                          </td>

                          <td className="px-6 py-4 text-sm">
                            {activity.source}
                          </td>

                          <td className="px-6 py-4 font-mono text-xs text-[var(--muted)]">
                            {activity.ip_address || "—"}
                          </td>

                          <td className="px-6 py-4">
                            <div className="flex items-center gap-2">
                              <span
                                className={`h-2 w-2 rounded-full ${
                                  activity.risk_score >= 70
                                    ? "bg-[var(--danger)]"
                                    : activity.risk_score >=
                                      40
                                    ? "bg-[var(--warning)]"
                                    : "bg-[var(--success)]"
                                }`}
                              />

                              <span className="text-sm font-medium">
                                {activity.risk_score}
                              </span>

                              <span className="text-xs text-[var(--muted)]">
                                {riskLabel}
                              </span>
                            </div>
                          </td>

                          <td className="px-6 py-4 text-sm text-[var(--muted)]">
                            {formatTimestamp(
                              activity.timestamp
                            )}
                          </td>
                        </tr>
                      );
                    })}
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
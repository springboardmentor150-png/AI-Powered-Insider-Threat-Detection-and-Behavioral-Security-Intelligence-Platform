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

export default function DashboardPage() {
  const [checkingAuth, setCheckingAuth] = useState(true);

  const [employeeCount, setEmployeeCount] = useState<number | null>(
    null
  );

  const [activityCount, setActivityCount] = useState<number | null>(
    null
  );

  const [recentActivities, setRecentActivities] = useState<Activity[]>(
    []
  );

  const [loadingData, setLoadingData] = useState(true);

  const loadDashboardData = async () => {
    try {
      setLoadingData(true);

      await verifyAuthentication();

      const [employeeResponse, activityResponse] =
        await Promise.all([
          api.get("/employees"),
          api.get("/activity"),
        ]);

      const employeeData = employeeResponse.data;
      const activityData = activityResponse.data;

      if (Array.isArray(employeeData)) {
        setEmployeeCount(employeeData.length);
      } else {
        setEmployeeCount(employeeData.count ?? 0);
      }

      if (Array.isArray(activityData)) {
        setActivityCount(activityData.length);
        setRecentActivities(activityData.slice(0, 5));
      } else {
        setActivityCount(activityData.count ?? 0);
        setRecentActivities(
          Array.isArray(activityData.activities)
            ? activityData.activities.slice(0, 5)
            : []
        );
      }

      setCheckingAuth(false);
    } catch (error: any) {
      if (error.response?.status === 401) {
        localStorage.removeItem("itbis-token");
        localStorage.removeItem("itbis-user");

        window.location.href = "/login";
        return;
      }

      setCheckingAuth(false);
    } finally {
      setLoadingData(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

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

  if (checkingAuth) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[var(--background)] text-[var(--foreground)]">
        <div className="text-center">
          <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--primary)]" />

          <p className="text-sm text-[var(--muted)]">
            Verifying authentication...
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen bg-[var(--background)] text-[var(--foreground)]">
      <Sidebar />

      <div className="flex min-w-0 flex-1 flex-col">
        <Navbar />

        <section className="flex-1 p-6">
          {/* Page Header */}
          <div className="mb-8">
            <p className="text-sm text-[var(--accent)]">
              Security Overview
            </p>

            <h2 className="mt-1 text-3xl font-bold tracking-tight">
              Dashboard
            </h2>

            <p className="mt-2 text-sm text-[var(--muted)]">
              Monitor employees, activity logs, and security events
              from the ITBIS console.
            </p>
          </div>

          {/* Overview Cards */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5">
              <p className="text-sm text-[var(--muted)]">
                Employees
              </p>

              <p className="mt-3 text-3xl font-bold">
                {loadingData ? "—" : employeeCount}
              </p>

              <p className="mt-2 text-xs text-[var(--muted)]">
                Connected to employee registry
              </p>
            </div>

            <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5">
              <p className="text-sm text-[var(--muted)]">
                Activity Events
              </p>

              <p className="mt-3 text-3xl font-bold">
                {loadingData ? "—" : activityCount}
              </p>

              <p className="mt-2 text-xs text-[var(--muted)]">
                Events collected from activity logs
              </p>
            </div>

            <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5">
              <p className="text-sm text-[var(--muted)]">
                System Status
              </p>

              <p className="mt-3 text-xl font-semibold text-[var(--success)]">
                Operational
              </p>

              <p className="mt-2 text-xs text-[var(--muted)]">
                ITBIS services are available
              </p>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="mt-6 overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--card)]">
            <div className="border-b border-[var(--border)] px-6 py-5">
              <h3 className="font-semibold">
                Recent Activity
              </h3>

              <p className="mt-1 text-xs text-[var(--muted)]">
                Latest activity events collected by the ITBIS platform.
              </p>
            </div>

            {loadingData ? (
              <div className="flex items-center justify-center px-6 py-16">
                <div className="text-center">
                  <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--primary)]" />

                  <p className="text-sm text-[var(--muted)]">
                    Loading recent activity...
                  </p>
                </div>
              </div>
            ) : recentActivities.length === 0 ? (
              <div className="px-6 py-16 text-center">
                <p className="font-medium">
                  No activity events found
                </p>

                <p className="mt-2 text-sm text-[var(--muted)]">
                  Activity data will appear here when events are recorded.
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[850px] text-left">
                  <thead>
                    <tr className="border-b border-[var(--border)] text-xs uppercase tracking-wider text-[var(--muted)]">
                      <th className="px-6 py-4 font-medium">
                        Event
                      </th>

                      <th className="px-6 py-4 font-medium">
                        Employee
                      </th>

                      <th className="px-6 py-4 font-medium">
                        Source
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
                    {recentActivities.map((activity) => {
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

                          <td className="px-6 py-4">
                            <span className="text-sm font-medium">
                              {activity.employee_code}
                            </span>
                          </td>

                          <td className="px-6 py-4 text-sm">
                            {activity.source}
                          </td>

                          <td className="px-6 py-4">
                            <div className="flex items-center gap-2">
                              <span
                                className={`h-2 w-2 rounded-full ${
                                  activity.risk_score >= 70
                                    ? "bg-[var(--danger)]"
                                    : activity.risk_score >= 40
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

          {/* Information Panel */}
          <div className="mt-6 rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6">
            <p className="text-sm font-medium">
              ITBIS Security Intelligence
            </p>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--muted)]">
              This console provides a centralized interface for
              monitoring employee activity and security-related
              events. Live data is loaded from the ITBIS backend.
            </p>
          </div>
        </section>
      </div>
    </main>
  );
}
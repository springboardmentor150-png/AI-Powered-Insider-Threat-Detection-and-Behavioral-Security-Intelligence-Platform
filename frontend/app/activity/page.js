"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import AuthGuard from "@/components/AuthGuard";
import api, { clearSession, isLoggedIn } from "@/lib/api";

export default function ActivityPage() {
  const router = useRouter();

  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [search, setSearch] = useState("");
  const [eventFilter, setEventFilter] = useState("all");

  useEffect(() => {
    if (!isLoggedIn()) {
      router.replace("/login");
      return;
    }

    loadActivities();
  }, [router]);

  const loadActivities = async () => {
    try {
      setLoading(true);
      setError("");

      /*
       * Existing backend endpoint:
       * GET /activity
       */
      const response = await api.get("/activity");

      const data = Array.isArray(response.data)
        ? response.data
        : response.data?.activities ||
          response.data?.logs ||
          response.data?.data ||
          [];

      setActivities(data);
    } catch (err) {
      console.error("Activity loading error:", err);

      if (err?.response?.status === 401) {
        clearSession();
        router.replace("/login");
        return;
      }

      setError(
        err?.response?.data?.detail ||
          "Unable to load employee activity."
      );
    } finally {
      setLoading(false);
    }
  };

  const eventTypes = useMemo(() => {
    const values = activities
      .map((activity) => activity.event_type)
      .filter(Boolean);

    return [...new Set(values)];
  }, [activities]);

  const filteredActivities = useMemo(() => {
    let data = [...activities];

    if (eventFilter !== "all") {
      data = data.filter(
        (activity) =>
          activity.event_type === eventFilter
      );
    }

    if (search.trim()) {
      const query = search.toLowerCase();

      data = data.filter((activity) =>
        JSON.stringify(activity)
          .toLowerCase()
          .includes(query)
      );
    }

    return data;
  }, [activities, eventFilter, search]);

  const stats = useMemo(() => {
    const employees = new Set(
      activities
        .map((item) => item.employee_id)
        .filter(Boolean)
    );

    const events = new Set(
      activities
        .map((item) => item.event_type)
        .filter(Boolean)
    );

    return {
      total: activities.length,
      employees: employees.size,
      eventTypes: events.size,
      today: activities.filter((item) => {
        if (!item.timestamp) return false;

        const date = new Date(item.timestamp);
        const now = new Date();

        return (
          date.getFullYear() === now.getFullYear() &&
          date.getMonth() === now.getMonth() &&
          date.getDate() === now.getDate()
        );
      }).length,
    };
  }, [activities]);

  const formatDate = (value) => {
    if (!value) return "N/A";

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return String(value);
    }

    return date.toLocaleString();
  };

  const formatDetails = (details) => {
    if (!details) return "No additional details";

    if (typeof details === "string") {
      return details;
    }

    try {
      return JSON.stringify(details, null, 2);
    } catch {
      return String(details);
    }
  };

  const getEventClass = (eventType) => {
    const value = String(eventType || "").toLowerCase();

    if (
      value.includes("login") ||
      value.includes("authentication")
    ) {
      return "border-blue-500/30 bg-blue-500/10 text-blue-400";
    }

    if (
      value.includes("download") ||
      value.includes("upload") ||
      value.includes("file")
    ) {
      return "border-purple-500/30 bg-purple-500/10 text-purple-400";
    }

    if (
      value.includes("delete") ||
      value.includes("remove")
    ) {
      return "border-red-500/30 bg-red-500/10 text-red-400";
    }

    if (
      value.includes("access") ||
      value.includes("permission")
    ) {
      return "border-yellow-500/30 bg-yellow-500/10 text-yellow-400";
    }

    return "border-slate-600 bg-slate-800 text-slate-300";
  };

  return (
    <AuthGuard>
      <main className="min-h-screen bg-slate-950 text-white">
        {/* Header */}
        <header className="border-b border-slate-800 bg-slate-900/80">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
            <div>
              <h1 className="text-2xl font-bold">
                Activity Monitoring
              </h1>

              <p className="mt-1 text-sm text-slate-400">
                Monitor employee activity and behavioral events.
              </p>
            </div>

            <div className="flex gap-3">
              <Link
                href="/dashboard"
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:bg-slate-800"
              >
                Dashboard
              </Link>

              <button
                onClick={loadActivities}
                disabled={loading}
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium transition hover:bg-blue-500 disabled:opacity-50"
              >
                {loading ? "Refreshing..." : "Refresh"}
              </button>
            </div>
          </div>
        </header>

        <div className="mx-auto max-w-7xl px-6 py-8">
          {/* Error */}
          {error && (
            <div className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4">
              <p className="font-medium text-red-400">
                Activity data unavailable
              </p>

              <p className="mt-1 text-sm text-red-300/80">
                {error}
              </p>
            </div>
          )}

          {/* Statistics */}
          <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Total Events"
              value={stats.total}
              description="Recorded activity"
            />

            <StatCard
              title="Employees"
              value={stats.employees}
              description="Active employees"
            />

            <StatCard
              title="Event Types"
              value={stats.eventTypes}
              description="Different event types"
            />

            <StatCard
              title="Today"
              value={stats.today}
              description="Events today"
              valueClass="text-blue-400"
            />
          </section>

          {/* Filters */}
          <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <h2 className="font-semibold">
                  Activity Logs
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Review recorded employee activity.
                </p>
              </div>

              <div className="flex flex-col gap-3 sm:flex-row">
                <input
                  type="text"
                  placeholder="Search employee, event..."
                  value={search}
                  onChange={(e) =>
                    setSearch(e.target.value)
                  }
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-2 text-sm text-white outline-none placeholder:text-slate-500 focus:border-blue-500 sm:w-64"
                />

                <select
                  value={eventFilter}
                  onChange={(e) =>
                    setEventFilter(e.target.value)
                  }
                  className="rounded-lg border border-slate-700 bg-slate-950 px-4 py-2 text-sm text-white outline-none focus:border-blue-500"
                >
                  <option value="all">
                    All Events
                  </option>

                  {eventTypes.map((eventType) => (
                    <option
                      key={eventType}
                      value={eventType}
                    >
                      {eventType}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </section>

          {/* Activity Table */}
          <section className="mt-5 overflow-hidden rounded-2xl border border-slate-800 bg-slate-900">
            {loading ? (
              <div className="flex min-h-[350px] items-center justify-center">
                <div className="text-center">
                  <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-slate-700 border-t-blue-500" />

                  <p className="mt-4 text-sm text-slate-500">
                    Loading activity...
                  </p>
                </div>
              </div>
            ) : filteredActivities.length === 0 ? (
              <div className="px-6 py-16 text-center">
                <div className="text-4xl">📋</div>

                <h3 className="mt-4 text-lg font-semibold">
                  No activity found
                </h3>

                <p className="mt-2 text-sm text-slate-500">
                  No activity matches the current filters.
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[950px]">
                  <thead className="border-b border-slate-800 bg-slate-950/60">
                    <tr className="text-left text-xs uppercase tracking-wider text-slate-500">
                      <th className="px-6 py-4">
                        Employee
                      </th>

                      <th className="px-6 py-4">
                        Event
                      </th>

                      <th className="px-6 py-4">
                        Details
                      </th>

                      <th className="px-6 py-4">
                        Timestamp
                      </th>

                      <th className="px-6 py-4 text-right">
                        Investigation
                      </th>
                    </tr>
                  </thead>

                  <tbody className="divide-y divide-slate-800">
                    {filteredActivities.map(
                      (activity, index) => (
                        <tr
                          key={
                            activity.id ||
                            `${activity.employee_id}-${index}`
                          }
                          className="transition hover:bg-slate-800/40"
                        >
                          {/* Employee */}
                          <td className="px-6 py-5">
                            <span className="rounded-lg bg-slate-800 px-3 py-2 text-xs font-medium text-slate-300">
                              {activity.employee_id ||
                                "Unknown"}
                            </span>
                          </td>

                          {/* Event */}
                          <td className="px-6 py-5">
                            <span
                              className={`rounded-full border px-3 py-1 text-xs font-medium ${getEventClass(
                                activity.event_type
                              )}`}
                            >
                              {activity.event_type ||
                                "Unknown Event"}
                            </span>
                          </td>

                          {/* Details */}
                          <td className="max-w-[380px] px-6 py-5">
                            <pre className="max-h-24 overflow-auto whitespace-pre-wrap break-words text-xs leading-5 text-slate-400">
                              {formatDetails(
                                activity.details
                              )}
                            </pre>
                          </td>

                          {/* Timestamp */}
                          <td className="px-6 py-5 text-sm text-slate-400">
                            {formatDate(
                              activity.timestamp
                            )}
                          </td>

                          {/* Action */}
                          <td className="px-6 py-5 text-right">
                            <Link
                              href="/investigation"
                              className="rounded-lg border border-slate-700 px-3 py-2 text-xs font-medium text-slate-300 transition hover:border-blue-500 hover:text-blue-400"
                            >
                              Investigate
                            </Link>
                          </td>
                        </tr>
                      )
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          {/* Navigation */}
          <section className="mt-8 grid grid-cols-1 gap-4 md:grid-cols-3">
            <NavigationCard
              href="/employees"
              title="Employee Intelligence"
              description="View employee risk scores and behavioral profiles."
            />

            <NavigationCard
              href="/anomalies"
              title="Anomaly Detection"
              description="Review rule-based and ML-detected anomalies."
            />

            <NavigationCard
              href="/investigation"
              title="Threat Investigation"
              description="Investigate suspicious employee activity."
            />
          </section>
        </div>
      </main>
    </AuthGuard>
  );
}

function StatCard({
  title,
  value,
  description,
  valueClass = "text-white",
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
        {title}
      </p>

      <p
        className={`mt-2 text-3xl font-bold ${valueClass}`}
      >
        {value}
      </p>

      <p className="mt-1 text-xs text-slate-500">
        {description}
      </p>
    </div>
  );
}

function NavigationCard({
  href,
  title,
  description,
}) {
  return (
    <Link
      href={href}
      className="group rounded-2xl border border-slate-800 bg-slate-900 p-5 transition hover:border-blue-500/50 hover:bg-slate-800/60"
    >
      <h3 className="font-semibold text-white group-hover:text-blue-400">
        {title}
      </h3>

      <p className="mt-2 text-sm leading-6 text-slate-400">
        {description}
      </p>

      <div className="mt-4 text-sm text-blue-400">
        Open →
      </div>
    </Link>
  );
}
"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import AuthGuard from "@/components/AuthGuard";
import api, { clearSession, getStoredRole, isLoggedIn } from "@/lib/api";

export default function AnomaliesPage() {
  const router = useRouter();

  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (!isLoggedIn()) {
      router.replace("/login");
      return;
    }

    loadAnomalies();
  }, [router]);

  const loadAnomalies = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/anomalies/summary");

      setSummary(response.data);
    } catch (err) {
      console.error("Anomaly summary error:", err);

      if (err?.response?.status === 401) {
        clearSession();
        router.replace("/login");
        return;
      }

      setError(
        err?.response?.data?.detail ||
          "Unable to load anomaly detection data."
      );
    } finally {
      setLoading(false);
    }
  };

  const normalizeArray = (value) => {
    if (Array.isArray(value)) return value;

    if (value && typeof value === "object") {
      for (const key of Object.keys(value)) {
        if (Array.isArray(value[key])) {
          return value[key];
        }
      }
    }

    return [];
  };

  const ruleAnomalies = useMemo(() => {
    if (!summary) return [];

    return normalizeArray(
      summary.rule_anomalies ||
        summary.ruleAnomalies ||
        summary.rules ||
        summary.rule_based_anomalies
    );
  }, [summary]);

  const mlAnomalies = useMemo(() => {
    if (!summary) return [];

    return normalizeArray(
      summary.ml_anomalies ||
        summary.mlAnomalies ||
        summary.ml ||
        summary.machine_learning_anomalies
    );
  }, [summary]);

  const allAnomalies = useMemo(() => {
    const rules = ruleAnomalies.map((item) => ({
      ...item,
      source: "Rule Engine",
      type:
        item.indicator ||
        item.anomaly_type ||
        item.type ||
        "Rule anomaly",
    }));

    const ml = mlAnomalies.map((item) => ({
      ...item,
      source: "ML Detection",
      type:
        item.indicator ||
        item.anomaly_type ||
        "Behavioral anomaly",
    }));

    return [...rules, ...ml];
  }, [ruleAnomalies, mlAnomalies]);

  const filteredAnomalies = useMemo(() => {
    let data = [...allAnomalies];

    if (filter !== "all") {
      data = data.filter((item) => {
        if (filter === "rule") return item.source === "Rule Engine";
        if (filter === "ml") return item.source === "ML Detection";

        if (filter === "critical") {
          return String(item.severity || "").toLowerCase() === "critical";
        }

        if (filter === "high") {
          return String(item.severity || "").toLowerCase() === "high";
        }

        return true;
      });
    }

    if (search.trim()) {
      const query = search.toLowerCase();

      data = data.filter((item) =>
        JSON.stringify(item).toLowerCase().includes(query)
      );
    }

    return data;
  }, [allAnomalies, filter, search]);

  const stats = useMemo(() => {
    const critical = allAnomalies.filter(
      (item) => String(item.severity || "").toLowerCase() === "critical"
    ).length;

    const high = allAnomalies.filter(
      (item) => String(item.severity || "").toLowerCase() === "high"
    ).length;

    const medium = allAnomalies.filter(
      (item) => String(item.severity || "").toLowerCase() === "medium"
    ).length;

    return {
      total: allAnomalies.length,
      rule: ruleAnomalies.length,
      ml: mlAnomalies.length,
      critical,
      high,
      medium,
    };
  }, [allAnomalies, ruleAnomalies, mlAnomalies]);

  const getSeverityClass = (severity) => {
    const value = String(severity || "").toLowerCase();

    if (value === "critical") {
      return "bg-red-500/20 text-red-400 border-red-500/30";
    }

    if (value === "high") {
      return "bg-orange-500/20 text-orange-400 border-orange-500/30";
    }

    if (value === "medium") {
      return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
    }

    if (value === "low") {
      return "bg-green-500/20 text-green-400 border-green-500/30";
    }

    return "bg-gray-500/20 text-gray-400 border-gray-500/30";
  };

  const getSourceClass = (source) => {
    if (source === "ML Detection") {
      return "bg-purple-500/20 text-purple-300 border-purple-500/30";
    }

    return "bg-blue-500/20 text-blue-300 border-blue-500/30";
  };

  const formatDate = (value) => {
    if (!value) return "N/A";

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return String(value);
    }

    return date.toLocaleString();
  };

  const getEmployeeId = (item) => {
    return (
      item.employee_id ||
      item.employeeId ||
      item.user_id ||
      item.userId ||
      "Unknown"
    );
  };

  const getMessage = (item) => {
    return (
      item.message ||
      item.description ||
      item.reason ||
      item.indicator ||
      item.anomaly_type ||
      "Anomalous activity detected"
    );
  };

  return (
    <AuthGuard>
      <main className="min-h-screen bg-slate-950 text-white">
        {/* Header */}
        <header className="border-b border-slate-800 bg-slate-900/80">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
            <div>
              <h1 className="text-2xl font-bold">
                Anomaly Detection
              </h1>

              <p className="mt-1 text-sm text-slate-400">
                Rule-based and machine-learning behavioral anomaly detection
              </p>
            </div>

            <div className="flex items-center gap-3">
              <Link
                href="/dashboard"
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:bg-slate-800"
              >
                Dashboard
              </Link>

              <button
                onClick={loadAnomalies}
                disabled={loading}
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
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
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h3 className="font-semibold text-red-400">
                    Anomaly data unavailable
                  </h3>

                  <p className="mt-1 text-sm text-red-300/80">
                    {error}
                  </p>
                </div>

                <button
                  onClick={loadAnomalies}
                  className="rounded-lg border border-red-500/30 px-3 py-1.5 text-sm text-red-300 hover:bg-red-500/10"
                >
                  Retry
                </button>
              </div>
            </div>
          )}

          {/* Loading */}
          {loading && !summary ? (
            <div className="flex min-h-[400px] items-center justify-center">
              <div className="text-center">
                <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-slate-700 border-t-blue-500" />

                <p className="mt-4 text-sm text-slate-400">
                  Loading anomaly intelligence...
                </p>
              </div>
            </div>
          ) : (
            <>
              {/* Statistics */}
              <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-6">
                <StatCard
                  title="Total"
                  value={stats.total}
                  description="All anomalies"
                />

                <StatCard
                  title="Rule"
                  value={stats.rule}
                  description="Rule engine"
                />

                <StatCard
                  title="ML"
                  value={stats.ml}
                  description="ML detection"
                />

                <StatCard
                  title="Critical"
                  value={stats.critical}
                  description="Critical severity"
                  valueClass="text-red-400"
                />

                <StatCard
                  title="High"
                  value={stats.high}
                  description="High severity"
                  valueClass="text-orange-400"
                />

                <StatCard
                  title="Medium"
                  value={stats.medium}
                  description="Medium severity"
                  valueClass="text-yellow-400"
                />
              </section>

              {/* Detection Overview */}
              <section className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
                <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-lg font-semibold">
                        Rule-Based Detection
                      </h2>

                      <p className="mt-1 text-sm text-slate-400">
                        Known suspicious behavior patterns
                      </p>
                    </div>

                    <div className="rounded-xl bg-blue-500/10 px-4 py-3 text-2xl font-bold text-blue-400">
                      {stats.rule}
                    </div>
                  </div>

                  <div className="mt-5 h-2 overflow-hidden rounded-full bg-slate-800">
                    <div
                      className="h-full rounded-full bg-blue-500"
                      style={{
                        width: `${
                          stats.total
                            ? Math.min(
                                (stats.rule / stats.total) * 100,
                                100
                              )
                            : 0
                        }%`,
                      }}
                    />
                  </div>
                </div>

                <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-lg font-semibold">
                        ML Detection
                      </h2>

                      <p className="mt-1 text-sm text-slate-400">
                        Behavioral model anomalies
                      </p>
                    </div>

                    <div className="rounded-xl bg-purple-500/10 px-4 py-3 text-2xl font-bold text-purple-400">
                      {stats.ml}
                    </div>
                  </div>

                  <div className="mt-5 h-2 overflow-hidden rounded-full bg-slate-800">
                    <div
                      className="h-full rounded-full bg-purple-500"
                      style={{
                        width: `${
                          stats.total
                            ? Math.min(
                                (stats.ml / stats.total) * 100,
                                100
                              )
                            : 0
                        }%`,
                      }}
                    />
                  </div>
                </div>
              </section>

              {/* Filters */}
              <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                  <div>
                    <h2 className="font-semibold">
                      Detected Anomalies
                    </h2>

                    <p className="mt-1 text-sm text-slate-400">
                      Review suspicious employee activity detected by ITBIS
                    </p>
                  </div>

                  <div className="flex flex-col gap-3 sm:flex-row">
                    <input
                      type="text"
                      placeholder="Search employee, anomaly..."
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                      className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-2 text-sm text-white outline-none placeholder:text-slate-500 focus:border-blue-500 sm:w-64"
                    />

                    <select
                      value={filter}
                      onChange={(e) => setFilter(e.target.value)}
                      className="rounded-lg border border-slate-700 bg-slate-950 px-4 py-2 text-sm text-white outline-none focus:border-blue-500"
                    >
                      <option value="all">All Anomalies</option>
                      <option value="rule">Rule Engine</option>
                      <option value="ml">ML Detection</option>
                      <option value="critical">Critical</option>
                      <option value="high">High</option>
                    </select>
                  </div>
                </div>
              </section>

              {/* Table */}
              <section className="mt-5 overflow-hidden rounded-2xl border border-slate-800 bg-slate-900">
                {filteredAnomalies.length === 0 ? (
                  <div className="px-6 py-16 text-center">
                    <div className="text-4xl">✓</div>

                    <h3 className="mt-4 text-lg font-semibold">
                      No anomalies found
                    </h3>

                    <p className="mt-2 text-sm text-slate-400">
                      No anomaly matches the current filter or search.
                    </p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full min-w-[900px]">
                      <thead className="border-b border-slate-800 bg-slate-950/60">
                        <tr className="text-left text-xs uppercase tracking-wider text-slate-500">
                          <th className="px-6 py-4">
                            Employee
                          </th>

                          <th className="px-6 py-4">
                            Detection Source
                          </th>

                          <th className="px-6 py-4">
                            Anomaly
                          </th>

                          <th className="px-6 py-4">
                            Severity
                          </th>

                          <th className="px-6 py-4">
                            Detected At
                          </th>

                          <th className="px-6 py-4 text-right">
                            Action
                          </th>
                        </tr>
                      </thead>

                      <tbody className="divide-y divide-slate-800">
                        {filteredAnomalies.map((item, index) => {
                          const employeeId = getEmployeeId(item);

                          return (
                            <tr
                              key={
                                item.id ||
                                item._id ||
                                `${employeeId}-${index}`
                              }
                              className="transition hover:bg-slate-800/40"
                            >
                              <td className="px-6 py-4">
                                <div className="font-medium text-white">
                                  {employeeId}
                                </div>

                                {item.name && (
                                  <div className="mt-1 text-xs text-slate-500">
                                    {item.name}
                                  </div>
                                )}
                              </td>

                              <td className="px-6 py-4">
                                <span
                                  className={`rounded-full border px-3 py-1 text-xs font-medium ${getSourceClass(
                                    item.source
                                  )}`}
                                >
                                  {item.source}
                                </span>
                              </td>

                              <td className="max-w-[300px] px-6 py-4">
                                <div className="font-medium text-slate-200">
                                  {item.type}
                                </div>

                                <div className="mt-1 truncate text-xs text-slate-500">
                                  {getMessage(item)}
                                </div>
                              </td>

                              <td className="px-6 py-4">
                                <span
                                  className={`rounded-full border px-3 py-1 text-xs font-semibold capitalize ${getSeverityClass(
                                    item.severity
                                  )}`}
                                >
                                  {item.severity || "Unknown"}
                                </span>
                              </td>

                              <td className="px-6 py-4 text-sm text-slate-400">
                                {formatDate(
                                  item.detected_at ||
                                    item.timestamp ||
                                    item.created_at
                                )}
                              </td>

                              <td className="px-6 py-4 text-right">
                                <Link
                                  href="/investigation"
                                  className="rounded-lg border border-slate-700 px-3 py-2 text-xs font-medium text-slate-300 transition hover:border-blue-500 hover:text-blue-400"
                                >
                                  Investigate
                                </Link>
                              </td>
                            </tr>
                          );
                        })}
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
                  description="View risk scores, UEBA profiles and peer comparison."
                />

                <NavigationCard
                  href="/investigation"
                  title="Threat Investigation"
                  description="Investigate suspicious employees and incidents."
                />

                <NavigationCard
                  href="/alerts"
                  title="Security Alerts"
                  description="Review generated alerts and response actions."
                />
              </section>
            </>
          )}
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

      <p className={`mt-2 text-3xl font-bold ${valueClass}`}>
        {value}
      </p>

      <p className="mt-1 text-xs text-slate-500">
        {description}
      </p>
    </div>
  );
}

function NavigationCard({ href, title, description }) {
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
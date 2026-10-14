"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import AuthGuard from "@/components/AuthGuard";
import api, { clearSession, isLoggedIn } from "@/lib/api";

export default function ReportsPage() {
  const router = useRouter();

  const [employees, setEmployees] = useState([]);
  const [anomalySummary, setAnomalySummary] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [incidents, setIncidents] = useState([]);

  const [riskProfiles, setRiskProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isLoggedIn()) {
      router.replace("/login");
      return;
    }

    loadReportData();
  }, [router]);

  const loadReportData = async () => {
    try {
      setLoading(true);
      setError("");

      const results = await Promise.allSettled([
        api.get("/employees"),
        api.get("/anomalies/summary"),
        api.get("/alerts"),
        api.get("/incidents"),
      ]);

      if (results[0].status === "fulfilled") {
        const data = results[0].value.data;

        setEmployees(
          Array.isArray(data)
            ? data
            : data?.employees || []
        );
      }

      if (results[1].status === "fulfilled") {
        setAnomalySummary(results[1].value.data);
      }

      if (results[2].status === "fulfilled") {
        const data = results[2].value.data;

        setAlerts(
          Array.isArray(data)
            ? data
            : data?.alerts || []
        );
      }

      if (results[3].status === "fulfilled") {
        const data = results[3].value.data;

        setIncidents(
          Array.isArray(data)
            ? data
            : data?.incidents || []
        );
      }

      const unauthorized = results.some(
        (result) =>
          result.status === "rejected" &&
          result.reason?.response?.status === 401
      );

      if (unauthorized) {
        clearSession();
        router.replace("/login");
        return;
      }

      const allFailed = results.every(
        (result) => result.status === "rejected"
      );

      if (allFailed) {
        setError(
          "Unable to load report data from the backend."
        );
      }
    } catch (err) {
      console.error("Report loading error:", err);

      if (err?.response?.status === 401) {
        clearSession();
        router.replace("/login");
        return;
      }

      setError(
        err?.response?.data?.detail ||
          "Unable to generate security report."
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
    if (!anomalySummary) return [];

    return normalizeArray(
      anomalySummary.rule_anomalies ||
        anomalySummary.ruleAnomalies ||
        anomalySummary.rules ||
        anomalySummary.rule_based_anomalies
    );
  }, [anomalySummary]);

  const mlAnomalies = useMemo(() => {
    if (!anomalySummary) return [];

    return normalizeArray(
      anomalySummary.ml_anomalies ||
        anomalySummary.mlAnomalies ||
        anomalySummary.ml ||
        anomalySummary.machine_learning_anomalies
    );
  }, [anomalySummary]);

  const anomalyCount = ruleAnomalies.length + mlAnomalies.length;

  const criticalAnomalies = useMemo(() => {
    return [...ruleAnomalies, ...mlAnomalies].filter(
      (item) =>
        String(item.severity || "").toLowerCase() ===
        "critical"
    ).length;
  }, [ruleAnomalies, mlAnomalies]);

  const highAnomalies = useMemo(() => {
    return [...ruleAnomalies, ...mlAnomalies].filter(
      (item) =>
        String(item.severity || "").toLowerCase() ===
        "high"
    ).length;
  }, [ruleAnomalies, mlAnomalies]);

  const openIncidents = useMemo(() => {
    return incidents.filter(
      (incident) =>
        String(incident.status || "").toLowerCase() !==
        "resolved"
    ).length;
  }, [incidents]);

  const criticalAlerts = useMemo(() => {
    return alerts.filter(
      (alert) =>
        String(alert.severity || "").toLowerCase() ===
        "critical"
    ).length;
  }, [alerts]);

  const loadRiskProfiles = async () => {
    if (!employees.length) return;

    const results = await Promise.allSettled(
      employees.map(async (employee) => {
        const employeeId =
          employee.employee_id ||
          employee.employeeId;

        if (!employeeId) return null;

        try {
          const response = await api.get(
            `/ueba/profile/${encodeURIComponent(employeeId)}`
          );

          const profile = response.data;

          return {
            employee_id: employeeId,
            name: employee.name,
            department: employee.department,
            final_score:
              profile?.risk_score?.final_score ?? 0,
            risk_level:
              profile?.risk_score?.risk_level || "Low",
          };
        } catch {
          return null;
        }
      })
    );

    const profiles = results
      .filter(
        (result) =>
          result.status === "fulfilled" &&
          result.value
      )
      .map((result) => result.value)
      .sort(
        (a, b) =>
          b.final_score - a.final_score
      );

    setRiskProfiles(profiles);
  };

  useEffect(() => {
    if (!loading && employees.length > 0) {
      loadRiskProfiles();
    }
  }, [loading, employees]);

  const highRiskEmployees = riskProfiles.filter(
    (employee) =>
      employee.risk_level === "High" ||
      employee.risk_level === "Critical"
  );

  const getRiskClass = (level) => {
    const value = String(level || "").toLowerCase();

    if (value === "critical") {
      return "text-red-400";
    }

    if (value === "high") {
      return "text-orange-400";
    }

    if (value === "medium") {
      return "text-yellow-400";
    }

    return "text-green-400";
  };

  const formatDate = (value) => {
    if (!value) return "N/A";

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return String(value);
    }

    return date.toLocaleString();
  };

  const generateTextReport = () => {
    const report = `
ITBIS SECURITY INTELLIGENCE REPORT
Generated: ${new Date().toLocaleString()}

==============================
SECURITY OVERVIEW
==============================

Total Employees: ${employees.length}
Total Anomalies: ${anomalyCount}
Rule-Based Anomalies: ${ruleAnomalies.length}
ML Anomalies: ${mlAnomalies.length}
Critical Anomalies: ${criticalAnomalies}
High Anomalies: ${highAnomalies}

Open Incidents: ${openIncidents}
Total Alerts: ${alerts.length}
Critical Alerts: ${criticalAlerts}

==============================
HIGH-RISK EMPLOYEES
==============================

${
  highRiskEmployees.length
    ? highRiskEmployees
        .map(
          (employee) =>
            `${employee.employee_id} | ${
              employee.name || "N/A"
            } | ${
              employee.department || "N/A"
            } | Risk Score: ${
              employee.final_score
            } | ${employee.risk_level}`
        )
        .join("\n")
    : "No high-risk employees detected."
}

==============================
END OF REPORT
==============================
`;

    const blob = new Blob([report], {
      type: "text/plain",
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = `ITBIS_Security_Report_${new Date()
      .toISOString()
      .slice(0, 10)}.txt`;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  };

  return (
    <AuthGuard>
      <main className="min-h-screen bg-slate-950 text-white">
        {/* Header */}
        <header className="border-b border-slate-800 bg-slate-900/80">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
            <div>
              <h1 className="text-2xl font-bold">
                Security Reports
              </h1>

              <p className="mt-1 text-sm text-slate-400">
                ITBIS security posture and intelligence overview.
              </p>
            </div>

            <div className="flex gap-3">
              <Link
                href="/dashboard"
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800"
              >
                Dashboard
              </Link>

              <button
                onClick={loadReportData}
                disabled={loading}
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium hover:bg-blue-500 disabled:opacity-50"
              >
                {loading ? "Refreshing..." : "Refresh"}
              </button>

              <button
                onClick={generateTextReport}
                disabled={loading}
                className="rounded-lg border border-blue-500/40 bg-blue-500/10 px-4 py-2 text-sm font-medium text-blue-400 hover:bg-blue-500/20 disabled:opacity-50"
              >
                Export Report
              </button>
            </div>
          </div>
        </header>

        <div className="mx-auto max-w-7xl px-6 py-8">
          {error && (
            <div className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4">
              <p className="font-medium text-red-400">
                Report data partially unavailable
              </p>

              <p className="mt-1 text-sm text-red-300/80">
                {error}
              </p>
            </div>
          )}

          {/* Overview */}
          <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <ReportCard
              title="Employees"
              value={employees.length}
              description="Employees monitored"
            />

            <ReportCard
              title="Anomalies"
              value={anomalyCount}
              description="Detected anomalies"
              valueClass="text-orange-400"
            />

            <ReportCard
              title="Open Incidents"
              value={openIncidents}
              description="Active investigations"
              valueClass="text-yellow-400"
            />

            <ReportCard
              title="Alerts"
              value={alerts.length}
              description="Security alerts"
              valueClass="text-red-400"
            />
          </section>

          {/* Detection Breakdown */}
          <section className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-lg font-semibold">
                Anomaly Detection
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Detection engine breakdown
              </p>

              <div className="mt-6 space-y-5">
                <ProgressRow
                  label="Rule-Based Detection"
                  value={ruleAnomalies.length}
                  total={anomalyCount}
                />

                <ProgressRow
                  label="Machine Learning"
                  value={mlAnomalies.length}
                  total={anomalyCount}
                />

                <ProgressRow
                  label="Critical"
                  value={criticalAnomalies}
                  total={anomalyCount}
                />

                <ProgressRow
                  label="High"
                  value={highAnomalies}
                  total={anomalyCount}
                />
              </div>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-lg font-semibold">
                Security Posture
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Current investigation and alert status
              </p>

              <div className="mt-6 grid grid-cols-2 gap-4">
                <MiniMetric
                  label="Open Incidents"
                  value={openIncidents}
                />

                <MiniMetric
                  label="Total Alerts"
                  value={alerts.length}
                />

                <MiniMetric
                  label="Critical Alerts"
                  value={criticalAlerts}
                />

                <MiniMetric
                  label="High-Risk Employees"
                  value={highRiskEmployees.length}
                />
              </div>
            </div>
          </section>

          {/* Risk Ranking */}
          <section className="mt-8 overflow-hidden rounded-2xl border border-slate-800 bg-slate-900">
            <div className="border-b border-slate-800 p-6">
              <h2 className="text-lg font-semibold">
                Employee Risk Ranking
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Employees ranked by current UEBA risk score.
              </p>
            </div>

            {loading ? (
              <div className="p-12 text-center text-sm text-slate-500">
                Loading security intelligence...
              </div>
            ) : riskProfiles.length === 0 ? (
              <div className="p-12 text-center text-sm text-slate-500">
                No UEBA risk profiles are currently available.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="border-b border-slate-800 bg-slate-950/50">
                    <tr className="text-left text-xs uppercase tracking-wider text-slate-500">
                      <th className="px-6 py-4">
                        Employee
                      </th>

                      <th className="px-6 py-4">
                        Department
                      </th>

                      <th className="px-6 py-4">
                        Risk Score
                      </th>

                      <th className="px-6 py-4">
                        Risk Level
                      </th>

                      <th className="px-6 py-4 text-right">
                        Action
                      </th>
                    </tr>
                  </thead>

                  <tbody className="divide-y divide-slate-800">
                    {riskProfiles
                      .slice(0, 10)
                      .map((employee) => (
                        <tr
                          key={employee.employee_id}
                          className="hover:bg-slate-800/40"
                        >
                          <td className="px-6 py-4">
                            <div className="font-medium">
                              {employee.employee_id}
                            </div>

                            <div className="mt-1 text-xs text-slate-500">
                              {employee.name || "N/A"}
                            </div>
                          </td>

                          <td className="px-6 py-4 text-sm text-slate-400">
                            {employee.department || "N/A"}
                          </td>

                          <td className="px-6 py-4">
                            <span className="text-lg font-bold">
                              {employee.final_score}
                            </span>
                            <span className="ml-1 text-xs text-slate-600">
                              / 100
                            </span>
                          </td>

                          <td className="px-6 py-4">
                            <span
                              className={`font-semibold ${getRiskClass(
                                employee.risk_level
                              )}`}
                            >
                              {employee.risk_level}
                            </span>
                          </td>

                          <td className="px-6 py-4 text-right">
                            <Link
                              href="/employees"
                              className="rounded-lg border border-slate-700 px-3 py-2 text-xs text-slate-300 hover:border-blue-500 hover:text-blue-400"
                            >
                              View Employee
                            </Link>
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          {/* Quick Navigation */}
          <section className="mt-8 grid grid-cols-1 gap-4 md:grid-cols-4">
            <NavigationCard
              href="/employees"
              title="Employees"
              description="Employee risk and UEBA intelligence."
            />

            <NavigationCard
              href="/anomalies"
              title="Anomalies"
              description="Rule and ML anomaly detection."
            />

            <NavigationCard
              href="/investigation"
              title="Investigations"
              description="Threat investigation and evidence."
            />

            <NavigationCard
              href="/alerts"
              title="Alerts"
              description="Security alert management."
            />
          </section>
        </div>
      </main>
    </AuthGuard>
  );
}

function ReportCard({
  title,
  value,
  description,
  valueClass = "text-white",
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <p className="text-xs uppercase tracking-wider text-slate-500">
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

function MiniMetric({ label, value }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
      <p className="text-xs text-slate-500">
        {label}
      </p>

      <p className="mt-2 text-2xl font-bold">
        {value}
      </p>
    </div>
  );
}

function ProgressRow({ label, value, total }) {
  const percentage =
    total > 0
      ? Math.min((value / total) * 100, 100)
      : 0;

  return (
    <div>
      <div className="mb-2 flex items-center justify-between text-sm">
        <span className="text-slate-300">
          {label}
        </span>

        <span className="font-semibold text-slate-400">
          {value}
        </span>
      </div>

      <div className="h-2 overflow-hidden rounded-full bg-slate-800">
        <div
          className="h-full rounded-full bg-blue-500 transition-all"
          style={{ width: `${percentage}%` }}
        />
      </div>
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
      <h3 className="font-semibold group-hover:text-blue-400">
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
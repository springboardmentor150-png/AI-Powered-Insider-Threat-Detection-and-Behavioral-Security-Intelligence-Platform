"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import AuthGuard from "@/components/AuthGuard";

import api, {
  clearSession,
  getStoredRole,
  isLoggedIn,
} from "@/lib/api";


// =========================================================
// EMPLOYEE INTELLIGENCE PAGE
// DAY 20–24
//
// Day 20  - Employee intelligence
// Day 21  - Risk scoring
// Day 22  - Risk posture
// Day 23  - UEBA peer comparison
// Day 24  - Behavioral trend analysis
// =========================================================

export default function EmployeesPage() {
  const router = useRouter();

  // =======================================================
  // STATE
  // =======================================================

  const [employees, setEmployees] = useState([]);

  const [selectedEmployee, setSelectedEmployee] =
    useState(null);

  const [riskProfile, setRiskProfile] =
    useState(null);

  const [riskTrend, setRiskTrend] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [riskLoading, setRiskLoading] =
    useState(false);

  const [refreshing, setRefreshing] =
    useState(false);

  const [error, setError] =
    useState("");

  const [search, setSearch] =
    useState("");

  const [departmentFilter, setDepartmentFilter] =
    useState("All");

  const [role, setRole] =
    useState("");

  // =======================================================
  // AUTHENTICATION
  // =======================================================

  useEffect(() => {
    if (!isLoggedIn()) {
      router.replace("/login");
      return;
    }

    setRole(getStoredRole() || "user");

    loadEmployees();
  }, [router]);

  // =======================================================
  // LOAD EMPLOYEES
  // =======================================================

  async function loadEmployees() {
    try {
      setLoading(true);
      setError("");

      const response =
        await api.get("/employees");

      const data = response.data;

      let employeeList = [];

      if (Array.isArray(data)) {
        employeeList = data;
      } else {
        employeeList =
          data?.employees || [];
      }

      setEmployees(employeeList);

      // Select first employee automatically
      if (employeeList.length > 0) {
        const currentEmployee =
          employeeList.find(
            (employee) =>
              employee.employee_id ===
              selectedEmployee
          );

        const employeeToSelect =
          currentEmployee ||
          employeeList[0];

        setSelectedEmployee(
          employeeToSelect.employee_id
        );

        await loadRiskIntelligence(
          employeeToSelect.employee_id
        );
      }
    } catch (err) {
      console.error(
        "Employee loading error:",
        err
      );

      if (
        err?.response?.status === 401
      ) {
        handleLogout();
        return;
      }

      setError(
        err?.response?.data?.detail ||
          "Unable to load employee data."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  // =======================================================
  // LOAD DAY 21–24 INTELLIGENCE
  // =======================================================

  async function loadRiskIntelligence(
    employeeId
  ) {
    if (!employeeId) {
      return;
    }

    try {
      setRiskLoading(true);

      const [
        profileResult,
        trendResult,
      ] = await Promise.allSettled([
        // Day 21–23
        api.get(
          `/ueba/profile/${employeeId}`
        ),

        // Day 24
        api.get(
          `/ueba/trend/${employeeId}?days=30`
        ),
      ]);

      // ===================================================
      // UEBA PROFILE
      // ===================================================

      if (
        profileResult.status ===
        "fulfilled"
      ) {
        setRiskProfile(
          profileResult.value.data
        );
      } else {
        console.error(
          "UEBA profile error:",
          profileResult.reason
        );

        setRiskProfile(null);
      }

      // ===================================================
      // 30 DAY TREND
      // ===================================================

      if (
        trendResult.status ===
        "fulfilled"
      ) {
        setRiskTrend(
          trendResult.value.data?.trend ||
            []
        );
      } else {
        console.error(
          "UEBA trend error:",
          trendResult.reason
        );

        setRiskTrend([]);
      }
    } catch (err) {
      console.error(
        "Risk intelligence error:",
        err
      );

      setRiskProfile(null);
      setRiskTrend([]);
    } finally {
      setRiskLoading(false);
    }
  }

  // =======================================================
  // EMPLOYEE SELECTION
  // =======================================================

  async function handleEmployeeSelect(
    employeeId
  ) {
    setSelectedEmployee(employeeId);

    await loadRiskIntelligence(
      employeeId
    );
  }

  // =======================================================
  // REFRESH
  // =======================================================

  async function handleRefresh() {
    setRefreshing(true);

    await loadEmployees();
  }

  // =======================================================
  // LOGOUT
  // =======================================================

  function handleLogout() {
    clearSession();

    router.replace("/login");
  }

  // =======================================================
  // DEPARTMENTS
  // =======================================================

  const departments = useMemo(() => {
    const values =
      employees
        .map(
          (employee) =>
            employee.department
        )
        .filter(Boolean);

    return [
      "All",
      ...Array.from(
        new Set(values)
      ),
    ];
  }, [employees]);

  // =======================================================
  // FILTER EMPLOYEES
  // =======================================================

  const filteredEmployees =
    useMemo(() => {
      const searchValue =
        search
          .trim()
          .toLowerCase();

      return employees.filter(
        (employee) => {
          const matchesSearch =
            !searchValue ||
            String(
              employee.employee_id ||
                ""
            )
              .toLowerCase()
              .includes(
                searchValue
              ) ||
            String(
              employee.name || ""
            )
              .toLowerCase()
              .includes(
                searchValue
              ) ||
            String(
              employee.department ||
                ""
            )
              .toLowerCase()
              .includes(
                searchValue
              ) ||
            String(
              employee.designation ||
                ""
            )
              .toLowerCase()
              .includes(
                searchValue
              );

          const matchesDepartment =
            departmentFilter ===
              "All" ||
            employee.department ===
              departmentFilter;

          return (
            matchesSearch &&
            matchesDepartment
          );
        }
      );
    }, [
      employees,
      search,
      departmentFilter,
    ]);

  // =======================================================
  // SELECTED EMPLOYEE OBJECT
  // =======================================================

  const selectedEmployeeData =
    employees.find(
      (employee) =>
        employee.employee_id ===
        selectedEmployee
    );

  // =======================================================
  // RISK DATA
  // =======================================================

  const riskScore =
    Number(
      riskProfile?.risk_score
        ?.final_score
    ) || 0;

  const riskLevel =
    riskProfile?.risk_score
      ?.risk_level ||
    "Low";

  const trendDirection =
    riskProfile?.trend
      ?.direction ||
    "stable";

  const peerComparison =
    riskProfile?.peer_comparison ||
    {};

  const subScores =
    riskProfile?.risk_score
      ?.sub_scores || {};

  // =======================================================
  // TREND MAX
  // =======================================================

  const maxTrendValue =
    Math.max(
      ...riskTrend.map(
        (item) =>
          Number(
            item.anomaly_count
          ) || 0
      ),
      1
    );

  // =======================================================
  // RISK COUNTS
  // =======================================================

  const lowRiskEmployees =
    employees.length;

  // =======================================================
  // LOADING
  // =======================================================

  if (loading) {
    return (
      <EmployeesSkeleton />
    );
  }

  // =======================================================
  // PAGE
  // =======================================================

  return (
    <AuthGuard>
      <main className="min-h-screen bg-[#07111f] text-slate-100">

        {/* =================================================
            SIDEBAR
        ================================================= */}

        <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-white/10 bg-[#091522] lg:flex lg:flex-col">

          {/* LOGO */}

          <div className="flex h-20 items-center border-b border-white/10 px-6">

            <div className="flex items-center gap-3">

              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/10 ring-1 ring-blue-400/30">

                <span className="text-lg font-black text-blue-400">
                  IT
                </span>

              </div>

              <div>

                <h1 className="text-lg font-black tracking-tight">
                  ITBIS
                </h1>

                <p className="text-[10px] uppercase tracking-[0.18em] text-slate-500">
                  Security Intelligence
                </p>

              </div>

            </div>

          </div>

          {/* NAVIGATION */}

          <nav className="flex-1 space-y-1 px-4 py-6">

            <NavItem
              href="/dashboard"
              label="Security Overview"
              icon="◈"
            />

            <NavItem
              href="/employees"
              label="Employee Intelligence"
              icon="◎"
              active
            />

            <NavItem
              href="/anomalies"
              label="Anomaly Detection"
              icon="△"
            />

            <div className="my-5 border-t border-white/10" />

            <p className="px-3 pb-2 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-600">
              Intelligence
            </p>

            <NavItem
              href="/activity"
              label="Activity Monitoring"
              icon="◌"
            />

            <NavItem
              href="/alerts"
              label="Security Alerts"
              icon="!"
            />

            <NavItem
              href="/reports"
              label="Security Reports"
              icon="▤"
            />

            <NavItem
              href="/investigation"
              label="Threat Investigation"
              icon="⌕"
            />

          </nav>

          {/* BOTTOM */}

          <div className="border-t border-white/10 p-4">

            <div className="mb-3 rounded-xl bg-white/[0.03] p-3">

              <p className="text-[10px] uppercase tracking-widest text-slate-600">
                Current Role
              </p>

              <p className="mt-1 text-sm font-semibold capitalize text-slate-300">
                {role || "User"}
              </p>

            </div>

            <button
              onClick={handleLogout}
              className="flex w-full items-center justify-center gap-2 rounded-xl border border-red-500/20 bg-red-500/5 px-4 py-2.5 text-sm font-semibold text-red-400 transition hover:border-red-500/40 hover:bg-red-500/10"
            >
              <span>↪</span>
              Logout
            </button>

          </div>

        </aside>

        {/* =================================================
            MAIN
        ================================================= */}

        <div className="lg:pl-64">

          {/* TOP BAR */}

          <header className="sticky top-0 z-30 border-b border-white/10 bg-[#07111f]/90 backdrop-blur-xl">

            <div className="flex h-20 items-center justify-between px-5 sm:px-8">

              <div>

                <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-blue-400">
                  Security Intelligence
                </p>

                <h2 className="mt-1 text-xl font-bold tracking-tight sm:text-2xl">
                  Employee Intelligence
                </h2>

              </div>

              <div className="flex items-center gap-3">

                <button
                  onClick={handleRefresh}
                  disabled={refreshing}
                  className="rounded-xl border border-white/10 bg-white/[0.03] px-4 py-2.5 text-sm font-semibold text-slate-300 transition hover:bg-white/[0.07] disabled:opacity-50"
                >
                  {refreshing
                    ? "Refreshing..."
                    : "↻ Refresh"}
                </button>

                <div className="hidden items-center gap-2 rounded-xl border border-emerald-400/20 bg-emerald-400/5 px-4 py-2.5 sm:flex">

                  <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.8)]" />

                  <span className="text-xs font-semibold text-emerald-300">
                    UEBA ACTIVE
                  </span>

                </div>

                <button
                  onClick={handleLogout}
                  className="rounded-xl border border-white/10 px-4 py-2.5 text-sm font-semibold text-slate-300 transition hover:bg-white/[0.07]"
                >
                  Logout
                </button>

              </div>

            </div>

          </header>

          {/* =================================================
              CONTENT
          ================================================= */}

          <div className="mx-auto max-w-[1600px] px-5 py-8 sm:px-8">

            {/* ERROR */}

            {error && (
              <div className="mb-6 rounded-2xl border border-amber-400/20 bg-amber-400/5 p-4">

                <div className="flex items-center gap-3">

                  <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-amber-400/10 text-amber-400">
                    !
                  </span>

                  <div>

                    <p className="text-sm font-semibold text-amber-300">
                      Employee service warning
                    </p>

                    <p className="mt-1 text-xs text-slate-400">
                      {error}
                    </p>

                  </div>

                </div>

              </div>
            )}

            {/* =================================================
                PAGE HEADER
            ================================================= */}

            <section className="mb-6">

              <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">

                <div>

                  <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-blue-400">
                    Workforce Intelligence
                  </p>

                  <h3 className="mt-2 text-3xl font-black tracking-tight">
                    Employee Risk Intelligence
                  </h3>

                  <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                    Monitor employee behavior, calculate
                    risk scores, compare employees with
                    their peers, and analyze behavioral
                    trends using UEBA.
                  </p>

                </div>

                <Link
                  href="/investigation"
                  className="rounded-xl border border-blue-400/20 bg-blue-400/5 px-4 py-3 text-sm font-semibold text-blue-400 transition hover:bg-blue-400/10"
                >
                  Threat Investigation →
                </Link>

              </div>

            </section>

            {/* =================================================
                KPI CARDS
            ================================================= */}

            <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

              <KpiCard
                label="Employees"
                value={employees.length}
                description="Registered employee identities"
                icon="◎"
              />

              <KpiCard
                label="Departments"
                value={departments.length - 1}
                description="Organizational units"
                icon="▦"
                accent="blue"
              />

              <KpiCard
                label="Selected Employee"
                value={
                  selectedEmployee ||
                  "N/A"
                }
                description="Current intelligence profile"
                icon="◉"
                accent="green"
              />

              <KpiCard
                label="Current Risk"
                value={
                  selectedEmployee
                    ? riskScore
                    : "—"
                }
                description={
                  selectedEmployee
                    ? `${riskLevel} risk`
                    : "Select an employee"
                }
                icon="!"
                accent={
                  riskScore >= 50
                    ? "red"
                    : riskScore >= 25
                    ? "yellow"
                    : "green"
                }
              />

            </section>

            {/* =================================================
                EMPLOYEE DIRECTORY
            ================================================= */}

            <section className="mt-6 rounded-3xl border border-white/10 bg-[#0b1727] p-6">

              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">

                <div>

                  <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">
                    Employee Directory
                  </p>

                  <h3 className="mt-1 text-lg font-bold">
                    Workforce Records
                  </h3>

                </div>

                <div className="flex flex-col gap-3 sm:flex-row">

                  <input
                    value={search}
                    onChange={(e) =>
                      setSearch(
                        e.target.value
                      )
                    }
                    placeholder="Search employee..."
                    className="w-full rounded-xl border border-white/10 bg-[#07111f] px-4 py-2.5 text-sm text-slate-300 outline-none placeholder:text-slate-600 focus:border-blue-400/40 sm:w-64"
                  />

                  <select
                    value={
                      departmentFilter
                    }
                    onChange={(e) =>
                      setDepartmentFilter(
                        e.target.value
                      )
                    }
                    className="rounded-xl border border-white/10 bg-[#07111f] px-4 py-2.5 text-sm text-slate-300 outline-none focus:border-blue-400/40"
                  >

                    {departments.map(
                      (department) => (
                        <option
                          key={
                            department
                          }
                          value={
                            department
                          }
                        >
                          {department}
                        </option>
                      )
                    )}

                  </select>

                </div>

              </div>

              <div className="mt-6 overflow-x-auto">

                <table className="w-full min-w-[900px]">

                  <thead>

                    <tr className="border-b border-white/10 text-left">

                      <th className="px-4 py-3 text-[10px] font-bold uppercase tracking-wider text-slate-600">
                        Employee
                      </th>

                      <th className="px-4 py-3 text-[10px] font-bold uppercase tracking-wider text-slate-600">
                        Department
                      </th>

                      <th className="px-4 py-3 text-[10px] font-bold uppercase tracking-wider text-slate-600">
                        Designation
                      </th>

                      <th className="px-4 py-3 text-[10px] font-bold uppercase tracking-wider text-slate-600">
                        Risk Score
                      </th>

                      <th className="px-4 py-3 text-[10px] font-bold uppercase tracking-wider text-slate-600">
                        Risk Level
                      </th>

                      <th className="px-4 py-3 text-[10px] font-bold uppercase tracking-wider text-slate-600">
                        Action
                      </th>

                    </tr>

                  </thead>

                  <tbody>

                    {filteredEmployees.length ===
                    0 ? (

                      <tr>

                        <td
                          colSpan="6"
                          className="px-4 py-12 text-center"
                        >

                          <p className="text-sm text-slate-500">
                            No employees found.
                          </p>

                        </td>

                      </tr>

                    ) : (

                      filteredEmployees.map(
                        (employee) => {

                          const isSelected =
                            selectedEmployee ===
                            employee.employee_id;

                          return (
                            <tr
                              key={
                                employee.employee_id
                              }
                              className={`border-b border-white/5 transition ${
                                isSelected
                                  ? "bg-blue-400/5"
                                  : "hover:bg-white/[0.02]"
                              }`}
                            >

                              <td className="px-4 py-4">

                                <button
                                  onClick={() =>
                                    handleEmployeeSelect(
                                      employee.employee_id
                                    )
                                  }
                                  className="flex items-center gap-3 text-left"
                                >

                                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/10 text-sm font-bold text-blue-400">

                                    {String(
                                      employee.name ||
                                        "?"
                                    )
                                      .charAt(0)
                                      .toUpperCase()}

                                  </div>

                                  <div>

                                    <p className="text-sm font-semibold text-slate-200">
                                      {
                                        employee.name
                                      }
                                    </p>

                                    <p className="mt-1 text-[10px] text-blue-400">
                                      {
                                        employee.employee_id
                                      }
                                    </p>

                                  </div>

                                </button>

                              </td>

                              <td className="px-4 py-4">

                                <span className="text-sm text-slate-400">
                                  {
                                    employee.department ||
                                    "N/A"
                                  }
                                </span>

                              </td>

                              <td className="px-4 py-4">

                                <span className="text-sm text-slate-400">
                                  {
                                    employee.designation ||
                                    "N/A"
                                  }
                                </span>

                              </td>

                              <td className="px-4 py-4">

                                {isSelected &&
                                riskProfile ? (

                                  <span
                                    className={`text-lg font-black ${
                                      riskScore >=
                                      75
                                        ? "text-red-400"
                                        : riskScore >=
                                          50
                                        ? "text-orange-400"
                                        : riskScore >=
                                          25
                                        ? "text-amber-400"
                                        : "text-emerald-400"
                                    }`}
                                  >
                                    {
                                      riskScore
                                    }
                                  </span>

                                ) : (

                                  <span className="text-xs text-slate-600">
                                    Select
                                  </span>

                                )}

                              </td>

                              <td className="px-4 py-4">

                                {isSelected &&
                                riskProfile ? (

                                  <RiskBadge
                                    level={
                                      riskLevel
                                    }
                                  />

                                ) : (

                                  <span className="text-xs text-slate-600">
                                    —
                                  </span>

                                )}

                              </td>

                              <td className="px-4 py-4">

                                <button
                                  onClick={() =>
                                    handleEmployeeSelect(
                                      employee.employee_id
                                    )
                                  }
                                  className={`rounded-lg px-3 py-2 text-xs font-semibold transition ${
                                    isSelected
                                      ? "bg-blue-500/10 text-blue-400"
                                      : "bg-white/[0.04] text-slate-400 hover:bg-blue-500/10 hover:text-blue-400"
                                  }`}
                                >
                                  {isSelected
                                    ? "Selected"
                                    : "View Intelligence"}
                                </button>

                              </td>

                            </tr>
                          );
                        }
                      )

                    )}

                  </tbody>

                </table>

              </div>

            </section>

            {/* =================================================
                SELECTED EMPLOYEE INTELLIGENCE
            ================================================= */}

            <section className="mt-6 rounded-3xl border border-white/10 bg-[#0b1727] p-7">

              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

                <div>

                  <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-blue-400">
                    Day 21–24 Intelligence
                  </p>

                  <h3 className="mt-1 text-xl font-bold">
                    Risk & UEBA Profile
                  </h3>

                  {selectedEmployeeData && (
                    <p className="mt-1 text-xs text-slate-500">
                      {
                        selectedEmployeeData.name
                      }{" "}
                      ·{" "}
                      {
                        selectedEmployeeData.employee_id
                      }
                    </p>
                  )}

                </div>

                {selectedEmployee && (
                  <Link
                    href={`/investigation?employee_id=${encodeURIComponent(
                      selectedEmployee
                    )}`}
                    className="rounded-xl border border-white/10 bg-white/[0.03] px-4 py-2.5 text-xs font-semibold text-slate-300 transition hover:bg-white/[0.07]"
                  >
                    Open Investigation →
                  </Link>
                )}

              </div>

              {riskLoading ? (

                <div className="mt-8 rounded-2xl border border-white/5 bg-white/[0.02] p-10 text-center">

                  <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-2 border-white/10 border-t-blue-400" />

                  <p className="text-sm text-slate-500">
                    Loading risk intelligence...
                  </p>

                </div>

              ) : riskProfile ? (

                <div className="mt-7">

                  {/* ==========================================
                      RISK SUMMARY
                  =========================================== */}

                  <div className="grid gap-4 md:grid-cols-3">

                    <div className="rounded-2xl border border-white/5 bg-white/[0.02] p-5">

                      <p className="text-[10px] uppercase tracking-widest text-slate-500">
                        Final Risk Score
                      </p>

                      <p
                        className={`mt-2 text-4xl font-black ${
                          riskScore >= 75
                            ? "text-red-400"
                            : riskScore >= 50
                            ? "text-orange-400"
                            : riskScore >=
                              25
                            ? "text-amber-400"
                            : "text-emerald-400"
                        }`}
                      >
                        {riskScore}
                      </p>

                      <p className="mt-1 text-xs text-slate-600">
                        Weighted score out of 100
                      </p>

                    </div>

                    <div className="rounded-2xl border border-white/5 bg-white/[0.02] p-5">

                      <p className="text-[10px] uppercase tracking-widest text-slate-500">
                        Risk Level
                      </p>

                      <div className="mt-4">
                        <RiskBadge
                          level={riskLevel}
                          large
                        />
                      </div>

                    </div>

                    <div className="rounded-2xl border border-white/5 bg-white/[0.02] p-5">

                      <p className="text-[10px] uppercase tracking-widest text-slate-500">
                        Trend Direction
                      </p>

                      <p
                        className={`mt-3 text-2xl font-black capitalize ${
                          String(
                            trendDirection
                          ).toLowerCase()
                            .includes(
                              "increase"
                            )
                            ? "text-red-400"
                            : String(
                                trendDirection
                              )
                                .toLowerCase()
                                .includes(
                                  "decrease"
                                )
                            ? "text-emerald-400"
                            : "text-blue-400"
                        }`}
                      >
                        {trendDirection}
                      </p>

                      <p className="mt-1 text-xs text-slate-600">
                        Based on behavioral activity
                      </p>

                    </div>

                  </div>

                  {/* ==========================================
                      RISK FACTORS
                  =========================================== */}

                  <div className="mt-6">

                    <p className="mb-4 text-xs font-bold uppercase tracking-widest text-slate-500">
                      Risk Factors
                    </p>

                    <div className="grid gap-3 md:grid-cols-2">

                      <RiskFactor
                        label="Behavioral Anomalies"
                        value={
                          subScores.behavioral_anomalies ??
                          0
                        }
                      />

                      <RiskFactor
                        label="Privilege Misuse"
                        value={
                          subScores.privilege_misuse ??
                          0
                        }
                      />

                      <RiskFactor
                        label="Data Access Violations"
                        value={
                          subScores.data_access_violations ??
                          0
                        }
                      />

                      <RiskFactor
                        label="Access Pattern Deviations"
                        value={
                          subScores.access_pattern_deviations ??
                          0
                        }
                      />

                      <RiskFactor
                        label="Historical Events"
                        value={
                          subScores.historical_events ??
                          0
                        }
                      />

                    </div>

                  </div>

                  {/* ==========================================
                      PEER COMPARISON
                  =========================================== */}

                  <div className="mt-6 rounded-2xl border border-white/5 bg-white/[0.02] p-5">

                    <div className="flex items-center justify-between">

                      <div>

                        <p className="text-xs font-bold uppercase tracking-widest text-slate-500">
                          UEBA Peer Comparison
                        </p>

                        <p className="mt-1 text-[10px] text-slate-600">
                          Compare employee behavior with organizational peers
                        </p>

                      </div>

                    </div>

                    <div className="mt-5 grid gap-4 sm:grid-cols-4">

                      <PeerMetric
                        label="Employee Score"
                        value={
                          peerComparison.employee_score ??
                          "N/A"
                        }
                      />

                      <PeerMetric
                        label="Peer Count"
                        value={
                          peerComparison.peer_count ??
                          "N/A"
                        }
                      />

                      <PeerMetric
                        label="Department Average"
                        value={
                          peerComparison.department_avg_score ??
                          "N/A"
                        }
                      />

                      <PeerMetric
                        label="Deviation"
                        value={
                          peerComparison.deviation_from_peers ??
                          "N/A"
                        }
                        highlight
                      />

                    </div>

                  </div>

                  {/* ==========================================
                      14 DAY TREND SUMMARY
                  =========================================== */}

                  <div className="mt-4 rounded-2xl border border-white/5 bg-white/[0.02] p-5">

                    <p className="text-xs font-bold uppercase tracking-widest text-slate-500">
                      14-Day Behavioral Trend
                    </p>

                    <div className="mt-5 grid gap-4 sm:grid-cols-3">

                      <TrendMetric
                        label="First Week Average"
                        value={
                          riskProfile
                            .trend
                            ?.first_week_avg ??
                          "N/A"
                        }
                      />

                      <TrendMetric
                        label="Second Week Average"
                        value={
                          riskProfile
                            .trend
                            ?.second_week_avg ??
                          "N/A"
                        }
                      />

                      <TrendMetric
                        label="Direction"
                        value={
                          riskProfile
                            .trend
                            ?.direction ??
                          "Stable"
                        }
                        blue
                      />

                    </div>

                  </div>

                  {/* ==========================================
                      30 DAY TREND
                  =========================================== */}

                  <div className="mt-4 rounded-2xl border border-white/5 bg-white/[0.02] p-5">

                    <div className="flex items-center justify-between">

                      <div>

                        <p className="text-xs font-bold uppercase tracking-widest text-slate-500">
                          30-Day Behavioral Trend
                        </p>

                        <p className="mt-1 text-[10px] text-slate-600">
                          Daily anomaly activity for selected employee
                        </p>

                      </div>

                      <span className="text-xs text-slate-500">
                        {riskTrend.length} days
                      </span>

                    </div>

                    {riskTrend.length ===
                    0 ? (

                      <div className="mt-6 rounded-xl border border-dashed border-white/10 p-8 text-center">

                        <p className="text-xs text-slate-500">
                          No 30-day trend data available.
                        </p>

                      </div>

                    ) : (

                      <div className="mt-6">

                        <div className="flex h-44 items-end gap-1 overflow-hidden">

                          {riskTrend.map(
                            (
                              item,
                              index
                            ) => {

                              const value =
                                Number(
                                  item.anomaly_count
                                ) || 0;

                              const height =
                                value === 0
                                  ? 3
                                  : Math.max(
                                      8,
                                      Math.round(
                                        (value /
                                          maxTrendValue) *
                                          100
                                      )
                                    );

                              return (
                                <div
                                  key={`${item.date}-${index}`}
                                  className="group relative flex h-full flex-1 items-end"
                                >

                                  <div
                                    className="w-full rounded-t bg-blue-500/70 transition-all duration-300 group-hover:bg-blue-400"
                                    style={{
                                      height: `${height}%`,
                                    }}
                                  />

                                  <div className="pointer-events-none absolute bottom-full left-1/2 z-10 mb-2 hidden -translate-x-1/2 whitespace-nowrap rounded-lg border border-white/10 bg-[#07111f] px-2 py-1 text-[9px] text-slate-300 shadow-xl group-hover:block">
                                    {item.date}
                                    {" · "}
                                    {value}
                                    {" anomalies"}
                                  </div>

                                </div>
                              );
                            }
                          )}

                        </div>

                        <div className="mt-3 flex justify-between text-[9px] text-slate-600">

                          <span>
                            {
                              riskTrend[0]
                                ?.date
                            }
                          </span>

                          <span>
                            {
                              riskTrend[
                                riskTrend.length -
                                  1
                              ]?.date
                            }
                          </span>

                        </div>

                      </div>

                    )}

                  </div>

                </div>

              ) : (

                <div className="mt-8 rounded-2xl border border-dashed border-white/10 p-10 text-center">

                  <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-blue-400/10 text-blue-400">
                    ◎
                  </div>

                  <p className="mt-4 text-sm font-semibold text-slate-400">
                    Select an employee to view intelligence
                  </p>

                  <p className="mt-1 text-xs text-slate-600">
                    Risk scoring, peer comparison and behavioral trends will appear here.
                  </p>

                </div>

              )}

            </section>

            {/* =================================================
                QUICK ACTIONS
            ================================================= */}

            <section className="mt-6 grid gap-4 md:grid-cols-3">

              <QuickAction
                href="/anomalies"
                title="Anomaly Detection"
                description="Review rule and ML anomalies"
              />

              <QuickAction
                href="/investigation"
                title="Threat Investigation"
                description="Investigate employee security incidents"
              />

              <QuickAction
                href="/alerts"
                title="Security Alerts"
                description="Review generated security alerts"
              />

            </section>

            {/* =================================================
                FOOTER
            ================================================= */}

            <footer className="mt-10 border-t border-white/10 py-6">

              <div className="flex flex-col gap-2 text-xs text-slate-600 sm:flex-row sm:items-center sm:justify-between">

                <p>
                  ITBIS · Insider Threat Detection & Behavioral Security Intelligence
                </p>

                <p>
                  Employee intelligence operational
                </p>

              </div>

            </footer>

          </div>

        </div>

      </main>
    </AuthGuard>
  );
}


// =========================================================
// NAV ITEM
// =========================================================

function NavItem({
  href,
  label,
  icon,
  active,
}) {
  return (
    <Link
      href={href}
      className={`flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-semibold transition ${
        active
          ? "bg-blue-500/10 text-blue-400 ring-1 ring-blue-400/10"
          : "text-slate-500 hover:bg-white/[0.04] hover:text-slate-200"
      }`}
    >

      <span className="w-5 text-center">
        {icon}
      </span>

      {label}

    </Link>
  );
}


// =========================================================
// KPI CARD
// =========================================================

function KpiCard({
  label,
  value,
  description,
  icon,
  accent = "default",
}) {
  const styles = {
    default:
      "bg-slate-400/10 text-slate-300",

    blue:
      "bg-blue-400/10 text-blue-400",

    red:
      "bg-red-400/10 text-red-400",

    green:
      "bg-emerald-400/10 text-emerald-400",

    yellow:
      "bg-amber-400/10 text-amber-400",
  };

  return (
    <div className="group rounded-2xl border border-white/10 bg-[#0b1727] p-5 transition hover:-translate-y-0.5 hover:border-white/20">

      <div className="flex items-start justify-between">

        <div>

          <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500">
            {label}
          </p>

          <p className="mt-3 text-2xl font-black tracking-tight">
            {value}
          </p>

        </div>

        <div
          className={`flex h-10 w-10 items-center justify-center rounded-xl text-sm font-bold ${styles[accent]}`}
        >
          {icon}
        </div>

      </div>

      <p className="mt-4 text-xs text-slate-600">
        {description}
      </p>

    </div>
  );
}


// =========================================================
// RISK BADGE
// =========================================================

function RiskBadge({
  level,
  large = false,
}) {
  const value =
    String(level || "Low")
      .toLowerCase();

  let classes =
    "border-emerald-400/20 bg-emerald-400/10 text-emerald-400";

  if (value === "critical") {
    classes =
      "border-red-400/20 bg-red-400/10 text-red-400";
  } else if (value === "high") {
    classes =
      "border-orange-400/20 bg-orange-400/10 text-orange-400";
  } else if (value === "medium") {
    classes =
      "border-amber-400/20 bg-amber-400/10 text-amber-400";
  }

  return (
    <span
      className={`inline-flex rounded-full border px-3 py-1 font-bold uppercase tracking-wider ${classes} ${
        large
          ? "px-4 py-2 text-sm"
          : "text-[10px]"
      }`}
    >
      {level || "Low"}
    </span>
  );
}


// =========================================================
// RISK FACTOR
// =========================================================

function RiskFactor({
  label,
  value,
}) {
  const score =
    Number(value) || 0;

  const percentage =
    Math.min(
      100,
      Math.max(0, score)
    );

  return (
    <div className="rounded-xl border border-white/5 bg-white/[0.02] p-4">

      <div className="flex items-center justify-between">

        <span className="text-xs font-semibold text-slate-400">
          {label}
        </span>

        <span className="text-sm font-bold text-slate-200">
          {score}
        </span>

      </div>

      <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/5">

        <div
          className={`h-full rounded-full transition-all duration-700 ${
            score >= 75
              ? "bg-red-500"
              : score >= 50
              ? "bg-orange-400"
              : score >= 25
              ? "bg-amber-400"
              : "bg-blue-500"
          }`}
          style={{
            width: `${percentage}%`,
          }}
        />

      </div>

    </div>
  );
}


// =========================================================
// PEER METRIC
// =========================================================

function PeerMetric({
  label,
  value,
  highlight = false,
}) {
  const numeric =
    Number(value);

  return (
    <div>

      <p className="text-[10px] text-slate-600">
        {label}
      </p>

      <p
        className={`mt-1 text-lg font-bold ${
          highlight &&
          !Number.isNaN(numeric) &&
          numeric > 0
            ? "text-amber-400"
            : "text-slate-200"
        }`}
      >
        {value}
      </p>

    </div>
  );
}


// =========================================================
// TREND METRIC
// =========================================================

function TrendMetric({
  label,
  value,
  blue = false,
}) {
  return (
    <div>

      <p className="text-[10px] text-slate-600">
        {label}
      </p>

      <p
        className={`mt-1 text-lg font-bold ${
          blue
            ? "capitalize text-blue-400"
            : "text-slate-200"
        }`}
      >
        {value}
      </p>

    </div>
  );
}


// =========================================================
// QUICK ACTION
// =========================================================

function QuickAction({
  href,
  title,
  description,
}) {
  return (
    <Link
      href={href}
      className="group rounded-2xl border border-white/10 bg-[#0b1727] p-5 transition hover:border-blue-400/20 hover:bg-blue-400/5"
    >

      <div className="flex items-center justify-between">

        <div>

          <p className="text-sm font-bold text-slate-300 group-hover:text-blue-300">
            {title}
          </p>

          <p className="mt-1 text-xs text-slate-600">
            {description}
          </p>

        </div>

        <span className="text-slate-600 transition group-hover:translate-x-1 group-hover:text-blue-400">
          →
        </span>

      </div>

    </Link>
  );
}


// =========================================================
// LOADING SKELETON
// =========================================================

function EmployeesSkeleton() {
  return (
    <main className="min-h-screen bg-[#07111f] p-6 text-white">

      <div className="mx-auto max-w-[1500px] animate-pulse">

        <div className="mb-8 flex items-center justify-between">

          <div>

            <div className="h-3 w-40 rounded bg-white/10" />

            <div className="mt-3 h-8 w-72 rounded bg-white/10" />

            <div className="mt-3 h-3 w-96 rounded bg-white/10" />

          </div>

          <div className="h-10 w-28 rounded-xl bg-white/10" />

        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

          {[1, 2, 3, 4].map(
            (item) => (
              <div
                key={item}
                className="h-36 rounded-2xl bg-white/5"
              />
            )
          )}

        </div>

        <div className="mt-6 h-96 rounded-3xl bg-white/5" />

        <div className="mt-6 h-[700px] rounded-3xl bg-white/5" />

      </div>

    </main>
  );
}
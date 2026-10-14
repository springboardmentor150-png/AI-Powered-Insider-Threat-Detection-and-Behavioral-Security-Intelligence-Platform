// "use client";

// import { useEffect, useState } from "react";
// import Link from "next/link";
// import api from "@/lib/api";


// import AuthGuard from "@/components/AuthGuard";

// export default function DashboardPage() {
//   const [summary, setSummary] = useState(null);
//   const [employees, setEmployees] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState("");

//   useEffect(() => {
//     loadDashboard();
//   }, []);

//   async function loadDashboard() {
//     try {
//       setLoading(true);
//       setError("");

//       const [summaryResponse, employeesResponse] = await Promise.all([
//         api.get("/anomalies/summary"),
//         api.get("/employees"),
//       ]);

//       setSummary(summaryResponse.data);

//       const employeeData = employeesResponse.data;

//       // Support either a direct array or { employees: [...] }
//       if (Array.isArray(employeeData)) {
//         setEmployees(employeeData);
//       } else {
//         setEmployees(employeeData.employees || []);
//       }
//     } catch (err) {
//       console.error("Dashboard error:", err);

//       if (err.response?.status === 401) {
//         setError("Your session has expired. Please login again.");
//       } else if (err.response?.status === 403) {
//         setError("You are not authorized to view the security dashboard.");
//       } else {
//         setError("Unable to load dashboard data.");
//       }
//     } finally {
//       setLoading(false);
//     }
//   }

//   const totalAnomalies = summary?.total_anomalies || 0;
//   const totalRuleAnomalies = summary?.total_rule_anomalies || 0;
//   const totalMLAnomalies = summary?.total_ml_anomalies || 0;

//   const critical =
//     summary?.rule_anomalies_by_severity?.critical || 0;

//   const high =
//     summary?.rule_anomalies_by_severity?.high || 0;

//   const medium =
//     summary?.rule_anomalies_by_severity?.medium || 0;

//   return (
//     <main className="min-h-screen bg-[#f5f7fb] text-slate-900">
//       {/* ================= HEADER ================= */}
//       <section className="border-b border-slate-200 bg-white">
//         <div className="mx-auto max-w-7xl px-6 py-8">
//           <div className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
//             <div>
//               <div className="mb-2 flex items-center gap-2">
//                 <span className="h-2.5 w-2.5 rounded-full bg-emerald-500" />
//                 <span className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-600">
//                   Security Operations
//                 </span>
//               </div>

//               <h1 className="text-3xl font-bold tracking-tight text-slate-950 md:text-4xl">
//                 Security Dashboard
//               </h1>

//               <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
//                 Monitor employee behavior, identify anomalous activity,
//                 and review insider-threat indicators across the ITBIS platform.
//               </p>
//             </div>

//             <div className="flex items-center gap-3">
//               <button
//                 onClick={loadDashboard}
//                 className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-slate-300 hover:bg-slate-50"
//               >
//                 Refresh
//               </button>

//               <Link
//                 href="/employees"
//                 className="rounded-xl bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800"
//               >
//                 View Employees
//               </Link>
//             </div>
//           </div>
//         </div>
//       </section>

//       {/* ================= CONTENT ================= */}
//       <section className="mx-auto max-w-7xl px-6 py-8">

//         {/* Error */}
//         {error && (
//           <div className="mb-6 rounded-2xl border border-red-200 bg-red-50 p-5">
//             <div className="flex items-start gap-3">
//               <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-red-100 text-red-600">
//                 !
//               </div>

//               <div>
//                 <h3 className="font-semibold text-red-900">
//                   Dashboard unavailable
//                 </h3>

//                 <p className="mt-1 text-sm text-red-700">
//                   {error}
//                 </p>
//               </div>
//             </div>
//           </div>
//         )}

//         {/* Loading */}
//         {loading ? (
//           <DashboardSkeleton />
//         ) : (
//           <>
//             {/* ================= STAT CARDS ================= */}
//             <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">

//               <StatCard
//                 label="Total Employees"
//                 value={employees.length}
//                 description="Registered identities"
//                 icon="◉"
//               />

//               <StatCard
//                 label="Total Anomalies"
//                 value={totalAnomalies}
//                 description="Detected security events"
//                 icon="!"
//                 danger
//               />

//               <StatCard
//                 label="Critical Alerts"
//                 value={critical}
//                 description="Require immediate review"
//                 icon="▲"
//                 critical
//               />

//               <StatCard
//                 label="ML Anomalies"
//                 value={totalMLAnomalies}
//                 description="Behavioral model detections"
//                 icon="AI"
//                 blue
//               />
//             </div>

//             {/* ================= MAIN GRID ================= */}
//             <div className="mt-6 grid gap-6 lg:grid-cols-3">

//               {/* Detection Overview */}
//               <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm lg:col-span-2">
//                 <div className="flex items-start justify-between">
//                   <div>
//                     <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-400">
//                       Detection Overview
//                     </p>

//                     <h2 className="mt-1 text-xl font-bold text-slate-950">
//                       Anomaly intelligence
//                     </h2>
//                   </div>

//                   <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
//                     Live data
//                   </span>
//                 </div>

//                 <div className="mt-8 grid gap-6 md:grid-cols-2">

//                   {/* Rule based */}
//                   <DetectionBox
//                     title="Rule-based Detection"
//                     value={totalRuleAnomalies}
//                     percentage={calculatePercentage(
//                       totalRuleAnomalies,
//                       totalAnomalies
//                     )}
//                     description="Known behavioral rules"
//                   />

//                   {/* ML */}
//                   <DetectionBox
//                     title="ML Detection"
//                     value={totalMLAnomalies}
//                     percentage={calculatePercentage(
//                       totalMLAnomalies,
//                       totalAnomalies
//                     )}
//                     description="Machine-learning anomalies"
//                     blue
//                   />
//                 </div>

//                 <div className="mt-8 border-t border-slate-100 pt-6">
//                   <div className="mb-3 flex justify-between text-sm">
//                     <span className="font-medium text-slate-600">
//                       Detection distribution
//                     </span>

//                     <span className="font-semibold text-slate-900">
//                       {totalAnomalies} total
//                     </span>
//                   </div>

//                   <div className="flex h-3 overflow-hidden rounded-full bg-slate-100">
//                     <div
//                       className="bg-slate-800 transition-all"
//                       style={{
//                         width: `${calculatePercentage(
//                           totalRuleAnomalies,
//                           totalAnomalies
//                         )}%`,
//                       }}
//                     />

//                     <div
//                       className="bg-blue-500 transition-all"
//                       style={{
//                         width: `${calculatePercentage(
//                           totalMLAnomalies,
//                           totalAnomalies
//                         )}%`,
//                       }}
//                     />
//                   </div>

//                   <div className="mt-3 flex gap-5 text-xs text-slate-500">
//                     <span className="flex items-center gap-2">
//                       <span className="h-2 w-2 rounded-full bg-slate-800" />
//                       Rule-based
//                     </span>

//                     <span className="flex items-center gap-2">
//                       <span className="h-2 w-2 rounded-full bg-blue-500" />
//                       ML-based
//                     </span>
//                   </div>
//                 </div>
//               </div>

//               {/* Severity */}
//               <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
//                 <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-400">
//                   Threat Severity
//                 </p>

//                 <h2 className="mt-1 text-xl font-bold text-slate-950">
//                   Risk distribution
//                 </h2>

//                 <div className="mt-8 space-y-5">
//                   <SeverityRow
//                     label="Critical"
//                     value={critical}
//                     total={totalRuleAnomalies}
//                     type="critical"
//                   />

//                   <SeverityRow
//                     label="High"
//                     value={high}
//                     total={totalRuleAnomalies}
//                     type="high"
//                   />

//                   <SeverityRow
//                     label="Medium"
//                     value={medium}
//                     total={totalRuleAnomalies}
//                     type="medium"
//                   />
//                 </div>

//                 <div className="mt-8 rounded-xl bg-slate-50 p-4">
//                   <p className="text-xs text-slate-500">
//                     Security status
//                   </p>

//                   <div className="mt-2 flex items-center gap-2">
//                     <span className="h-2.5 w-2.5 rounded-full bg-emerald-500" />
//                     <span className="text-sm font-bold text-slate-900">
//                       Monitoring Active
//                     </span>
//                   </div>
//                 </div>
//               </div>
//             </div>

//             {/* ================= EMPLOYEE SECTION ================= */}
//             <div className="mt-6 rounded-2xl border border-slate-200 bg-white shadow-sm">

//               <div className="flex flex-col gap-4 border-b border-slate-100 p-6 sm:flex-row sm:items-center sm:justify-between">
//                 <div>
//                   <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-400">
//                     Workforce Intelligence
//                   </p>

//                   <h2 className="mt-1 text-xl font-bold text-slate-950">
//                     Employee monitoring
//                   </h2>

//                   <p className="mt-1 text-sm text-slate-500">
//                     Review registered employees and investigate suspicious activity.
//                   </p>
//                 </div>

//                 <Link
//                   href="/employees"
//                   className="text-sm font-semibold text-blue-600 hover:text-blue-700"
//                 >
//                   View all employees →
//                 </Link>
//               </div>

//               {employees.length === 0 ? (
//                 <div className="p-10 text-center">
//                   <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 text-slate-500">
//                     ◉
//                   </div>

//                   <h3 className="mt-4 font-semibold text-slate-900">
//                     No employees found
//                   </h3>

//                   <p className="mt-1 text-sm text-slate-500">
//                     Employee records will appear here once they are added.
//                   </p>
//                 </div>
//               ) : (
//                 <div className="overflow-x-auto">
//                   <table className="w-full min-w-[650px] text-left">
//                     <thead className="bg-slate-50">
//                       <tr className="text-xs uppercase tracking-wider text-slate-400">
//                         <th className="px-6 py-4 font-semibold">
//                           Employee
//                         </th>

//                         <th className="px-6 py-4 font-semibold">
//                           Department
//                         </th>

//                         <th className="px-6 py-4 font-semibold">
//                           Position
//                         </th>

//                         <th className="px-6 py-4 font-semibold">
//                           Status
//                         </th>

//                         <th className="px-6 py-4 text-right font-semibold">
//                           Action
//                         </th>
//                       </tr>
//                     </thead>

//                     <tbody className="divide-y divide-slate-100">
//                       {employees.slice(0, 8).map((employee, index) => (
//                         <tr
//                           key={
//                             employee.id ||
//                             employee.employee_id ||
//                             index
//                           }
//                           className="transition hover:bg-slate-50"
//                         >
//                           <td className="px-6 py-4">
//                             <div className="flex items-center gap-3">
//                               <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900 text-sm font-bold text-white">
//                                 {getInitials(employee)}
//                               </div>

//                               <div>
//                                 <p className="font-semibold text-slate-900">
//                                   {getEmployeeName(employee)}
//                                 </p>

//                                 <p className="text-xs text-slate-400">
//                                   {employee.employee_id ||
//                                     employee.id ||
//                                     "Employee"}
//                                 </p>
//                               </div>
//                             </div>
//                           </td>

//                           <td className="px-6 py-4 text-sm text-slate-600">
//                             {employee.department || "—"}
//                           </td>

//                           <td className="px-6 py-4 text-sm text-slate-600">
//                             {employee.designation ||
//                               employee.position ||
//                               employee.job_title ||
//                               "—"}
//                           </td>

//                           <td className="px-6 py-4">
//                             <span className="inline-flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
//                               <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
//                               Active
//                             </span>
//                           </td>

//                           <td className="px-6 py-4 text-right">
//                             <Link
//                               href={`/employees`}
//                               className="text-sm font-semibold text-blue-600 hover:text-blue-700"
//                             >
//                               View
//                             </Link>
//                           </td>
//                         </tr>
//                       ))}
//                     </tbody>
//                   </table>
//                 </div>
//               )}
//             </div>

//             {/* ================= BOTTOM CTA ================= */}
//             <div className="mt-6 overflow-hidden rounded-2xl bg-slate-950 p-7 text-white shadow-sm">
//               <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
//                 <div>
//                   <div className="flex items-center gap-2">
//                     <span className="h-2 w-2 rounded-full bg-blue-400" />
//                     <span className="text-xs font-bold uppercase tracking-[0.2em] text-blue-300">
//                       ITBIS Security Intelligence
//                     </span>
//                   </div>

//                   <h2 className="mt-3 text-2xl font-bold">
//                     Investigate suspicious behavior
//                   </h2>

//                   <p className="mt-2 max-w-xl text-sm leading-6 text-slate-400">
//                     Review employee activity and anomaly signals to understand
//                     potential insider-threat behavior.
//                   </p>
//                 </div>

//                 <Link
//                   href="/employees"
//                   className="inline-flex shrink-0 items-center justify-center rounded-xl bg-white px-5 py-3 text-sm font-bold text-slate-950 transition hover:bg-slate-100"
//                 >
//                   Open Employee Intelligence
//                   <span className="ml-2">→</span>
//                 </Link>
//               </div>
//             </div>
//           </>
//         )}
//       </section>
//     </main>
//   );
// }

// /* =========================================================
//    STAT CARD
// ========================================================= */

// function StatCard({
//   label,
//   value,
//   description,
//   icon,
//   danger,
//   critical,
//   blue,
// }) {
//   return (
//     <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
//       <div className="flex items-start justify-between">
//         <div>
//           <p className="text-xs font-bold uppercase tracking-[0.14em] text-slate-400">
//             {label}
//           </p>

//           <p className="mt-3 text-3xl font-bold tracking-tight text-slate-950">
//             {value}
//           </p>
//         </div>

//         <div
//           className={`flex h-10 w-10 items-center justify-center rounded-xl text-sm font-bold ${
//             danger
//               ? "bg-red-50 text-red-600"
//               : critical
//               ? "bg-orange-50 text-orange-600"
//               : blue
//               ? "bg-blue-50 text-blue-600"
//               : "bg-slate-100 text-slate-700"
//           }`}
//         >
//           {icon}
//         </div>
//       </div>

//       <p className="mt-3 text-xs text-slate-400">
//         {description}
//       </p>
//     </div>
//   );
// }

// /* =========================================================
//    DETECTION BOX
// ========================================================= */

// function DetectionBox({
//   title,
//   value,
//   percentage,
//   description,
//   blue,
// }) {
//   return (
//     <div className="rounded-2xl border border-slate-100 bg-slate-50 p-5">
//       <div className="flex items-center justify-between">
//         <p className="text-sm font-semibold text-slate-700">
//           {title}
//         </p>

//         <span
//           className={`text-xs font-bold ${
//             blue ? "text-blue-600" : "text-slate-700"
//           }`}
//         >
//           {percentage}%
//         </span>
//       </div>

//       <p className="mt-3 text-3xl font-bold text-slate-950">
//         {value}
//       </p>

//       <p className="mt-1 text-xs text-slate-400">
//         {description}
//       </p>

//       <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-200">
//         <div
//           className={`h-full rounded-full transition-all ${
//             blue ? "bg-blue-500" : "bg-slate-800"
//           }`}
//           style={{
//             width: `${percentage}%`,
//           }}
//         />
//       </div>
//     </div>
//   );
// }

// /* =========================================================
//    SEVERITY ROW
// ========================================================= */

// function SeverityRow({
//   label,
//   value,
//   total,
//   type,
// }) {
//   const percentage = calculatePercentage(value, total);

//   const styles = {
//     critical: {
//       bar: "bg-red-500",
//       badge: "bg-red-50 text-red-700",
//     },
//     high: {
//       bar: "bg-orange-500",
//       badge: "bg-orange-50 text-orange-700",
//     },
//     medium: {
//       bar: "bg-yellow-500",
//       badge: "bg-yellow-50 text-yellow-700",
//     },
//   };

//   const style = styles[type];

//   return (
//     <div>
//       <div className="flex items-center justify-between">
//         <div className="flex items-center gap-2">
//           <span
//             className={`rounded-full px-2.5 py-1 text-xs font-bold ${style.badge}`}
//           >
//             {label}
//           </span>
//         </div>

//         <span className="text-sm font-bold text-slate-900">
//           {value}
//         </span>
//       </div>

//       <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
//         <div
//           className={`h-full rounded-full ${style.bar}`}
//           style={{
//             width: `${percentage}%`,
//           }}
//         />
//       </div>
//     </div>
//   );
// }

// /* =========================================================
//    LOADING SKELETON
// ========================================================= */

// function DashboardSkeleton() {
//   return (
//     <div className="animate-pulse">
//       <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
//         {[1, 2, 3, 4].map((item) => (
//           <div
//             key={item}
//             className="h-36 rounded-2xl bg-white"
//           />
//         ))}
//       </div>

//       <div className="mt-6 grid gap-6 lg:grid-cols-3">
//         <div className="h-80 rounded-2xl bg-white lg:col-span-2" />
//         <div className="h-80 rounded-2xl bg-white" />
//       </div>

//       <div className="mt-6 h-96 rounded-2xl bg-white" />
//     </div>
//   );
// }

// /* =========================================================
//    HELPERS
// ========================================================= */

// function calculatePercentage(value, total) {
//   if (!total || total <= 0) {
//     return 0;
//   }

//   return Math.round((value / total) * 100);
// }

// function getEmployeeName(employee) {
//   if (employee.name) {
//     return employee.name;
//   }

//   if (employee.full_name) {
//     return employee.full_name;
//   }

//   if (employee.first_name || employee.last_name) {
//     return `${employee.first_name || ""} ${
//       employee.last_name || ""
//     }`.trim();
//   }

//   return "Unknown Employee";
// }

// function getInitials(employee) {
//   const name = getEmployeeName(employee);

//   if (!name || name === "Unknown Employee") {
//     return "EM";
//   }

//   const parts = name.split(" ").filter(Boolean);

//   if (parts.length === 1) {
//     return parts[0].slice(0, 2).toUpperCase();
//   }

//   return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
// }


// <Link
//   href="/employees"
//   className="flex items-center gap-4 rounded-xl px-5 py-3 text-slate-400 transition hover:bg-slate-800 hover:text-white"
// >
//   <span className="text-lg">◎</span>
//   <span>Employee Intelligence</span>
// </Link>



"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import api, {
  clearSession,
  isLoggedIn,
} from "@/lib/api";

import AuthGuard from "@/components/AuthGuard";

export default function DashboardPage() {
  return (
    <AuthGuard>
      <DashboardContent />
    </AuthGuard>
  );
}

function DashboardContent() {
  const router = useRouter();

  const [summary, setSummary] = useState(null);
  const [employees, setEmployees] = useState([]);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const loadDashboard = useCallback(async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      setError("");

      /*
       * Make sure a token exists before requesting protected APIs.
       */
      if (!isLoggedIn()) {
        router.replace("/login");
        return;
      }

      const [summaryResponse, employeesResponse] =
        await Promise.all([
          api.get("/anomalies/summary"),
          api.get("/employees"),
        ]);

      setSummary(summaryResponse.data);

      const employeeData = employeesResponse.data;

      if (Array.isArray(employeeData)) {
        setEmployees(employeeData);
      } else if (Array.isArray(employeeData?.employees)) {
        setEmployees(employeeData.employees);
      } else {
        setEmployees([]);
      }
    } catch (err) {
      console.error("Dashboard error:", err);

      const status = err?.response?.status;

      if (status === 401) {
        clearSession();
        router.replace("/login");
        return;
      }

      if (status === 403) {
        setError(
          "Your account does not have permission to access the security dashboard."
        );
        return;
      }

      setError(
        err?.response?.data?.detail ||
          err?.response?.data?.message ||
          "Unable to load dashboard data. Please check the backend connection."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [router]);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  function handleLogout() {
    clearSession();
    router.replace("/login");
  }

  /*
   * Summary values
   */
  const totalAnomalies =
    Number(summary?.total_anomalies) || 0;

  const totalRuleAnomalies =
    Number(summary?.total_rule_anomalies) || 0;

  const totalMLAnomalies =
    Number(summary?.total_ml_anomalies) || 0;

  const severity =
    summary?.rule_anomalies_by_severity || {};

  const critical =
    Number(severity?.critical) || 0;

  const high =
    Number(severity?.high) || 0;

  const medium =
    Number(severity?.medium) || 0;

  const low =
    Number(severity?.low) || 0;

  const highRisk = critical + high;

  const departmentCount = new Set(
    employees
      .map((employee) => employee?.department)
      .filter(Boolean)
  ).size;

  const rulePercentage = calculatePercentage(
    totalRuleAnomalies,
    totalAnomalies
  );

  const mlPercentage = calculatePercentage(
    totalMLAnomalies,
    totalAnomalies
  );

  return (
    <main className="min-h-screen bg-[#07111f] text-white">
      {/* =====================================================
          TOP NAVIGATION
      ===================================================== */}

      <header className="fixed left-0 right-0 top-0 z-50 h-[74px] border-b border-slate-200 bg-white text-slate-900">
        <div className="flex h-full items-center justify-between px-6 lg:px-8">

          {/* Logo */}
          <Link
            href="/dashboard"
            className="flex items-center gap-3"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-950 text-sm font-bold text-white">
              IT
            </div>

            <div>
              <div className="text-lg font-bold tracking-tight">
                ITBIS
              </div>

              <div className="text-[9px] font-semibold tracking-[0.22em] text-slate-400">
                SECURITY INTELLIGENCE
              </div>
            </div>
          </Link>

          {/* Main navigation */}
          <nav className="hidden items-center gap-7 md:flex">

            <Link
              href="/"
              className="text-sm font-semibold text-slate-600 transition hover:text-slate-950"
            >
              Home
            </Link>

            <Link
              href="/employees"
              className="text-sm font-semibold text-slate-600 transition hover:text-slate-950"
            >
              Employees
            </Link>

            <Link
              href="/dashboard"
              className="text-sm font-semibold text-slate-950"
            >
              Dashboard
            </Link>

            <div className="h-7 w-px bg-slate-200" />

            <Link
              href="/login"
              className="text-sm font-semibold text-slate-600 hover:text-slate-950"
            >
              Sign in
            </Link>

            <Link
              href="/employees"
              className="rounded-xl bg-slate-950 px-5 py-2.5 text-sm font-bold text-white transition hover:bg-slate-800"
            >
              Get Started
            </Link>
          </nav>
        </div>
      </header>

      {/* =====================================================
          SIDEBAR
      ===================================================== */}

      <aside className="fixed bottom-0 left-0 top-[74px] z-40 hidden w-[285px] border-r border-slate-800 bg-[#091522] lg:block">

        <div className="flex h-full flex-col">

          {/* Sidebar navigation */}
          <div className="flex-1 overflow-y-auto px-4 py-7">

            <p className="mb-4 px-3 text-[10px] font-bold uppercase tracking-[0.24em] text-slate-500">
              Security Operations
            </p>

            <SidebarLink
              href="/dashboard"
              icon="◆"
              label="Security Overview"
              active
            />

            <SidebarLink
              href="/employees"
              icon="◎"
              label="Employee Intelligence"
            />

            <SidebarLink
              href="/anomaly-detection"
              icon="△"
              label="Anomaly Detection"
            />

            <div className="my-5 border-t border-slate-800" />

            <p className="mb-3 px-3 text-[10px] font-bold uppercase tracking-[0.24em] text-slate-500">
              Intelligence
            </p>

            <SidebarLink
              href="/activity-monitoring"
              icon="◌"
              label="Activity Monitoring"
            />

            <SidebarLink
              href="/security-alerts"
              icon="!"
              label="Security Alerts"
            />

            <SidebarLink
              href="/security-reports"
              icon="▤"
              label="Security Reports"
            />
          </div>

          {/* Current role */}
          <div className="border-t border-slate-800 p-4">

            <div className="mb-3 rounded-xl border border-slate-800 bg-[#0e1c2b] p-4">
              <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500">
                Current Role
              </p>

              <p className="mt-2 text-sm font-bold text-white">
                Admin
              </p>
            </div>

            <button
              onClick={handleLogout}
              className="flex w-full items-center justify-center gap-2 rounded-xl border border-red-500/30 bg-red-500/5 px-4 py-3 text-sm font-bold text-red-400 transition hover:bg-red-500/10"
            >
              <span>↪</span>
              Logout
            </button>
          </div>
        </div>
      </aside>

      {/* =====================================================
          MAIN CONTENT
      ===================================================== */}

      <section className="pt-[74px] lg:pl-[285px]">

        {/* Page header */}
        <div className="border-b border-slate-800 bg-[#081320]">
          <div className="flex flex-col gap-4 px-6 py-7 md:flex-row md:items-center md:justify-between lg:px-9">

            <div>
              <p className="text-[11px] font-bold uppercase tracking-[0.25em] text-blue-400">
                Security Operations
              </p>

              <h1 className="mt-2 text-3xl font-bold tracking-tight text-white">
                Security Overview
              </h1>

              <p className="mt-1 text-sm text-slate-500">
                Monitor threats, employee behavior and anomaly intelligence.
              </p>
            </div>

            <div className="flex items-center gap-3">

              <button
                onClick={() => loadDashboard(true)}
                disabled={refreshing}
                className="rounded-xl border border-slate-700 bg-[#0d1a29] px-4 py-2.5 text-sm font-semibold text-slate-300 transition hover:border-slate-600 hover:bg-[#112235] disabled:cursor-not-allowed disabled:opacity-60"
              >
                {refreshing ? "Refreshing..." : "↻ Refresh"}
              </button>

              <div className="flex items-center gap-2 rounded-xl border border-emerald-500/30 bg-emerald-500/5 px-4 py-2.5">
                <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
                <span className="text-xs font-bold text-emerald-400">
                  SYSTEM ONLINE
                </span>
              </div>

              <button
                onClick={handleLogout}
                className="hidden rounded-xl border border-slate-700 px-4 py-2.5 text-sm font-semibold text-slate-300 transition hover:bg-slate-800 md:block"
              >
                Logout
              </button>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="px-6 py-8 lg:px-9">

          {error && (
            <div className="mb-6 rounded-2xl border border-red-500/30 bg-red-500/5 p-5">
              <div className="flex items-start gap-3">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-red-500/10 font-bold text-red-400">
                  !
                </div>

                <div>
                  <h3 className="font-bold text-red-300">
                    Dashboard unavailable
                  </h3>

                  <p className="mt-1 text-sm text-red-400/80">
                    {error}
                  </p>

                  <button
                    onClick={() => loadDashboard()}
                    className="mt-3 text-sm font-bold text-red-300 underline underline-offset-4"
                  >
                    Try again
                  </button>
                </div>
              </div>
            </div>
          )}

          {loading ? (
            <DashboardSkeleton />
          ) : (
            <>
              {/* =================================================
                  SECURITY POSTURE
              ================================================= */}

              <div className="grid gap-6 xl:grid-cols-[1.55fr_1fr]">

                {/* Main security card */}
                <div className="relative overflow-hidden rounded-3xl border border-slate-800 bg-gradient-to-br from-[#0d2035] to-[#091724] p-7">

                  <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-blue-500/5 blur-3xl" />

                  <div className="relative">

                    <div className="flex items-center gap-2">
                      <span className="h-2.5 w-2.5 rounded-full bg-blue-400 shadow-[0_0_15px_rgba(96,165,250,0.8)]" />

                      <span className="text-[10px] font-bold uppercase tracking-[0.22em] text-blue-400">
                        Current Security Posture
                      </span>
                    </div>

                    <div className="mt-12 flex items-center justify-between gap-6">

                      <div>
                        {critical > 0 ? (
                          <>
                            <h2 className="text-4xl font-bold tracking-tight text-white">
                              Attention Required
                            </h2>

                            <p className="mt-3 text-sm text-slate-400">
                              Critical anomalies require investigation.
                            </p>
                          </>
                        ) : high > 0 ? (
                          <>
                            <h2 className="text-4xl font-bold tracking-tight text-white">
                              Review Required
                            </h2>

                            <p className="mt-3 text-sm text-slate-400">
                              High-severity activity requires review.
                            </p>
                          </>
                        ) : (
                          <>
                            <h2 className="text-4xl font-bold tracking-tight text-white">
                              Security Stable
                            </h2>

                            <p className="mt-3 text-sm text-slate-400">
                              No critical security anomalies detected.
                            </p>
                          </>
                        )}
                      </div>

                      <div className="hidden h-28 w-28 shrink-0 items-center justify-center rounded-full border border-emerald-500/30 bg-emerald-500/5 sm:flex">
                        <div className="text-center">
                          <p className="text-3xl font-bold text-emerald-400">
                            {critical}
                          </p>

                          <p className="mt-1 text-[9px] font-semibold uppercase tracking-widest text-slate-500">
                            Critical
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Severity mini cards */}
                    <div className="mt-10 grid gap-3 sm:grid-cols-3">

                      <MiniSeverity
                        label="Critical"
                        value={critical}
                        color="red"
                      />

                      <MiniSeverity
                        label="High"
                        value={high}
                        color="orange"
                      />

                      <MiniSeverity
                        label="Medium"
                        value={medium}
                        color="yellow"
                      />
                    </div>
                  </div>
                </div>

                {/* Platform health */}
                <div className="rounded-3xl border border-slate-800 bg-[#0b1928] p-7">

                  <div className="flex items-center justify-between">

                    <div>
                      <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-slate-500">
                        Platform Health
                      </p>

                      <h2 className="mt-2 text-xl font-bold text-white">
                        ITBIS Services
                      </h2>
                    </div>

                    <span className="rounded-full bg-emerald-500/10 px-3 py-1.5 text-[10px] font-bold uppercase text-emerald-400">
                      Operational
                    </span>
                  </div>

                  <div className="mt-6 divide-y divide-slate-800">

                    <HealthRow
                      label="Authentication"
                      status="Protected"
                    />

                    <HealthRow
                      label="PostgreSQL"
                      status="Connected"
                    />

                    <HealthRow
                      label="MongoDB"
                      status="Connected"
                    />

                    <HealthRow
                      label="Behavior Monitoring"
                      status="Active"
                    />
                  </div>
                </div>
              </div>

              {/* =================================================
                  STAT CARDS
              ================================================= */}

              <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

                <DashboardStat
                  label="Employees"
                  value={employees.length}
                  description="Registered identities"
                  icon="◎"
                />

                <DashboardStat
                  label="Total Anomalies"
                  value={totalAnomalies}
                  description={`${totalRuleAnomalies} rule · ${totalMLAnomalies} ML`}
                  icon="△"
                  blue
                />

                <DashboardStat
                  label="High Risk"
                  value={highRisk}
                  description="Critical + high severity"
                  icon="!"
                  danger
                />

                <DashboardStat
                  label="Departments"
                  value={departmentCount}
                  description="Organizational units"
                  icon="▦"
                  green
                />
              </div>

              {/* =================================================
                  ANALYTICS
              ================================================= */}

              <div className="mt-6 grid gap-6 xl:grid-cols-2">

                {/* Detection analytics */}
                <div className="rounded-3xl border border-slate-800 bg-[#0b1928] p-7">

                  <div className="flex items-start justify-between">

                    <div>
                      <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">
                        Threat Analytics
                      </p>

                      <h2 className="mt-2 text-xl font-bold text-white">
                        Anomaly Detection
                      </h2>
                    </div>

                    <Link
                      href="/anomaly-detection"
                      className="text-xs font-bold text-blue-400 transition hover:text-blue-300"
                    >
                      View all →
                    </Link>
                  </div>

                  <div className="mt-8 space-y-7">

                    <AnalyticsBar
                      label="Rule-based Detection"
                      value={totalRuleAnomalies}
                      percentage={rulePercentage}
                      type="rule"
                    />

                    <AnalyticsBar
                      label="ML Detection"
                      value={totalMLAnomalies}
                      percentage={mlPercentage}
                      type="ml"
                    />

                  </div>

                  <div className="mt-8 border-t border-slate-800 pt-6">

                    <div className="flex justify-between text-xs">
                      <span className="text-slate-500">
                        Total detected events
                      </span>

                      <span className="font-bold text-white">
                        {totalAnomalies}
                      </span>
                    </div>

                    <div className="mt-4 flex h-2 overflow-hidden rounded-full bg-slate-800">

                      <div
                        className="bg-blue-500 transition-all duration-700"
                        style={{
                          width: `${rulePercentage}%`,
                        }}
                      />

                      <div
                        className="bg-cyan-400 transition-all duration-700"
                        style={{
                          width: `${mlPercentage}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>

                {/* Severity analytics */}
                <div className="rounded-3xl border border-slate-800 bg-[#0b1928] p-7">

                  <div className="flex items-start justify-between">

                    <div>
                      <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">
                        Risk Analysis
                      </p>

                      <h2 className="mt-2 text-xl font-bold text-white">
                        Severity Distribution
                      </h2>
                    </div>

                    <Link
                      href="/security-alerts"
                      className="text-xs font-bold text-blue-400 hover:text-blue-300"
                    >
                      Alerts →
                    </Link>
                  </div>

                  <div className="mt-8 space-y-6">

                    <SeverityRow
                      label="Critical"
                      value={critical}
                      total={totalRuleAnomalies}
                      type="critical"
                    />

                    <SeverityRow
                      label="High"
                      value={high}
                      total={totalRuleAnomalies}
                      type="high"
                    />

                    <SeverityRow
                      label="Medium"
                      value={medium}
                      total={totalRuleAnomalies}
                      type="medium"
                    />

                    <SeverityRow
                      label="Low"
                      value={low}
                      total={totalRuleAnomalies}
                      type="low"
                    />
                  </div>

                  <div className="mt-8 rounded-2xl border border-emerald-500/10 bg-emerald-500/5 p-4">

                    <div className="flex items-center gap-3">

                      <span className="h-2.5 w-2.5 rounded-full bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.7)]" />

                      <div>
                        <p className="text-xs font-bold text-white">
                          Monitoring Active
                        </p>

                        <p className="mt-1 text-[11px] text-slate-500">
                          Security intelligence services are running.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* =================================================
                  EMPLOYEE INTELLIGENCE
              ================================================= */}

              <div className="mt-6 overflow-hidden rounded-3xl border border-slate-800 bg-[#0b1928]">

                <div className="flex flex-col gap-4 border-b border-slate-800 p-7 sm:flex-row sm:items-center sm:justify-between">

                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">
                      Behavioral Intelligence
                    </p>

                    <h2 className="mt-2 text-xl font-bold text-white">
                      Employee Intelligence
                    </h2>

                    <p className="mt-1 text-sm text-slate-500">
                      Review registered identities and employee behavior.
                    </p>
                  </div>

                  <Link
                    href="/employees"
                    className="rounded-xl border border-blue-500/20 bg-blue-500/5 px-4 py-2.5 text-xs font-bold text-blue-400 transition hover:bg-blue-500/10"
                  >
                    View Employees →
                  </Link>
                </div>

                {employees.length === 0 ? (
                  <div className="p-12 text-center">

                    <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-800 text-xl text-slate-500">
                      ◎
                    </div>

                    <h3 className="mt-4 font-bold text-white">
                      No employee records
                    </h3>

                    <p className="mt-2 text-sm text-slate-500">
                      Employee records will appear here once registered.
                    </p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">

                    <table className="w-full min-w-[750px]">

                      <thead>
                        <tr className="border-b border-slate-800 bg-[#091522] text-left text-[10px] font-bold uppercase tracking-[0.15em] text-slate-500">

                          <th className="px-7 py-4">
                            Employee
                          </th>

                          <th className="px-7 py-4">
                            Department
                          </th>

                          <th className="px-7 py-4">
                            Position
                          </th>

                          <th className="px-7 py-4">
                            Status
                          </th>

                          <th className="px-7 py-4 text-right">
                            Action
                          </th>
                        </tr>
                      </thead>

                      <tbody className="divide-y divide-slate-800">

                        {employees.slice(0, 8).map(
                          (employee, index) => (
                            <tr
                              key={
                                employee?.id ||
                                employee?.employee_id ||
                                index
                              }
                              className="transition hover:bg-[#0d1c2c]"
                            >

                              <td className="px-7 py-4">

                                <div className="flex items-center gap-3">

                                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/10 text-xs font-bold text-blue-400">
                                    {getInitials(employee)}
                                  </div>

                                  <div>
                                    <p className="text-sm font-bold text-white">
                                      {getEmployeeName(employee)}
                                    </p>

                                    <p className="mt-1 text-[11px] text-slate-500">
                                      {employee?.employee_id ||
                                        employee?.id ||
                                        "Employee"}
                                    </p>
                                  </div>
                                </div>
                              </td>

                              <td className="px-7 py-4 text-sm text-slate-400">
                                {employee?.department || "—"}
                              </td>

                              <td className="px-7 py-4 text-sm text-slate-400">
                                {employee?.designation ||
                                  employee?.position ||
                                  employee?.job_title ||
                                  "—"}
                              </td>

                              <td className="px-7 py-4">

                                <span className="inline-flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/5 px-3 py-1.5 text-[10px] font-bold text-emerald-400">
                                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                                  ACTIVE
                                </span>
                              </td>

                              <td className="px-7 py-4 text-right">

                                <Link
                                  href="/employees"
                                  className="text-xs font-bold text-blue-400 hover:text-blue-300"
                                >
                                  View →
                                </Link>
                              </td>
                            </tr>
                          )
                        )}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>

              {/* =================================================
                  QUICK ACTIONS
              ================================================= */}

              <div className="mt-6 grid gap-4 md:grid-cols-3">

                <QuickAction
                  href="/activity-monitoring"
                  title="Activity Monitoring"
                  description="Review employee activity events"
                  icon="◌"
                />

                <QuickAction
                  href="/security-alerts"
                  title="Security Alerts"
                  description="Investigate detected threats"
                  icon="!"
                />

                <QuickAction
                  href="/security-reports"
                  title="Security Reports"
                  description="Generate security intelligence"
                  icon="▤"
                />
              </div>

            </>
          )}
        </div>
      </section>
    </main>
  );
}

/* =========================================================
   SIDEBAR LINK
========================================================= */

function SidebarLink({
  href,
  icon,
  label,
  active = false,
}) {
  return (
    <Link
      href={href}
      className={`mb-1 flex items-center gap-4 rounded-xl px-4 py-3.5 text-sm font-semibold transition ${
        active
          ? "bg-blue-500/10 text-blue-400"
          : "text-slate-400 hover:bg-slate-800/70 hover:text-white"
      }`}
    >
      <span
        className={`w-5 text-center text-sm ${
          active ? "text-blue-400" : "text-slate-500"
        }`}
      >
        {icon}
      </span>

      <span>{label}</span>
    </Link>
  );
}

/* =========================================================
   PLATFORM HEALTH
========================================================= */

function HealthRow({ label, status }) {
  return (
    <div className="flex items-center justify-between py-4">

      <div className="flex items-center gap-3">
        <span className="h-2.5 w-2.5 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.5)]" />

        <span className="text-sm text-slate-400">
          {label}
        </span>
      </div>

      <span className="text-xs font-bold text-emerald-400">
        {status}
      </span>
    </div>
  );
}

/* =========================================================
   MINI SEVERITY
========================================================= */

function MiniSeverity({
  label,
  value,
  color,
}) {
  const styles = {
    red: "border-red-500/10 bg-red-500/5 text-red-400",
    orange:
      "border-orange-500/10 bg-orange-500/5 text-orange-400",
    yellow:
      "border-yellow-500/10 bg-yellow-500/5 text-yellow-400",
  };

  return (
    <div
      className={`rounded-xl border p-4 ${styles[color]}`}
    >
      <p className="text-[9px] font-semibold uppercase tracking-widest opacity-60">
        {label}
      </p>

      <p className="mt-2 text-xl font-bold">
        {value}
      </p>
    </div>
  );
}

/* =========================================================
   DASHBOARD STAT
========================================================= */

function DashboardStat({
  label,
  value,
  description,
  icon,
  blue,
  danger,
  green,
}) {
  let iconStyle =
    "bg-slate-800 text-slate-300";

  if (blue) {
    iconStyle = "bg-blue-500/10 text-blue-400";
  }

  if (danger) {
    iconStyle = "bg-red-500/10 text-red-400";
  }

  if (green) {
    iconStyle = "bg-emerald-500/10 text-emerald-400";
  }

  return (
    <div className="rounded-2xl border border-slate-800 bg-[#0b1928] p-5 transition hover:-translate-y-0.5 hover:border-slate-700">

      <div className="flex items-start justify-between">

        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500">
            {label}
          </p>

          <p className="mt-3 text-3xl font-bold tracking-tight text-white">
            {value}
          </p>
        </div>

        <div
          className={`flex h-11 w-11 items-center justify-center rounded-xl text-sm font-bold ${iconStyle}`}
        >
          {icon}
        </div>
      </div>

      <p className="mt-3 text-xs text-slate-500">
        {description}
      </p>
    </div>
  );
}

/* =========================================================
   ANALYTICS BAR
========================================================= */

function AnalyticsBar({
  label,
  value,
  percentage,
  type,
}) {
  const isML = type === "ml";

  return (
    <div>

      <div className="flex items-center justify-between">

        <span className="text-sm font-semibold text-slate-300">
          {label}
        </span>

        <div className="flex items-center gap-3">

          <span className="text-xs text-slate-500">
            {percentage}%
          </span>

          <span
            className={`text-sm font-bold ${
              isML
                ? "text-cyan-400"
                : "text-blue-400"
            }`}
          >
            {value}
          </span>
        </div>
      </div>

      <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-800">

        <div
          className={`h-full rounded-full transition-all duration-700 ${
            isML
              ? "bg-cyan-400"
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

/* =========================================================
   SEVERITY ROW
========================================================= */

function SeverityRow({
  label,
  value,
  total,
  type,
}) {
  const percentage = calculatePercentage(
    value,
    total
  );

  const styles = {
    critical: {
      bar: "bg-red-500",
      text: "text-red-400",
    },

    high: {
      bar: "bg-orange-500",
      text: "text-orange-400",
    },

    medium: {
      bar: "bg-yellow-500",
      text: "text-yellow-400",
    },

    low: {
      bar: "bg-blue-400",
      text: "text-blue-400",
    },
  };

  const style =
    styles[type] || styles.low;

  return (
    <div>

      <div className="flex items-center justify-between">

        <span className={`text-sm font-semibold ${style.text}`}>
          {label}
        </span>

        <span className="text-sm font-bold text-white">
          {value}
        </span>
      </div>

      <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-800">

        <div
          className={`h-full rounded-full ${style.bar}`}
          style={{
            width: `${percentage}%`,
          }}
        />
      </div>
    </div>
  );
}

/* =========================================================
   QUICK ACTION
========================================================= */

function QuickAction({
  href,
  title,
  description,
  icon,
}) {
  return (
    <Link
      href={href}
      className="group rounded-2xl border border-slate-800 bg-[#0b1928] p-5 transition hover:border-blue-500/30 hover:bg-[#0d1c2c]"
    >
      <div className="flex items-center gap-4">

        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-500/10 text-blue-400">
          {icon}
        </div>

        <div>
          <h3 className="text-sm font-bold text-white">
            {title}
          </h3>

          <p className="mt-1 text-xs text-slate-500">
            {description}
          </p>
        </div>

        <span className="ml-auto text-slate-600 transition group-hover:translate-x-1 group-hover:text-blue-400">
          →
        </span>
      </div>
    </Link>
  );
}

/* =========================================================
   LOADING SKELETON
========================================================= */

function DashboardSkeleton() {
  return (
    <div className="animate-pulse">

      <div className="grid gap-6 xl:grid-cols-[1.55fr_1fr]">

        <div className="h-[350px] rounded-3xl bg-[#0b1928]" />

        <div className="h-[350px] rounded-3xl bg-[#0b1928]" />
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

        {[1, 2, 3, 4].map((item) => (
          <div
            key={item}
            className="h-32 rounded-2xl bg-[#0b1928]"
          />
        ))}
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-2">

        <div className="h-80 rounded-3xl bg-[#0b1928]" />

        <div className="h-80 rounded-3xl bg-[#0b1928]" />
      </div>

      <div className="mt-6 h-96 rounded-3xl bg-[#0b1928]" />
    </div>
  );
}

/* =========================================================
   HELPERS
========================================================= */

function calculatePercentage(value, total) {
  if (!total || total <= 0) {
    return 0;
  }

  return Math.min(
    100,
    Math.round((value / total) * 100)
  );
}

function getEmployeeName(employee) {
  if (!employee) {
    return "Unknown Employee";
  }

  if (employee.name) {
    return employee.name;
  }

  if (employee.full_name) {
    return employee.full_name;
  }

  if (
    employee.first_name ||
    employee.last_name
  ) {
    return `${employee.first_name || ""} ${
      employee.last_name || ""
    }`.trim();
  }

  return "Unknown Employee";
}

function getInitials(employee) {
  const name = getEmployeeName(employee);

  if (
    !name ||
    name === "Unknown Employee"
  ) {
    return "EM";
  }

  const parts = name
    .split(" ")
    .filter(Boolean);

  if (parts.length === 1) {
    return parts[0]
      .slice(0, 2)
      .toUpperCase();
  }

  return `${parts[0][0]}${
    parts[parts.length - 1][0]
  }`.toUpperCase();
}

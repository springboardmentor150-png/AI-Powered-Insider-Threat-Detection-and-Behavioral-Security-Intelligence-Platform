import "./globals.css";

export const metadata = {
  title: "ITBIS | Insider Threat Detection & Security Intelligence",
  description:
    "AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900">
        {/* Professional Navigation */}
        <nav className="sticky top-0 z-50 border-b border-slate-200/80 bg-white/95 backdrop-blur-md">
          <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6 lg:px-8">

            {/* Brand */}
            <a
              href="/"
              className="group flex items-center gap-3"
            >
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-950 text-sm font-bold text-white shadow-sm transition group-hover:bg-blue-600">
                IT
              </div>

              <div className="hidden sm:block">
                <div className="text-base font-bold tracking-tight text-slate-950">
                  ITBIS
                </div>
                <div className="text-[9px] font-medium uppercase tracking-[0.18em] text-slate-500">
                  Security Intelligence
                </div>
              </div>
            </a>

            {/* Navigation Links */}
            <div className="flex items-center gap-1">
              <a
                href="/"
                className="rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-950"
              >
                Home
              </a>

              <a
                href="/employees"
                className="rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-950"
              >
                Employees
              </a>

              <a
                href="/dashboard"
                className="rounded-lg px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 hover:text-slate-950"
              >
                Dashboard
              </a>

              <div className="mx-2 hidden h-6 w-px bg-slate-200 sm:block" />

              {/* Login */}
              <a
                href="/login"
                className="hidden rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition hover:text-slate-950 sm:block"
              >
                Sign in
              </a>

              {/* Signup / CTA */}
              <a
                href="/signup"
                className="rounded-lg bg-slate-950 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-600 hover:shadow-md"
              >
                Get Started
              </a>
            </div>
          </div>
        </nav>

        {/* Page Content */}
        <main>{children}</main>

        {/* Professional Footer */}
        <footer className="border-t border-slate-200 bg-white">
          <div className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-8 sm:flex-row sm:items-center sm:justify-between lg:px-8">

            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-md bg-slate-950 text-xs font-bold text-white">
                IT
              </div>

              <div>
                <p className="text-sm font-semibold text-slate-900">
                  ITBIS
                </p>
                <p className="text-xs text-slate-500">
                  Insider Threat Behavioral Intelligence
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 text-xs text-slate-500">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
              Security Platform Operational
            </div>

            <p className="text-xs text-slate-400">
              © 2026 ITBIS. Security Intelligence Platform.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}


// "use client";

// import { useEffect, useState } from "react";
// import api from "@/lib/api";

// export default function DashboardPage() {
//   const [summary, setSummary] = useState(null);
//   const [employeeId, setEmployeeId] = useState("EMP1001");
//   const [employeeData, setEmployeeData] = useState(null);

//   const [loading, setLoading] = useState(true);
//   const [employeeLoading, setEmployeeLoading] = useState(false);
//   const [error, setError] = useState("");

//   // =========================================================
//   // Load overall anomaly summary
//   // =========================================================

//   const loadSummary = async () => {
//     try {
//       setLoading(true);
//       setError("");

//       const response = await api.get("/anomalies/summary");

//       setSummary(response.data);
//     } catch (err) {
//       console.error("Dashboard summary error:", err);

//       if (err.response?.status === 401) {
//         setError("Session expired. Please sign in again.");
//       } else if (err.response?.status === 403) {
//         setError(
//           "Your account does not have permission to access the security dashboard."
//         );
//       } else {
//         setError("Unable to load anomaly summary.");
//       }
//     } finally {
//       setLoading(false);
//     }
//   };

//   // =========================================================
//   // Load employee anomalies
//   // =========================================================

//   const loadEmployeeAnomalies = async () => {
//     if (!employeeId.trim()) {
//       return;
//     }

//     try {
//       setEmployeeLoading(true);

//       const response = await api.get(
//         `/anomalies/${employeeId.trim().toUpperCase()}`
//       );

//       setEmployeeData(response.data);
//     } catch (err) {
//       console.error("Employee anomaly error:", err);

//       setEmployeeData(null);

//       if (err.response?.status === 404) {
//         alert("Employee anomalies not found.");
//       } else if (err.response?.status === 403) {
//         alert("You are not authorized to view anomalies.");
//       } else {
//         alert("Unable to load employee anomalies.");
//       }
//     } finally {
//       setEmployeeLoading(false);
//     }
//   };

//   // =========================================================
//   // Initial load
//   // =========================================================

//   useEffect(() => {
//     loadSummary();
//     loadEmployeeAnomalies();
//   }, []);

//   // =========================================================
//   // Helpers
//   // =========================================================

//   const severityClass = (severity) => {
//     if (severity === "critical") {
//       return "bg-red-50 text-red-700 border-red-200";
//     }

//     if (severity === "high") {
//       return "bg-orange-50 text-orange-700 border-orange-200";
//     }

//     if (severity === "medium") {
//       return "bg-yellow-50 text-yellow-700 border-yellow-200";
//     }

//     return "bg-slate-50 text-slate-600 border-slate-200";
//   };

//   const formatDate = (value) => {
//     if (!value) return "—";

//     try {
//       return new Date(value).toLocaleString();
//     } catch {
//       return "—";
//     }
//   };

//   // =========================================================
//   // Loading
//   // =========================================================

//   if (loading) {
//     return (
//       <main className="min-h-screen bg-slate-50 px-6 py-10">
//         <div className="mx-auto max-w-7xl">
//           <div className="animate-pulse space-y-8">

//             <div className="h-8 w-72 rounded bg-slate-200" />
//             <div className="h-4 w-96 rounded bg-slate-200" />

//             <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
//               {[1, 2, 3, 4].map((item) => (
//                 <div
//                   key={item}
//                   className="h-32 rounded-2xl border border-slate-200 bg-white"
//                 />
//               ))}
//             </div>

//             <div className="h-80 rounded-2xl border border-slate-200 bg-white" />
//           </div>
//         </div>
//       </main>
//     );
//   }

//   // =========================================================
//   // Dashboard
//   // =========================================================

//   return (
//     <main className="min-h-screen bg-slate-50">

//       {/* =====================================================
//           Header
//       ===================================================== */}

//       <section className="border-b border-slate-200 bg-white">
//         <div className="mx-auto max-w-7xl px-6 py-10">

//           <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-end">

//             <div>
//               <div className="mb-3 flex items-center gap-2">
//                 <span className="h-2 w-2 rounded-full bg-green-500" />

//                 <span className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-600">
//                   Security Operations
//                 </span>
//               </div>

//               <h1 className="text-4xl font-bold tracking-tight text-slate-950">
//                 Security Dashboard
//               </h1>

//               <p className="mt-3 max-w-2xl text-slate-500">
//                 Monitor behavioral anomalies detected through rule-based
//                 analysis and machine learning intelligence.
//               </p>
//             </div>

//             <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
//               <span className="h-2.5 w-2.5 rounded-full bg-green-500" />

//               <div>
//                 <p className="text-xs font-medium uppercase tracking-wider text-slate-400">
//                   Platform Status
//                 </p>

//                 <p className="text-sm font-semibold text-slate-800">
//                   Operational
//                 </p>
//               </div>
//             </div>

//           </div>
//         </div>
//       </section>

//       <div className="mx-auto max-w-7xl px-6 py-10">

//         {/* =====================================================
//             Error
//         ===================================================== */}

//         {error && (
//           <div className="mb-8 rounded-xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
//             {error}
//           </div>
//         )}

//         {/* =====================================================
//             Summary Cards
//         ===================================================== */}

//         <section className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">

//           {/* Total anomalies */}

//           <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
//             <div className="flex items-start justify-between">

//               <div>
//                 <p className="text-sm font-medium text-slate-500">
//                   Total Anomalies
//                 </p>

//                 <p className="mt-3 text-4xl font-bold text-slate-950">
//                   {summary?.total_anomalies ?? 0}
//                 </p>
//               </div>

//               <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
//                 ◉
//               </div>

//             </div>

//             <p className="mt-4 text-xs text-slate-400">
//               Combined detection signals
//             </p>
//           </div>

//           {/* Rule anomalies */}

//           <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
//             <div className="flex items-start justify-between">

//               <div>
//                 <p className="text-sm font-medium text-slate-500">
//                   Rule Anomalies
//                 </p>

//                 <p className="mt-3 text-4xl font-bold text-slate-950">
//                   {summary?.total_rule_anomalies ?? 0}
//                 </p>
//               </div>

//               <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-orange-50 text-orange-600">
//                 !
//               </div>

//             </div>

//             <p className="mt-4 text-xs text-slate-400">
//               Behavioral rule detection
//             </p>
//           </div>

//           {/* ML anomalies */}

//           <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
//             <div className="flex items-start justify-between">

//               <div>
//                 <p className="text-sm font-medium text-slate-500">
//                   ML Anomalies
//                 </p>

//                 <p className="mt-3 text-4xl font-bold text-slate-950">
//                   {summary?.total_ml_anomalies ?? 0}
//                 </p>
//               </div>

//               <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-purple-50 text-purple-600">
//                 AI
//               </div>

//             </div>

//             <p className="mt-4 text-xs text-slate-400">
//               Isolation Forest detection
//             </p>
//           </div>

//           {/* Critical */}

//           <div className="rounded-2xl border border-red-100 bg-white p-6 shadow-sm">
//             <div className="flex items-start justify-between">

//               <div>
//                 <p className="text-sm font-medium text-slate-500">
//                   Critical Alerts
//                 </p>

//                 <p className="mt-3 text-4xl font-bold text-red-600">
//                   {summary?.rule_anomalies_by_severity?.critical ?? 0}
//                 </p>
//               </div>

//               <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-red-50 text-red-600">
//                 !
//               </div>

//             </div>

//             <p className="mt-4 text-xs text-red-400">
//               Requires security attention
//             </p>
//           </div>

//         </section>

//         {/* =====================================================
//             Detection Overview
//         ===================================================== */}

//         <section className="mt-8 grid gap-6 lg:grid-cols-2">

//           {/* Severity */}

//           <div className="rounded-2xl border border-slate-200 bg-white p-7 shadow-sm">

//             <div className="flex items-center justify-between">
//               <div>
//                 <p className="text-xs font-semibold uppercase tracking-[0.18em] text-blue-600">
//                   Detection Analysis
//                 </p>

//                 <h2 className="mt-2 text-xl font-bold text-slate-950">
//                   Rule Anomaly Severity
//                 </h2>
//               </div>

//               <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-500">
//                 Live Data
//               </span>
//             </div>

//             <div className="mt-8 space-y-5">

//               {/* Critical */}

//               <div>
//                 <div className="mb-2 flex justify-between text-sm">
//                   <span className="font-medium text-slate-600">
//                     Critical
//                   </span>

//                   <span className="font-semibold text-red-600">
//                     {summary?.rule_anomalies_by_severity?.critical ?? 0}
//                   </span>
//                 </div>

//                 <div className="h-2.5 overflow-hidden rounded-full bg-slate-100">
//                   <div
//                     className="h-full rounded-full bg-red-500"
//                     style={{
//                       width: `${
//                         summary?.total_rule_anomalies
//                           ? ((summary.rule_anomalies_by_severity?.critical ?? 0) /
//                               summary.total_rule_anomalies) *
//                             100
//                           : 0
//                       }%`,
//                     }}
//                   />
//                 </div>
//               </div>

//               {/* High */}

//               <div>
//                 <div className="mb-2 flex justify-between text-sm">
//                   <span className="font-medium text-slate-600">
//                     High
//                   </span>

//                   <span className="font-semibold text-orange-600">
//                     {summary?.rule_anomalies_by_severity?.high ?? 0}
//                   </span>
//                 </div>

//                 <div className="h-2.5 overflow-hidden rounded-full bg-slate-100">
//                   <div
//                     className="h-full rounded-full bg-orange-500"
//                     style={{
//                       width: `${
//                         summary?.total_rule_anomalies
//                           ? ((summary.rule_anomalies_by_severity?.high ?? 0) /
//                               summary.total_rule_anomalies) *
//                             100
//                           : 0
//                       }%`,
//                     }}
//                   />
//                 </div>
//               </div>

//               {/* Medium */}

//               <div>
//                 <div className="mb-2 flex justify-between text-sm">
//                   <span className="font-medium text-slate-600">
//                     Medium
//                   </span>

//                   <span className="font-semibold text-yellow-600">
//                     {summary?.rule_anomalies_by_severity?.medium ?? 0}
//                   </span>
//                 </div>

//                 <div className="h-2.5 overflow-hidden rounded-full bg-slate-100">
//                   <div
//                     className="h-full rounded-full bg-yellow-400"
//                     style={{
//                       width: `${
//                         summary?.total_rule_anomalies
//                           ? ((summary.rule_anomalies_by_severity?.medium ?? 0) /
//                               summary.total_rule_anomalies) *
//                             100
//                           : 0
//                       }%`,
//                     }}
//                   />
//                 </div>
//               </div>

//             </div>
//           </div>

//           {/* Detection methods */}

//           <div className="rounded-2xl border border-slate-200 bg-white p-7 shadow-sm">

//             <p className="text-xs font-semibold uppercase tracking-[0.18em] text-blue-600">
//               Detection Engine
//             </p>

//             <h2 className="mt-2 text-xl font-bold text-slate-950">
//               Behavioral Intelligence
//             </h2>

//             <div className="mt-7 space-y-4">

//               <div className="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50 p-4">
//                 <div>
//                   <p className="font-semibold text-slate-800">
//                     Rule-Based Detection
//                   </p>

//                   <p className="mt-1 text-xs text-slate-400">
//                     Employee behavioral baselines
//                   </p>
//                 </div>

//                 <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-600">
//                   {summary?.total_rule_anomalies ?? 0} detected
//                 </span>
//               </div>

//               <div className="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50 p-4">
//                 <div>
//                   <p className="font-semibold text-slate-800">
//                     Machine Learning
//                   </p>

//                   <p className="mt-1 text-xs text-slate-400">
//                     Isolation Forest analysis
//                   </p>
//                 </div>

//                 <span className="rounded-full bg-purple-50 px-3 py-1 text-xs font-semibold text-purple-600">
//                   {summary?.total_ml_anomalies ?? 0} detected
//                 </span>
//               </div>

//             </div>
//           </div>

//         </section>

//         {/* =====================================================
//             Employee Investigation
//         ===================================================== */}

//         <section className="mt-8 rounded-2xl border border-slate-200 bg-white p-7 shadow-sm">

//           <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-end">

//             <div>
//               <p className="text-xs font-semibold uppercase tracking-[0.18em] text-blue-600">
//                 Employee Investigation
//               </p>

//               <h2 className="mt-2 text-xl font-bold text-slate-950">
//                 Investigate Employee Activity
//               </h2>

//               <p className="mt-2 text-sm text-slate-500">
//                 Search for rule-based and machine-learning anomalies
//                 associated with a specific employee.
//               </p>
//             </div>

//             <div className="flex w-full flex-col gap-3 sm:flex-row lg:w-auto">

//               <input
//                 type="text"
//                 value={employeeId}
//                 onChange={(e) => setEmployeeId(e.target.value)}
//                 onKeyDown={(e) => {
//                   if (e.key === "Enter") {
//                     loadEmployeeAnomalies();
//                   }
//                 }}
//                 placeholder="EMP1001"
//                 className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-800 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 sm:w-56"
//               />

//               <button
//                 onClick={loadEmployeeAnomalies}
//                 disabled={employeeLoading}
//                 className="rounded-xl bg-slate-950 px-6 py-3 text-sm font-semibold text-white transition hover:bg-blue-600 disabled:cursor-not-allowed disabled:opacity-60"
//               >
//                 {employeeLoading ? "Loading..." : "Investigate"}
//               </button>

//             </div>
//           </div>

//           {/* Employee result */}

//           {employeeData && (
//             <div className="mt-8 border-t border-slate-100 pt-7">

//               <div className="mb-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">

//                 <div>
//                   <p className="text-xs uppercase tracking-wider text-slate-400">
//                     Employee
//                   </p>

//                   <h3 className="mt-1 text-2xl font-bold text-slate-950">
//                     {employeeData.employee_id}
//                   </h3>
//                 </div>

//                 <div className="flex gap-3">

//                   <div className="rounded-xl bg-orange-50 px-4 py-3 text-center">
//                     <p className="text-xs text-orange-500">
//                       Rule
//                     </p>

//                     <p className="text-lg font-bold text-orange-700">
//                       {employeeData.total_rule_anomalies}
//                     </p>
//                   </div>

//                   <div className="rounded-xl bg-purple-50 px-4 py-3 text-center">
//                     <p className="text-xs text-purple-500">
//                       ML
//                     </p>

//                     <p className="text-lg font-bold text-purple-700">
//                       {employeeData.total_ml_anomalies}
//                     </p>
//                   </div>

//                   <div className="rounded-xl bg-red-50 px-4 py-3 text-center">
//                     <p className="text-xs text-red-500">
//                       Total
//                     </p>

//                     <p className="text-lg font-bold text-red-700">
//                       {employeeData.total_anomalies}
//                     </p>
//                   </div>

//                 </div>

//               </div>

//               {/* Rule anomalies */}

//               {employeeData.rule_anomalies?.length > 0 && (
//                 <div>

//                   <div className="mb-4 flex items-center justify-between">
//                     <h3 className="font-bold text-slate-900">
//                       Rule-Based Anomalies
//                     </h3>

//                     <span className="text-xs text-slate-400">
//                       {employeeData.rule_anomalies.length} records
//                     </span>
//                   </div>

//                   <div className="overflow-x-auto rounded-xl border border-slate-200">

//                     <table className="w-full min-w-[700px] text-left">

//                       <thead className="bg-slate-50">
//                         <tr>
//                           <th className="px-5 py-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
//                             Indicator
//                           </th>

//                           <th className="px-5 py-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
//                             New Value
//                           </th>

//                           <th className="px-5 py-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
//                             Severity
//                           </th>

//                           <th className="px-5 py-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
//                             Reason
//                           </th>

//                           <th className="px-5 py-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
//                             Detected
//                           </th>
//                         </tr>
//                       </thead>

//                       <tbody className="divide-y divide-slate-100 bg-white">

//                         {employeeData.rule_anomalies.map((anomaly) => (

//                           <tr
//                             key={anomaly._id}
//                             className="transition hover:bg-slate-50"
//                           >

//                             <td className="px-5 py-4">
//                               <span className="font-semibold text-slate-800">
//                                 {anomaly.indicator || "—"}
//                               </span>
//                             </td>

//                             <td className="px-5 py-4 text-sm text-slate-600">
//                               {String(anomaly.new_value ?? "—")}
//                             </td>

//                             <td className="px-5 py-4">

//                               <span
//                                 className={`rounded-full border px-3 py-1 text-xs font-semibold ${severityClass(
//                                   anomaly.severity
//                                 )}`}
//                               >
//                                 {anomaly.severity || "unknown"}
//                               </span>

//                             </td>

//                             <td className="max-w-xs px-5 py-4 text-sm text-slate-500">
//                               {anomaly.reason || "Behavioral deviation"}
//                             </td>

//                             <td className="px-5 py-4 text-xs text-slate-400">
//                               {formatDate(anomaly.detected_at)}
//                             </td>

//                           </tr>

//                         ))}

//                       </tbody>

//                     </table>

//                   </div>

//                 </div>
//               )}

//               {/* ML anomalies */}

//               {employeeData.ml_anomalies?.length > 0 && (
//                 <div className="mt-8">

//                   <div className="mb-4 flex items-center justify-between">
//                     <h3 className="font-bold text-slate-900">
//                       Machine Learning Anomalies
//                     </h3>

//                     <span className="text-xs text-slate-400">
//                       {employeeData.ml_anomalies.length} records
//                     </span>
//                   </div>

//                   <div className="grid gap-4 md:grid-cols-2">

//                     {employeeData.ml_anomalies.map((anomaly) => (

//                       <div
//                         key={anomaly._id}
//                         className="rounded-xl border border-purple-100 bg-purple-50/40 p-5"
//                       >

//                         <div className="flex items-start justify-between">

//                           <div>
//                             <p className="text-xs font-semibold uppercase tracking-wider text-purple-500">
//                               ML Detection
//                             </p>

//                             <p className="mt-2 font-semibold text-slate-900">
//                               {formatDate(anomaly.date)}
//                             </p>
//                           </div>

//                           <span className="rounded-full bg-purple-100 px-3 py-1 text-xs font-bold text-purple-700">
//                             Anomaly
//                           </span>

//                         </div>

//                         <div className="mt-5 grid grid-cols-2 gap-3">

//                           <div className="rounded-lg bg-white p-3">
//                             <p className="text-xs text-slate-400">
//                               ML Score
//                             </p>

//                             <p className="mt-1 font-semibold text-slate-800">
//                               {typeof anomaly.ml_score === "number"
//                                 ? anomaly.ml_score.toFixed(4)
//                                 : "—"}
//                             </p>
//                           </div>

//                           <div className="rounded-lg bg-white p-3">
//                             <p className="text-xs text-slate-400">
//                               Prediction
//                             </p>

//                             <p className="mt-1 font-semibold text-red-600">
//                               {anomaly.prediction ?? "—"}
//                             </p>
//                           </div>

//                         </div>

//                       </div>

//                     ))}

//                   </div>

//                 </div>
//               )}

//               {/* No anomalies */}

//               {employeeData.total_anomalies === 0 && (
//                 <div className="rounded-xl border border-green-200 bg-green-50 p-6 text-center">

//                   <p className="text-lg font-semibold text-green-700">
//                     No anomalies detected
//                   </p>

//                   <p className="mt-1 text-sm text-green-600">
//                     No rule-based or machine-learning anomalies were
//                     returned for this employee.
//                   </p>

//                 </div>
//               )}

//             </div>
//           )}

//         </section>

//         {/* =====================================================
//             Top Employees
//         ===================================================== */}

//         <section className="mt-8 rounded-2xl border border-slate-200 bg-white p-7 shadow-sm">

//           <div className="flex items-center justify-between">

//             <div>
//               <p className="text-xs font-semibold uppercase tracking-[0.18em] text-blue-600">
//                 Monitoring Overview
//               </p>

//               <h2 className="mt-2 text-xl font-bold text-slate-950">
//                 Employees With Detected Anomalies
//               </h2>
//             </div>

//             <span className="hidden rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-500 sm:block">
//               Top 10
//             </span>

//           </div>

//           <div className="mt-6 space-y-3">

//             {summary?.top_rule_anomaly_employees?.length > 0 ? (

//               summary.top_rule_anomaly_employees.map(
//                 (employee, index) => (

//                   <div
//                     key={employee.employee_id}
//                     className="flex items-center justify-between rounded-xl border border-slate-100 px-5 py-4 transition hover:border-blue-200 hover:bg-slate-50"
//                   >

//                     <div className="flex items-center gap-4">

//                       <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-100 text-xs font-bold text-slate-500">
//                         {String(index + 1).padStart(2, "0")}
//                       </span>

//                       <div>
//                         <p className="font-semibold text-slate-900">
//                           {employee.employee_id}
//                         </p>

//                         <p className="text-xs text-slate-400">
//                           Employee anomaly activity
//                         </p>
//                       </div>

//                     </div>

//                     <span className="rounded-full bg-red-50 px-3 py-1 text-xs font-semibold text-red-600">
//                       {employee.anomaly_count} anomalies
//                     </span>

//                   </div>

//                 )
//               )

//             ) : (

//               <div className="rounded-xl bg-slate-50 p-6 text-center text-sm text-slate-500">
//                 No rule-based anomaly employees found.
//               </div>

//             )}

//           </div>

//         </section>

//         {/* =====================================================
//             Footer note
//         ===================================================== */}

//         <div className="mt-8 flex flex-col justify-between gap-3 border-t border-slate-200 pt-6 text-xs text-slate-400 sm:flex-row">

//           <p>
//             ITBIS Security Intelligence Platform
//           </p>

//           <p>
//             Behavioral Rules + Machine Learning
//           </p>

//         </div>

//       </div>
//     </main>
//   );
// }
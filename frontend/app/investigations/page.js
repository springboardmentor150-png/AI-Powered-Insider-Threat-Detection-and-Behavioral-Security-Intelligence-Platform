// "use client";

// import { useEffect, useState } from "react";
// import api from "@/lib/api";

// export default function InvestigationsPage() {
//   const [incidents, setIncidents] = useState([]);
//   const [employees, setEmployees] = useState([]);
//   const [selectedIncident, setSelectedIncident] = useState(null);

//   const [notes, setNotes] = useState([]);
//   const [timeline, setTimeline] = useState([]);

//   const [note, setNote] = useState("");
//   const [evidenceReference, setEvidenceReference] = useState("");
//   const [resolutionSummary, setResolutionSummary] = useState("");

//   const [loading, setLoading] = useState(true);
//   const [detailsLoading, setDetailsLoading] = useState(false);
//   const [submitting, setSubmitting] = useState(false);
//   const [error, setError] = useState("");

//   // --------------------------------------------------
//   // Load incidents + employees
//   // --------------------------------------------------

//   useEffect(() => {
//     loadInvestigationData();
//   }, []);

//   async function loadInvestigationData() {
//     try {
//       setLoading(true);
//       setError("");

//       const [incidentsResponse, employeesResponse] = await Promise.all([
//         api.get("/incidents"),
//         api.get("/employees"),
//       ]);

//       setIncidents(
//         incidentsResponse.data?.incidents ||
//         incidentsResponse.data ||
//         []
//       );

//       const employeeData = employeesResponse.data;

//       if (Array.isArray(employeeData)) {
//         setEmployees(employeeData);
//       } else {
//         setEmployees(employeeData?.employees || []);
//       }
//     } catch (err) {
//       console.error(err);
//       setError(
//         err?.response?.data?.detail ||
//         "Unable to load investigation data."
//       );
//     } finally {
//       setLoading(false);
//     }
//   }

//   // --------------------------------------------------
//   // Employee helpers
//   // --------------------------------------------------

//   function getEmployee(employeeId) {
//     return employees.find(
//       (employee) => Number(employee.id) === Number(employeeId)
//     );
//   }

//   function getEmployeeName(employeeId) {
//     const employee = getEmployee(employeeId);

//     if (!employee) {
//       return `Employee #${employeeId}`;
//     }

//     return `${employee.name} (${employee.employee_id})`;
//   }

//   function getEmployeeCode(employeeId) {
//     const employee = getEmployee(employeeId);

//     return employee?.employee_id || null;
//   }

//   // --------------------------------------------------
//   // Select incident
//   // --------------------------------------------------

//   async function selectIncident(incident) {
//     try {
//       setSelectedIncident(incident);
//       setDetailsLoading(true);
//       setError("");

//       setNotes([]);
//       setTimeline([]);

//       const employeeCode = getEmployeeCode(incident.employee_id);

//       const requests = [
//         api.get(`/incidents/${incident.id}/notes`),
//       ];

//       if (employeeCode) {
//         requests.push(
//           api.get(`/investigations/${employeeCode}/timeline`)
//         );
//       }

//       const responses = await Promise.all(requests);

//       setNotes(responses[0].data?.notes || []);

//       if (responses[1]) {
//         setTimeline(responses[1].data?.timeline || []);
//       }
//     } catch (err) {
//       console.error(err);
//       setError(
//         err?.response?.data?.detail ||
//         "Unable to load investigation details."
//       );
//     } finally {
//       setDetailsLoading(false);
//     }
//   }

//   // --------------------------------------------------
//   // Add investigation note
//   // --------------------------------------------------

//   async function addNote(event) {
//     event.preventDefault();

//     if (!selectedIncident || !note.trim()) {
//       return;
//     }

//     try {
//       setSubmitting(true);
//       setError("");

//       await api.post(
//         `/incidents/${selectedIncident.id}/notes`,
//         {
//           note: note.trim(),
//           evidence_reference:
//             evidenceReference.trim() || null,
//         }
//       );

//       setNote("");
//       setEvidenceReference("");

//       await selectIncident({
//         ...selectedIncident,
//         status:
//           selectedIncident.status === "open"
//             ? "investigating"
//             : selectedIncident.status,
//       });

//       await loadInvestigationData();
//     } catch (err) {
//       console.error(err);
//       setError(
//         err?.response?.data?.detail ||
//         "Unable to add investigation note."
//       );
//     } finally {
//       setSubmitting(false);
//     }
//   }

//   // --------------------------------------------------
//   // Resolve incident
//   // --------------------------------------------------

//   async function resolveIncident(event) {
//     event.preventDefault();

//     if (!selectedIncident || !resolutionSummary.trim()) {
//       return;
//     }

//     try {
//       setSubmitting(true);
//       setError("");

//       await api.patch(
//         `/incidents/${selectedIncident.id}/resolve`,
//         {
//           resolution_summary: resolutionSummary.trim(),
//         }
//       );

//       setResolutionSummary("");
//       setSelectedIncident(null);

//       await loadInvestigationData();
//     } catch (err) {
//       console.error(err);
//       setError(
//         err?.response?.data?.detail ||
//         "Unable to resolve incident."
//       );
//     } finally {
//       setSubmitting(false);
//     }
//   }

//   // --------------------------------------------------
//   // Formatting
//   // --------------------------------------------------

//   function formatDate(value) {
//     if (!value) return "—";

//     const date = new Date(value);

//     if (Number.isNaN(date.getTime())) {
//       return String(value);
//     }

//     return date.toLocaleString();
//   }

//   function severityClass(severity) {
//     switch (String(severity || "").toLowerCase()) {
//       case "critical":
//         return "border-red-500/30 bg-red-500/10 text-red-400";

//       case "high":
//         return "border-orange-500/30 bg-orange-500/10 text-orange-400";

//       case "medium":
//         return "border-yellow-500/30 bg-yellow-500/10 text-yellow-400";

//       default:
//         return "border-slate-500/30 bg-slate-500/10 text-slate-300";
//     }
//   }

//   function statusClass(status) {
//     switch (String(status || "").toLowerCase()) {
//       case "investigating":
//         return "border-blue-500/30 bg-blue-500/10 text-blue-400";

//       case "resolved":
//         return "border-emerald-500/30 bg-emerald-500/10 text-emerald-400";

//       default:
//         return "border-slate-500/30 bg-slate-500/10 text-slate-300";
//     }
//   }

//   // --------------------------------------------------
//   // Loading
//   // --------------------------------------------------

//   if (loading) {
//     return (
//       <main className="min-h-screen bg-[#06111f] text-white p-8">
//         <div className="max-w-7xl mx-auto">
//           <div className="animate-pulse text-slate-400">
//             Loading investigation workspace...
//           </div>
//         </div>
//       </main>
//     );
//   }

//   return (
//     <main className="min-h-screen bg-[#06111f] text-white">
//       <div className="max-w-7xl mx-auto px-6 py-8">

//         {/* Header */}
//         <div className="mb-8">
//           <div className="text-xs tracking-[0.3em] text-blue-400 font-semibold mb-3">
//             SECURITY OPERATIONS
//           </div>

//           <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
//             <div>
//               <h1 className="text-3xl md:text-4xl font-bold">
//                 Threat Investigation
//               </h1>

//               <p className="text-slate-400 mt-2">
//                 Investigate active incidents, review evidence, and track
//                 employee security activity.
//               </p>
//             </div>

//             <button
//               onClick={loadInvestigationData}
//               className="border border-slate-700 hover:border-blue-500 px-5 py-2.5 rounded-xl text-sm transition"
//             >
//               ↻ Refresh
//             </button>
//           </div>
//         </div>

//         {/* Error */}
//         {error && (
//           <div className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-red-300">
//             {error}
//           </div>
//         )}

//         {/* Summary cards */}
//         <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">

//           <div className="rounded-2xl border border-slate-800 bg-[#0b1a2b] p-5">
//             <p className="text-xs tracking-widest text-slate-500">
//               ACTIVE INCIDENTS
//             </p>
//             <p className="text-3xl font-bold mt-2">
//               {incidents.length}
//             </p>
//           </div>

//           <div className="rounded-2xl border border-slate-800 bg-[#0b1a2b] p-5">
//             <p className="text-xs tracking-widest text-slate-500">
//               INVESTIGATING
//             </p>
//             <p className="text-3xl font-bold text-blue-400 mt-2">
//               {
//                 incidents.filter(
//                   (incident) => incident.status === "investigating"
//                 ).length
//               }
//             </p>
//           </div>

//           <div className="rounded-2xl border border-slate-800 bg-[#0b1a2b] p-5">
//             <p className="text-xs tracking-widest text-slate-500">
//               HIGH / CRITICAL
//             </p>
//             <p className="text-3xl font-bold text-red-400 mt-2">
//               {
//                 incidents.filter((incident) =>
//                   ["high", "critical"].includes(
//                     String(incident.severity).toLowerCase()
//                   )
//                 ).length
//               }
//             </p>
//           </div>
//         </div>

//         {/* Main layout */}
//         <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">

//           {/* Incident list */}
//           <section className="lg:col-span-2 rounded-2xl border border-slate-800 bg-[#0b1a2b] overflow-hidden">

//             <div className="px-5 py-4 border-b border-slate-800">
//               <h2 className="font-semibold text-lg">
//                 Active Incidents
//               </h2>

//               <p className="text-sm text-slate-500 mt-1">
//                 Select an incident to investigate.
//               </p>
//             </div>

//             {incidents.length === 0 ? (
//               <div className="p-8 text-center text-slate-500">
//                 No active incidents found.
//               </div>
//             ) : (
//               <div className="divide-y divide-slate-800">
//                 {incidents.map((incident) => (
//                   <button
//                     key={incident.id}
//                     onClick={() => selectIncident(incident)}
//                     className={`w-full text-left p-5 transition hover:bg-slate-900/70 ${
//                       selectedIncident?.id === incident.id
//                         ? "bg-blue-500/10 border-l-2 border-blue-500"
//                         : ""
//                     }`}
//                   >
//                     <div className="flex items-start justify-between gap-3">

//                       <div>
//                         <p className="font-semibold">
//                           Incident #{incident.id}
//                         </p>

//                         <p className="text-sm text-slate-400 mt-1">
//                           {getEmployeeName(incident.employee_id)}
//                         </p>
//                       </div>

//                       <span
//                         className={`px-2.5 py-1 rounded-full border text-xs font-semibold uppercase ${severityClass(
//                           incident.severity
//                         )}`}
//                       >
//                         {incident.severity}
//                       </span>
//                     </div>

//                     <p className="text-sm text-slate-400 mt-4 line-clamp-2">
//                       {incident.summary || "No incident summary available."}
//                     </p>

//                     <div className="flex items-center justify-between mt-4">

//                       <span
//                         className={`px-2.5 py-1 rounded-full border text-xs ${statusClass(
//                           incident.status
//                         )}`}
//                       >
//                         {incident.status}
//                       </span>

//                       <span className="text-xs text-slate-600">
//                         {formatDate(incident.created_at)}
//                       </span>

//                     </div>
//                   </button>
//                 ))}
//               </div>
//             )}
//           </section>

//           {/* Investigation workspace */}
//           <section className="lg:col-span-3 space-y-6">

//             {!selectedIncident ? (
//               <div className="min-h-[500px] rounded-2xl border border-slate-800 bg-[#0b1a2b] flex items-center justify-center text-center p-8">
//                 <div>
//                   <div className="text-5xl mb-4">🔎</div>

//                   <h2 className="text-xl font-semibold">
//                     Select an incident
//                   </h2>

//                   <p className="text-slate-500 mt-2 max-w-md">
//                     Choose an active incident from the left panel to
//                     review investigation notes, evidence, and the
//                     employee activity timeline.
//                   </p>
//                 </div>
//               </div>
//             ) : (
//               <>
//                 {/* Incident details */}
//                 <div className="rounded-2xl border border-slate-800 bg-[#0b1a2b] p-6">

//                   <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">

//                     <div>
//                       <p className="text-xs tracking-widest text-blue-400">
//                         INCIDENT #{selectedIncident.id}
//                       </p>

//                       <h2 className="text-2xl font-bold mt-2">
//                         {getEmployeeName(selectedIncident.employee_id)}
//                       </h2>

//                       <p className="text-sm text-slate-500 mt-1">
//                         Created {formatDate(selectedIncident.created_at)}
//                       </p>
//                     </div>

//                     <div className="flex gap-2">
//                       <span
//                         className={`px-3 py-1.5 rounded-full border text-xs uppercase font-semibold ${severityClass(
//                           selectedIncident.severity
//                         )}`}
//                       >
//                         {selectedIncident.severity}
//                       </span>

//                       <span
//                         className={`px-3 py-1.5 rounded-full border text-xs uppercase ${statusClass(
//                           selectedIncident.status
//                         )}`}
//                       >
//                         {selectedIncident.status}
//                       </span>
//                     </div>

//                   </div>

//                   <div className="mt-6 rounded-xl bg-slate-900/60 p-4">
//                     <p className="text-xs tracking-widest text-slate-500 mb-2">
//                       INCIDENT SUMMARY
//                     </p>

//                     <p className="text-slate-300">
//                       {selectedIncident.summary ||
//                         "No summary available."}
//                     </p>
//                   </div>
//                 </div>

//                 {detailsLoading ? (
//                   <div className="rounded-2xl border border-slate-800 bg-[#0b1a2b] p-8 text-slate-400">
//                     Loading investigation details...
//                   </div>
//                 ) : (
//                   <>
//                     {/* Add note */}
//                     {selectedIncident.status !== "resolved" && (
//                       <form
//                         onSubmit={addNote}
//                         className="rounded-2xl border border-slate-800 bg-[#0b1a2b] p-6"
//                       >
//                         <h3 className="text-lg font-semibold">
//                           Add Investigation Note
//                         </h3>

//                         <p className="text-sm text-slate-500 mt-1 mb-5">
//                           Document findings and supporting evidence.
//                         </p>

//                         <textarea
//                           value={note}
//                           onChange={(e) => setNote(e.target.value)}
//                           placeholder="Enter investigation findings..."
//                           rows={4}
//                           className="w-full rounded-xl border border-slate-700 bg-[#071321] px-4 py-3 text-sm outline-none focus:border-blue-500"
//                           required
//                         />

//                         <input
//                           value={evidenceReference}
//                           onChange={(e) =>
//                             setEvidenceReference(e.target.value)
//                           }
//                           placeholder="Evidence reference (optional)"
//                           className="w-full mt-3 rounded-xl border border-slate-700 bg-[#071321] px-4 py-3 text-sm outline-none focus:border-blue-500"
//                         />

//                         <button
//                           type="submit"
//                           disabled={submitting}
//                           className="mt-4 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 px-5 py-2.5 font-semibold text-sm"
//                         >
//                           {submitting
//                             ? "Saving..."
//                             : "Add Investigation Note"}
//                         </button>
//                       </form>
//                     )}

//                     {/* Notes */}
//                     <div className="rounded-2xl border border-slate-800 bg-[#0b1a2b] p-6">

//                       <div className="flex justify-between items-center mb-5">
//                         <div>
//                           <h3 className="text-lg font-semibold">
//                             Investigation Notes
//                           </h3>

//                           <p className="text-sm text-slate-500 mt-1">
//                             Analyst findings and evidence references.
//                           </p>
//                         </div>

//                         <span className="text-sm text-slate-500">
//                           {notes.length} notes
//                         </span>
//                       </div>

//                       {notes.length === 0 ? (
//                         <p className="text-slate-500">
//                           No investigation notes yet.
//                         </p>
//                       ) : (
//                         <div className="space-y-4">
//                           {notes.map((item) => (
//                             <div
//                               key={item.id}
//                               className="rounded-xl border border-slate-800 bg-[#071321] p-4"
//                             >
//                               <div className="flex justify-between gap-4">
//                                 <span className="text-xs text-blue-400">
//                                   Analyst #{item.author_user_id}
//                                 </span>

//                                 <span className="text-xs text-slate-600">
//                                   {formatDate(item.created_at)}
//                                 </span>
//                               </div>

//                               <p className="text-sm text-slate-300 mt-3 whitespace-pre-wrap">
//                                 {item.note}
//                               </p>

//                               {item.evidence_reference && (
//                                 <div className="mt-3 text-xs text-slate-400">
//                                   <span className="text-slate-500">
//                                     Evidence:
//                                   </span>{" "}
//                                   {item.evidence_reference}
//                                 </div>
//                               )}
//                             </div>
//                           ))}
//                         </div>
//                       )}
//                     </div>

//                     {/* Timeline */}
//                     <div className="rounded-2xl border border-slate-800 bg-[#0b1a2b] p-6">

//                       <div className="mb-5">
//                         <h3 className="text-lg font-semibold">
//                           Investigation Timeline
//                         </h3>

//                         <p className="text-sm text-slate-500 mt-1">
//                           Unified employee activity and anomaly events.
//                         </p>
//                       </div>

//                       {timeline.length === 0 ? (
//                         <p className="text-slate-500">
//                           No timeline events found.
//                         </p>
//                       ) : (
//                         <div className="space-y-4">
//                           {timeline.map((event, index) => (
//                             <div
//                               key={`${event.source}-${index}`}
//                               className="flex gap-4"
//                             >
//                               <div className="flex flex-col items-center">
//                                 <div className="w-3 h-3 rounded-full bg-blue-500 mt-1" />

//                                 {index !== timeline.length - 1 && (
//                                   <div className="w-px flex-1 bg-slate-800 mt-2" />
//                                 )}
//                               </div>

//                               <div className="pb-5 flex-1">
//                                 <div className="flex flex-wrap items-center gap-2">
//                                   <span className="text-sm font-semibold capitalize">
//                                     {String(event.source).replace(
//                                       "_",
//                                       " "
//                                     )}
//                                   </span>

//                                   {event.severity && (
//                                     <span
//                                       className={`px-2 py-0.5 rounded-full border text-[10px] uppercase ${severityClass(
//                                         event.severity
//                                       )}`}
//                                     >
//                                       {event.severity}
//                                     </span>
//                                   )}
//                                 </div>

//                                 <p className="text-xs text-slate-600 mt-1">
//                                   {formatDate(event.time)}
//                                 </p>

//                                 <pre className="mt-3 text-xs text-slate-400 bg-[#071321] rounded-lg p-3 overflow-auto whitespace-pre-wrap">
//                                   {JSON.stringify(
//                                     event.detail,
//                                     null,
//                                     2
//                                   )}
//                                 </pre>
//                               </div>
//                             </div>
//                           ))}
//                         </div>
//                       )}
//                     </div>

//                     {/* Resolve */}
//                     {selectedIncident.status !== "resolved" && (
//                       <form
//                         onSubmit={resolveIncident}
//                         className="rounded-2xl border border-red-500/20 bg-red-500/5 p-6"
//                       >
//                         <h3 className="text-lg font-semibold text-red-300">
//                           Resolve Incident
//                         </h3>

//                         <p className="text-sm text-slate-500 mt-1 mb-5">
//                           Record the final resolution before closing
//                           this investigation.
//                         </p>

//                         <textarea
//                           value={resolutionSummary}
//                           onChange={(e) =>
//                             setResolutionSummary(e.target.value)
//                           }
//                           placeholder="Enter resolution summary..."
//                           rows={3}
//                           className="w-full rounded-xl border border-slate-700 bg-[#071321] px-4 py-3 text-sm outline-none focus:border-red-500"
//                           required
//                         />

//                         <button
//                           type="submit"
//                           disabled={submitting}
//                           className="mt-4 rounded-xl bg-red-600 hover:bg-red-500 disabled:opacity-50 px-5 py-2.5 font-semibold text-sm"
//                         >
//                           {submitting
//                             ? "Resolving..."
//                             : "Resolve Incident"}
//                         </button>
//                       </form>
//                     )}
//                   </>
//                 )}
//               </>
//             )}
//           </section>
//         </div>
//       </div>
//     </main>
//   );
// }


"use client";

import { useEffect, useMemo, useState } from "react";
import api, {
  clearSession,
  getStoredRole,
  isLoggedIn,
} from "@/lib/api";
import { useRouter } from "next/navigation";

export default function InvestigationsPage() {
  const router = useRouter();

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const [incidents, setIncidents] = useState([]);
  const [selectedIncident, setSelectedIncident] = useState(null);

  const [notes, setNotes] = useState([]);
  const [timeline, setTimeline] = useState([]);

  const [noteText, setNoteText] = useState("");
  const [evidenceReference, setEvidenceReference] = useState("");

  const [resolutionSummary, setResolutionSummary] = useState("");

  const [loadingDetails, setLoadingDetails] = useState(false);
  const [submittingNote, setSubmittingNote] = useState(false);
  const [resolving, setResolving] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [role, setRole] = useState("");

  // =========================================================
  // AUTH
  // =========================================================

  useEffect(() => {
    if (!isLoggedIn()) {
      router.replace("/login");
      return;
    }

    setRole(getStoredRole() || "user");
    loadIncidents();
  }, [router]);

  // =========================================================
  // LOAD INCIDENTS
  // =========================================================

  async function loadIncidents() {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/incidents");

      const data = response.data;

      const incidentList = Array.isArray(data)
        ? data
        : data?.incidents || [];

      setIncidents(incidentList);

      if (incidentList.length > 0) {
        const current =
          selectedIncident &&
          incidentList.find(
            (item) => item.id === selectedIncident.id
          );

        const incidentToSelect = current || incidentList[0];

        setSelectedIncident(incidentToSelect);
        await loadInvestigationDetails(incidentToSelect);
      } else {
        setSelectedIncident(null);
        setNotes([]);
        setTimeline([]);
      }
    } catch (err) {
      console.error("Incident loading error:", err);

      if (err?.response?.status === 401) {
        handleLogout();
        return;
      }

      setError(
        err?.response?.data?.detail ||
          "Unable to load investigation data."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  // =========================================================
  // LOAD SELECTED INCIDENT DETAILS
  // =========================================================

  async function loadInvestigationDetails(incident) {
    if (!incident) return;

    try {
      setLoadingDetails(true);
      setError("");

      /*
       * Backend incidents return employee_id as the
       * PostgreSQL employee numeric ID.
       *
       * Timeline requires EMP1001-style employee_id.
       *
       * If your incident API later returns employee_code,
       * this automatically uses it.
       */

      const employeeCode =
        incident.employee_code ||
        incident.employee?.employee_id ||
        incident.employee_id;

      const results = await Promise.allSettled([
        api.get(`/incidents/${incident.id}/notes`),
        api.get(
          `/investigations/${employeeCode}/timeline`
        ),
      ]);

      // Notes
      if (results[0].status === "fulfilled") {
        const data = results[0].value.data;

        setNotes(data?.notes || []);
      }

      // Timeline
      if (results[1].status === "fulfilled") {
        const data = results[1].value.data;

        setTimeline(data?.timeline || []);
      }

      const unauthorized = results.some(
        (result) =>
          result.status === "rejected" &&
          result.reason?.response?.status === 401
      );

      if (unauthorized) {
        handleLogout();
      }
    } catch (err) {
      console.error(
        "Investigation detail loading error:",
        err
      );

      setError(
        err?.response?.data?.detail ||
          "Unable to load investigation details."
      );
    } finally {
      setLoadingDetails(false);
    }
  }

  // =========================================================
  // SELECT INCIDENT
  // =========================================================

  async function handleSelectIncident(incident) {
    setSelectedIncident(incident);
    setSuccess("");
    setError("");
    setNoteText("");
    setEvidenceReference("");
    setResolutionSummary("");

    await loadInvestigationDetails(incident);
  }

  // =========================================================
  // REFRESH
  // =========================================================

  async function handleRefresh() {
    setRefreshing(true);
    await loadIncidents();
  }

  // =========================================================
  // ADD INVESTIGATION NOTE
  // =========================================================

  async function handleAddNote() {
    if (!selectedIncident) return;

    if (!noteText.trim()) {
      setError("Please enter investigation findings.");
      return;
    }

    try {
      setSubmittingNote(true);
      setError("");
      setSuccess("");

      await api.post(
        `/incidents/${selectedIncident.id}/notes`,
        {
          note: noteText.trim(),
          evidence_reference:
            evidenceReference.trim() || null,
        }
      );

      setNoteText("");
      setEvidenceReference("");

      setSuccess(
        "Investigation note added successfully."
      );

      await loadIncidents();
    } catch (err) {
      console.error("Add note error:", err);

      if (err?.response?.status === 401) {
        handleLogout();
        return;
      }

      setError(
        err?.response?.data?.detail ||
          "Unable to add investigation note."
      );
    } finally {
      setSubmittingNote(false);
    }
  }

  // =========================================================
  // RESOLVE INCIDENT
  // =========================================================

  async function handleResolveIncident() {
    if (!selectedIncident) return;

    if (!resolutionSummary.trim()) {
      setError("Please enter a resolution summary.");
      return;
    }

    try {
      setResolving(true);
      setError("");
      setSuccess("");

      await api.patch(
        `/incidents/${selectedIncident.id}/resolve`,
        {
          resolution_summary:
            resolutionSummary.trim(),
        }
      );

      setResolutionSummary("");

      setSuccess(
        "Incident resolved successfully."
      );

      await loadIncidents();
    } catch (err) {
      console.error("Resolve incident error:", err);

      if (err?.response?.status === 401) {
        handleLogout();
        return;
      }

      setError(
        err?.response?.data?.detail ||
          "Unable to resolve incident."
      );
    } finally {
      setResolving(false);
    }
  }

  // =========================================================
  // LOGOUT
  // =========================================================

  function handleLogout() {
    clearSession();
    router.replace("/login");
  }

  // =========================================================
  // CALCULATED DATA
  // =========================================================

  const activeIncidentCount = incidents.length;

  const investigatingCount = incidents.filter(
    (incident) =>
      incident.status?.toLowerCase() ===
      "investigating"
  ).length;

  const highCriticalCount = incidents.filter(
    (incident) =>
      ["high", "critical"].includes(
        incident.severity?.toLowerCase()
      )
  ).length;

  const statusLabel = selectedIncident?.status
    ? selectedIncident.status.toUpperCase()
    : "";

  const severityLabel = selectedIncident?.severity
    ? selectedIncident.severity.toUpperCase()
    : "";

  // =========================================================
  // PAGE
  // =========================================================

  if (loading) {
    return <InvestigationSkeleton />;
  }

  return (
    <main className="min-h-screen bg-[#07111f] text-slate-100">

      {/* =====================================================
          TOP NAVIGATION
      ===================================================== */}

      <header className="sticky top-0 z-30 border-b border-white/10 bg-[#07111f]/95 backdrop-blur-xl">

        <div className="mx-auto flex h-20 max-w-[1600px] items-center justify-between px-5 sm:px-8">

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

              <p className="text-[9px] uppercase tracking-[0.18em] text-slate-500">
                Security Intelligence
              </p>
            </div>

          </div>

          <nav className="hidden items-center gap-7 md:flex">

            <a
              href="/"
              className="text-sm font-medium text-slate-400 transition hover:text-white"
            >
              Home
            </a>

            <a
              href="/employees"
              className="text-sm font-medium text-slate-400 transition hover:text-white"
            >
              Employees
            </a>

            <a
              href="/dashboard"
              className="text-sm font-medium text-slate-400 transition hover:text-white"
            >
              Dashboard
            </a>

            <span className="h-6 w-px bg-white/10" />

            <button
              onClick={handleLogout}
              className="text-sm font-medium text-slate-400 transition hover:text-white"
            >
              Sign out
            </button>

          </nav>

        </div>

      </header>

      {/* =====================================================
          MAIN CONTENT
      ===================================================== */}

      <div className="mx-auto max-w-[1500px] px-5 py-8 sm:px-8">

        {/* HEADER */}

        <section className="mb-8 flex flex-col justify-between gap-5 md:flex-row md:items-end">

          <div>

            <p className="text-[10px] font-bold uppercase tracking-[0.24em] text-blue-400">
              Security Operations
            </p>

            <h2 className="mt-2 text-3xl font-black tracking-tight sm:text-4xl">
              Threat Investigation
            </h2>

            <p className="mt-2 text-sm text-slate-400">
              Investigate active incidents, review evidence,
              and track employee security activity.
            </p>

          </div>

          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="w-fit rounded-xl border border-white/10 bg-white/[0.03] px-5 py-3 text-sm font-semibold text-slate-300 transition hover:bg-white/[0.07] disabled:opacity-50"
          >
            {refreshing
              ? "Refreshing..."
              : "↻ Refresh"}
          </button>

        </section>

        {/* =====================================================
            ALERTS
        ===================================================== */}

        {error && (
          <div className="mb-5 rounded-2xl border border-red-400/20 bg-red-400/5 p-4">

            <p className="text-sm font-semibold text-red-300">
              Investigation Error
            </p>

            <p className="mt-1 text-xs text-slate-400">
              {error}
            </p>

          </div>
        )}

        {success && (
          <div className="mb-5 rounded-2xl border border-emerald-400/20 bg-emerald-400/5 p-4">

            <p className="text-sm font-semibold text-emerald-300">
              ✓ {success}
            </p>

          </div>
        )}

        {/* =====================================================
            KPI
        ===================================================== */}

        <section className="mb-6 grid gap-4 md:grid-cols-3">

          <MetricCard
            label="Active Incidents"
            value={activeIncidentCount}
            color="blue"
          />

          <MetricCard
            label="Investigating"
            value={investigatingCount}
            color="blue"
          />

          <MetricCard
            label="High / Critical"
            value={highCriticalCount}
            color="red"
          />

        </section>

        {/* =====================================================
            MAIN INVESTIGATION AREA
        ===================================================== */}

        {incidents.length === 0 ? (

          <EmptyState />

        ) : (

          <section className="grid gap-6 xl:grid-cols-[0.75fr_1.25fr]">

            {/* =================================================
                INCIDENT LIST
            ================================================= */}

            <div className="overflow-hidden rounded-3xl border border-white/10 bg-[#0b1727]">

              <div className="border-b border-white/10 p-6">

                <h3 className="text-lg font-bold">
                  Active Incidents
                </h3>

                <p className="mt-1 text-xs text-slate-500">
                  Select an incident to investigate.
                </p>

              </div>

              <div className="max-h-[700px] overflow-y-auto">

                {incidents.map((incident) => {

                  const selected =
                    selectedIncident?.id === incident.id;

                  return (
                    <button
                      key={incident.id}
                      onClick={() =>
                        handleSelectIncident(incident)
                      }
                      className={`w-full border-b border-white/5 p-5 text-left transition ${
                        selected
                          ? "border-l-2 border-l-blue-400 bg-blue-500/[0.07]"
                          : "hover:bg-white/[0.03]"
                      }`}
                    >

                      <div className="flex items-start justify-between gap-3">

                        <div>

                          <p className="text-sm font-bold text-slate-200">
                            Incident #{incident.id}
                          </p>

                          <p className="mt-1 text-xs text-slate-400">
                            Employee ID:{" "}
                            {incident.employee_id}
                          </p>

                        </div>

                        <SeverityBadge
                          severity={incident.severity}
                        />

                      </div>

                      <p className="mt-4 line-clamp-2 text-xs leading-5 text-slate-400">
                        {incident.summary ||
                          "No incident summary available."}
                      </p>

                      <div className="mt-4 flex items-center justify-between">

                        <StatusBadge
                          status={incident.status}
                        />

                        <span className="text-[10px] text-slate-600">
                          {formatDate(
                            incident.created_at
                          )}
                        </span>

                      </div>

                    </button>
                  );
                })}

              </div>

            </div>

            {/* =================================================
                DETAILS
            ================================================= */}

            <div className="space-y-6">

              {/* INCIDENT HEADER */}

              <div className="rounded-3xl border border-white/10 bg-[#0b1727] p-7">

                <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">

                  <div>

                    <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-blue-400">
                      INCIDENT #{selectedIncident?.id}
                    </p>

                    <h3 className="mt-2 text-2xl font-black">
                      Employee #{selectedIncident?.employee_id}
                    </h3>

                    <p className="mt-2 text-xs text-slate-500">
                      Created{" "}
                      {formatDate(
                        selectedIncident?.created_at
                      )}
                    </p>

                  </div>

                  <div className="flex gap-2">

                    <SeverityBadge
                      severity={selectedIncident?.severity}
                    />

                    <StatusBadge
                      status={selectedIncident?.status}
                    />

                  </div>

                </div>

                <div className="mt-7 rounded-2xl border border-white/5 bg-[#081321] p-5">

                  <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-600">
                    Incident Summary
                  </p>

                  <p className="mt-3 text-sm leading-6 text-slate-300">
                    {selectedIncident?.summary ||
                      "No summary provided."}
                  </p>

                </div>

              </div>

              {/* =================================================
                  NOTES
              ================================================= */}

              <div className="rounded-3xl border border-white/10 bg-[#0b1727] p-7">

                <div>

                  <h3 className="text-lg font-bold">
                    Add Investigation Note
                  </h3>

                  <p className="mt-1 text-xs text-slate-500">
                    Document findings and supporting evidence.
                  </p>

                </div>

                <textarea
                  value={noteText}
                  onChange={(event) =>
                    setNoteText(event.target.value)
                  }
                  placeholder="Enter investigation findings..."
                  rows={5}
                  className="mt-5 w-full resize-none rounded-2xl border border-white/10 bg-[#081321] px-4 py-4 text-sm text-slate-200 outline-none transition placeholder:text-slate-600 focus:border-blue-400/40"
                />

                <input
                  value={evidenceReference}
                  onChange={(event) =>
                    setEvidenceReference(
                      event.target.value
                    )
                  }
                  placeholder="Evidence reference (optional)"
                  className="mt-3 w-full rounded-xl border border-white/10 bg-[#081321] px-4 py-3 text-sm text-slate-200 outline-none transition placeholder:text-slate-600 focus:border-blue-400/40"
                />

                <button
                  onClick={handleAddNote}
                  disabled={submittingNote}
                  className="mt-4 rounded-xl bg-blue-500 px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-400 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {submittingNote
                    ? "Adding..."
                    : "Add Investigation Note"}
                </button>

                {/* NOTES HISTORY */}

                <div className="mt-8">

                  <div className="mb-4 flex items-center justify-between">

                    <h4 className="text-sm font-bold">
                      Investigation Notes
                    </h4>

                    <span className="text-xs text-slate-600">
                      {notes.length} notes
                    </span>

                  </div>

                  {loadingDetails ? (

                    <div className="rounded-xl bg-white/[0.02] p-5 text-xs text-slate-500">
                      Loading investigation evidence...
                    </div>

                  ) : notes.length === 0 ? (

                    <div className="rounded-xl border border-dashed border-white/10 p-6 text-center text-xs text-slate-600">
                      No investigation notes yet.
                    </div>

                  ) : (

                    <div className="space-y-3">

                      {notes.map((note) => (

                        <div
                          key={note.id}
                          className="rounded-2xl border border-white/5 bg-white/[0.02] p-4"
                        >

                          <div className="flex items-center justify-between">

                            <span className="text-[10px] font-semibold text-blue-400">
                              Analyst #{note.author_user_id}
                            </span>

                            <span className="text-[10px] text-slate-600">
                              {formatDate(
                                note.created_at
                              )}
                            </span>

                          </div>

                          <p className="mt-3 text-sm leading-6 text-slate-300">
                            {note.note}
                          </p>

                          {note.evidence_reference && (
                            <div className="mt-3 rounded-lg bg-black/20 px-3 py-2">

                              <span className="text-[10px] uppercase tracking-wider text-slate-600">
                                Evidence
                              </span>

                              <p className="mt-1 text-xs text-blue-300">
                                {note.evidence_reference}
                              </p>

                            </div>
                          )}

                        </div>

                      ))}

                    </div>

                  )}

                </div>

              </div>

              {/* =================================================
                  TIMELINE
              ================================================= */}

              <div className="rounded-3xl border border-white/10 bg-[#0b1727] p-7">

                <div className="flex items-center justify-between">

                  <div>

                    <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">
                      Unified Evidence
                    </p>

                    <h3 className="mt-1 text-lg font-bold">
                      Investigation Timeline
                    </h3>

                  </div>

                  <span className="text-xs text-slate-600">
                    {timeline.length} events
                  </span>

                </div>

                <div className="mt-6">

                  {timeline.length === 0 ? (

                    <div className="rounded-xl border border-dashed border-white/10 p-8 text-center text-xs text-slate-600">
                      No timeline events available.
                    </div>

                  ) : (

                    <div className="space-y-3">

                      {timeline.map((event, index) => (

                        <TimelineItem
                          key={`${event.source}-${index}`}
                          event={event}
                        />

                      ))}

                    </div>

                  )}

                </div>

              </div>

              {/* =================================================
                  RESOLUTION
              ================================================= */}

              {selectedIncident?.status !== "resolved" && (

                <div className="rounded-3xl border border-white/10 bg-[#0b1727] p-7">

                  <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">
                    Incident Resolution
                  </p>

                  <h3 className="mt-1 text-lg font-bold">
                    Resolve Incident
                  </h3>

                  <p className="mt-1 text-xs text-slate-500">
                    Record the final investigation outcome.
                  </p>

                  <textarea
                    value={resolutionSummary}
                    onChange={(event) =>
                      setResolutionSummary(
                        event.target.value
                      )
                    }
                    placeholder="Enter resolution summary..."
                    rows={4}
                    className="mt-5 w-full resize-none rounded-2xl border border-white/10 bg-[#081321] px-4 py-4 text-sm text-slate-200 outline-none placeholder:text-slate-600 focus:border-emerald-400/40"
                  />

                  <button
                    onClick={handleResolveIncident}
                    disabled={resolving}
                    className="mt-4 rounded-xl border border-emerald-400/20 bg-emerald-400/10 px-5 py-3 text-sm font-bold text-emerald-400 transition hover:bg-emerald-400/15 disabled:opacity-50"
                  >
                    {resolving
                      ? "Resolving..."
                      : "✓ Resolve Incident"}
                  </button>

                </div>

              )}

            </div>

          </section>

        )}

        {/* =====================================================
            FOOTER
        ===================================================== */}

        <footer className="mt-10 border-t border-white/10 py-6">

          <div className="flex flex-col gap-2 text-xs text-slate-600 sm:flex-row sm:items-center sm:justify-between">

            <p>
              ITBIS · Insider Threat Detection & Behavioral Security Intelligence
            </p>

            <p>
              Role: {role || "User"}
            </p>

          </div>

        </footer>

      </div>

    </main>
  );
}

/* =========================================================
   METRIC CARD
========================================================= */

function MetricCard({
  label,
  value,
  color = "blue",
}) {
  const styles = {
    blue: "text-blue-400",
    red: "text-red-400",
  };

  return (
    <div className="rounded-2xl border border-white/10 bg-[#0b1727] p-6">

      <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500">
        {label}
      </p>

      <p
        className={`mt-3 text-3xl font-black ${styles[color]}`}
      >
        {value}
      </p>

    </div>
  );
}

/* =========================================================
   SEVERITY BADGE
========================================================= */

function SeverityBadge({ severity }) {
  const value = severity || "unknown";

  const styles = {
    critical:
      "border-red-400/30 bg-red-400/10 text-red-400",
    high:
      "border-orange-400/30 bg-orange-400/10 text-orange-400",
    medium:
      "border-amber-400/30 bg-amber-400/10 text-amber-400",
    low:
      "border-blue-400/30 bg-blue-400/10 text-blue-400",
    informational:
      "border-slate-400/20 bg-slate-400/10 text-slate-400",
    unknown:
      "border-slate-400/20 bg-slate-400/10 text-slate-500",
  };

  return (
    <span
      className={`rounded-full border px-3 py-1 text-[10px] font-bold ${styles[value.toLowerCase()] || styles.unknown}`}
    >
      {value.toUpperCase()}
    </span>
  );
}

/* =========================================================
   STATUS BADGE
========================================================= */

function StatusBadge({ status }) {
  const value = status || "unknown";

  const styles = {
    open:
      "bg-slate-400/10 text-slate-400",
    investigating:
      "bg-blue-400/10 text-blue-400",
    resolved:
      "bg-emerald-400/10 text-emerald-400",
  };

  return (
    <span
      className={`rounded-full px-3 py-1 text-[10px] font-semibold ${
        styles[value.toLowerCase()] ||
        "bg-slate-400/10 text-slate-500"
      }`}
    >
      {value}
    </span>
  );
}

/* =========================================================
   TIMELINE ITEM
========================================================= */

function TimelineItem({ event }) {
  const source = event.source || "unknown";

  const sourceLabel = {
    activity_log: "Activity Log",
    rule_anomaly: "Rule Detection",
    ml_anomaly: "ML Detection",
  };

  const detail = event.detail || {};

  return (
    <div className="relative rounded-2xl border border-white/5 bg-white/[0.02] p-4">

      <div className="flex items-start gap-4">

        <div className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-400/10 text-blue-400">
          {source === "ml_anomaly"
            ? "◇"
            : source === "rule_anomaly"
            ? "△"
            : "◌"}
        </div>

        <div className="min-w-0 flex-1">

          <div className="flex flex-col justify-between gap-1 sm:flex-row">

            <p className="text-xs font-bold text-slate-300">
              {sourceLabel[source] || source}
            </p>

            <span className="text-[10px] text-slate-600">
              {formatDate(event.time)}
            </span>

          </div>

          <div className="mt-3">

            {source === "activity_log" && (
              <>
                <p className="text-xs text-slate-400">
                  Event:{" "}
                  <span className="text-slate-300">
                    {detail.event_type || "Unknown"}
                  </span>
                </p>

                {detail.details &&
                  Object.keys(detail.details).length > 0 && (
                    <pre className="mt-2 overflow-x-auto rounded-lg bg-black/20 p-3 text-[10px] text-slate-500">
                      {JSON.stringify(
                        detail.details,
                        null,
                        2
                      )}
                    </pre>
                  )}
              </>
            )}

            {source === "rule_anomaly" && (
              <>
                <p className="text-xs text-slate-400">
                  Indicator:{" "}
                  <span className="text-slate-300">
                    {detail.indicator || "Unknown"}
                  </span>
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  Type:{" "}
                  {detail.anomaly_type || "Unknown"}
                </p>
              </>
            )}

            {source === "ml_anomaly" && (
              <p className="text-xs text-slate-400">
                ML prediction:{" "}
                <span className="font-semibold text-red-400">
                  {detail.prediction}
                </span>
              </p>
            )}

          </div>

          {event.severity && (
            <div className="mt-3">
              <SeverityBadge
                severity={event.severity}
              />
            </div>
          )}

        </div>

      </div>

    </div>
  );
}

/* =========================================================
   EMPTY STATE
========================================================= */

function EmptyState() {
  return (
    <div className="rounded-3xl border border-dashed border-white/10 bg-[#0b1727] p-16 text-center">

      <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-emerald-400/10 text-xl text-emerald-400">
        ✓
      </div>

      <h3 className="mt-5 text-lg font-bold">
        No Active Incidents
      </h3>

      <p className="mx-auto mt-2 max-w-md text-sm text-slate-500">
        There are currently no unresolved security
        incidents requiring investigation.
      </p>

    </div>
  );
}

/* =========================================================
   DATE FORMATTER
========================================================= */

function formatDate(value) {
  if (!value) return "Unknown time";

  try {
    return new Date(value).toLocaleString();
  } catch {
    return String(value);
  }
}

/* =========================================================
   LOADING SKELETON
========================================================= */

function InvestigationSkeleton() {
  return (
    <main className="min-h-screen bg-[#07111f] p-8 text-white">

      <div className="mx-auto max-w-[1500px] animate-pulse">

        <div className="mb-8">

          <div className="h-3 w-40 rounded bg-white/10" />

          <div className="mt-4 h-10 w-80 rounded bg-white/10" />

          <div className="mt-3 h-4 w-96 rounded bg-white/10" />

        </div>

        <div className="grid gap-4 md:grid-cols-3">

          {[1, 2, 3].map((item) => (
            <div
              key={item}
              className="h-28 rounded-2xl bg-white/5"
            />
          ))}

        </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-[0.75fr_1.25fr]">

          <div className="h-[650px] rounded-3xl bg-white/5" />

          <div className="space-y-6">

            <div className="h-56 rounded-3xl bg-white/5" />

            <div className="h-96 rounded-3xl bg-white/5" />

          </div>

        </div>

      </div>

    </main>
  );
}
// "use client";

// import { useEffect, useMemo, useState } from "react";
// import api, {
//   clearSession,
//   getStoredRole,
//   isLoggedIn,
// } from "@/lib/api";

// const EDIT_ROLES = ["admin", "security_manager"];

// const EMPTY_FORM = {
//   employee_id: "",
//   name: "",
//   department: "",
//   designation: "",
//   manager_id: "",
//   device_info: "",
//   access_privileges: "",
// };

// export default function EmployeesPage() {
//   const [employees, setEmployees] = useState([]);
//   const [role, setRole] = useState(null);

//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState("");
//   const [message, setMessage] = useState("");

//   const [search, setSearch] = useState("");
//   const [department, setDepartment] = useState("All");

//   const [selectedEmployee, setSelectedEmployee] = useState(null);
//   const [directReports, setDirectReports] = useState([]);
//   const [reportsLoading, setReportsLoading] = useState(false);

//   const [showAddModal, setShowAddModal] = useState(false);
//   const [showEditModal, setShowEditModal] = useState(false);

//   const [form, setForm] = useState(EMPTY_FORM);
//   const [formLoading, setFormLoading] = useState(false);

//   const canManageEmployees = EDIT_ROLES.includes(role);

//   useEffect(() => {
//     if (!isLoggedIn()) {
//       setError("You're not logged in. Please go to /login first.");
//       setLoading(false);
//       return;
//     }

//     setRole(getStoredRole());
//     loadEmployees();
//   }, []);

//   async function loadEmployees() {
//     try {
//       setLoading(true);
//       setError("");

//       const res = await api.get("/employees");
//       setEmployees(res.data || []);
//     } catch (err) {
//       const detail =
//         err?.response?.data?.detail ||
//         "Failed to load employees.";

//       setError(
//         Array.isArray(detail)
//           ? detail.map((item) => item.msg).join(", ")
//           : detail
//       );
//     } finally {
//       setLoading(false);
//     }
//   }

//   const departments = useMemo(() => {
//     const values = employees
//       .map((employee) => employee.department)
//       .filter(Boolean);

//     return ["All", ...new Set(values)];
//   }, [employees]);

//   const filteredEmployees = useMemo(() => {
//     const query = search.trim().toLowerCase();

//     return employees.filter((employee) => {
//       const matchesSearch =
//         !query ||
//         employee.employee_id?.toLowerCase().includes(query) ||
//         employee.name?.toLowerCase().includes(query) ||
//         employee.department?.toLowerCase().includes(query) ||
//         employee.designation?.toLowerCase().includes(query);

//       const matchesDepartment =
//         department === "All" ||
//         employee.department === department;

//       return matchesSearch && matchesDepartment;
//     });
//   }, [employees, search, department]);

//   function updateForm(field, value) {
//     setForm((current) => ({
//       ...current,
//       [field]: value,
//     }));

//     setError("");
//     setMessage("");
//   }

//   /*
//    * View employee profile and load direct reports.
//    *
//    * IMPORTANT:
//    * Backend route expects employee_id such as EMP1001,
//    * not the database numeric id.
//    */
//   async function viewEmployee(employee) {
//     try {
//       setError("");
//       setMessage("");

//       setSelectedEmployee(employee);
//       setDirectReports([]);
//       setReportsLoading(true);

//       const reportsResponse = await api.get(
//         `/employees/${employee.employee_id}/reports`
//       );

//       setDirectReports(reportsResponse.data || []);
//     } catch (err) {
//       setDirectReports([]);

//       const detail =
//         err?.response?.data?.detail ||
//         "Unable to load direct reports.";

//       setError(
//         Array.isArray(detail)
//           ? detail.map((item) => item.msg).join(", ")
//           : detail
//       );
//     } finally {
//       setReportsLoading(false);
//     }
//   }

//   function openAddModal() {
//     setForm(EMPTY_FORM);
//     setError("");
//     setMessage("");
//     setShowAddModal(true);
//   }

//   function openEditModal(employee) {
//     setForm({
//       employee_id: employee.employee_id || "",
//       name: employee.name || "",
//       department: employee.department || "",
//       designation: employee.designation || "",
//       manager_id:
//         employee.manager_id === null ||
//         employee.manager_id === undefined
//           ? ""
//           : String(employee.manager_id),
//       device_info: employee.device_info || "",
//       access_privileges: employee.access_privileges || "",
//     });

//     setSelectedEmployee(employee);
//     setError("");
//     setMessage("");
//     setShowEditModal(true);
//   }

//   async function addEmployee(event) {
//     event.preventDefault();

//     try {
//       setFormLoading(true);
//       setError("");
//       setMessage("");

//       const payload = {
//         employee_id: form.employee_id.trim(),
//         name: form.name.trim(),
//         department: form.department.trim(),
//         designation: form.designation.trim(),
//         manager_id: form.manager_id
//           ? Number(form.manager_id)
//           : null,
//         device_info: form.device_info.trim(),
//         access_privileges: form.access_privileges.trim(),
//       };

//       await api.post("/employees", payload);

//       setMessage("Employee added successfully.");
//       setShowAddModal(false);
//       setForm(EMPTY_FORM);

//       await loadEmployees();
//     } catch (err) {
//       const detail =
//         err?.response?.data?.detail ||
//         "Failed to add employee.";

//       setError(
//         Array.isArray(detail)
//           ? detail.map((item) => item.msg).join(", ")
//           : detail
//       );
//     } finally {
//       setFormLoading(false);
//     }
//   }

//   async function updateEmployee(event) {
//     event.preventDefault();

//     if (!selectedEmployee) {
//       setError("No employee selected.");
//       return;
//     }

//     try {
//       setFormLoading(true);
//       setError("");
//       setMessage("");

//       const payload = {
//         name: form.name.trim(),
//         department: form.department.trim(),
//         designation: form.designation.trim(),
//         manager_id: form.manager_id
//           ? Number(form.manager_id)
//           : null,
//         device_info: form.device_info.trim(),
//         access_privileges: form.access_privileges.trim(),
//       };

//       /*
//        * IMPORTANT:
//        * Use employee.employee_id (EMP1001),
//        * NOT employee.id (1, 2, 3...).
//        */
//       await api.patch(
//         `/employees/${selectedEmployee.employee_id}`,
//         payload
//       );

//       setMessage("Employee updated successfully.");
//       setShowEditModal(false);

//       await loadEmployees();
//     } catch (err) {
//       const detail =
//         err?.response?.data?.detail ||
//         "Failed to update employee.";

//       setError(
//         Array.isArray(detail)
//           ? detail.map((item) => item.msg).join(", ")
//           : detail
//       );
//     } finally {
//       setFormLoading(false);
//     }
//   }

//   function closeViewModal() {
//     setSelectedEmployee(null);
//     setDirectReports([]);
//     setError("");
//   }

//   function closeEditModal() {
//     setShowEditModal(false);
//     setError("");
//   }

//   function closeAddModal() {
//     setShowAddModal(false);
//     setForm(EMPTY_FORM);
//     setError("");
//   }

//   function logout() {
//     clearSession();
//     window.location.href = "/login";
//   }

//   if (loading) {
//     return (
//       <div className="max-w-6xl">
//         <p className="text-slate-600">
//           Loading employees...
//         </p>
//       </div>
//     );
//   }

//   return (
//     <div className="max-w-6xl">

//       {/* Header */}
//       <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
//         <div>
//           <h1 className="text-2xl font-semibold text-slate-900">
//             Employees
//           </h1>

//           <p className="text-sm text-slate-500 mt-1">
//             Manage employee identities, reporting relationships and
//             access information.
//           </p>
//         </div>

//         {role && (
//           <div className="flex items-center gap-3 text-sm">
//             <span className="text-slate-500">
//               Signed in as:
//             </span>

//             <span className="font-medium text-slate-800">
//               {role}
//             </span>

//             <button
//               onClick={logout}
//               className="text-blue-600 hover:underline"
//             >
//               Log out
//             </button>
//           </div>
//         )}
//       </div>

//       {/* Error Message */}
//       {error && (
//         <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3">
//           <p className="text-sm text-red-600">
//             {error}
//           </p>
//         </div>
//       )}

//       {/* Success Message */}
//       {message && (
//         <div className="mb-4 rounded-lg border border-green-200 bg-green-50 px-4 py-3">
//           <p className="text-sm text-green-600">
//             {message}
//           </p>
//         </div>
//       )}

//       {/* Statistics */}
//       <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">

//         <div className="bg-white border rounded-xl p-4 shadow-sm">
//           <p className="text-sm text-slate-500">
//             Total Employees
//           </p>

//           <p className="text-2xl font-semibold text-slate-900 mt-1">
//             {employees.length}
//           </p>
//         </div>

//         <div className="bg-white border rounded-xl p-4 shadow-sm">
//           <p className="text-sm text-slate-500">
//             Departments
//           </p>

//           <p className="text-2xl font-semibold text-slate-900 mt-1">
//             {departments.length - 1}
//           </p>
//         </div>

//         <div className="bg-white border rounded-xl p-4 shadow-sm">
//           <p className="text-sm text-slate-500">
//             Visible Results
//           </p>

//           <p className="text-2xl font-semibold text-slate-900 mt-1">
//             {filteredEmployees.length}
//           </p>
//         </div>

//       </div>

//       {/* Search / Filter / Add */}
//       <div className="bg-white border rounded-xl p-4 shadow-sm mb-5">

//         <div className="flex flex-col md:flex-row gap-3">

//           <input
//             type="text"
//             placeholder="Search by ID, name, department or designation..."
//             value={search}
//             onChange={(e) => setSearch(e.target.value)}
//             className="border rounded-lg px-3 py-2 w-full outline-none focus:ring-2 focus:ring-slate-200"
//           />

//           <select
//             value={department}
//             onChange={(e) => setDepartment(e.target.value)}
//             className="border rounded-lg px-3 py-2 md:w-56 bg-white"
//           >
//             {departments.map((item) => (
//               <option key={item} value={item}>
//                 {item === "All"
//                   ? "All Departments"
//                   : item}
//               </option>
//             ))}
//           </select>

//           {canManageEmployees && (
//             <button
//               onClick={openAddModal}
//               className="bg-slate-800 hover:bg-slate-900 text-white rounded-lg px-5 py-2 font-medium whitespace-nowrap"
//             >
//               + Add Employee
//             </button>
//           )}

//         </div>

//       </div>

//       {/* Employee Table */}
//       <div className="bg-white border rounded-xl shadow-sm overflow-hidden">

//         <div className="overflow-x-auto">

//           <table className="w-full border-collapse">

//             <thead>
//               <tr className="bg-slate-100 text-left text-sm">

//                 <th className="p-3 font-semibold">
//                   Employee ID
//                 </th>

//                 <th className="p-3 font-semibold">
//                   Name
//                 </th>

//                 <th className="p-3 font-semibold">
//                   Department
//                 </th>

//                 <th className="p-3 font-semibold">
//                   Designation
//                 </th>

//                 <th className="p-3 font-semibold">
//                   Manager ID
//                 </th>

//                 <th className="p-3 font-semibold text-right">
//                   Actions
//                 </th>

//               </tr>
//             </thead>

//             <tbody>

//               {filteredEmployees.map((emp) => (
//                 <tr
//                   key={emp.id}
//                   className="border-t hover:bg-slate-50"
//                 >

//                   <td className="p-3 text-sm font-medium">
//                     {emp.employee_id}
//                   </td>

//                   <td className="p-3 text-sm">
//                     {emp.name}
//                   </td>

//                   <td className="p-3 text-sm">
//                     {emp.department}
//                   </td>

//                   <td className="p-3 text-sm">
//                     {emp.designation}
//                   </td>

//                   <td className="p-3 text-sm">
//                     {emp.manager_id ?? "—"}
//                   </td>

//                   <td className="p-3">

//                     <div className="flex justify-end gap-2">

//                       <button
//                         onClick={() => viewEmployee(emp)}
//                         className="border rounded-md px-3 py-1.5 text-sm hover:bg-slate-100"
//                       >
//                         View
//                       </button>

//                       {canManageEmployees && (
//                         <button
//                           onClick={() => openEditModal(emp)}
//                           className="bg-slate-800 text-white rounded-md px-3 py-1.5 text-sm hover:bg-slate-900"
//                         >
//                           Edit
//                         </button>
//                       )}

//                     </div>

//                   </td>

//                 </tr>
//               ))}

//               {filteredEmployees.length === 0 && (
//                 <tr>
//                   <td
//                     colSpan="6"
//                     className="p-8 text-center text-slate-500"
//                   >
//                     No employees found.
//                   </td>
//                 </tr>
//               )}

//             </tbody>

//           </table>

//         </div>

//       </div>

//       {/* View Employee Modal */}
//       {selectedEmployee && !showEditModal && (
//         <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">

//           <div className="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">

//             <div className="p-5 border-b flex justify-between items-center">

//               <div>
//                 <h2 className="text-xl font-semibold">
//                   Employee Profile
//                 </h2>

//                 <p className="text-sm text-slate-500 mt-1">
//                   {selectedEmployee.employee_id}
//                 </p>
//               </div>

//               <button
//                 onClick={closeViewModal}
//                 className="text-slate-500 hover:text-slate-900 text-xl"
//               >
//                 ×
//               </button>

//             </div>

//             <div className="p-5 space-y-4">

//               <Info
//                 label="Name"
//                 value={selectedEmployee.name}
//               />

//               <Info
//                 label="Department"
//                 value={selectedEmployee.department}
//               />

//               <Info
//                 label="Designation"
//                 value={selectedEmployee.designation}
//               />

//               <Info
//                 label="Manager ID"
//                 value={selectedEmployee.manager_id ?? "—"}
//               />

//               <Info
//                 label="Device Info"
//                 value={selectedEmployee.device_info || "—"}
//               />

//               <Info
//                 label="Access Privileges"
//                 value={selectedEmployee.access_privileges || "—"}
//               />

//               {/* Direct Reports */}
//               <div className="pt-3 border-t">

//                 <h3 className="font-semibold text-slate-900 mb-2">
//                   Direct Reports
//                 </h3>

//                 {reportsLoading ? (
//                   <p className="text-sm text-slate-500">
//                     Loading direct reports...
//                   </p>
//                 ) : directReports.length === 0 ? (
//                   <p className="text-sm text-slate-500">
//                     No direct reports.
//                   </p>
//                 ) : (
//                   <div className="space-y-2">

//                     {directReports.map((report) => (
//                       <div
//                         key={report.id}
//                         className="border rounded-lg p-3"
//                       >

//                         <p className="font-medium text-sm">
//                           {report.name}
//                         </p>

//                         <p className="text-xs text-slate-500">
//                           {report.employee_id} •{" "}
//                           {report.designation}
//                         </p>

//                       </div>
//                     ))}

//                   </div>
//                 )}

//               </div>

//               {canManageEmployees && (
//                 <button
//                   onClick={() => openEditModal(selectedEmployee)}
//                   className="w-full bg-slate-800 hover:bg-slate-900 text-white rounded-lg py-2.5 font-medium"
//                 >
//                   Edit Profile
//                 </button>
//               )}

//             </div>

//           </div>

//         </div>
//       )}

//       {/* Add Employee Modal */}
//       {showAddModal && (
//         <EmployeeForm
//           title="Add Employee"
//           form={form}
//           updateForm={updateForm}
//           loading={formLoading}
//           onSubmit={addEmployee}
//           onClose={closeAddModal}
//         />
//       )}

//       {/* Edit Employee Modal */}
//       {showEditModal && selectedEmployee && (
//         <EmployeeForm
//           title="Edit Employee"
//           form={form}
//           updateForm={updateForm}
//           loading={formLoading}
//           onSubmit={updateEmployee}
//           onClose={closeEditModal}
//           editing
//         />
//       )}

//     </div>
//   );
// }


// /* ---------------------------------------------
//    Information Display
// --------------------------------------------- */

// function Info({ label, value }) {
//   return (
//     <div>

//       <p className="text-xs uppercase tracking-wide text-slate-500">
//         {label}
//       </p>

//       <p className="text-sm text-slate-900 mt-1">
//         {value}
//       </p>

//     </div>
//   );
// }


// /* ---------------------------------------------
//    Employee Add/Edit Form
// --------------------------------------------- */

// function EmployeeForm({
//   title,
//   form,
//   updateForm,
//   loading,
//   onSubmit,
//   onClose,
//   editing = false,
// }) {
//   return (
//     <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">

//       <div className="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">

//         {/* Modal Header */}
//         <div className="p-5 border-b flex justify-between items-center">

//           <div>

//             <h2 className="text-xl font-semibold">
//               {title}
//             </h2>

//             <p className="text-sm text-slate-500 mt-1">
//               {editing
//                 ? "Update employee profile information."
//                 : "Create a new employee profile."}
//             </p>

//           </div>

//           <button
//             type="button"
//             onClick={onClose}
//             className="text-slate-500 hover:text-slate-900 text-xl"
//           >
//             ×
//           </button>

//         </div>

//         {/* Form */}
//         <form
//           onSubmit={onSubmit}
//           className="p-5 space-y-4"
//         >

//           {/* Employee ID */}
//           <Field
//             label="Employee ID"
//             value={form.employee_id}
//             disabled={editing}
//             onChange={(value) =>
//               updateForm("employee_id", value)
//             }
//             placeholder="EMP1007"
//           />

//           {/* Name */}
//           <Field
//             label="Name"
//             value={form.name}
//             onChange={(value) =>
//               updateForm("name", value)
//             }
//             placeholder="Employee name"
//           />

//           {/* Department */}
//           <Field
//             label="Department"
//             value={form.department}
//             onChange={(value) =>
//               updateForm("department", value)
//             }
//             placeholder="Finance"
//           />

//           {/* Designation */}
//           <Field
//             label="Designation"
//             value={form.designation}
//             onChange={(value) =>
//               updateForm("designation", value)
//             }
//             placeholder="Financial Analyst"
//           />

//           {/* Manager ID */}
//           <Field
//             label="Manager ID"
//             value={form.manager_id}
//             onChange={(value) =>
//               updateForm("manager_id", value)
//             }
//             placeholder="1"
//             type="number"
//           />

//           {/* Device Info */}
//           <Field
//             label="Device Info"
//             value={form.device_info}
//             onChange={(value) =>
//               updateForm("device_info", value)
//             }
//             placeholder="Laptop / workstation information"
//           />

//           {/* Access Privileges */}
//           <Field
//             label="Access Privileges"
//             value={form.access_privileges}
//             onChange={(value) =>
//               updateForm("access_privileges", value)
//             }
//             placeholder="Standard user access"
//           />

//           {/* Buttons */}
//           <div className="flex gap-3 pt-2">

//             <button
//               type="button"
//               onClick={onClose}
//               className="flex-1 border rounded-lg py-2.5 hover:bg-slate-50"
//             >
//               Cancel
//             </button>

//             <button
//               type="submit"
//               disabled={loading}
//               className="flex-1 bg-slate-800 hover:bg-slate-900 text-white rounded-lg py-2.5 disabled:opacity-50"
//             >
//               {loading
//                 ? "Saving..."
//                 : editing
//                 ? "Save Changes"
//                 : "Add Employee"}
//             </button>

//           </div>

//         </form>

//       </div>

//     </div>
//   );
// }


// /* ---------------------------------------------
//    Reusable Input Field
// --------------------------------------------- */

// function Field({
//   label,
//   value,
//   onChange,
//   placeholder,
//   type = "text",
//   disabled = false,
// }) {
//   const optionalFields = [
//     "Manager ID",
//     "Device Info",
//     "Access Privileges",
//   ];

//   return (
//     <div>

//       <label className="block text-sm font-medium text-slate-700 mb-1">
//         {label}
//       </label>

//       <input
//         type={type}
//         value={value}
//         disabled={disabled}
//         placeholder={placeholder}
//         onChange={(e) => onChange(e.target.value)}
//         required={!optionalFields.includes(label)}
//         className="border rounded-lg px-3 py-2.5 w-full outline-none focus:ring-2 focus:ring-slate-200 disabled:bg-slate-100 disabled:text-slate-500"
//       />

//     </div>
//   );
// }


"use client";

import { useEffect, useMemo, useState } from "react";
import api, {
  clearSession,
  getStoredRole,
  isLoggedIn,
} from "@/lib/api";

const EDIT_ROLES = ["admin", "security_manager"];

const EMPTY_FORM = {
  employee_id: "",
  name: "",
  department: "",
  designation: "",
  manager_id: "",
  device_info: "",
  access_privileges: "",
};

export default function EmployeesPage() {
  const [employees, setEmployees] = useState([]);
  const [role, setRole] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const [search, setSearch] = useState("");
  const [department, setDepartment] = useState("All");

  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [directReports, setDirectReports] = useState([]);
  const [reportsLoading, setReportsLoading] = useState(false);

  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);

  const [form, setForm] = useState(EMPTY_FORM);
  const [formLoading, setFormLoading] = useState(false);

  const canManageEmployees = EDIT_ROLES.includes(role);

  useEffect(() => {
    if (!isLoggedIn()) {
      setError("You're not logged in. Please go to /login first.");
      setLoading(false);
      return;
    }

    setRole(getStoredRole());
    loadEmployees();
  }, []);

  async function loadEmployees() {
    try {
      setLoading(true);
      setError("");

      const res = await api.get("/employees");

      const data = Array.isArray(res.data)
        ? res.data
        : Array.isArray(res.data?.employees)
        ? res.data.employees
        : [];

      setEmployees(data);
    } catch (err) {
      const detail =
        err?.response?.data?.detail ||
        "Failed to load employees.";

      setError(
        Array.isArray(detail)
          ? detail.map((item) => item.msg).join(", ")
          : detail
      );
    } finally {
      setLoading(false);
    }
  }

  const departments = useMemo(() => {
    const values = employees
      .map((employee) => employee.department)
      .filter(Boolean);

    return ["All", ...new Set(values)];
  }, [employees]);

  const filteredEmployees = useMemo(() => {
    const query = search.trim().toLowerCase();

    return employees.filter((employee) => {
      const matchesSearch =
        !query ||
        employee.employee_id?.toLowerCase().includes(query) ||
        employee.name?.toLowerCase().includes(query) ||
        employee.department?.toLowerCase().includes(query) ||
        employee.designation?.toLowerCase().includes(query);

      const matchesDepartment =
        department === "All" ||
        employee.department === department;

      return matchesSearch && matchesDepartment;
    });
  }, [employees, search, department]);

  function updateForm(field, value) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));

    setError("");
    setMessage("");
  }

  /*
   * View employee profile.
   *
   * IMPORTANT:
   * Backend route expects employee_id such as EMP1001,
   * not the database numeric id.
   *
   * The API may return:
   * - an array
   * - { direct_reports: [...] }
   * - { reports: [...] }
   *
   * We normalize all supported responses into an array.
   */
  async function viewEmployee(employee) {
    try {
      setError("");
      setMessage("");

      setSelectedEmployee(employee);
      setDirectReports([]);
      setReportsLoading(true);

      const reportsResponse = await api.get(
        `/employees/${employee.employee_id}/reports`
      );

      const reportsData = reportsResponse.data;

      let reports = [];

      if (Array.isArray(reportsData)) {
        reports = reportsData;
      } else if (Array.isArray(reportsData?.direct_reports)) {
        reports = reportsData.direct_reports;
      } else if (Array.isArray(reportsData?.reports)) {
        reports = reportsData.reports;
      }

      setDirectReports(reports);
    } catch (err) {
      setDirectReports([]);

      const detail =
        err?.response?.data?.detail ||
        "Unable to load direct reports.";

      setError(
        Array.isArray(detail)
          ? detail.map((item) => item.msg).join(", ")
          : detail
      );
    } finally {
      setReportsLoading(false);
    }
  }

  function openAddModal() {
    setForm({ ...EMPTY_FORM });
    setError("");
    setMessage("");
    setShowAddModal(true);
  }

  function openEditModal(employee) {
    setForm({
      employee_id: employee.employee_id || "",
      name: employee.name || "",
      department: employee.department || "",
      designation: employee.designation || "",
      manager_id:
        employee.manager_id === null ||
        employee.manager_id === undefined
          ? ""
          : String(employee.manager_id),
      device_info: employee.device_info || "",
      access_privileges: employee.access_privileges || "",
    });

    setSelectedEmployee(employee);
    setError("");
    setMessage("");
    setShowEditModal(true);
  }

  async function addEmployee(event) {
    event.preventDefault();

    try {
      setFormLoading(true);
      setError("");
      setMessage("");

      const payload = {
        employee_id: form.employee_id.trim(),
        name: form.name.trim(),
        department: form.department.trim(),
        designation: form.designation.trim(),
        manager_id: form.manager_id
          ? Number(form.manager_id)
          : null,
        device_info: form.device_info.trim(),
        access_privileges: form.access_privileges.trim(),
      };

      await api.post("/employees", payload);

      setMessage("Employee added successfully.");
      setShowAddModal(false);
      setForm({ ...EMPTY_FORM });

      await loadEmployees();
    } catch (err) {
      const detail =
        err?.response?.data?.detail ||
        "Failed to add employee.";

      setError(
        Array.isArray(detail)
          ? detail.map((item) => item.msg).join(", ")
          : detail
      );
    } finally {
      setFormLoading(false);
    }
  }

  async function updateEmployee(event) {
    event.preventDefault();

    if (!selectedEmployee) {
      setError("No employee selected.");
      return;
    }

    try {
      setFormLoading(true);
      setError("");
      setMessage("");

      const payload = {
        name: form.name.trim(),
        department: form.department.trim(),
        designation: form.designation.trim(),
        manager_id: form.manager_id
          ? Number(form.manager_id)
          : null,
        device_info: form.device_info.trim(),
        access_privileges: form.access_privileges.trim(),
      };

      /*
       * IMPORTANT:
       * Use employee.employee_id such as EMP1001,
       * NOT employee.id such as 1, 2, 3.
       */
      await api.patch(
        `/employees/${selectedEmployee.employee_id}`,
        payload
      );

      setMessage("Employee updated successfully.");
      setShowEditModal(false);

      await loadEmployees();
    } catch (err) {
      const detail =
        err?.response?.data?.detail ||
        "Failed to update employee.";

      setError(
        Array.isArray(detail)
          ? detail.map((item) => item.msg).join(", ")
          : detail
      );
    } finally {
      setFormLoading(false);
    }
  }

  function closeViewModal() {
    setSelectedEmployee(null);
    setDirectReports([]);
    setError("");
  }

  function closeEditModal() {
    setShowEditModal(false);
    setError("");
  }

  function closeAddModal() {
    setShowAddModal(false);
    setForm({ ...EMPTY_FORM });
    setError("");
  }

  function logout() {
    clearSession();
    window.location.href = "/login";
  }

  if (loading) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">
        <div className="text-center">
          <div className="w-10 h-10 border-4 border-slate-200 border-t-slate-800 rounded-full animate-spin mx-auto mb-4" />

          <p className="text-slate-600">
            Loading employees...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-7xl mx-auto">

      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-5 mb-8">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <span className="inline-flex items-center justify-center w-9 h-9 rounded-lg bg-slate-900 text-white text-sm font-bold">
              E
            </span>

            <span className="text-xs font-semibold uppercase tracking-widest text-slate-500">
              Workforce Intelligence
            </span>
          </div>

          <h1 className="text-3xl font-semibold tracking-tight text-slate-900">
            Employees
          </h1>

          <p className="text-sm text-slate-500 mt-2 max-w-2xl">
            Manage employee identities, reporting relationships,
            device information and access privileges.
          </p>
        </div>

        {role && (
          <div className="flex items-center gap-3 text-sm bg-white border border-slate-200 rounded-xl px-4 py-3 shadow-sm">
            <span className="w-2 h-2 rounded-full bg-green-500" />

            <span className="text-slate-500">
              Signed in as
            </span>

            <span className="font-semibold text-slate-900">
              {role}
            </span>

            <span className="text-slate-300">
              |
            </span>

            <button
              onClick={logout}
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              Log out
            </button>
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="mb-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 flex items-start gap-3">
          <span className="text-red-600 font-bold">
            !
          </span>

          <p className="text-sm text-red-700">
            {error}
          </p>
        </div>
      )}

      {/* Success */}
      {message && (
        <div className="mb-5 rounded-xl border border-green-200 bg-green-50 px-4 py-3 flex items-start gap-3">
          <span className="text-green-600 font-bold">
            ✓
          </span>

          <p className="text-sm text-green-700">
            {message}
          </p>
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">

        <StatCard
          label="Total Employees"
          value={employees.length}
          description="Registered workforce"
        />

        <StatCard
          label="Departments"
          value={departments.length - 1}
          description="Active departments"
        />

        <StatCard
          label="Visible Results"
          value={filteredEmployees.length}
          description="Current filtered view"
        />

      </div>

      {/* Search / Filters */}
      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-4 mb-6">

        <div className="flex flex-col lg:flex-row gap-3">

          <div className="relative flex-1">

            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">
              ⌕
            </span>

            <input
              type="text"
              placeholder="Search by ID, name, department or designation..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full border border-slate-200 rounded-xl pl-10 pr-4 py-3 outline-none transition focus:border-slate-400 focus:ring-4 focus:ring-slate-100"
            />

          </div>

          <select
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
            className="border border-slate-200 rounded-xl px-4 py-3 bg-white outline-none focus:border-slate-400 lg:w-56"
          >
            {departments.map((item) => (
              <option key={item} value={item}>
                {item === "All"
                  ? "All Departments"
                  : item}
              </option>
            ))}
          </select>

          {canManageEmployees && (
            <button
              onClick={openAddModal}
              className="bg-slate-900 hover:bg-slate-800 text-white rounded-xl px-6 py-3 font-semibold transition shadow-sm whitespace-nowrap"
            >
              + Add Employee
            </button>
          )}

        </div>

        <div className="flex items-center justify-between mt-3 px-1">

          <p className="text-xs text-slate-400">
            Showing {filteredEmployees.length} of{" "}
            {employees.length} employees
          </p>

          {(search || department !== "All") && (
            <button
              onClick={() => {
                setSearch("");
                setDepartment("All");
              }}
              className="text-xs text-blue-600 hover:underline"
            >
              Clear filters
            </button>
          )}

        </div>

      </div>

      {/* Employee Directory */}
      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">

        <div className="px-5 py-4 border-b border-slate-200 flex items-center justify-between">

          <div>
            <h2 className="font-semibold text-slate-900">
              Employee Directory
            </h2>

            <p className="text-xs text-slate-500 mt-1">
              Employee identity and organizational information
            </p>
          </div>

          <span className="text-xs font-medium bg-slate-100 text-slate-600 rounded-full px-3 py-1">
            {filteredEmployees.length} records
          </span>

        </div>

        <div className="overflow-x-auto">

          <table className="w-full border-collapse">

            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-left">

                <th className="px-5 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Employee
                </th>

                <th className="px-5 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Department
                </th>

                <th className="px-5 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Designation
                </th>

                <th className="px-5 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Manager
                </th>

                <th className="px-5 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500 text-right">
                  Actions
                </th>

              </tr>
            </thead>

            <tbody>

              {filteredEmployees.map((emp) => (
                <tr
                  key={emp.id ?? emp.employee_id}
                  className="border-b border-slate-100 last:border-0 hover:bg-slate-50/80 transition"
                >

                  {/* Employee */}
                  <td className="px-5 py-4">

                    <div className="flex items-center gap-3">

                      <div className="w-10 h-10 rounded-xl bg-slate-100 text-slate-700 flex items-center justify-center font-semibold">
                        {getInitials(emp.name)}
                      </div>

                      <div>
                        <p className="font-semibold text-slate-900">
                          {emp.name}
                        </p>

                        <p className="text-xs text-slate-500 mt-0.5">
                          {emp.employee_id}
                        </p>
                      </div>

                    </div>

                  </td>

                  {/* Department */}
                  <td className="px-5 py-4">

                    <span className="inline-flex items-center rounded-full bg-blue-50 text-blue-700 px-3 py-1 text-xs font-medium">
                      {emp.department}
                    </span>

                  </td>

                  {/* Designation */}
                  <td className="px-5 py-4">

                    <p className="text-sm text-slate-700">
                      {emp.designation}
                    </p>

                  </td>

                  {/* Manager */}
                  <td className="px-5 py-4">

                    <span className="text-sm text-slate-600">
                      {emp.manager_id ?? "No manager"}
                    </span>

                  </td>

                  {/* Actions */}
                  <td className="px-5 py-4">

                    <div className="flex justify-end gap-2">

                      <button
                        onClick={() => viewEmployee(emp)}
                        className="border border-slate-200 bg-white text-slate-700 rounded-lg px-3 py-2 text-sm font-medium hover:bg-slate-50 hover:border-slate-300 transition"
                      >
                        View
                      </button>

                      {canManageEmployees && (
                        <button
                          onClick={() => openEditModal(emp)}
                          className="bg-slate-900 text-white rounded-lg px-3 py-2 text-sm font-medium hover:bg-slate-800 transition"
                        >
                          Edit
                        </button>
                      )}

                    </div>

                  </td>

                </tr>
              ))}

              {filteredEmployees.length === 0 && (
                <tr>
                  <td
                    colSpan="5"
                    className="px-5 py-16 text-center"
                  >

                    <div className="text-4xl mb-3">
                      🔍
                    </div>

                    <p className="font-medium text-slate-700">
                      No employees found
                    </p>

                    <p className="text-sm text-slate-500 mt-1">
                      Try changing your search or department filter.
                    </p>

                  </td>
                </tr>
              )}

            </tbody>

          </table>

        </div>

      </div>

      {/* View Employee Modal */}
      {selectedEmployee && !showEditModal && (
        <div className="fixed inset-0 bg-slate-950/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">

          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-xl max-h-[90vh] overflow-y-auto">

            {/* Modal Header */}
            <div className="p-6 border-b border-slate-200 flex justify-between items-start">

              <div className="flex items-center gap-4">

                <div className="w-12 h-12 rounded-xl bg-slate-900 text-white flex items-center justify-center font-semibold text-lg">
                  {getInitials(selectedEmployee.name)}
                </div>

                <div>

                  <h2 className="text-xl font-semibold text-slate-900">
                    Employee Profile
                  </h2>

                  <p className="text-sm text-slate-500 mt-1">
                    {selectedEmployee.employee_id}
                  </p>

                </div>

              </div>

              <button
                type="button"
                onClick={closeViewModal}
                className="w-9 h-9 rounded-lg text-slate-400 hover:text-slate-900 hover:bg-slate-100 text-xl"
              >
                ×
              </button>

            </div>

            {/* Employee Information */}
            <div className="p-6">

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">

                <Info
                  label="Name"
                  value={selectedEmployee.name}
                />

                <Info
                  label="Employee ID"
                  value={selectedEmployee.employee_id}
                />

                <Info
                  label="Department"
                  value={selectedEmployee.department}
                />

                <Info
                  label="Designation"
                  value={selectedEmployee.designation}
                />

                <Info
                  label="Manager ID"
                  value={
                    selectedEmployee.manager_id ??
                    "No manager"
                  }
                />

                <Info
                  label="Device Info"
                  value={
                    selectedEmployee.device_info ||
                    "Not provided"
                  }
                />

              </div>

              {/* Access Privileges */}
              <div className="mt-5">

                <Info
                  label="Access Privileges"
                  value={
                    selectedEmployee.access_privileges ||
                    "Not provided"
                  }
                />

              </div>

              {/* Direct Reports */}
              <div className="mt-6 pt-5 border-t border-slate-200">

                <div className="flex items-center justify-between mb-3">

                  <h3 className="font-semibold text-slate-900">
                    Direct Reports
                  </h3>

                  <span className="text-xs bg-slate-100 text-slate-600 rounded-full px-3 py-1">
                    {directReports.length}
                  </span>

                </div>

                {reportsLoading ? (
                  <div className="py-5 text-center">

                    <div className="w-7 h-7 border-3 border-slate-200 border-t-slate-800 rounded-full animate-spin mx-auto mb-3" />

                    <p className="text-sm text-slate-500">
                      Loading direct reports...
                    </p>

                  </div>
                ) : directReports.length === 0 ? (
                  <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50 p-5 text-center">

                    <p className="text-sm text-slate-500">
                      No direct reports.
                    </p>

                  </div>
                ) : (
                  <div className="space-y-2">

                    {directReports.map((report) => (
                      <div
                        key={
                          report.id ??
                          report.employee_id
                        }
                        className="border border-slate-200 rounded-xl p-3 flex items-center gap-3"
                      >

                        <div className="w-9 h-9 rounded-lg bg-slate-100 flex items-center justify-center text-xs font-semibold text-slate-700">
                          {getInitials(report.name)}
                        </div>

                        <div>

                          <p className="font-medium text-sm text-slate-900">
                            {report.name}
                          </p>

                          <p className="text-xs text-slate-500 mt-0.5">
                            {report.employee_id} •{" "}
                            {report.designation}
                          </p>

                        </div>

                      </div>
                    ))}

                  </div>
                )}

              </div>

              {/* Edit Profile */}
              {canManageEmployees && (
                <button
                  onClick={() =>
                    openEditModal(selectedEmployee)
                  }
                  className="w-full mt-6 bg-slate-900 hover:bg-slate-800 text-white rounded-xl py-3 font-semibold transition"
                >
                  Edit Profile
                </button>
              )}

            </div>

          </div>

        </div>
      )}

      {/* Add Employee Modal */}
      {showAddModal && (
        <EmployeeForm
          title="Add Employee"
          form={form}
          updateForm={updateForm}
          loading={formLoading}
          onSubmit={addEmployee}
          onClose={closeAddModal}
        />
      )}

      {/* Edit Employee Modal */}
      {showEditModal && selectedEmployee && (
        <EmployeeForm
          title="Edit Employee"
          form={form}
          updateForm={updateForm}
          loading={formLoading}
          onSubmit={updateEmployee}
          onClose={closeEditModal}
          editing
        />
      )}

    </div>
  );
}

/* ---------------------------------------------
   Statistics Card
--------------------------------------------- */

function StatCard({
  label,
  value,
  description,
}) {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">

      <div className="flex items-start justify-between">

        <div>

          <p className="text-sm text-slate-500">
            {label}
          </p>

          <p className="text-3xl font-semibold text-slate-900 mt-2">
            {value}
          </p>

          <p className="text-xs text-slate-400 mt-1">
            {description}
          </p>

        </div>

        <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-slate-600">
          ◉
        </div>

      </div>

    </div>
  );
}

/* ---------------------------------------------
   Information Display
--------------------------------------------- */

function Info({ label, value }) {
  return (
    <div className="rounded-xl bg-slate-50 border border-slate-100 p-4">

      <p className="text-xs uppercase tracking-wide text-slate-400">
        {label}
      </p>

      <p className="text-sm font-medium text-slate-900 mt-1 break-words">
        {value}
      </p>

    </div>
  );
}

/* ---------------------------------------------
   Employee Add/Edit Form
--------------------------------------------- */

function EmployeeForm({
  title,
  form,
  updateForm,
  loading,
  onSubmit,
  onClose,
  editing = false,
}) {
  return (
    <div className="fixed inset-0 bg-slate-950/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">

      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-xl max-h-[90vh] overflow-y-auto">

        {/* Modal Header */}
        <div className="p-6 border-b border-slate-200 flex justify-between items-start">

          <div>

            <div className="flex items-center gap-2 mb-2">

              <span className="w-2 h-2 rounded-full bg-green-500" />

              <span className="text-xs uppercase tracking-widest text-slate-400 font-semibold">
                Employee Management
              </span>

            </div>

            <h2 className="text-xl font-semibold text-slate-900">
              {title}
            </h2>

            <p className="text-sm text-slate-500 mt-1">
              {editing
                ? "Update employee profile information."
                : "Create a new employee profile."}
            </p>

          </div>

          <button
            type="button"
            onClick={onClose}
            className="w-9 h-9 rounded-lg text-slate-400 hover:text-slate-900 hover:bg-slate-100 text-xl"
          >
            ×
          </button>

        </div>

        {/* Form */}
        <form
          onSubmit={onSubmit}
          className="p-6 space-y-4"
        >

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">

            <Field
              label="Employee ID"
              value={form.employee_id}
              disabled={editing}
              onChange={(value) =>
                updateForm(
                  "employee_id",
                  value
                )
              }
              placeholder="EMP1007"
            />

            <Field
              label="Name"
              value={form.name}
              onChange={(value) =>
                updateForm(
                  "name",
                  value
                )
              }
              placeholder="Employee name"
            />

            <Field
              label="Department"
              value={form.department}
              onChange={(value) =>
                updateForm(
                  "department",
                  value
                )
              }
              placeholder="Finance"
            />

            <Field
              label="Designation"
              value={form.designation}
              onChange={(value) =>
                updateForm(
                  "designation",
                  value
                )
              }
              placeholder="Financial Analyst"
            />

            <Field
              label="Manager ID"
              value={form.manager_id}
              onChange={(value) =>
                updateForm(
                  "manager_id",
                  value
                )
              }
              placeholder="1"
              type="number"
            />

            <Field
              label="Device Info"
              value={form.device_info}
              onChange={(value) =>
                updateForm(
                  "device_info",
                  value
                )
              }
              placeholder="Laptop / workstation"
            />

          </div>

          <Field
            label="Access Privileges"
            value={form.access_privileges}
            onChange={(value) =>
              updateForm(
                "access_privileges",
                value
              )
            }
            placeholder="Standard user access"
          />

          {/* Buttons */}
          <div className="flex gap-3 pt-3">

            <button
              type="button"
              onClick={onClose}
              className="flex-1 border border-slate-200 text-slate-700 rounded-xl py-3 font-medium hover:bg-slate-50 transition"
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-slate-900 hover:bg-slate-800 text-white rounded-xl py-3 font-semibold disabled:opacity-50 transition"
            >
              {loading
                ? "Saving..."
                : editing
                ? "Save Changes"
                : "Add Employee"}
            </button>

          </div>

        </form>

      </div>

    </div>
  );
}

/* ---------------------------------------------
   Reusable Input Field
--------------------------------------------- */

function Field({
  label,
  value,
  onChange,
  placeholder,
  type = "text",
  disabled = false,
}) {
  const optionalFields = [
    "Manager ID",
    "Device Info",
    "Access Privileges",
  ];

  return (
    <div>

      <label className="block text-sm font-medium text-slate-700 mb-1.5">
        {label}
      </label>

      <input
        type={type}
        value={value}
        disabled={disabled}
        placeholder={placeholder}
        onChange={(e) =>
          onChange(e.target.value)
        }
        required={
          !optionalFields.includes(label)
        }
        className="border border-slate-200 rounded-xl px-3.5 py-3 w-full outline-none transition focus:border-slate-400 focus:ring-4 focus:ring-slate-100 disabled:bg-slate-100 disabled:text-slate-500"
      />

    </div>
  );
}

/* ---------------------------------------------
   Employee Initials
--------------------------------------------- */

function getInitials(name) {
  if (!name) return "?";

  const parts = name
    .trim()
    .split(/\s+/);

  if (parts.length === 1) {
    return parts[0]
      .slice(0, 2)
      .toUpperCase();
  }

  return (
    parts[0][0] +
    parts[parts.length - 1][0]
  ).toUpperCase();
}
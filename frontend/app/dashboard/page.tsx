"use client";

import { useEffect, useState } from "react";

interface User {
  username: string;
  role: string;
}

interface Employee {
  id?: number;
  employee_id: string;
  name: string;
  department: string;
  designation: string;
}

interface ActivityLog {
  _id: string;
  employee_id: string;
  activity_type: string;
  resource?: string;
  timestamp?: string;
  ip_address?: string;
  device?: string;
  ingested_by?: string;
  ingested_at?: string;
}

export default function Dashboard() {
  const [user, setUser] = useState<User | null>(null);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [activities, setActivities] = useState<ActivityLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      window.location.href = "/";
      return;
    }

    const fetchData = async () => {
      try {
        const headers = {
          Authorization: `Bearer ${token}`,
        };

        const [
          meResponse,
          employeesResponse,
          logsResponse,
        ] = await Promise.all([
          fetch("http://127.0.0.1:8000/me", {
            headers,
          }),

          fetch("http://127.0.0.1:8000/employees", {
            headers,
          }),

          fetch("http://127.0.0.1:8000/logs", {
            headers,
          }),
        ]);

        if (!meResponse.ok) {
          localStorage.removeItem("access_token");
          localStorage.removeItem("username");
          localStorage.removeItem("role");

          window.location.href = "/";
          return;
        }

        if (!employeesResponse.ok) {
          throw new Error("Unable to load employees");
        }

        if (!logsResponse.ok) {
          throw new Error("Unable to load activity logs");
        }

        const meData = await meResponse.json();
        const employeeData = await employeesResponse.json();
        const logsData = await logsResponse.json();

        setUser(meData);
        setEmployees(employeeData);
        setActivities(logsData);
      } catch (error) {
        console.error("Dashboard error:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    localStorage.removeItem("role");

    window.location.href = "/";
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-[#020617] text-white flex items-center justify-center">
        <p className="text-xl text-slate-400">
          Loading security dashboard...
        </p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#020617] text-white p-8">

      {/* ================================================= */}
      {/* HEADER */}
      {/* ================================================= */}

      <div className="flex items-center justify-between mb-10">

        <div>
          <h1 className="text-4xl font-bold">
            ITBIS Dashboard
          </h1>

          <p className="text-slate-400 mt-2">
            Insider Threat & Behavioral Intelligence System
          </p>
        </div>

        <div className="flex items-center gap-6">

          {user && (
            <div className="text-right">
              <p className="font-semibold">
                {user.username}
              </p>

              <p className="text-sm text-blue-400">
                {user.role}
              </p>
            </div>
          )}

          <button
            onClick={logout}
            className="px-5 py-2 rounded-lg bg-red-600 hover:bg-red-700"
          >
            Logout
          </button>

        </div>
      </div>


      {/* ================================================= */}
      {/* STATISTICS */}
      {/* ================================================= */}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">

          <p className="text-slate-400">
            Employees
          </p>

          <p className="text-4xl font-bold mt-2">
            {employees.length}
          </p>

        </div>


        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">

          <p className="text-slate-400">
            Activity Logs
          </p>

          <p className="text-4xl font-bold mt-2">
            {activities.length}
          </p>

        </div>


        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">

          <p className="text-slate-400">
            Threat Status
          </p>

          <p className="text-4xl font-bold text-green-400 mt-2">
            Secure
          </p>

        </div>

      </div>


      {/* ================================================= */}
      {/* EMPLOYEES */}
      {/* ================================================= */}

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 mb-8">

        <h2 className="text-2xl font-semibold mb-5">
          Employees
        </h2>

        {employees.length === 0 ? (

          <p className="text-slate-400">
            No employees registered yet.
          </p>

        ) : (

          <div className="overflow-x-auto">

            <table className="w-full text-left">

              <thead>

                <tr className="border-b border-slate-700">

                  <th className="p-3">
                    Employee ID
                  </th>

                  <th className="p-3">
                    Name
                  </th>

                  <th className="p-3">
                    Department
                  </th>

                  <th className="p-3">
                    Designation
                  </th>

                </tr>

              </thead>


              <tbody>

                {employees.map((employee) => (

                  <tr
                    key={
                      employee.id ||
                      employee.employee_id
                    }
                    className="border-b border-slate-800"
                  >

                    <td className="p-3">
                      {employee.employee_id}
                    </td>

                    <td className="p-3">
                      {employee.name}
                    </td>

                    <td className="p-3">
                      {employee.department}
                    </td>

                    <td className="p-3">
                      {employee.designation}
                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>

        )}

      </div>


      {/* ================================================= */}
      {/* MONGODB ACTIVITY LOGS */}
      {/* ================================================= */}

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">

        <div className="flex items-center justify-between mb-5">

          <div>

            <h2 className="text-2xl font-semibold">
              Recent Activity Logs
            </h2>

            <p className="text-sm text-slate-400 mt-1">
              Activity data retrieved from MongoDB
            </p>

          </div>

          <div className="text-sm text-blue-400">
            MongoDB
          </div>

        </div>


        {activities.length === 0 ? (

          <p className="text-slate-400">
            No activity logs recorded yet.
          </p>

        ) : (

          <div className="space-y-3">

            {activities
              .slice(0, 10)
              .map((activity) => (

                <div
                  key={activity._id}
                  className="bg-slate-800 rounded-lg p-4"
                >

                  <div className="flex flex-col md:flex-row md:justify-between gap-4">

                    {/* Activity information */}

                    <div>

                      <p className="font-semibold text-lg">
                        {activity.activity_type}
                      </p>

                      <p className="text-sm text-slate-400 mt-1">
                        Employee:{" "}
                        {activity.employee_id}
                      </p>

                      {activity.resource && (
                        <p className="text-sm text-slate-400">
                          Resource:{" "}
                          {activity.resource}
                        </p>
                      )}

                    </div>


                    {/* Network/device information */}

                    <div className="text-sm text-slate-400 md:text-right">

                      {activity.ip_address && (
                        <p>
                          IP:{" "}
                          {activity.ip_address}
                        </p>
                      )}

                      {activity.device && (
                        <p>
                          Device:{" "}
                          {activity.device}
                        </p>
                      )}

                      {activity.timestamp && (
                        <p>
                          Event:{" "}
                          {activity.timestamp}
                        </p>
                      )}

                    </div>

                  </div>


                  {/* Ingestion information */}

                  <div className="mt-3 pt-3 border-t border-slate-700 text-xs text-slate-500">

                    Ingested by:{" "}
                    {activity.ingested_by || "system"}

                  </div>

                </div>

              ))}

          </div>

        )}

      </div>

    </main>
  );
}
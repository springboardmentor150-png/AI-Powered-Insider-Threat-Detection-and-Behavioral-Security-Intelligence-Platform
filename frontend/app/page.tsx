"use client";

import { useEffect, useState } from "react";

interface Employee {
  id: number;
  name: string;
  department: string;
  role: string;
}

export default function Home() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      setLoading(true);
      setError("");

      // Get JWT token saved during login
      const token = localStorage.getItem("access_token");

      if (!token) {
        setError("You are not logged in. Please login first.");
        setLoading(false);
        return;
      }

      const response = await fetch("http://127.0.0.1:8000/employees/", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.status === 401) {
        setError("Authentication failed. Please login again.");
        setLoading(false);
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to fetch employees");
      }

      const data = await response.json();

      setEmployees(data);
    } catch (error) {
      console.error(error);
      setError("Unable to connect to the backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-100 p-8">
      <div className="mx-auto max-w-6xl">

        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Employee Dashboard
            </h1>

            <p className="mt-2 text-gray-600">
              Employees registered in the system
            </p>
          </div>

          <button
            onClick={fetchEmployees}
            className="rounded-lg bg-blue-600 px-5 py-2.5 font-medium text-white hover:bg-blue-700"
          >
            Refresh
          </button>
        </div>

        {/* Loading */}
        {loading && (
          <div className="rounded-lg bg-white p-8 text-center shadow">
            <p className="text-gray-600">
              Loading employees...
            </p>
          </div>
        )}

        {/* Error */}
        {!loading && error && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-6">
            <p className="font-medium text-red-700">
              {error}
            </p>
          </div>
        )}

        {/* Employee Count */}
        {!loading && !error && (
          <>
            <div className="mb-6 rounded-lg bg-white p-6 shadow">
              <p className="text-sm text-gray-500">
                Total Employees
              </p>

              <p className="mt-1 text-3xl font-bold text-gray-900">
                {employees.length}
              </p>
            </div>

            {/* Employee Table */}
            <div className="overflow-hidden rounded-lg bg-white shadow">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                        ID
                      </th>

                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                        Name
                      </th>

                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                        Department
                      </th>

                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                        Role
                      </th>
                    </tr>
                  </thead>

                  <tbody className="divide-y divide-gray-200">
                    {employees.map((employee) => (
                      <tr
                        key={employee.id}
                        className="hover:bg-gray-50"
                      >
                        <td className="px-6 py-4 text-sm text-gray-700">
                          {employee.id}
                        </td>

                        <td className="px-6 py-4 font-medium text-gray-900">
                          {employee.name}
                        </td>

                        <td className="px-6 py-4 text-sm text-gray-700">
                          {employee.department}
                        </td>

                        <td className="px-6 py-4 text-sm text-gray-700">
                          {employee.role}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* No employees */}
              {employees.length === 0 && (
                <div className="p-8 text-center">
                  <p className="text-gray-500">
                    No employees found.
                  </p>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </main>
  );
}
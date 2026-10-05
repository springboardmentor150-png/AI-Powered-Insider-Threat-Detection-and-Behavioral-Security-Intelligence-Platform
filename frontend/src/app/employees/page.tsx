"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { employeeAPI, aiAPI, logAPI, uebaAPI, investigationAPI } from "@/lib/api";
import { ThreatScoreBadge } from "@/components/ThreatScoreBadge";
import {
  Users,
  Search,
  UserPlus,
  Shield,
  Activity,
  Cpu,
  Clock,
  HardDrive,
  Laptop,
  CheckCircle,
  X,
  AlertCircle,
  TrendingUp,
  Sparkles,
  BarChart,
  FolderPlus,
  ArrowUpRight,
  GitFork
} from "lucide-react";

export default function EmployeesPage() {
  const { user } = useAuth();
  const [employees, setEmployees] = useState<any[]>([]);
  const [selectedEmp, setSelectedEmp] = useState<any | null>(null);
  const [selectedBaseline, setSelectedBaseline] = useState<any | null>(null);
  const [peerComparison, setPeerComparison] = useState<any | null>(null);
  const [riskTrend, setRiskTrend] = useState<any[]>([]);
  const [recentLogs, setRecentLogs] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [deptFilter, setDeptFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [incidentCreating, setIncidentCreating] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any | null>(null);

  // Onboarding Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newEmp, setNewEmp] = useState({
    employee_id: "",
    name: "",
    department: "Engineering",
    designation: "",
    device_info: "",
    access_privileges: "",
  });

  const fetchEmployees = async () => {
    try {
      setLoading(true);
      const res = await employeeAPI.getAll();
      setEmployees(res.data || []);
      if (res.data && res.data.length > 0 && !selectedEmp) {
        selectEmployee(res.data[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const selectEmployee = async (emp: any) => {
    setSelectedEmp(emp);
    setAnalysisResult(null);
    try {
      const [baselineRes, logsRes, peerRes, trendRes] = await Promise.all([
        employeeAPI.getBaseline(emp.employee_id),
        logAPI.getAll({ employee_id: emp.employee_id, limit: 10 }),
        uebaAPI.getPeerComparison(emp.employee_id),
        uebaAPI.getRiskTrend(emp.employee_id, 30),
      ]);
      setSelectedBaseline(baselineRes.data);
      setRecentLogs(logsRes.data || []);
      setPeerComparison(peerRes.data);
      setRiskTrend(trendRes.data || []);
    } catch (e) {
      console.error("Error loading baseline/UEBA:", e);
    }
  };

  useEffect(() => {
    fetchEmployees();
  }, []);

  const handleAnalyzeSelected = async () => {
    if (!selectedEmp) return;
    setAnalyzing(true);
    try {
      const res = await aiAPI.analyzeEmployee(selectedEmp.employee_id);
      setAnalysisResult(res.data);
      setSelectedEmp((prev: any) => ({ ...prev, baseline_risk_score: res.data.overall_risk_score }));
      fetchEmployees();
    } catch (e) {
      console.error("AI Analysis error:", e);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleCreateIncidentFromRisk = async () => {
    if (!selectedEmp) return;
    setIncidentCreating(true);
    try {
      const res = await investigationAPI.createFromRisk(selectedEmp.employee_id);
      alert(`Incident ${res.data.incident_code || res.data.id} successfully created for ${selectedEmp.name}!`);
    } catch (err: any) {
      alert(err.response?.data?.detail || "Could not create incident. Risk score may be too low.");
    } finally {
      setIncidentCreating(false);
    }
  };

  const handleCreateEmployee = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await employeeAPI.create(newEmp);
      setIsModalOpen(false);
      setNewEmp({
        employee_id: "",
        name: "",
        department: "Engineering",
        designation: "",
        device_info: "",
        access_privileges: "",
      });
      fetchEmployees();
    } catch (err) {
      alert("Failed to create employee. Check ID uniqueness or permissions.");
    }
  };

  const canOnboard = user?.role === "admin" || user?.role === "security_manager";

  const filteredEmployees = employees.filter((emp) => {
    const matchesSearch =
      emp.name.toLowerCase().includes(search.toLowerCase()) ||
      emp.employee_id.toLowerCase().includes(search.toLowerCase()) ||
      emp.designation.toLowerCase().includes(search.toLowerCase());
    const matchesDept = deptFilter === "ALL" || emp.department.toUpperCase() === deptFilter.toUpperCase();
    return matchesSearch && matchesDept;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800 uppercase">
              Milestone 3 UEBA Module
            </span>
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2 mt-1">
            <Users className="w-5 h-5 text-cyan-400" />
            <span>Employee Behavioral Directory & UEBA Analytics</span>
          </h1>
          <p className="text-xs text-slate-400">
            Weighted risk scoring, peer group comparison, 30-day anomaly trends & incident creation.
          </p>
        </div>

        {canOnboard && (
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold shadow-lg shadow-cyan-600/20 transition"
          >
            <UserPlus className="w-4 h-4" />
            <span>Onboard Monitored Employee</span>
          </button>
        )}
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center gap-3 p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-2.5" />
          <input
            type="text"
            placeholder="Search by name, EMP ID, or designation..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
          />
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <span className="text-xs text-slate-400 font-mono">Dept:</span>
          <select
            value={deptFilter}
            onChange={(e) => setDeptFilter(e.target.value)}
            className="px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Departments</option>
            <option value="ENGINEERING">Engineering</option>
            <option value="FINANCE">Finance</option>
            <option value="CLOUD OPS">Cloud Ops</option>
            <option value="HUMAN RESOURCES">Human Resources</option>
            <option value="IT OPS">IT Ops</option>
            <option value="LEGAL">Legal</option>
          </select>
        </div>
      </div>

      {/* Two Column Layout: List on Left, Detail & Baseline on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left List */}
        <div className="lg:col-span-5 space-y-3">
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider font-mono">
              Monitored Workforce ({filteredEmployees.length})
            </h3>
            <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
              {filteredEmployees.map((emp) => {
                const isSelected = selectedEmp?.employee_id === emp.employee_id;
                return (
                  <div
                    key={emp.employee_id}
                    onClick={() => selectEmployee(emp)}
                    className={`p-3.5 rounded-xl cursor-pointer transition border ${
                      isSelected
                        ? "bg-cyan-950/40 border-cyan-500/50 shadow-md shadow-cyan-500/10"
                        : "bg-slate-950/50 border-slate-800/80 hover:border-slate-700"
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="text-xs font-bold text-slate-100">{emp.name}</h4>
                        <p className="text-[11px] text-slate-400">{emp.designation}</p>
                      </div>
                      <ThreatScoreBadge score={emp.baseline_risk_score || 15} size="sm" />
                    </div>
                    <div className="mt-2 flex items-center justify-between text-[10px] font-mono text-slate-400 pt-2 border-t border-slate-800/60">
                      <span>ID: {emp.employee_id}</span>
                      <span className="text-slate-300">{emp.department}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Detail Pane */}
        <div className="lg:col-span-7 space-y-6">
          {selectedEmp ? (
            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-6">
              {/* Profile Card Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
                <div>
                  <div className="flex items-center space-x-3">
                    <h2 className="text-lg font-bold text-white">{selectedEmp.name}</h2>
                    <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-cyan-300 font-mono border border-slate-700">
                      {selectedEmp.employee_id}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    {selectedEmp.designation} &bull; {selectedEmp.department}
                  </p>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={handleCreateIncidentFromRisk}
                    disabled={incidentCreating}
                    title="Spawn incident if risk >= 50"
                    className="flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-purple-900/40 hover:bg-purple-800/50 text-purple-300 border border-purple-700/60 text-xs font-semibold transition"
                  >
                    <FolderPlus className="w-3.5 h-3.5" />
                    <span>Create Incident</span>
                  </button>
                  <button
                    onClick={handleAnalyzeSelected}
                    disabled={analyzing}
                    className="flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-semibold shadow-lg shadow-cyan-600/20 transition"
                  >
                    <Sparkles className={`w-3.5 h-3.5 ${analyzing ? "animate-spin" : ""}`} />
                    <span>{analyzing ? "Evaluating..." : "Run AI Check"}</span>
                  </button>
                  <ThreatScoreBadge score={selectedEmp.baseline_risk_score || 15} size="lg" />
                </div>
              </div>

              {/* Milestone 3: UEBA Peer Group Comparison Card */}
              {peerComparison && (
                <div className="p-4 rounded-2xl bg-slate-950/70 border border-purple-500/30 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-purple-300 flex items-center gap-1.5 font-mono">
                      <GitFork className="w-4 h-4 text-purple-400" />
                      Part 2: UEBA Peer Group Comparison ({selectedEmp.department})
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      Peers Evaluated: {peerComparison.peer_count}
                    </span>
                  </div>

                  {peerComparison.peer_count > 0 ? (
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
                      <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                        <div className="text-[10px] text-slate-400 font-mono">Employee Score</div>
                        <div className="text-lg font-bold text-white font-mono">{peerComparison.employee_score}</div>
                      </div>
                      <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                        <div className="text-[10px] text-slate-400 font-mono">Department Peer Avg</div>
                        <div className="text-lg font-bold text-cyan-400 font-mono">{peerComparison.department_avg_score}</div>
                      </div>
                      <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                        <div className="text-[10px] text-slate-400 font-mono">Deviation From Peers</div>
                        <div className={`text-lg font-bold font-mono ${peerComparison.deviation_from_peers > 0 ? "text-rose-400" : "text-emerald-400"}`}>
                          {peerComparison.deviation_from_peers > 0 ? `+${peerComparison.deviation_from_peers}` : peerComparison.deviation_from_peers}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <p className="text-xs text-slate-400 italic bg-slate-900/50 p-3 rounded-xl border border-slate-800">
                      {peerComparison.note || "No peers in this department for statistical baseline comparison."}
                    </p>
                  )}
                </div>
              )}

              {/* Milestone 3: 30-Day Behavioral Trend Histogram */}
              {riskTrend.length > 0 && (
                <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-300 flex items-center gap-1.5 font-mono">
                      <TrendingUp className="w-4 h-4 text-cyan-400" />
                      30-Day Anomaly Detection Trend
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">{riskTrend.length} Spike Dates</span>
                  </div>
                  <div className="flex items-end gap-2 h-20 pt-2 overflow-x-auto">
                    {riskTrend.map((item, idx) => (
                      <div key={idx} className="flex flex-col items-center flex-1 min-w-[36px]">
                        <div
                          className="w-full rounded-t bg-cyan-500/80 hover:bg-cyan-400 transition"
                          style={{ height: `${Math.min(item.anomaly_count * 20, 60)}px` }}
                          title={`${item.date}: ${item.anomaly_count} anomalies`}
                        />
                        <span className="text-[9px] font-mono text-slate-500 mt-1 truncate w-full text-center">
                          {item.date.slice(5)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Behavioral Baseline Matrix */}
              <div className="space-y-3">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider font-mono">
                  Learned Behavioral Baseline
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                    <div className="flex items-center space-x-2 text-slate-400 text-xs">
                      <Clock className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Nominal Hours</span>
                    </div>
                    <p className="text-xs font-bold text-slate-100 font-mono">
                      {selectedBaseline?.typical_work_hours || "09:00 - 18:00 UTC"}
                    </p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                    <div className="flex items-center space-x-2 text-slate-400 text-xs">
                      <HardDrive className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Avg Daily Egress</span>
                    </div>
                    <p className="text-xs font-bold text-slate-100 font-mono">
                      {selectedBaseline?.avg_daily_download_mb || 20.0} MB / day
                    </p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                    <div className="flex items-center space-x-2 text-slate-400 text-xs">
                      <Laptop className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Registered Host</span>
                    </div>
                    <p className="text-xs font-bold text-slate-100 truncate font-mono">
                      {selectedEmp.device_info || "Standard Workstation"}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-12 text-center text-slate-400 bg-slate-900/40 rounded-2xl border border-slate-800">
              Select an employee identity from the directory to inspect behavioral profiles.
            </div>
          )}
        </div>
      </div>

      {/* Onboarding Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fade-in">
          <div className="bg-slate-900 border border-slate-700 w-full max-w-lg rounded-2xl p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-sm font-bold text-white">Onboard Monitored Employee</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateEmployee} className="space-y-3 text-xs">
              <div>
                <label className="text-slate-300 font-medium">Employee ID</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. EMP1009"
                  value={newEmp.employee_id}
                  onChange={(e) => setNewEmp({ ...newEmp, employee_id: e.target.value })}
                  className="w-full mt-1 p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-mono"
                />
              </div>

              <div>
                <label className="text-slate-300 font-medium">Full Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Robert McCall"
                  value={newEmp.name}
                  onChange={(e) => setNewEmp({ ...newEmp, name: e.target.value })}
                  className="w-full mt-1 p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-100"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-300 font-medium">Department</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Engineering"
                    value={newEmp.department}
                    onChange={(e) => setNewEmp({ ...newEmp, department: e.target.value })}
                    className="w-full mt-1 p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-100"
                  />
                </div>
                <div>
                  <label className="text-slate-300 font-medium">Designation</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Security Specialist"
                    value={newEmp.designation}
                    onChange={(e) => setNewEmp({ ...newEmp, designation: e.target.value })}
                    className="w-full mt-1 p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-100"
                  />
                </div>
              </div>

              <div>
                <label className="text-slate-300 font-medium">Device Info / Hostname</label>
                <input
                  type="text"
                  placeholder="e.g. MacBook Pro - Host: r-mccall-mbp"
                  value={newEmp.device_info}
                  onChange={(e) => setNewEmp({ ...newEmp, device_info: e.target.value })}
                  className="w-full mt-1 p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-mono"
                />
              </div>

              <div>
                <label className="text-slate-300 font-medium">Access Privileges (Comma Separated)</label>
                <input
                  type="text"
                  placeholder="e.g. AWS_DEV, PROD_READ, JIRA_RW"
                  value={newEmp.access_privileges}
                  onChange={(e) => setNewEmp({ ...newEmp, access_privileges: e.target.value })}
                  className="w-full mt-1 p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-mono"
                />
              </div>

              <div className="pt-3 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold shadow"
                >
                  Create Identity
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
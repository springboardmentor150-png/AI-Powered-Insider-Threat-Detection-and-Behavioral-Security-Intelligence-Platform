"use client";

import React, { useEffect, useState } from "react";
import { employeeAPI, simulationAPI, aiAPI } from "@/lib/api";
import {
  PlaySquare,
  ShieldAlert,
  HardDrive,
  Database,
  Terminal,
  CheckCircle,
  Play,
  Cpu,
  Sparkles,
  Lock
} from "lucide-react";

export default function SimulationPage() {
  const [employees, setEmployees] = useState<any[]>([]);
  const [selectedEmpId, setSelectedEmpId] = useState("");
  const [runningScenario, setRunningScenario] = useState<string | null>(null);
  const [simulationResult, setSimulationResult] = useState<any | null>(null);
  const [autoAnalyze, setAutoAnalyze] = useState(true);

  useEffect(() => {
    employeeAPI.getAll().then((res) => {
      setEmployees(res.data || []);
      if (res.data && res.data.length > 0) {
        setSelectedEmpId(res.data[0].employee_id);
      }
    });
  }, []);

  const handleRunSimulation = async (scenario: string) => {
    setRunningScenario(scenario);
    setSimulationResult(null);
    try {
      const simRes = await simulationAPI.runScenario({
        scenario,
        employee_id: selectedEmpId,
      });
      setSimulationResult(simRes.data);

      if (autoAnalyze && selectedEmpId) {
        await aiAPI.analyzeEmployee(selectedEmpId);
      }
    } catch (e) {
      alert("Simulation failed.");
    } finally {
      setRunningScenario(null);
    }
  };

  const scenarios = [
    {
      id: "mass_exfiltration",
      title: "Mass Data Exfiltration & Physical USB Egress",
      badge: "CRITICAL VECTOR",
      badgeColor: "bg-rose-950 text-rose-300 border-rose-800",
      description:
        "Simulates an employee archiving 600MB+ confidential intellectual property at 02:15 AM, mounting an unauthorized USB flash drive, and sending encrypted data outwards.",
      icon: HardDrive,
    },
    {
      id: "compromised_admin",
      title: "Compromised Admin Identity via Tor Exit Node",
      badge: "ACCOUNT TAKEOVER",
      badgeColor: "bg-amber-950 text-amber-300 border-amber-800",
      description:
        "Simulates off-hours login from suspicious Tor proxy IP, executing 'sudo su - root' privilege escalation and disabling Linux auditd security daemons.",
      icon: Lock,
    },
    {
      id: "database_scraping",
      title: "Bulk Production Database Scraping",
      badge: "DATA THEFT",
      badgeColor: "bg-purple-950 text-purple-300 border-purple-800",
      description:
        "Simulates abnormal SQL query volume exceeding 18,500 customer records from high-security tables followed by a compressed SQL export download.",
      icon: Database,
    },
    {
      id: "normal",
      title: "Nominal Developer Workday (Benign Baseline)",
      badge: "CLEAN TELEMETRY",
      badgeColor: "bg-emerald-950 text-emerald-300 border-emerald-800",
      description:
        "Simulates standard business-hours SSO Okta authentication, normal git repository commits, and benign team collaboration messages.",
      icon: CheckCircle,
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <PlaySquare className="w-5 h-5 text-cyan-400" />
            <span>Insider Threat Scenario Simulation Lab</span>
          </h1>
          <p className="text-xs text-slate-400">
            Inject realistic threat attack vectors into the ingestion stream to demonstrate live detection and scoring.
          </p>
        </div>

        {/* Target Identity Selector */}
        <div className="flex items-center space-x-3 p-3 rounded-2xl bg-slate-900 border border-slate-800">
          <span className="text-xs font-mono text-slate-400">Target Identity:</span>
          <select
            value={selectedEmpId}
            onChange={(e) => setSelectedEmpId(e.target.value)}
            className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
          >
            {employees.map((emp) => (
              <option key={emp.employee_id} value={emp.employee_id}>
                {emp.name} ({emp.employee_id}) - {emp.department}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Scenario Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {scenarios.map((sc) => {
          const Icon = sc.icon;
          const isRunning = runningScenario === sc.id;
          return (
            <div
              key={sc.id}
              className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between space-y-4 hover:border-slate-700 transition"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded border font-bold ${sc.badgeColor}`}>
                    {sc.badge}
                  </span>
                  <Icon className="w-4 h-4 text-cyan-400" />
                </div>
                <h3 className="text-sm font-bold text-white">{sc.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed font-sans">{sc.description}</p>
              </div>

              <button
                onClick={() => handleRunSimulation(sc.id)}
                disabled={!!runningScenario}
                className="w-full flex items-center justify-center space-x-2 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-300 text-xs font-semibold border border-slate-700 shadow transition disabled:opacity-50"
              >
                <Play className={`w-3.5 h-3.5 fill-current ${isRunning ? "animate-spin" : ""}`} />
                <span>{isRunning ? "Streaming Events..." : "Execute Simulation Vector"}</span>
              </button>
            </div>
          );
        })}
      </div>

      {/* Live Simulation Output Terminal */}
      {simulationResult && (
        <div className="p-6 rounded-2xl bg-slate-950 border border-cyan-500/40 space-y-4 animate-fade-in font-mono">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-2 text-xs font-bold text-cyan-400">
              <Terminal className="w-4 h-4" />
              <span>Simulation Ingestion Telemetry Stream Output</span>
            </div>
            <span className="text-[11px] text-emerald-400">
              Generated {simulationResult.generated_events_count} Document Events
            </span>
          </div>

          <div className="space-y-2 text-xs">
            <p className="text-slate-400">
              Target: <span className="text-white">{simulationResult.target_employee.name}</span> ({simulationResult.target_employee.employee_id}) &bull; Scenario: <span className="text-cyan-300">{simulationResult.scenario}</span>
            </p>

            <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-2 max-h-48 overflow-y-auto">
              {simulationResult.events.map((ev: any, idx: number) => (
                <div key={idx} className="text-[11px] text-slate-300 flex items-start space-x-2">
                  <span className="text-cyan-500 font-bold">&gt;</span>
                  <span className="text-slate-400">[{ev.timestamp.split("T")[1]?.slice(0, 8) || "LIVE"}]</span>
                  <span className="text-purple-400 font-semibold">{ev.event_type}</span>
                  <span className="text-slate-300">{JSON.stringify(ev.details)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

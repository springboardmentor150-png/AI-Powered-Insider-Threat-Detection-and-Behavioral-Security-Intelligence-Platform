"use client";

import { useState, useEffect, useCallback, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  FileSearch,
  Shield,
  AlertTriangle,
  Clock,
  Laptop,
  Globe,
  HardDrive,
  Download,
  PlusCircle,
  MessageSquare,
  CheckCircle2,
  TrendingUp,
  ShieldAlert,
  Loader2,
  RefreshCw,
  ExternalLink,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import { api } from "@/lib/api";

interface InvestigationDossier {
  employee: {
    id: number;
    employee_id: string;
    name: string;
    department?: string;
    designation?: string;
    manager_name?: string;
    employment_type?: string;
    work_location?: string;
    joining_date?: string;
    years_of_experience?: number;
    education?: string;
    skills?: string;
    professional_summary?: string;
    device_info?: string;
    access_privileges?: string;
    risk_score: number;
    risk_level: string;
    status: string;
  };
  activity_profile: {
    typical_login_time: string;
    typical_logout_time: string;
    known_devices: string[];
    known_ips: string[];
    average_daily_events: number;
    most_common_event_type: string;
    total_downloads_mb: number;
    off_hours_percentage: number;
    total_events: number;
    suspicious_events: number;
  };
  active_alerts: any[];
  active_incidents: any[];
  risk_history: any[];
  notes: any[];
  timeline: {
    id: string;
    timestamp: string;
    event_type: string;
    source: string;
    title: string;
    description: string;
    severity: string;
    employee_id: string;
    risk_impact?: number;
    related_id?: string;
    metadata?: any;
  }[];
}

function InvestigationContent() {
  const searchParams = useSearchParams();
  const initialEmpId = searchParams.get("employee_id") || "FIN-2187";

  const [employees, setEmployees] = useState<any[]>([]);
  const [selectedEmpId, setSelectedEmpId] = useState<string>(initialEmpId);
  const [dossier, setDossier] = useState<InvestigationDossier | null>(null);
  const [loading, setLoading] = useState(true);

  // Add Note State
  const [newNote, setNewNote] = useState("");
  const [addingNote, setAddingNote] = useState(false);
  const [noteSuccess, setNoteSuccess] = useState(false);

  // Timeline expanded items
  const [expandedItems, setExpandedItems] = useState<Record<string, boolean>>({});

  // Fetch employee list for selector
  useEffect(() => {
    const fetchEmps = async () => {
      try {
        const res = await api.get("/employees?limit=50");
        setEmployees(res.data.items || []);
      } catch (err) {
        console.error("Error fetching employees:", err);
      }
    };
    fetchEmps();
  }, []);

  const fetchDossier = useCallback(async (empId: string) => {
    setLoading(true);
    try {
      const res = await api.get(`/investigations/${empId}`);
      setDossier(res.data);
    } catch (err) {
      console.error("Error fetching investigation dossier:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (selectedEmpId) {
      fetchDossier(selectedEmpId);
    }
  }, [selectedEmpId, fetchDossier]);

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNote.trim() || !dossier) return;
    setAddingNote(true);
    try {
      await api.post(`/investigations/${dossier.employee.employee_id}/notes`, {
        note_text: newNote.trim(),
      });
      setNewNote("");
      setNoteSuccess(true);
      setTimeout(() => setNoteSuccess(false), 3000);
      fetchDossier(dossier.employee.employee_id);
    } catch (err) {
      alert("Failed to add analyst investigation note.");
    } finally {
      setAddingNote(false);
    }
  };

  const handleExportSummary = () => {
    if (!dossier) return;
    const content = `=====================================================
ITBIS SECURITY INVESTIGATION SUMMARY
=====================================================
Subject: ${dossier.employee.name} (${dossier.employee.employee_id})
Department: ${dossier.employee.department} | Role: ${dossier.employee.designation}
Risk Score: ${dossier.employee.risk_score} / 100 (${dossier.employee.risk_level})
Status: ${dossier.employee.status}

PROFESSIONAL BACKGROUND:
Experience: ${dossier.employee.years_of_experience} years
Education: ${dossier.employee.education}
Skills: ${dossier.employee.skills}
Access Privileges: ${dossier.employee.access_privileges}

ACTIVITY PROFILE:
Normal Shift: ${dossier.activity_profile.typical_login_time} – ${dossier.activity_profile.typical_logout_time}
Total Events: ${dossier.activity_profile.total_events}
Suspicious Events: ${dossier.activity_profile.suspicious_events}
Total Downloads: ${dossier.activity_profile.total_downloads_mb} MB

THREAT TIMELINE EVENTS:
${dossier.timeline.map((t) => `[${t.timestamp}] [${t.source}] ${t.title} - ${t.description}`).join("\n")}

ANALYST CASE NOTES:
${dossier.notes.map((n) => `[${n.created_at}] (${n.author_email}): ${n.note_text}`).join("\n")}
`;

    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `ITBIS_Investigation_${dossier.employee.employee_id}.txt`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  const toggleExpand = (id: string) => {
    setExpandedItems((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="space-y-6">
      {/* Top Header & Subject Selector */}
      <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[var(--background)] border border-[#00E5FF]/40 flex items-center justify-center text-[#00E5FF]">
            <FileSearch className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold uppercase tracking-wider text-[var(--foreground)]">
              Insider Threat Investigation Center
            </h2>
            <p className="text-xs text-[var(--text-muted)]">
              Unified forensic correlation: Telemetry → Baselines → Anomalies → Risk → Alerts → Incidents
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          <select
            value={selectedEmpId}
            onChange={(e) => setSelectedEmpId(e.target.value)}
            className="w-full sm:w-72 bg-[var(--background)] border border-[var(--panel-border)] focus:border-[#00A8FF] rounded-lg px-3 py-2 text-xs text-[var(--foreground)] font-medium"
          >
            {employees.map((emp) => (
              <option key={emp.id} value={emp.employee_id}>
                {emp.name} ({emp.employee_id}) — {emp.department} [Risk: {emp.risk_score}]
              </option>
            ))}
          </select>

          <button
            onClick={() => fetchDossier(selectedEmpId)}
            className="p-2 rounded-lg bg-[var(--background)] border border-[var(--panel-border)] text-[var(--text-muted)] hover:text-[#00E5FF] transition cursor-pointer"
            title="Refresh Dossier"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          <button
            onClick={handleExportSummary}
            className="px-3 py-2 bg-[#00A8FF] hover:bg-[#00E5FF] text-[#050B14] font-bold text-xs rounded-lg transition flex items-center gap-1.5 cursor-pointer shadow-[0_0_12px_rgba(0,168,255,0.3)]"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Summary</span>
          </button>
        </div>
      </div>

      {loading ? (
        <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-20 text-center text-[var(--text-muted)]">
          <Loader2 className="w-8 h-8 animate-spin text-[#00E5FF] mx-auto mb-3" />
          <p className="text-xs uppercase tracking-wider">Correlating multi-source intelligence dossier...</p>
        </div>
      ) : dossier ? (
        <div className="space-y-6">
          {/* Subject Overview & Professional Profile Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Card 1: Professional Background */}
            <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-5 shadow-xl space-y-4">
              <div className="flex items-start justify-between border-b border-[var(--panel-border)] pb-3">
                <div>
                  <h3 className="text-base font-bold text-[var(--foreground)]">{dossier.employee.name}</h3>
                  <div className="text-xs font-mono text-[#00E5FF]">{dossier.employee.employee_id} • {dossier.employee.designation}</div>
                </div>
                <span className={`px-2.5 py-1 rounded text-xs font-mono font-black border ${
                  dossier.employee.risk_score >= 80
                    ? "bg-cyan-950 text-[#00E5FF] border-[#00E5FF]/40 shadow-[0_0_10px_rgba(0,229,255,0.2)]"
                    : dossier.employee.risk_score >= 60
                    ? "bg-[#00A8FF]/20 text-[#00A8FF] border-[#00A8FF]/40"
                    : "bg-[var(--background)] text-[var(--text-muted)] border-[var(--panel-border)]"
                }`}>
                  Risk: {dossier.employee.risk_score}/100
                </span>
              </div>

              <div className="space-y-2 text-xs">
                <div className="flex justify-between py-1 border-b border-[var(--panel-border)]/50">
                  <span className="text-[var(--text-muted)]">Department:</span>
                  <span className="font-semibold text-[var(--foreground)]">{dossier.employee.department}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-[var(--panel-border)]/50">
                  <span className="text-[var(--text-muted)]">Experience:</span>
                  <span className="font-semibold text-[var(--foreground)]">{dossier.employee.years_of_experience} Years ({dossier.employee.education})</span>
                </div>
                <div className="flex justify-between py-1 border-b border-[var(--panel-border)]/50">
                  <span className="text-[var(--text-muted)]">Location:</span>
                  <span className="font-semibold text-[var(--foreground)]">{dossier.employee.work_location} ({dossier.employee.employment_type})</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-[var(--text-muted)]">Reporting To:</span>
                  <span className="font-semibold text-[var(--foreground)]">{dossier.employee.manager_name || "Executive Leadership"}</span>
                </div>
              </div>

              {/* Skills Tag Pills */}
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-[var(--text-muted)] block mb-1.5">
                  Core Skills & Expertise
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {dossier.employee.skills?.split(",").map((s, i) => (
                    <span key={i} className="px-2 py-0.5 rounded text-[10px] font-mono bg-[var(--background)] border border-[var(--panel-border)] text-[var(--foreground)]">
                      {s.trim()}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Card 2: Access Profile & Permissions */}
            <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-5 shadow-xl space-y-4">
              <div className="border-b border-[var(--panel-border)] pb-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-[var(--foreground)]">
                  Access Profile & Security Permissions
                </h3>
                <p className="text-[11px] text-[var(--text-muted)] mt-0.5">Enrolled system privileges and security boundaries</p>
              </div>

              <div className="space-y-2 text-xs">
                {dossier.employee.access_privileges?.split(",").map((priv, idx) => (
                  <div key={idx} className="p-2 rounded-lg bg-[var(--background)] border border-[var(--panel-border)] flex items-center justify-between">
                    <span className="font-mono text-xs text-[#00E5FF]">{priv.trim()}</span>
                    <span className="px-2 py-0.5 rounded text-[9px] font-mono font-bold bg-emerald-950/60 text-emerald-400 border border-emerald-800">
                      AUTHORIZED
                    </span>
                  </div>
                ))}
              </div>

              <div className="pt-2 border-t border-[var(--panel-border)] text-xs text-[var(--text-muted)] flex justify-between">
                <span>Hardware Node:</span>
                <span className="font-mono text-[var(--foreground)]">{dossier.employee.device_info || "Standard Laptop"}</span>
              </div>
            </div>

            {/* Card 3: Activity & Behavioral Profile */}
            <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-5 shadow-xl space-y-3 flex flex-col justify-between">
              <div>
                <div className="border-b border-[var(--panel-border)] pb-3">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-[var(--foreground)]">
                    Behavioral Activity Profile
                  </h3>
                  <p className="text-[11px] text-[var(--text-muted)] mt-0.5">Calculated baseline parameters from MongoDB</p>
                </div>

                <div className="mt-3 space-y-2 text-xs">
                  <div className="flex justify-between py-1 border-b border-[var(--panel-border)]/50">
                    <span className="text-[var(--text-muted)] flex items-center gap-1.5"><Clock className="w-3.5 h-3.5 text-[#00A8FF]" /> Normal Shift:</span>
                    <span className="font-mono text-[var(--foreground)]">{dossier.activity_profile.typical_login_time} – {dossier.activity_profile.typical_logout_time}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-[var(--panel-border)]/50">
                    <span className="text-[var(--text-muted)] flex items-center gap-1.5"><HardDrive className="w-3.5 h-3.5 text-[#00E5FF]" /> Downloads:</span>
                    <span className="font-mono text-[var(--foreground)]">{dossier.activity_profile.total_downloads_mb} MB</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-[var(--panel-border)]/50">
                    <span className="text-[var(--text-muted)] flex items-center gap-1.5"><Globe className="w-3.5 h-3.5 text-[#00A8FF]" /> Off-Hours Activity:</span>
                    <span className={`font-mono font-bold ${dossier.activity_profile.off_hours_percentage > 20 ? "text-[#00E5FF]" : "text-[var(--text-muted)]"}`}>
                      {dossier.activity_profile.off_hours_percentage}%
                    </span>
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-[var(--panel-border)] flex justify-between text-xs">
                <span className="text-[var(--text-muted)]">Active Alerts / Incidents:</span>
                <span className="font-mono font-bold text-[#00E5FF]">
                  {dossier.active_alerts.length} Alerts / {dossier.active_incidents.length} Incidents
                </span>
              </div>
            </div>
          </div>

          {/* Unified Threat Story Timeline & Analyst Notes Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Timeline Column (2 spans) */}
            <div className="lg:col-span-2 bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl shadow-xl overflow-hidden">
              <div className="p-5 border-b border-[var(--panel-border)] flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold uppercase tracking-wider text-[var(--foreground)] flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-[#00E5FF]" />
                    Forensic Security Narrative Timeline
                  </h3>
                  <p className="text-xs text-[var(--text-muted)] mt-0.5">
                    Step-by-step reconstruction of telemetry, anomaly evaluations, risk spikes, and alerts
                  </p>
                </div>
                <span className="text-xs font-mono text-[var(--text-muted)]">
                  {dossier.timeline.length} Recorded Events
                </span>
              </div>

              <div className="p-5 space-y-4 max-h-[600px] overflow-y-auto">
                {dossier.timeline.length > 0 ? (
                  dossier.timeline.map((item, idx) => (
                    <div
                      key={item.id}
                      className={`p-4 rounded-xl border transition ${
                        item.severity === "CRITICAL"
                          ? "bg-cyan-950/40 border-[#00E5FF]/40 shadow-[0_0_12px_rgba(0,229,255,0.15)]"
                          : item.severity === "HIGH"
                          ? "bg-[#00A8FF]/10 border-[#00A8FF]/30"
                          : "bg-[var(--background)] border-[var(--panel-border)]"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className={`px-2 py-0.5 rounded text-[9px] font-mono font-bold uppercase ${
                              item.source === "ALERT"
                                ? "bg-cyan-900 text-[#00E5FF] border border-[#00E5FF]/40"
                                : item.source === "INCIDENT"
                                ? "bg-indigo-950 text-indigo-300 border border-indigo-800"
                                : item.source === "RISK_CHANGE"
                                ? "bg-[#00A8FF]/20 text-[#00A8FF]"
                                : "bg-[var(--panel)] text-[var(--text-muted)]"
                            }`}>
                              {item.source}
                            </span>
                            <span className="font-mono text-[10px] text-[var(--text-muted)]">
                              {new Date(item.timestamp).toLocaleString()}
                            </span>
                          </div>
                          <div className="font-bold text-xs text-[var(--foreground)] mt-1">
                            {item.title}
                          </div>
                          <div className="text-xs text-[var(--text-muted)] leading-relaxed">
                            {item.description}
                          </div>
                        </div>

                        {item.metadata && Object.keys(item.metadata).length > 0 && (
                          <button
                            onClick={() => toggleExpand(item.id)}
                            className="p-1 text-[var(--text-muted)] hover:text-[#00E5FF] cursor-pointer"
                            title="Expand Event Details"
                          >
                            {expandedItems[item.id] ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                          </button>
                        )}
                      </div>

                      {/* Expandable JSON details */}
                      {expandedItems[item.id] && item.metadata && (
                        <pre className="mt-3 p-3 rounded-lg bg-[var(--background)] border border-[var(--panel-border)] text-[11px] font-mono text-[#00E5FF] overflow-x-auto">
                          {JSON.stringify(item.metadata, null, 2)}
                        </pre>
                      )}
                    </div>
                  ))
                ) : (
                  <div className="text-center py-12 text-xs text-[var(--text-muted)]">
                    No timeline telemetry recorded for this subject.
                  </div>
                )}
              </div>
            </div>

            {/* Analyst Case Notes Column (1 span) */}
            <div className="bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl p-5 shadow-xl flex flex-col justify-between space-y-4">
              <div>
                <div className="border-b border-[var(--panel-border)] pb-3">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-[var(--foreground)] flex items-center gap-2">
                    <MessageSquare className="w-4 h-4 text-[#00A8FF]" />
                    Analyst Investigation Notes
                  </h3>
                  <p className="text-xs text-[var(--text-muted)] mt-0.5">Persistent SOC case log stored in PostgreSQL</p>
                </div>

                {/* Notes List */}
                <div className="mt-4 space-y-3 max-h-80 overflow-y-auto">
                  {dossier.notes.length > 0 ? (
                    dossier.notes.map((n) => (
                      <div key={n.id} className="p-3 rounded-lg bg-[var(--background)] border border-[var(--panel-border)] space-y-1 text-xs">
                        <div className="flex items-center justify-between text-[10px] text-[var(--text-muted)]">
                          <span className="font-semibold text-[#00E5FF]">{n.author_email}</span>
                          <span className="font-mono">{new Date(n.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
                        </div>
                        <p className="text-[var(--foreground)] leading-relaxed">{n.note_text}</p>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8 text-xs text-[var(--text-muted)]">
                      No investigation case notes logged yet.
                    </div>
                  )}
                </div>
              </div>

              {/* Add Note Form */}
              <form onSubmit={handleAddNote} className="pt-3 border-t border-[var(--panel-border)] space-y-2">
                {noteSuccess && (
                  <div className="p-2 rounded bg-emerald-950/70 border border-emerald-800 text-emerald-300 text-[11px] flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Case note logged to PostgreSQL.</span>
                  </div>
                )}
                <textarea
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  placeholder="Record investigation notes (e.g., Interviewed manager, confirmed unauthorized off-hours work)..."
                  rows={3}
                  className="w-full bg-[var(--background)] border border-[var(--panel-border)] focus:border-[#00A8FF] rounded-lg p-2.5 text-xs text-[var(--foreground)] placeholder-[var(--text-muted)] outline-none resize-none"
                />
                <button
                  type="submit"
                  disabled={addingNote || !newNote.trim()}
                  className="w-full py-2 bg-[#00A8FF] hover:bg-[#00E5FF] disabled:opacity-40 text-[#050B14] font-bold text-xs rounded-lg transition flex items-center justify-center gap-1.5 cursor-pointer shadow-[0_0_10px_rgba(0,168,255,0.2)]"
                >
                  {addingNote ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <PlusCircle className="w-3.5 h-3.5" />}
                  <span>Log Case Note</span>
                </button>
              </form>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

export default function InvestigationsPage() {
  return (
    <DashboardLayout
      pageTitle="Investigation Center"
      pageSubtitle="Comprehensive forensic intelligence and security timeline correlation"
    >
      <Suspense fallback={
        <div className="p-20 text-center text-[var(--text-muted)]">
          <Loader2 className="w-8 h-8 animate-spin text-[#00E5FF] mx-auto mb-2" />
          <p className="text-xs">Loading investigation workspace...</p>
        </div>
      }>
        <InvestigationContent />
      </Suspense>
    </DashboardLayout>
  );
}

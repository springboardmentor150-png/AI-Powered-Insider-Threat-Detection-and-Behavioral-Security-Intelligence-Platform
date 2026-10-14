"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";

export interface TimelineEvent {
  event_id: string;
  event_type: "activity" | "rule_anomaly" | "ml_anomaly" | "incident" | string;
  timestamp: string | null;
  severity?: string | null;
  title: string;
  description: string;
  details?: Record<string, any>;
}

interface InvestigationTimelineProps {
  incidentId?: number;
  employeeCode?: string;
  initialEvents?: TimelineEvent[];
}

export default function InvestigationTimeline({
  incidentId,
  employeeCode,
  initialEvents,
}: InvestigationTimelineProps) {
  const [events, setEvents] = useState<TimelineEvent[]>(initialEvents || []);
  const [loading, setLoading] = useState(!initialEvents);
  const [filter, setFilter] = useState<"all" | "anomalies" | "activities">("all");
  const [expandedEventId, setExpandedEventId] = useState<string | null>(null);

  useEffect(() => {
    if (initialEvents) {
      setEvents(initialEvents);
      return;
    }

    const fetchTimeline = async () => {
      try {
        setLoading(true);
        let res;
        if (incidentId) {
          res = await api.get(`/incidents/${incidentId}/timeline`);
        } else if (employeeCode) {
          res = await api.get(`/incidents/timeline/${employeeCode}`);
        }
        if (res && res.data) {
          const list = Array.isArray(res.data) ? res.data : res.data.timeline || [];
          setEvents(list);
        }
      } catch (err) {
        console.error("Failed to load timeline", err);
      } finally {
        setLoading(false);
      }
    };

    fetchTimeline();
  }, [incidentId, employeeCode, initialEvents]);

  const filteredEvents = events.filter((ev) => {
    if (filter === "anomalies") {
      return ev.event_type === "rule_anomaly" || ev.event_type === "ml_anomaly";
    }
    if (filter === "activities") {
      return ev.event_type === "activity";
    }
    return true;
  });

  const getEventBadge = (type: string, severity?: string | null) => {
    if (type === "incident") {
      return {
        bg: "bg-red-500/20 text-red-400 border-red-500/30",
        icon: "🚨",
        label: "INCIDENT",
      };
    }
    if (type === "rule_anomaly") {
      return {
        bg: "bg-amber-500/20 text-amber-400 border-amber-500/30",
        icon: "⚡",
        label: "RULE ANOMALY",
      };
    }
    if (type === "ml_anomaly") {
      return {
        bg: "bg-purple-500/20 text-purple-400 border-purple-500/30",
        icon: "🧠",
        label: "ML OUTLIER",
      };
    }
    return {
      bg: "bg-blue-500/20 text-blue-400 border-blue-500/30",
      icon: "📋",
      label: "TELEMETRY",
    };
  };

  const formatTimestamp = (ts: string | null) => {
    if (!ts) return "N/A";
    const d = new Date(ts);
    return isNaN(d.getTime()) ? ts : d.toLocaleString();
  };

  if (loading) {
    return (
      <div className="flex h-48 items-center justify-center">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--primary)]" />
      </div>
    );
  }

  if (events.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-[var(--border)] p-8 text-center text-sm text-[var(--muted)]">
        No chronological audit events recorded for this entity.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Timeline Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--border)] pb-3">
        <div className="flex items-center gap-1.5 text-xs text-[var(--muted)]">
          <span className="font-semibold text-[var(--foreground)]">{filteredEvents.length}</span> events recorded
        </div>
        <div className="flex items-center gap-1 rounded-lg border border-[var(--border)] bg-[var(--card)] p-1 text-xs">
          {(["all", "anomalies", "activities"] as const).map((mode) => (
            <button
              key={mode}
              onClick={() => setFilter(mode)}
              className={`rounded-md px-2.5 py-1 font-medium capitalize transition ${
                filter === mode
                  ? "bg-[var(--primary)] text-white"
                  : "text-[var(--muted)] hover:text-[var(--foreground)]"
              }`}
            >
              {mode}
            </button>
          ))}
        </div>
      </div>

      {/* Vertical Timeline Nodes */}
      <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-[var(--border)]">
        {filteredEvents.map((ev, idx) => {
          const badge = getEventBadge(ev.event_type, ev.severity);
          const isExpanded = expandedEventId === (ev.event_id || `ev-${idx}`);

          return (
            <div key={ev.event_id || idx} className="relative group">
              {/* Dot Icon */}
              <div
                className={`absolute -left-6 top-1 flex h-5 w-5 items-center justify-center rounded-full border bg-[var(--card)] text-[10px] shadow-sm transition group-hover:scale-110 ${badge.bg}`}
              >
                {badge.icon}
              </div>

              {/* Event Card */}
              <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4 transition hover:border-[var(--primary)]/50">
                <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`rounded-md border px-2 py-0.5 text-[10px] font-bold tracking-wider ${badge.bg}`}>
                      {badge.label}
                    </span>
                    {ev.severity && (
                      <span className="rounded bg-red-950/60 px-1.5 py-0.5 text-[10px] font-bold uppercase text-red-400">
                        {ev.severity}
                      </span>
                    )}
                    <h4 className="text-sm font-semibold text-[var(--foreground)]">{ev.title}</h4>
                  </div>
                  <span className="font-mono text-xs text-[var(--muted)]">
                    {formatTimestamp(ev.timestamp)}
                  </span>
                </div>

                <p className="mt-2 text-xs text-[var(--muted)] leading-relaxed">{ev.description}</p>

                {/* Optional expandable details */}
                {ev.details && Object.keys(ev.details).length > 0 && (
                  <div className="mt-3">
                    <button
                      onClick={() => setExpandedEventId(isExpanded ? null : (ev.event_id || `ev-${idx}`))}
                      className="text-[11px] font-semibold text-[var(--primary)] hover:underline"
                    >
                      {isExpanded ? "Hide Metadata ▲" : "Inspect Raw Event Payload ▼"}
                    </button>
                    {isExpanded && (
                      <pre className="mt-2 max-h-40 overflow-auto rounded-lg bg-[var(--background)] p-3 text-[10px] font-mono text-[var(--muted)] border border-[var(--border)]">
                        {JSON.stringify(ev.details, null, 2)}
                      </pre>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

"use client";

import { useState } from "react";
import api from "@/lib/api";

export interface ContributingFactor {
  feature: string;
  label: string;
  unit: string;
  actual_value: number;
  formatted_actual: string;
  baseline_mean: number;
  formatted_baseline: string;
  z_score: number;
  direction: string;
  contribution_percentage: number;
  impact: "critical" | "high" | "moderate" | "low";
  description: string;
}

export interface XAIExplanation {
  employee_code: string;
  date?: string;
  anomaly_score: number;
  is_anomaly: boolean;
  summary: string;
  top_contributor: string;
  contributing_factors: ContributingFactor[];
}

interface ExplainableAICardProps {
  explanation: XAIExplanation;
  anomalyId?: string;
  onFeedbackSubmitted?: () => void;
}

export default function ExplainableAICard({
  explanation,
  anomalyId,
  onFeedbackSubmitted,
}: ExplainableAICardProps) {
  const [feedbackState, setFeedbackState] = useState<string | null>(null);
  const [submittingFeedback, setSubmittingFeedback] = useState(false);
  const [feedbackNotes, setFeedbackNotes] = useState("");
  const [showNotesModal, setShowNotesModal] = useState(false);
  const [targetFeedback, setTargetFeedback] = useState<"false_positive" | "confirmed" | "benign">("false_positive");
  const [feedbackSuccess, setFeedbackSuccess] = useState("");

  const handleOpenFeedback = (type: "false_positive" | "confirmed" | "benign") => {
    setTargetFeedback(type);
    setShowNotesModal(true);
    setFeedbackSuccess("");
  };

  const handleConfirmFeedback = async () => {
    try {
      setSubmittingFeedback(true);
      const aid = anomalyId || `anom_${explanation.employee_code}_${explanation.date || "recent"}`;
      await api.post(`/anomalies/${aid}/feedback`, {
        feedback: targetFeedback,
        notes: feedbackNotes || undefined,
      });
      setFeedbackState(targetFeedback);
      setFeedbackSuccess(`Feedback '${targetFeedback.replace("_", " ")}' recorded successfully. Active learning model updated.`);
      setShowNotesModal(false);
      setFeedbackNotes("");
      if (onFeedbackSubmitted) onFeedbackSubmitted();
    } catch (err: any) {
      console.error("Failed to submit feedback", err);
    } finally {
      setSubmittingFeedback(false);
    }
  };

  const getImpactColor = (impact: string) => {
    if (impact === "critical") return "bg-red-500 text-red-400 border-red-500/40";
    if (impact === "high") return "bg-orange-500 text-orange-400 border-orange-500/40";
    if (impact === "moderate") return "bg-amber-500 text-amber-400 border-amber-500/40";
    return "bg-emerald-500 text-emerald-400 border-emerald-500/40";
  };

  return (
    <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between border-b border-[var(--border)] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex h-6 w-6 items-center justify-center rounded-lg bg-purple-500/20 text-xs font-bold text-purple-400">
              🧠
            </span>
            <h3 className="text-base font-bold text-[var(--foreground)]">
              Explainable AI (XAI) Behavioral Breakdown
            </h3>
          </div>
          <p className="mt-1 text-xs text-[var(--muted)]">
            Isolation Forest multi-dimensional attribution for employee <span className="font-mono text-[var(--foreground)]">{explanation.employee_code}</span>
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="rounded-xl border border-purple-500/30 bg-purple-500/10 px-3 py-1 text-xs font-mono font-bold text-purple-300">
            Score: {explanation.anomaly_score}
          </span>
        </div>
      </div>

      {/* Narrative Summary */}
      <div className="rounded-xl border border-blue-500/20 bg-blue-500/5 p-4 text-xs text-blue-300/90 leading-relaxed">
        <span className="font-bold text-blue-200">Model Reasoning: </span>
        {explanation.summary}
      </div>

      {/* Feature Attribution Bars */}
      <div className="space-y-4">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">
          Feature Contribution Weights
        </h4>

        <div className="space-y-3">
          {explanation.contributing_factors.map((factor) => {
            const impactBadge = getImpactColor(factor.impact);
            return (
              <div key={factor.feature} className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-[var(--foreground)]">{factor.label}</span>
                    <span className={`rounded px-1.5 py-0.2 text-[9px] font-bold uppercase border ${impactBadge}`}>
                      {factor.impact}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-[var(--muted)]">
                      {factor.formatted_actual} <span className="text-[10px] text-[var(--muted)]/70">(base: {factor.formatted_baseline})</span>
                    </span>
                    <span className="font-mono font-bold text-[var(--primary)]">
                      {factor.contribution_percentage}%
                    </span>
                  </div>
                </div>

                {/* Progress bar */}
                <div className="h-2 w-full overflow-hidden rounded-full bg-[var(--background)] border border-[var(--border)]">
                  <div
                    className={`h-full transition-all duration-500 ${
                      factor.impact === "critical"
                        ? "bg-red-500"
                        : factor.impact === "high"
                        ? "bg-orange-500"
                        : factor.impact === "moderate"
                        ? "bg-amber-500"
                        : "bg-emerald-500"
                    }`}
                    style={{ width: `${Math.min(100, factor.contribution_percentage * 1.5)}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Active Learning & Feedback Controls */}
      <div className="border-t border-[var(--border)] pt-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <p className="text-xs font-semibold text-[var(--foreground)]">Analyst Verification Feedback</p>
          <p className="text-[11px] text-[var(--muted)]">Submit human-in-the-loop validation to tune active learning model.</p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => handleOpenFeedback("false_positive")}
            className={`rounded-lg border px-3 py-1.5 text-xs font-semibold transition ${
              feedbackState === "false_positive"
                ? "bg-amber-500/30 border-amber-500 text-amber-300"
                : "border-[var(--border)] bg-[var(--background)] text-[var(--muted)] hover:text-amber-400 hover:border-amber-500/50"
            }`}
          >
            Mark False Positive
          </button>
          <button
            onClick={() => handleOpenFeedback("confirmed")}
            className={`rounded-lg border px-3 py-1.5 text-xs font-semibold transition ${
              feedbackState === "confirmed"
                ? "bg-red-500/30 border-red-500 text-red-300"
                : "border-[var(--border)] bg-[var(--background)] text-[var(--muted)] hover:text-red-400 hover:border-red-500/50"
            }`}
          >
            Confirm Threat
          </button>
        </div>
      </div>

      {feedbackSuccess && (
        <div className="rounded-lg bg-emerald-500/10 border border-emerald-500/30 p-2.5 text-xs text-emerald-400">
          ✓ {feedbackSuccess}
        </div>
      )}

      {/* Feedback Notes Modal */}
      {showNotesModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="w-full max-w-md rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6 shadow-2xl space-y-4">
            <h4 className="text-sm font-bold text-[var(--foreground)]">
              Record Anomaly Feedback ({targetFeedback.replace("_", " ").toUpperCase()})
            </h4>
            <p className="text-xs text-[var(--muted)]">
              Provide context for why this ML outlier should be treated as {targetFeedback.replace("_", " ")}. This will be added to the audit trail and training set.
            </p>
            <textarea
              value={feedbackNotes}
              onChange={(e) => setFeedbackNotes(e.target.value)}
              placeholder="e.g. Approved database backup cron, or employee confirmed travel."
              rows={3}
              className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] p-3 text-xs outline-none focus:border-[var(--primary)]"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowNotesModal(false)}
                className="rounded-lg border border-[var(--border)] px-3 py-1.5 text-xs font-medium text-[var(--muted)] hover:text-[var(--foreground)]"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmFeedback}
                disabled={submittingFeedback}
                className="rounded-lg bg-[var(--primary)] px-4 py-1.5 text-xs font-semibold text-white transition hover:bg-[var(--primary-hover)]"
              >
                {submittingFeedback ? "Recording..." : "Submit Feedback"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

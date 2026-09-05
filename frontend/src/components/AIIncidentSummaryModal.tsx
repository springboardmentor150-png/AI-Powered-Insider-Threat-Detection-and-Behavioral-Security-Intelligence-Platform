"use client";

import React from "react";
import { X, ShieldAlert, Sparkles, CheckCircle, ExternalLink } from "lucide-react";

interface AIIncidentSummaryModalProps {
  isOpen: boolean;
  onClose: () => void;
  incidentCode: string;
  reportData: {
    ai_report?: string;
    mitre_mapping?: Array<{ technique_id: string; name: string; description: string }>;
    recommended_actions?: string[];
  } | null;
  isLoading?: boolean;
}

export const AIIncidentSummaryModal: React.FC<AIIncidentSummaryModalProps> = ({
  isOpen,
  onClose,
  incidentCode,
  reportData,
  isLoading = false,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fade-in">
      <div className="bg-slate-900 border border-slate-700/80 w-full max-w-3xl rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-950/60 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-800">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                AI Forensic Threat Intelligence Dossier
                <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-cyan-300 font-mono border border-slate-700">
                  {incidentCode}
                </span>
              </h3>
              <p className="text-xs text-slate-400">Automated behavioral synthesis & MITRE ATT&CK correlation</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-6 text-sm text-slate-300">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-16 space-y-3 text-cyan-400">
              <Sparkles className="w-8 h-8 animate-spin" />
              <p className="font-mono text-sm text-slate-300">Synthesizing multi-vector telemetry & training models...</p>
            </div>
          ) : reportData ? (
            <>
              {/* MITRE ATT&CK Matrix Badges */}
              {reportData.mitre_mapping && reportData.mitre_mapping.length > 0 && (
                <div className="space-y-3">
                  <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider font-mono">
                    MITRE ATT&CK Classified Techniques
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {reportData.mitre_mapping.map((m, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded-xl bg-slate-950/70 border border-slate-800/80 space-y-1"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold font-mono text-rose-400">{m.technique_id}</span>
                          <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                            Enterprise Matrix
                          </span>
                        </div>
                        <p className="text-xs font-semibold text-slate-100">{m.name}</p>
                        <p className="text-[11px] text-slate-400 leading-relaxed">{m.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommended Playbook Checklist */}
              {reportData.recommended_actions && reportData.recommended_actions.length > 0 && (
                <div className="space-y-3">
                  <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider font-mono">
                    SOC Containment Playbook Actions
                  </h4>
                  <div className="space-y-2">
                    {reportData.recommended_actions.map((act, idx) => (
                      <div
                        key={idx}
                        className="flex items-start space-x-3 p-3 rounded-xl bg-slate-800/40 border border-slate-700/50"
                      >
                        <CheckCircle className="w-4 h-4 text-cyan-400 mt-0.5 shrink-0" />
                        <span className="text-xs text-slate-200">{act}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Full Narrative Output */}
              {reportData.ai_report && (
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider font-mono">
                    Raw Intelligence Briefing
                  </h4>
                  <div className="p-4 rounded-xl bg-slate-950/90 border border-slate-800 text-xs font-mono whitespace-pre-wrap text-slate-300 leading-relaxed">
                    {reportData.ai_report}
                  </div>
                </div>
              )}
            </>
          ) : (
            <p className="text-slate-400 text-center py-8">No report data generated yet.</p>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-950/60 flex items-center justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition"
          >
            Close Dossier
          </button>
        </div>
      </div>
    </div>
  );
};

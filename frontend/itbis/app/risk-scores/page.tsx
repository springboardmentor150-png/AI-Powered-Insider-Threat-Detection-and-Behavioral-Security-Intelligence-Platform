"use client";

import { useState, useEffect, useCallback } from "react";
import {
  TrendingUp,
  Search,
  Filter,
  ShieldAlert,
  Clock,
  ChevronRight,
  Loader2,
  X,
  History,
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import { api } from "@/lib/api";

interface RiskItem {
  employee_id: string;
  name: string;
  department?: string;
  risk_score: number;
  risk_level: string;
  status: string;
  top_factor?: string;
  last_calculated: string;
}

interface RiskHistoryItem {
  id: number;
  score: number;
  risk_level: string;
  contributing_factors?: string;
  calculated_at: string;
}

export default function RiskScoresPage() {
  const [items, setItems] = useState<RiskItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [riskFilter, setRiskFilter] = useState("ALL");
  const [selectedEmp, setSelectedEmp] = useState<RiskItem | null>(null);
  const [history, setHistory] = useState<RiskHistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  const fetchRiskScores = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (riskFilter !== "ALL") params.append("risk_level", riskFilter);
      params.append("limit", "50");

      const res = await api.get(`/risk-scores?${params.toString()}`);
      setItems(res.data.items || []);
    } catch (err) {
      console.error("Error fetching risk scores:", err);
    } finally {
      setLoading(false);
    }
  }, [riskFilter]);

  useEffect(() => {
    fetchRiskScores();
  }, [fetchRiskScores]);

  const handleOpenHistory = async (emp: RiskItem) => {
    setSelectedEmp(emp);
    setHistoryLoading(true);
    try {
      const res = await api.get(`/risk-scores/${emp.employee_id}/history`);
      setHistory(res.data || []);
    } catch (err) {
      console.error("Error fetching risk history:", err);
      setHistory([]);
    } finally {
      setHistoryLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-[#00E5FF] bg-cyan-950/70 border-[#00E5FF]/50 shadow-[0_0_8px_rgba(0,229,255,0.2)]";
    if (score >= 60) return "text-[#00A8FF] bg-[#00A8FF]/20 border-[#00A8FF]/40";
    if (score >= 30) return "text-cyan-400 bg-[#132B45] border-[#1E3A5F]";
    return "text-[#8E9EB5] bg-[#050B14] border-[#132B45]";
  };

  return (
    <DashboardLayout
      pageTitle="Risk Score Matrix"
      pageSubtitle="Continuous behavioral threat scoring and anomaly weight aggregation"
    >
      <div className="space-y-6">
        {/* Tier Cards Summary */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-4">
            <span className="text-[10px] uppercase font-bold text-[#8E9EB5] tracking-wider">Critical Tier (80–100)</span>
            <div className="text-2xl font-black text-[#00E5FF] mt-1">
              {items.filter((i) => i.risk_score >= 80).length}
            </div>
            <span className="text-[10px] text-[#8E9EB5]">Immediate SOC Intervention</span>
          </div>

          <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-4">
            <span className="text-[10px] uppercase font-bold text-[#8E9EB5] tracking-wider">High Tier (60–79)</span>
            <div className="text-2xl font-black text-[#00A8FF] mt-1">
              {items.filter((i) => i.risk_score >= 60 && i.risk_score < 80).length}
            </div>
            <span className="text-[10px] text-[#8E9EB5]">Targeted Sensor Monitoring</span>
          </div>

          <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-4">
            <span className="text-[10px] uppercase font-bold text-[#8E9EB5] tracking-wider">Medium Tier (30–59)</span>
            <div className="text-2xl font-black text-[#F4F8FF] mt-1">
              {items.filter((i) => i.risk_score >= 30 && i.risk_score < 60).length}
            </div>
            <span className="text-[10px] text-[#8E9EB5]">Moderate Behavioral Anomaly</span>
          </div>

          <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-4">
            <span className="text-[10px] uppercase font-bold text-[#8E9EB5] tracking-wider">Low Tier (0–29)</span>
            <div className="text-2xl font-black text-[#8E9EB5] mt-1">
              {items.filter((i) => i.risk_score < 30).length}
            </div>
            <span className="text-[10px] text-[#8E9EB5]">Standard Operational Baseline</span>
          </div>
        </div>

        {/* Filter Toolbar */}
        <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Filter className="w-4 h-4 text-[#00A8FF]" />
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="bg-[#050B14] border border-[#132B45] text-xs text-[#F4F8FF] rounded-lg px-3 py-1.5"
            >
              <option value="ALL">All Risk Tiers</option>
              <option value="CRITICAL">Critical Risk (80–100)</option>
              <option value="HIGH">High Risk (60–79)</option>
              <option value="MEDIUM">Medium Risk (30–59)</option>
              <option value="LOW">Low Risk (0–29)</option>
            </select>
          </div>

          <span className="text-xs text-[#8E9EB5] font-mono">
            {items.length} Monitored Entities Scored
          </span>
        </div>

        {/* Risk Scores Table */}
        <div className="bg-[#0B1626] border border-[#132B45] rounded-xl shadow-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-[#050B14] border-b border-[#132B45] text-[10px] font-bold uppercase tracking-wider text-[#8E9EB5]">
                  <th className="py-3 px-4">Score</th>
                  <th className="py-3 px-4">Tier</th>
                  <th className="py-3 px-4">Monitored Subject</th>
                  <th className="py-3 px-4">Department</th>
                  <th className="py-3 px-4">Primary Anomaly Trigger</th>
                  <th className="py-3 px-4">Last Calculated</th>
                  <th className="py-3 px-4 text-right">Telemetry</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#132B45] text-xs">
                {loading ? (
                  <tr>
                    <td colSpan={7} className="py-12 text-center text-[#8E9EB5]">
                      <div className="flex items-center justify-center gap-2">
                        <Loader2 className="w-4 h-4 animate-spin text-[#00E5FF]" />
                        <span>Aggregating continuous risk scores...</span>
                      </div>
                    </td>
                  </tr>
                ) : items.length > 0 ? (
                  items.map((item) => (
                    <tr key={item.employee_id} className="hover:bg-[#050B14]/60 transition">
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span className={`inline-block px-2.5 py-1 rounded text-xs font-mono font-black border ${getScoreColor(item.risk_score)}`}>
                          {item.risk_score}
                        </span>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap font-mono font-bold text-[11px] text-[#00A8FF]">
                        {item.risk_level}
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <div className="font-semibold text-[#F4F8FF]">{item.name}</div>
                        <div className="text-[10px] font-mono text-[#8E9EB5]">{item.employee_id}</div>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap text-[#8E9EB5]">
                        {item.department || "General"}
                      </td>
                      <td className="py-3 px-4 text-xs text-[#F4F8FF] max-w-sm truncate">
                        {item.top_factor || "Operational Baseline Monitoring"}
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap font-mono text-[11px] text-[#8E9EB5]">
                        {new Date(item.last_calculated).toLocaleString([], { dateStyle: "short", timeStyle: "short" })}
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap text-right">
                        <button
                          onClick={() => handleOpenHistory(item)}
                          className="px-2.5 py-1 rounded bg-[#050B14] hover:bg-[#00A8FF]/20 border border-[#132B45] hover:border-[#00A8FF] text-[11px] text-[#00E5FF] transition flex items-center gap-1.5 ml-auto cursor-pointer"
                        >
                          <History className="w-3 h-3" /> History
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={7} className="py-12 text-center text-[#8E9EB5]">
                      No employees match the specified risk score filter.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Risk History Modal */}
        {selectedEmp && (
          <div className="fixed inset-0 z-50 bg-[#050B14]/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-[#0B1626] border border-[#132B45] rounded-xl max-w-xl w-full p-6 shadow-2xl space-y-4 animate-in fade-in zoom-in-95">
              <div className="flex items-center justify-between pb-3 border-b border-[#132B45]">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-[#00E5FF]" />
                  <h3 className="font-bold text-sm text-[#F4F8FF]">
                    Score Volatility Timeline: {selectedEmp.name} ({selectedEmp.employee_id})
                  </h3>
                </div>
                <button
                  onClick={() => setSelectedEmp(null)}
                  className="p-1 text-[#8E9EB5] hover:text-[#F4F8FF] cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {historyLoading ? (
                <div className="py-12 text-center text-[#8E9EB5]">
                  <Loader2 className="w-5 h-5 animate-spin text-[#00E5FF] mx-auto mb-2" />
                  <span>Loading risk calculation history...</span>
                </div>
              ) : history.length > 0 ? (
                <div className="divide-y divide-[#132B45] max-h-80 overflow-y-auto">
                  {history.map((h) => (
                    <div key={h.id} className="py-3 flex items-start justify-between text-xs gap-3">
                      <div>
                        <div className="font-mono text-[10px] text-[#8E9EB5]">
                          {new Date(h.calculated_at).toLocaleString()}
                        </div>
                        <div className="text-[#F4F8FF] font-medium mt-1">
                          {h.contributing_factors ? JSON.parse(h.contributing_factors).join(", ") : "Audit Baseline"}
                        </div>
                      </div>
                      <span className={`px-2 py-1 rounded font-mono font-bold text-xs ${getScoreColor(h.score)}`}>
                        {h.score} ({h.risk_level})
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-xs text-[#8E9EB5]">
                  No historical calculation logs available.
                </div>
              )}

              <div className="pt-3 border-t border-[#132B45] text-right">
                <button
                  onClick={() => setSelectedEmp(null)}
                  className="px-4 py-1.5 bg-[#050B14] hover:bg-[#132B45] border border-[#132B45] text-xs text-[#F4F8FF] rounded-lg transition cursor-pointer"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

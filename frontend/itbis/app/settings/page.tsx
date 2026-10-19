"use client";

import { useState, useEffect } from "react";
import {
  Sliders,
  Save,
  CheckCircle2,
  Shield,
  Clock,
  HardDrive,
  Bell,
  Loader2,
  RefreshCw,
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import { api } from "@/lib/api";

export default function SettingsPage() {
  const [settings, setSettings] = useState<Record<string, string>>({
    anomaly_threshold: "60",
    critical_threshold: "80",
    max_download_mb: "500",
    business_start_hour: "8",
    business_end_hour: "19",
    alert_dedup_window_mins: "15",
    sensor_sensitivity: "HIGH",
    auto_flag_critical: "true",
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    const fetchSettings = async () => {
      setLoading(true);
      try {
        const res = await api.get("/settings");
        if (res.data) setSettings(res.data);
      } catch (err) {
        console.error("Error fetching settings:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchSettings();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSaveSuccess(false);
    try {
      await api.post("/settings", { settings });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to update settings");
    } finally {
      setSaving(false);
    }
  };

  return (
    <DashboardLayout
      pageTitle="System & Detection Settings"
      pageSubtitle="Behavioral engine thresholds, telemetry sensitivity, and notification rules"
    >
      <div className="max-w-4xl space-y-6">
        {saveSuccess && (
          <div className="p-4 rounded-xl bg-emerald-950/80 border border-emerald-800 text-emerald-300 text-xs flex items-center gap-2 animate-in fade-in">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>Detection parameters successfully updated and committed to database engine.</span>
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-6">
          {/* Anomaly Detection Engine */}
          <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-6 shadow-xl space-y-4">
            <div className="flex items-center gap-2.5 pb-3 border-b border-[#132B45]">
              <Shield className="w-5 h-5 text-[#00E5FF]" />
              <div>
                <h3 className="text-sm font-bold text-[#F4F8FF] uppercase tracking-wider">
                  Behavioral Detection Engine Thresholds
                </h3>
                <p className="text-xs text-[#8E9EB5]">Configure scoring triggers and automated alert boundaries</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-[#8E9EB5] mb-1">
                  High Risk Alert Trigger Threshold (0–100)
                </label>
                <input
                  type="number"
                  min="30"
                  max="90"
                  value={settings.anomaly_threshold || "60"}
                  onChange={(e) => setSettings({ ...settings, anomaly_threshold: e.target.value })}
                  className="w-full bg-[#050B14] border border-[#132B45] focus:border-[#00A8FF] rounded-lg px-3 py-2 text-xs text-[#F4F8FF] font-mono"
                />
                <span className="text-[10px] text-[#8E9EB5] mt-1 block">Scores above this generate an automated SOC alert</span>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#8E9EB5] mb-1">
                  Critical Risk Threshold (0–100)
                </label>
                <input
                  type="number"
                  min="70"
                  max="100"
                  value={settings.critical_threshold || "80"}
                  onChange={(e) => setSettings({ ...settings, critical_threshold: e.target.value })}
                  className="w-full bg-[#050B14] border border-[#132B45] focus:border-[#00A8FF] rounded-lg px-3 py-2 text-xs text-[#F4F8FF] font-mono"
                />
                <span className="text-[10px] text-[#8E9EB5] mt-1 block">Scores above this flag the monitored subject status</span>
              </div>
            </div>
          </div>

          {/* Operational Baselines */}
          <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-6 shadow-xl space-y-4">
            <div className="flex items-center gap-2.5 pb-3 border-b border-[#132B45]">
              <Clock className="w-5 h-5 text-[#00A8FF]" />
              <div>
                <h3 className="text-sm font-bold text-[#F4F8FF] uppercase tracking-wider">
                  Operational Window & Transfer Quotas
                </h3>
                <p className="text-xs text-[#8E9EB5]">Baseline working shifts and data extraction safeguards</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-[#8E9EB5] mb-1">
                  Business Shift Start (UTC Hour)
                </label>
                <input
                  type="number"
                  min="0"
                  max="23"
                  value={settings.business_start_hour || "8"}
                  onChange={(e) => setSettings({ ...settings, business_start_hour: e.target.value })}
                  className="w-full bg-[#050B14] border border-[#132B45] focus:border-[#00A8FF] rounded-lg px-3 py-2 text-xs text-[#F4F8FF] font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#8E9EB5] mb-1">
                  Business Shift End (UTC Hour)
                </label>
                <input
                  type="number"
                  min="0"
                  max="23"
                  value={settings.business_end_hour || "19"}
                  onChange={(e) => setSettings({ ...settings, business_end_hour: e.target.value })}
                  className="w-full bg-[#050B14] border border-[#132B45] focus:border-[#00A8FF] rounded-lg px-3 py-2 text-xs text-[#F4F8FF] font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#8E9EB5] mb-1">
                  Max Download Quota (MB)
                </label>
                <input
                  type="number"
                  min="50"
                  max="50000"
                  value={settings.max_download_mb || "500"}
                  onChange={(e) => setSettings({ ...settings, max_download_mb: e.target.value })}
                  className="w-full bg-[#050B14] border border-[#132B45] focus:border-[#00A8FF] rounded-lg px-3 py-2 text-xs text-[#F4F8FF] font-mono"
                />
              </div>
            </div>
          </div>

          {/* Alert Deduplication & Notifications */}
          <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-6 shadow-xl space-y-4">
            <div className="flex items-center gap-2.5 pb-3 border-b border-[#132B45]">
              <Bell className="w-5 h-5 text-[#00E5FF]" />
              <div>
                <h3 className="text-sm font-bold text-[#F4F8FF] uppercase tracking-wider">
                  Alert Anti-Spam & Sensor Sensitivity
                </h3>
                <p className="text-xs text-[#8E9EB5]">Control alert deduplication windows and telemetry density</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-[#8E9EB5] mb-1">
                  Alert Deduplication Window (Minutes)
                </label>
                <input
                  type="number"
                  min="1"
                  max="120"
                  value={settings.alert_dedup_window_mins || "15"}
                  onChange={(e) => setSettings({ ...settings, alert_dedup_window_mins: e.target.value })}
                  className="w-full bg-[#050B14] border border-[#132B45] focus:border-[#00A8FF] rounded-lg px-3 py-2 text-xs text-[#F4F8FF] font-mono"
                />
                <span className="text-[10px] text-[#8E9EB5] mt-1 block">Suppresses redundant alerts for repeated anomaly triggers</span>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#8E9EB5] mb-1">
                  Sensor Telemetry Sensitivity
                </label>
                <select
                  value={settings.sensor_sensitivity || "HIGH"}
                  onChange={(e) => setSettings({ ...settings, sensor_sensitivity: e.target.value })}
                  className="w-full bg-[#050B14] border border-[#132B45] focus:border-[#00A8FF] rounded-lg px-3 py-2 text-xs text-[#F4F8FF]"
                >
                  <option value="AGGRESSIVE">Aggressive (High Frequency Sampling)</option>
                  <option value="HIGH">High (Standard Enterprise Security)</option>
                  <option value="BALANCED">Balanced (Noise Reduction Mode)</option>
                </select>
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="submit"
              disabled={saving}
              className="px-6 py-2.5 bg-[#00A8FF] hover:bg-[#00E5FF] text-[#050B14] font-bold text-xs rounded-lg transition flex items-center gap-2 cursor-pointer shadow-[0_0_15px_rgba(0,168,255,0.3)]"
            >
              {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              <span>Save System Settings</span>
            </button>
          </div>
        </form>
      </div>
    </DashboardLayout>
  );
}

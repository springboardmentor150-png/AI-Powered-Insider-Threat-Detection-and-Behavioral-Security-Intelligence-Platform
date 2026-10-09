"use client";
import React from "react";

export default function SettingsPage() {
  return (
    <div>
      <div style={{ marginBottom: "2rem" }}>
        <h2 className="title-h1">Platform Configuration</h2>
        <p className="text-caption">Global settings and environmental variable mappings.</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "1.5rem" }}>
        <div className="card">
          <h3 style={{ fontSize: "1.125rem", fontWeight: 600, marginBottom: "1.5rem" }}>System Limits & Tuning</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div style={{ display: "grid", gridTemplateColumns: "200px 1fr", alignItems: "center" }}>
              <label className="input-label" style={{ margin: 0 }}>JWT Expiration (mins)</label>
              <input type="number" className="input-field" value={30} disabled style={{ background: "transparent", color: "var(--text-muted)", cursor: "not-allowed" }} />
            </div>
            
            <div style={{ display: "grid", gridTemplateColumns: "200px 1fr", alignItems: "center" }}>
              <label className="input-label" style={{ margin: 0 }}>Log Ingestion Rate Limit</label>
              <input type="number" className="input-field" value={1000} disabled style={{ background: "transparent", color: "var(--text-muted)", cursor: "not-allowed" }} />
            </div>
          </div>
          <div style={{ marginTop: "1rem", fontSize: "0.75rem", color: "var(--text-muted)" }}>* Configuration changes via dashboard are disabled in this environment. Modify backend `.env` to change variables.</div>
        </div>

        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
            <h3 style={{ fontSize: "1.125rem", fontWeight: 600, margin: 0 }}>Anomaly Detection Engine</h3>
            <span className="badge badge-success">Online</span>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div style={{ display: "grid", gridTemplateColumns: "200px 1fr", alignItems: "center" }}>
              <label className="input-label" style={{ margin: 0 }}>Risk Threshold (0-100)</label>
              <input type="number" className="input-field" defaultValue={75} />
            </div>
          </div>
        </div>
        
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
            <h3 style={{ fontSize: "1.125rem", fontWeight: 600, margin: 0 }}>External Integrations</h3>
            <span className="badge badge-success">Online</span>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div style={{ display: "grid", gridTemplateColumns: "200px 1fr", alignItems: "center" }}>
              <label className="input-label" style={{ margin: 0 }}>SIEM Export URI</label>
              <input type="text" className="input-field" defaultValue="https://siem.internal/api/ingest" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

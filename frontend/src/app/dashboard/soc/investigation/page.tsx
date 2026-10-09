"use client";

export default function ThreatInvestigation() {
  return (
    <div className="soc-subpage">
      <h2 style={{ fontSize: "1.25rem", color: "#f1f5f9", marginBottom: "0.25rem", letterSpacing: "1px" }}>THREAT INVESTIGATION</h2>
      <p style={{ color: "#00e5ff", fontSize: "0.85rem", marginBottom: "1.5rem" }}>Entity resolution and behavioral risk analysis.</p>

      <div style={{ background: "rgba(10,16,30,0.8)", border: "1px solid rgba(255,255,255,0.05)", borderRadius: "8px", padding: "2rem", textAlign: "center" }}>
         <input type="text" placeholder="Search Identity (e.g. EMP-101)..." style={{ width: "100%", maxWidth: "400px", padding: "0.75rem 1rem", background: "rgba(0,0,0,0.5)", border: "1px solid rgba(0,229,255,0.2)", color: "#f1f5f9", borderRadius: "6px", outline: "none", marginBottom: "1.5rem" }} />
         <div style={{ padding: "3rem 1rem", color: "#64748b", fontSize: "0.85rem" }}>
            Query an entity ID to initialize the investigation timeline matrix.
         </div>
      </div>
    </div>
  );
}

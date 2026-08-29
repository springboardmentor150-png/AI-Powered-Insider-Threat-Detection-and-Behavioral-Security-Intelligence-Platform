"use client";
import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { getDecodedRole, logout } from "@/lib/api";
import Link from "next/link";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [role, setRole] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const r = getDecodedRole();
    if (!r) {
      router.push("/login");
    } else {
      setRole(r);
    }
  }, [router]);

  if (!mounted || !role) return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
       <div className="loader"></div>
    </div>
  );

  const isActive = (path: string) => pathname === path;

  const navItemStyle = (path: string) => ({
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
    padding: "0.75rem 1rem",
    borderRadius: "8px",
    color: isActive(path) ? "var(--accent)" : "var(--text-muted)",
    background: isActive(path) ? "var(--accent-light)" : "transparent",
    fontWeight: isActive(path) ? 600 : 500,
    transition: "all 0.2s ease"
  });

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "var(--bg-dark)" }}>
      {/* Sidebar */}
      <aside style={{ width: "280px", background: "var(--bg-sidebar)", padding: "1.5rem", borderRight: "1px solid var(--border)", display: "flex", flexDirection: "column" }}>
        
        {/* Brand */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "2.5rem" }}>
          <div style={{ width: "32px", height: "32px", background: "var(--accent)", borderRadius: "8px", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0B0F19" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            </svg>
          </div>
          <h2 style={{ color: "white", fontSize: "1.25rem", fontWeight: 700, letterSpacing: "0.01em" }}>
            ITBIS <span style={{ color: "var(--text-muted)", fontWeight: 400 }}>Ops</span>
          </h2>
        </div>
        
        {/* Navigation */}
        <div style={{ fontSize: "0.75rem", color: "var(--text-placeholder)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "1rem", marginLeft: "1rem" }}>
          Core Modules
        </div>
        <nav style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
          <Link href="/dashboard" style={navItemStyle("/dashboard")}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
            Operations Overview
          </Link>
          <Link href="/dashboard/employees" style={navItemStyle("/dashboard/employees")}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
            Identity Registry
          </Link>
          <Link href="/dashboard/logs" style={navItemStyle("/dashboard/logs")}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
            Activity Telemetry
          </Link>
        </nav>

        {/* User Card */}
        <div style={{ marginTop: "auto", padding: "1rem", background: "var(--bg-input)", borderRadius: "10px", border: "1px solid var(--border-light)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <div style={{ width: "36px", height: "36px", background: "var(--bg-dark)", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", border: "1px solid var(--border)" }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
            </div>
            <div style={{ flex: 1, overflow: "hidden" }}>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.15rem" }}>Clearance Level</div>
              <div style={{ fontWeight: 600, color: "var(--text-main)", fontSize: "0.875rem", whiteSpace: "nowrap", textOverflow: "ellipsis", overflow: "hidden" }}>
                {role.replace('_', ' ').toUpperCase()}
              </div>
            </div>
          </div>
          <button onClick={logout} style={{ marginTop: "1rem", width: "100%", padding: "0.625rem", background: "var(--bg-dark)", border: "1px solid var(--border)", color: "var(--text-muted)", borderRadius: "6px", fontSize: "0.875rem", display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem", transition: "all 0.2s" }} onMouseOver={e => e.currentTarget.style.color = "var(--danger)"} onMouseOut={e => e.currentTarget.style.color = "var(--text-muted)"}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
            Terminate Session
          </button>
        </div>
      </aside>

      {/* Main Area */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        {/* Top Header */}
        <header style={{ height: "72px", background: "var(--bg-card)", borderBottom: "1px solid var(--border)", display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 2rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
            <h1 className="title-h1" style={{ margin: 0, fontSize: "1.125rem" }}>
              {pathname === "/dashboard" && "Operations Overview"}
              {pathname === "/dashboard/employees" && "Identity Registry Database"}
              {pathname === "/dashboard/logs" && "Live Activity Telemetry"}
            </h1>
            <span className="badge badge-success" style={{ display: "flex", gap: "0.375rem" }}>
              <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "currentColor", alignSelf: "center", animation: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite" }}></span>
              SYSTEM ONLINE
            </span>
          </div>
        </header>

        {/* Content */}
        <main style={{ flex: 1, padding: "2rem", overflowY: "auto" }}>
          <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}

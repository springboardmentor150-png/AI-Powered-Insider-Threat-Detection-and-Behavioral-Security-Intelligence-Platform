"use client";
import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { getDecodedRole, logout } from "@/lib/api";
import Link from "next/link";
import Image from "next/image";
import SocLayout from "@/components/SocLayout";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [role, setRole] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);
  const [theme, setTheme] = useState("dark");

  useEffect(() => {
    setMounted(true);
    document.documentElement.setAttribute("data-theme", "dark");
    const r = getDecodedRole();
    if (!r) {
      router.push("/login");
    } else {
      setRole(r);
    }
  }, [router]);

  if (!mounted || !role) return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh", background: "var(--bg-dark)" }}>
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

  const isRole = (r: string) => role.toUpperCase() === r;

  const isAdmin = isRole("ADMIN");
  const isSocEngine = isRole("SOC_ENGINEER");
  const isAnalyst = isRole("SECURITY_ANALYST");
  const isManager = isRole("SECURITY_MANAGER");



  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "var(--bg-dark)" }}>
      {/* Sidebar */}
      <aside style={{ width: "280px", background: "var(--bg-sidebar)", padding: "1.5rem", borderRight: "1px solid var(--border)", display: "flex", flexDirection: "column" }}>
        
        {/* Brand */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "2.5rem" }}>
          <div style={{ width: "40px", height: "40px", position: "relative" }}>
             <Image src="/logo.png" alt="Insider Threat Logo" fill style={{ objectFit: "contain" }} />
          </div>
          <h2 style={{ color: "var(--text-main)", fontSize: "1.125rem", fontWeight: 700, letterSpacing: "0.02em" }}>
            ITBIS <span style={{ color: "var(--accent)", fontWeight: 500, fontSize: "0.875rem", display: "block" }}>{role.replace('_', ' ')}</span>
          </h2>
        </div>
        
        {isManager ? (
          <>
            <div style={{ fontSize: "0.75rem", color: "var(--text-placeholder)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "1rem", marginLeft: "1rem" }}>
              Manager Operations
            </div>
            <nav style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              <Link href="/dashboard" style={navItemStyle("/dashboard")}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
                Overview
              </Link>
              <Link href="/dashboard/employees" style={navItemStyle("/dashboard/employees")}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                Team Security
              </Link>
              <Link href="/dashboard/logs" style={navItemStyle("/dashboard/logs")}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
                Employee Risk
              </Link>
              <Link href="/dashboard/alerts" style={navItemStyle("/dashboard/alerts")}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                Security Alerts
              </Link>
              <Link href="/dashboard/incidents" style={navItemStyle("/dashboard/incidents")}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>
                Incidents
              </Link>
            </nav>
          </>
        ) : (
          <>
            <div style={{ fontSize: "0.75rem", color: "var(--text-placeholder)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "1rem", marginLeft: "1rem" }}>
              Core Modules
            </div>
            <nav style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              
              <Link href="/dashboard" style={navItemStyle("/dashboard")}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
                Personal Dashboard
              </Link>
              
              {isAdmin && (
                <Link href="/dashboard/users" style={navItemStyle("/dashboard/users")}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                  User Management
                </Link>
              )}

              {(isAdmin || isSocEngine || isAnalyst) && (
                <Link href="/dashboard/employees" style={navItemStyle("/dashboard/employees")}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                  Employee Directory
                </Link>
              )}
              
              {(isAdmin || isSocEngine || isAnalyst) && (
                <Link href="/dashboard/logs" style={navItemStyle("/dashboard/logs")}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
                  Activity Logs
                </Link>
              )}

              {(isAdmin || isAnalyst || isSocEngine) && (
                <Link href="/dashboard/alerts" style={navItemStyle("/dashboard/alerts")}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                  Security Alerts
                </Link>
              )}

              {(isAdmin || isAnalyst || isSocEngine) && (
                <Link href="/dashboard/incidents" style={navItemStyle("/dashboard/incidents")}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>
                  Incidents
                </Link>
              )}

          
          
          {(isAdmin || isSocEngine) && (
            <>
              <div style={{ fontSize: "0.75rem", color: "var(--text-placeholder)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.1em", marginTop: "1rem", marginBottom: "1rem", marginLeft: "1rem" }}>
                System Controls
              </div>
              {isAdmin && (
                  <Link href="/dashboard/settings" style={navItemStyle("/dashboard/settings")}>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
                    System Settings
                  </Link>
              )}
              <Link href="/dashboard/simulator" style={navItemStyle("/dashboard/simulator")}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
                Security Simulator
              </Link>
              {isAdmin && (
                  <Link href="/dashboard/security" style={navItemStyle("/dashboard/security")}>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                    Access & Security
                  </Link>
              )}
            </>
          )}
        </nav>
        </>
      )}
        {/* User Card */}
        <div style={{ marginTop: "auto", padding: "1rem", background: "var(--bg-input)", borderRadius: "10px", border: "1px solid var(--border-light)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <div style={{ width: "36px", height: "36px", background: "var(--bg-dark)", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", border: "1px solid var(--border)" }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
            </div>
            <div style={{ flex: 1, overflow: "hidden" }}>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.15rem" }}>Clearance Level</div>
              <div style={{ fontWeight: 600, color: isAdmin ? "var(--danger)" : "var(--text-main)", fontSize: "0.875rem", whiteSpace: "nowrap", textOverflow: "ellipsis", overflow: "hidden" }}>
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
              {pathname === "/dashboard" && (isAdmin ? "Platform Command Center" : "Operations Overview")}
              {pathname === "/dashboard/users" && "User Access Management"}
              {pathname === "/dashboard/employees" && "Employee Directory Hub"}
              {pathname === "/dashboard/logs" && "System Activity Telemetry"}
              {pathname === "/dashboard/settings" && "Platform Configuration"}
              {pathname === "/dashboard/security" && "Security Policies & Access"}
            </h1>
            <span className="badge badge-success" style={{ display: "flex", gap: "0.375rem" }}>
              <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "currentColor", alignSelf: "center", animation: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite" }}></span>
              SYSTEM ONLINE
            </span>
          </div>
          
          <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
            <button 
              onClick={() => {
                const newTheme = theme === "dark" ? "light" : "dark";
                setTheme(newTheme);
                document.documentElement.setAttribute("data-theme", newTheme);
              }}
              className="btn-outline" 
              style={{ padding: "0.5rem 1rem", display: "flex", alignItems: "center", gap: "0.5rem" }}
            >
              {theme === "dark" ? (
                <><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg> Light Mode</>
              ) : (
                <><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg> Dark Mode</>
              )}
            </button>
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

"use client";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { logout } from "@/lib/api";

export default function SocLayout({ children, role }: { children: React.ReactNode, role: string }) {
  const pathname = usePathname();
  const isActive = (path: string) => pathname === path;

  return (
    <div className="soc-layout" style={{ display: "flex", minHeight: "100vh", background: "#05070a", color: "#f1f5f9", overflow: "hidden", fontFamily: "inherit" }}>
      
      {/* Animated Background */}
      <div className="soc-bg">
         <div className="bg-glow"></div>
         <div className="bg-grid"></div>
         <div className="bg-scan"></div>
         <div className="bg-particles"></div>
         <div className="bg-vignette"></div>
      </div>

      {/* Sidebar */}
      <aside className="soc-sidebar">
        <div className="sidebar-brand">
          <div className="logo-box">
             <Image src="/logo.png" alt="ITBIS" fill style={{ objectFit: 'contain' }} />
          </div>
          <div className="brand-text">
             <span className="b-title">ITBIS</span>
             <span className="b-role">SOC ENGINEER</span>
          </div>
        </div>

        <div className="nav-header">SOC OPERATIONS</div>
        <nav className="soc-nav">
          <Link href="/dashboard" className={`soc-link ${isActive('/dashboard') ? 'active' : ''}`}>
             <span className="icon">▣</span> Operations Overview
          </Link>
          <Link href="/dashboard/soc/telemetry" className={`soc-link ${isActive('/dashboard/soc/telemetry') ? 'active' : ''}`}>
             <span className="icon">◉</span> Live Telemetry
          </Link>
          <Link href="/dashboard/soc/alerts" className={`soc-link ${isActive('/dashboard/soc/alerts') ? 'active' : ''}`}>
             <span className="icon">⚠</span> Alert Queue
          </Link>
          <Link href="/dashboard/soc/investigation" className={`soc-link ${isActive('/dashboard/soc/investigation') ? 'active' : ''}`}>
             <span className="icon">⌕</span> Threat Investigation
          </Link>
          <Link href="/dashboard/soc/incidents" className={`soc-link ${isActive('/dashboard/soc/incidents') ? 'active' : ''}`}>
             <span className="icon">◈</span> Incident Response
          </Link>
          <Link href="/dashboard/soc/monitoring" className={`soc-link ${isActive('/dashboard/soc/monitoring') ? 'active' : ''}`}>
             <span className="icon">◫</span> Security Monitoring
          </Link>
        </nav>

        <button onClick={logout} className="soc-logout">
          ⏻ Terminate Session
        </button>
      </aside>

      <div className="soc-main-wrapper">
        {/* Header */}
        <header className="soc-header">
           <div className="h-left">SECURITY OPERATIONS CENTER</div>
           <div className="h-right">
              <div className="status-pill"><span className="pulse-dot"></span> SYSTEM LIVE</div>
              <div className="time-display">{new Date().toLocaleTimeString()}</div>
              <div className="user-profile">
                <span className="u-icon">👤</span> SOC ENGINEER
              </div>
           </div>
        </header>
        
        {/* Content */}
        <main className="soc-content">
          <div className="content-inner">
             {children}
          </div>
        </main>
      </div>

      <style>{`
        .soc-layout {
          position: relative;
          z-index: 1;
        }

        /* Background */
        .soc-bg { position: fixed; inset: 0; pointer-events: none; z-index: -1; }
        .bg-glow {
          position: absolute; top: -20%; left: -10%; width: 60vw; height: 60vh;
          background: radial-gradient(circle, rgba(0, 229, 255, 0.05) 0%, transparent 60%);
        }
        .bg-grid {
          position: absolute; inset: 0;
          background-image: 
            linear-gradient(rgba(0, 229, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 229, 255, 0.03) 1px, transparent 1px);
          background-size: 40px 40px;
          opacity: 0.5;
        }
        .bg-scan {
          position: absolute; top: 0; left: 0; width: 100%; height: 2px;
          background: rgba(0, 229, 255, 0.1);
          box-shadow: 0 0 10px rgba(0, 229, 255, 0.3);
          animation: scanline 8s linear infinite;
        }
        .bg-vignette {
          position: absolute; inset: 0;
          background: radial-gradient(circle, transparent 50%, rgba(5,7,10,0.8) 100%);
        }

        /* Layout */
        .soc-sidebar {
          width: 280px; background: rgba(5,7,10,0.8);
          border-right: 1px solid rgba(0, 229, 255, 0.1);
          backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
          display: flex; flex-direction: column;
          padding: 1.5rem;
          z-index: 10;
        }
        .soc-main-wrapper {
          flex: 1; display: flex; flex-direction: column; overflow: hidden;
        }
        
        /* Sidebar Elements */
        .sidebar-brand { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 2.5rem; }
        .logo-box { width: 36px; height: 36px; position: relative; }
        .brand-text { display: flex; flex-direction: column; letter-spacing: normal; }
        .b-title { font-weight: 600; font-size: 1.125rem; color: #f1f5f9; }
        .b-role { font-weight: 500; font-size: 0.875rem; color: #00e5ff; }

        .nav-header {
          font-size: 0.8rem; color: #94a3b8; font-weight: 600;
          letter-spacing: 1px; margin-bottom: 1rem; padding-left: 0.5rem; text-transform: uppercase;
        }
        .soc-nav { display: flex; flex-direction: column; gap: 0.25rem; }
        .soc-link {
          display: flex; align-items: center; gap: 0.75rem;
          padding: 0.75rem 1rem; border-radius: 6px;
          color: #cbd5e1; text-decoration: none; font-size: 0.95rem; font-weight: 500;
          letter-spacing: normal; text-transform: none; text-shadow: none;
          transition: all 0.2s; border: 1px solid transparent;
        }
        .soc-link .icon {
          font-size: 1.125rem; display: flex; align-items: center; justify-content: center;
        }
        .soc-link:hover {
          background: rgba(0, 229, 255, 0.05); color: #f1f5f9;
        }
        .soc-link.active {
          background: rgba(0, 229, 255, 0.1); color: #00e5ff;
          border-color: rgba(0, 229, 255, 0.2);
          box-shadow: 0 0 10px rgba(0,229,255,0.05);
          font-weight: 600;
        }
        
        .soc-logout {
          margin-top: auto; padding: 0.75rem; background: transparent;
          border: 1px solid rgba(239, 68, 68, 0.2); color: #ef4444; border-radius: 6px;
          cursor: pointer; transition: all 0.2s; font-size: 0.9rem; font-weight: 500;
          letter-spacing: normal;
        }
        .soc-logout:hover { background: rgba(239, 68, 68, 0.1); }

        /* Header */
        .soc-header {
          height: 64px; background: rgba(5,7,10,0.6); backdrop-filter: blur(10px);
          border-bottom: 1px solid rgba(0, 229, 255, 0.05);
          display: flex; justify-content: space-between; align-items: center;
          padding: 0 2rem; z-index: 10;
        }
        .h-left { font-weight: 600; font-size: 0.9rem; letter-spacing: 2px; color: #f1f5f9; }
        .h-right { display: flex; align-items: center; gap: 1.5rem; }
        .status-pill {
          display: flex; align-items: center; gap: 6px;
          background: rgba(16, 185, 129, 0.1); color: #10b981;
          padding: 4px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: 700;
          border: 1px solid rgba(16, 185, 129, 0.2);
        }
        .pulse-dot {
          width: 5px; height: 5px; background: #10b981; border-radius: 50%;
          animation: pulse 2s infinite;
        }
        .time-display { font-family: monospace; font-size: 0.85rem; color: #94a3b8; }
        .user-profile {
          display: flex; align-items: center; gap: 6px;
          font-size: 0.75rem; font-weight: 600; color: #94a3b8;
          border-left: 1px solid rgba(255,255,255,0.1); padding-left: 1.5rem;
        }

        /* Main Content Area */
        .soc-content { flex: 1; overflow-y: auto; padding: 2rem; }
        .content-inner { max-width: 1400px; margin: 0 auto; animation: pageEnter 0.4s ease forwards; }

        @keyframes scanline {
          0% { transform: translateY(-5vh); }
          100% { transform: translateY(105vh); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
        @keyframes pageEnter {
          0% { opacity: 0; transform: translateY(8px); }
          100% { opacity: 1; transform: translateY(0); }
        }
        
        @media (prefers-reduced-motion: reduce) {
          .bg-scan, .pulse-dot, .content-inner { animation: none !important; }
        }
      `}</style>
    </div>
  );
}

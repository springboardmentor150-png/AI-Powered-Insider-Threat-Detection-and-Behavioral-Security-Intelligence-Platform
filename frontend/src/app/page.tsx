import Link from "next/link";
import Image from "next/image";
import "./globals.css";

export default function PortalSelection() {
  return (
    <div className="landing-container">
      {/* 4. & 5. Premium Cybersecurity Background (CSS Only) */}
      <div className="bg-base"></div>
      <div className="bg-grid"></div>
      <div className="bg-glow-cyan"></div>
      <div className="bg-glow-violet"></div>
      <div className="bg-scanline"></div>
      <div className="bg-radar">
        <div className="radar-ring r1"></div>
        <div className="radar-ring r2"></div>
      </div>
      <div className="bg-vignette"></div>

      {/* 2. Top Header */}
      <header className="page-header">
        <div className="header-left">
          <div className="header-logo-container">
            <Image src="/logo.png" alt="ITBIS" fill style={{ objectFit: 'contain' }} priority />
          </div>
          <div className="header-brand-text">
            <span>INSIDER THREAT</span>
            <span>DETECTION</span>
          </div>
        </div>
        <div className="header-right">
          <div className="status-pill">
            <span className="live-dot"></span>
            SYSTEM LIVE
          </div>
          <div className="profile-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </div>
        </div>
      </header>

      {/* 3. Hero & Cards (Locked to 100vh on Desktop) */}
      <main className="landing-main">
        
        {/* 6. Hero Section */}
        <section className="hero-section">
          <div className="hero-status">
            <span className="live-dot-cyan"></span> SECURITY PLATFORM ONLINE
          </div>
          <h1 className="hero-title">SELECT YOUR PORTAL</h1>
          <h2 className="hero-subtitle">BEHAVIORAL SECURITY INTELLIGENCE PLATFORM </h2>
          <p className="hero-desc">
            Detect abnormal employee behavior, identify insider-risk signals, and protect critical organizational assets through modern behavioral security intelligence.
          </p>
        </section>

        {/* 7. & 8. & 9. Five Portal Cards */}
        <section className="cards-section">
          <div className="cards-grid">
            
            {/* Removed EMPLOYEE portal because they are monitored entities, not users */}

            {/* ADMIN (Red) */}
            <Link href="/login" className="portal-card c-admin" style={{ textDecoration: 'none' }}>
              <div className="card-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                </svg>
              </div>
              <h3 className="card-title">ADMIN</h3>
              <p className="card-desc">Manage users, employees, access policies and platform configuration.</p>
            </Link>

            {/* SOC ENGINEER (Amber) */}
            <Link href="/login" className="portal-card c-soc" style={{ textDecoration: 'none' }}>
              <div className="card-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                </svg>
              </div>
              <h3 className="card-title">SOC ENGINEER</h3>
              <p className="card-desc">Monitor telemetry, infrastructure activity and security operations.</p>
            </Link>

            {/* SECURITY ANALYST (Violet) */}
            <Link href="/login" className="portal-card c-analyst" style={{ textDecoration: 'none' }}>
              <div className="card-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
                </svg>
              </div>
              <h3 className="card-title">SECURITY ANALYST</h3>
              <p className="card-desc">Investigate behavioral anomalies, alerts and security incidents.</p>
            </Link>

            {/* MANAGER (Green) */}
            <Link href="/login" className="portal-card c-manager" style={{ textDecoration: 'none' }}>
              <div className="card-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                </svg>
              </div>
              <h3 className="card-title">MANAGER</h3>
              <p className="card-desc">Review team security posture, employee risk and organizational insights.</p>
            </Link>

          </div>
        </section>
      </main>

      <style>{`
        /* =========================================
           GLOBAL LAYOUT & 100VH LOCK 
           ========================================= */
        .landing-container {
          position: relative;
          width: 100%;
          background: #05070a;
          color: #f1f5f9;
          font-family: inherit;
        }

        /* Desktop specific 100vh NO-SCROLL constraint */
        @media (min-width: 1024px) {
          .landing-container {
            height: 100vh;
            min-height: 100vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
          }
        }

        /* =========================================
           4. & 5. CYBER BACKGROUND
           ========================================= */
        .bg-base {
          position: fixed; inset: 0; z-index: 0;
          background: #05070a;
        }
        
        .bg-grid {
          position: fixed; inset: 0; z-index: 1;
          background-image: 
            linear-gradient(rgba(0, 229, 255, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 229, 255, 0.05) 1px, transparent 1px);
          background-size: 60px 60px;
          opacity: 0.5;
          transform: perspective(600px) rotateX(45deg) scale(2);
          transform-origin: top;
          animation: slideGrid 30s linear infinite;
        }

        .bg-glow-cyan {
          position: fixed; top: -10%; left: -10%; width: 50vw; height: 50vh; z-index: 2;
          background: radial-gradient(circle, rgba(0, 229, 255, 0.08) 0%, transparent 60%);
          animation: pulseGlow 8s ease-in-out infinite alternate;
        }
        
        .bg-glow-violet {
          position: fixed; bottom: -10%; right: -10%; width: 60vw; height: 60vh; z-index: 2;
          background: radial-gradient(circle, rgba(139, 92, 246, 0.06) 0%, transparent 60%);
          animation: pulseGlow 12s ease-in-out infinite alternate-reverse;
        }

        .bg-scanline {
          position: fixed; top: 0; left: 0; right: 0; height: 2px; z-index: 3;
          background: rgba(0, 229, 255, 0.15);
          box-shadow: 0 0 10px rgba(0, 229, 255, 0.3);
          animation: scanlineMove 6s linear infinite;
        }

        .bg-radar {
          position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 1;
          width: 80vw; height: 80vw; max-width: 1200px; max-height: 1200px;
          opacity: 0.15;
          pointer-events: none;
        }
        .radar-ring {
          position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
          border: 1px dashed rgba(0, 229, 255, 0.4); border-radius: 50%;
        }
        .r1 { width: 100%; height: 100%; border-width: 1px; }
        .r2 { width: 60%; height: 60%; border-width: 1px; border-style: solid; opacity: 0.5; }

        .bg-vignette {
          position: fixed; inset: 0; z-index: 4;
          background: radial-gradient(circle, transparent 40%, rgba(5, 7, 10, 0.9) 100%);
          pointer-events: none;
        }

        /* =========================================
           2. HEADER
           ========================================= */
        .page-header {
          position: relative; z-index: 20;
          display: flex; justify-content: space-between; align-items: center;
          padding: 1.25rem 2rem;
          background: transparent;
        }
        
        .header-left {
          display: flex; align-items: center; gap: 1rem;
        }
        .header-logo-container {
          position: relative; width: 44px; height: 44px;
        }
        .header-brand-text {
          display: flex; flex-direction: column;
          font-size: 0.95rem; font-weight: 700; letter-spacing: 2px;
          line-height: 1.2; color: #f8fafc;
        }
        .header-brand-text span:last-child {
          color: rgba(0, 229, 255, 0.8);
        }

        .header-right {
          display: flex; align-items: center; gap: 1.5rem;
        }
        .status-pill {
          display: flex; align-items: center; gap: 0.5rem;
          font-size: 0.75rem; font-weight: 600; letter-spacing: 1px;
          color: #10b981;
          background: rgba(16, 185, 129, 0.05);
          border: 1px solid rgba(16, 185, 129, 0.2);
          padding: 0.35rem 0.875rem;
          border-radius: 999px;
        }
        .live-dot {
          width: 6px; height: 6px; border-radius: 50%;
          background: #10b981;
          box-shadow: 0 0 6px #10b981;
          animation: pulseStatus 2s infinite ease-in-out;
        }
        .profile-icon {
          width: 32px; height: 32px;
          border-radius: 50%;
          border: 1px solid rgba(255,255,255,0.1);
          background: rgba(0,0,0,0.3);
          display: flex; align-items: center; justify-content: center;
          color: #94a3b8;
        }

        /* =========================================
           MAIN LAYOUT constraints
           ========================================= */
        .landing-main {
          position: relative; z-index: 10;
          flex: 1; 
          display: flex; flex-direction: column; 
          justify-content: center; align-items: center;
          width: 100%; max-width: 1400px; margin: 0 auto;
          padding: 0 2rem;
        }

        /* =========================================
           6. HERO SECTION
           ========================================= */
        .hero-section {
          text-align: center;
          margin-bottom: 2.5rem; /* tight margin for 100vh lock */
          display: flex; flex-direction: column; align-items: center;
        }
        .hero-status {
          display: flex; align-items: center; gap: 6px;
          font-size: 0.65rem; font-weight: 600; letter-spacing: 1.5px;
          color: rgba(255,255,255,0.6);
          margin-bottom: 1.25rem;
          animation: fadeUpIn 0.8s ease-out forwards;
        }
        .live-dot-cyan {
          width: 5px; height: 5px; border-radius: 50%;
          background: var(--accent); box-shadow: 0 0 5px var(--accent);
          animation: pulseStatus 2s infinite ease-in-out;
        }
        .hero-title {
          font-size: clamp(2rem, 4vw, 3.25rem);
          font-weight: 800; letter-spacing: 4px;
          margin: 0 0 0.25rem 0;
          color: #ffffff;
          opacity: 0; animation: fadeUpIn 0.8s ease-out 0.1s forwards;
        }
        .hero-subtitle {
          font-size: clamp(0.75rem, 1.5vw, 1rem);
          font-weight: 600; letter-spacing: 3px;
          color: var(--accent);
          margin: 0 0 1rem 0;
          opacity: 0; animation: fadeUpIn 0.8s ease-out 0.2s forwards;
        }
        .hero-desc {
          max-width: 580px;
          font-size: 0.95rem; line-height: 1.5; color: #94a3b8;
          margin: 0;
          opacity: 0; animation: fadeUpIn 0.8s ease-out 0.3s forwards;
        }

        /* =========================================
           7. CARDS LAYOUT
           ========================================= */
        .cards-section {
          width: 100%;
        }
        .cards-grid {
          display: grid;
          /* 4 Columns for the 4 core roles */
          grid-template-columns: repeat(4, 1fr);
          gap: 1.25rem;
          width: 100%;
        }

        /* RESPONSIVE OVERRIDES */
        @media (max-width: 1023px) {
          .landing-main { padding-top: 3rem; padding-bottom: 3rem; }
          .cards-grid { grid-template-columns: repeat(3, 1fr); }
        }
        @media (max-width: 768px) {
          .cards-grid { grid-template-columns: repeat(2, 1fr); gap: 1rem; }
          .page-header { padding: 1rem; }
          .header-brand-text { display: none; }
        }
        @media (max-width: 480px) {
          .cards-grid { grid-template-columns: 1fr; }
        }

        /* =========================================
           8. CARD DESIGN
           ========================================= */
        .portal-card {
           background: rgba(10, 16, 30, 0.70);
           backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
           border: 1px solid rgba(255, 255, 255, 0.05); /* base subtle border */
           border-radius: 18px;
           padding: 1.5rem 1.25rem;
           text-align: center;
           display: flex; flex-direction: column; align-items: center;
           height: 100%;
           box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
           transition: transform 0.3s cubic-bezier(0.2, 0.8, 0.2, 1), 
                       border-color 0.3s ease, 
                       box-shadow 0.3s ease;
           
           /* initial load state */
           opacity: 0;
           transform: translateY(15px) scale(0.96);
        }
        /* Entrance stagger timing (approx 80ms diff) */
        .c-employee { animation: cardEnter 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) 0.40s forwards; }
        .c-admin    { animation: cardEnter 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) 0.48s forwards; }
        .c-soc      { animation: cardEnter 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) 0.56s forwards; }
        .c-analyst  { animation: cardEnter 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) 0.64s forwards; }
        .c-manager  { animation: cardEnter 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) 0.72s forwards; }

        .card-icon {
          width: 50px; height: 50px;
          border-radius: 50%;
          background: rgba(0,0,0,0.4);
          display: flex; align-items: center; justify-content: center;
          margin-bottom: 1.25rem;
          border: 1px solid rgba(255,255,255,0.03);
          transition: transform 0.3s ease;
        }

        .card-title {
          font-size: 0.95rem; font-weight: 700; letter-spacing: 1.5px;
          color: #f1f5f9; margin: 0 0 0.5rem 0;
        }

        .card-desc {
          font-size: 0.75rem; line-height: 1.5; color: #94a3b8; margin: 0;
        }

        /* =========================================
           9. & 10. ROLE ACCENTS & HOVERS
           ========================================= */
        
        /* Employee: Cyan/Blue */
        .c-employee { --clr: #00e5ff; }
        .c-employee .card-icon { color: var(--clr); }
        .c-employee:hover {
          border-color: rgba(0, 229, 255, 0.4);
          box-shadow: 0 10px 30px rgba(0,0,0,0.5), 0 0 15px rgba(0, 229, 255, 0.1);
          transform: translateY(-8px);
        }

        /* Admin: Red/Crimson */
        .c-admin { --clr: #f43f5e; }
        .c-admin .card-icon { color: var(--clr); }
        .c-admin:hover {
          border-color: rgba(244, 63, 94, 0.4);
          box-shadow: 0 10px 30px rgba(0,0,0,0.5), 0 0 15px rgba(244, 63, 94, 0.1);
          transform: translateY(-8px);
        }

        /* SOC Engineer: Amber/Orange */
        .c-soc { --clr: #f59e0b; }
        .c-soc .card-icon { color: var(--clr); }
        .c-soc:hover {
          border-color: rgba(245, 158, 11, 0.4);
          box-shadow: 0 10px 30px rgba(0,0,0,0.5), 0 0 15px rgba(245, 158, 11, 0.1);
          transform: translateY(-8px);
        }

        /* Security Analyst: Violet/Magenta */
        .c-analyst { --clr: #a855f7; }
        .c-analyst .card-icon { color: var(--clr); }
        .c-analyst:hover {
          border-color: rgba(168, 85, 247, 0.4);
          box-shadow: 0 10px 30px rgba(0,0,0,0.5), 0 0 15px rgba(168, 85, 247, 0.1);
          transform: translateY(-8px);
        }

        /* Manager: Green/Emerald */
        .c-manager { --clr: #10b981; }
        .c-manager .card-icon { color: var(--clr); }
        .c-manager:hover {
          border-color: rgba(16, 185, 129, 0.4);
          box-shadow: 0 10px 30px rgba(0,0,0,0.5), 0 0 15px rgba(16, 185, 129, 0.1);
          transform: translateY(-8px);
        }

        /* Hover Icon glow boost */
        .portal-card:hover .card-icon {
          filter: drop-shadow(0 0 8px var(--clr));
        }

        /* =========================================
           11. ANIMATIONS
           ========================================= */
        @keyframes scanlineMove {
          0% { transform: translateY(-5vh); }
          100% { transform: translateY(105vh); }
        }
        @keyframes slideGrid {
          0% { transform: perspective(600px) rotateX(45deg) scale(2) translateY(0); }
          100% { transform: perspective(600px) rotateX(45deg) scale(2) translateY(60px); }
        }
        @keyframes pulseGlow {
          0% { opacity: 0.6; transform: scale(0.9); }
          100% { opacity: 1; transform: scale(1.1); }
        }
        @keyframes pulseStatus {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
        @keyframes fadeUpIn {
          0% { opacity: 0; transform: translateY(15px); }
          100% { opacity: 1; transform: translateY(0); }
        }
        @keyframes cardEnter {
          100% { opacity: 1; transform: translateY(0) scale(1); }
        }

        /* =========================================
           13. REDUCED MOTION OVERRIDE
           ========================================= */
        @media (prefers-reduced-motion: reduce) {
          .bg-scanline, .bg-grid, .bg-glow-cyan, .bg-glow-violet {
            animation: none !important;
          }
          .hero-status, .hero-title, .hero-subtitle, .hero-desc, .portal-card {
            animation: none !important;
            opacity: 1 !important;
            transform: none !important;
          }
          .portal-card:hover {
            transform: none !important;
          }
        }
      `}</style>
    </div>
  );
}

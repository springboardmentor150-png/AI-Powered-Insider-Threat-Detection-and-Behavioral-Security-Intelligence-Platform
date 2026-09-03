// "use client";

// import { useEffect, useState } from "react";
// import api from "@/lib/api";

// export default function Home() {
//   const [status, setStatus] = useState("");
//   const [error, setError] = useState(false);

//   useEffect(() => {
//     api
//       .get("/")
//       .then((res) => setStatus(res.data.status))
//       .catch((err) => {
//         console.error(err);
//         setError(true);
//       });
//   }, []);

//   return (
//     <div className="max-w-xl">
//       <h1 className="text-2xl font-semibold mb-4">
//         {status || "Connecting to backend..."}
//       </h1>
//       {error && (
//         <p className="text-red-600">
//           Could not reach the backend. Make sure `uvicorn app.main:app --reload`
//           is running on port 8000, and that NEXT_PUBLIC_API_URL in .env.local
//           points at it.
//         </p>
//       )}
//       <p className="text-slate-500 mt-4">
//         This page confirms the frontend and backend can talk to each other
//         (Day 3-4). Go to <a className="underline" href="/login">Login</a> to
//         test authentication (Day 5-6), then{" "}
//         <a className="underline" href="/employees">Employees</a> to test
//         profile management (Day 7-8).
//       </p>
//     </div>
//   );
// }


"use client";

import Link from "next/link";

const features = [
  {
    number: "01",
    title: "Authentication & RBAC",
    description:
      "Secure platform access with JWT authentication and role-based permissions for security teams.",
    tags: ["JWT", "RBAC", "Secure Access"],
  },
  {
    number: "02",
    title: "Employee Intelligence",
    description:
      "Maintain employee identities, departments, reporting relationships, devices and access privileges.",
    tags: ["Profiles", "Hierarchy", "Access"],
  },
  {
    number: "03",
    title: "Behavior Monitoring",
    description:
      "Build the foundation for detecting unusual employee activity and potential insider-threat behavior.",
    tags: ["Activity", "Behavior", "Risk"],
  },
];

const roles = [
  "Security Analyst",
  "SOC Engineer",
  "Security Manager",
  "Administrator",
];

export default function HomePage() {
  return (
    <main className="itbis-home">

      {/* Hero */}
      <section className="hero-section">
        <div className="hero-grid">

          <div className="hero-content">
            <div className="status-badge">
              <span className="status-dot"></span>
              Security Intelligence Platform
            </div>

            <h1>
              Insider Threat
              <span> Behavioral Intelligence</span>
            </h1>

            <p className="hero-description">
              ITBIS is a security platform designed to help organizations
              understand employee behavior, manage identities and access,
              and build a strong foundation for insider-threat detection.
            </p>

            <div className="hero-actions">
              <Link href="/login" className="hero-primary">
                Sign in
                <span>→</span>
              </Link>

              <Link href="/signup" className="hero-secondary">
                Create account
              </Link>
            </div>

            <div className="hero-meta">
              <div>
                <strong>4</strong>
                <span>Platform Roles</span>
              </div>

              <div>
                <strong>RBAC</strong>
                <span>Access Control</span>
              </div>

              <div>
                <strong>24/7</strong>
                <span>Security Ready</span>
              </div>
            </div>
          </div>

          {/* Security visual */}
          <div className="security-panel">

            <div className="panel-header">
              <div>
                <span className="panel-label">ITBIS</span>
                <h2>Security Overview</h2>
              </div>

              <span className="live-badge">
                <span></span>
                ACTIVE
              </span>
            </div>

            <div className="security-core">
              <div className="core-ring ring-one"></div>
              <div className="core-ring ring-two"></div>
              <div className="core-center">
                <span>IT</span>
                <strong>SECURE</strong>
              </div>
            </div>

            <div className="security-stats">
              <div>
                <span>Identity</span>
                <strong>Protected</strong>
              </div>

              <div>
                <span>Access Control</span>
                <strong>Enabled</strong>
              </div>

              <div>
                <span>Monitoring</span>
                <strong>Ready</strong>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* Platform introduction */}
      <section className="platform-section">

        <div className="section-heading">
          <span className="eyebrow">PLATFORM FOUNDATION</span>

          <h2>
            Security intelligence built
            <span> around people and behavior.</span>
          </h2>

          <p>
            ITBIS brings identity management, access control and employee
            intelligence together in one platform. The current foundation
            prepares the system for advanced behavioral analytics and
            insider-threat detection.
          </p>
        </div>

        <div className="feature-grid">
          {features.map((feature) => (
            <article className="feature-card" key={feature.number}>

              <div className="feature-top">
                <span className="feature-number">
                  {feature.number}
                </span>

                <span className="feature-arrow">↗</span>
              </div>

              <h3>{feature.title}</h3>

              <p>{feature.description}</p>

              <div className="feature-tags">
                {feature.tags.map((tag) => (
                  <span key={tag}>{tag}</span>
                ))}
              </div>

            </article>
          ))}
        </div>

      </section>

      {/* Access section */}
      <section className="access-section">

        <div className="access-content">

          <span className="eyebrow">CONTROLLED ACCESS</span>

          <h2>
            Designed for
            <span> security teams.</span>
          </h2>

          <p>
            ITBIS uses role-based access control so each security professional
            can work with the information and operations appropriate to their
            responsibility.
          </p>

          <div className="role-list">
            {roles.map((role, index) => (
              <div className="role-item" key={role}>
                <span>0{index + 1}</span>
                <strong>{role}</strong>
              </div>
            ))}
          </div>

        </div>

        <div className="access-card">

          <div className="access-card-header">
            <span>PLATFORM STATUS</span>
            <span className="secure-status">● Operational</span>
          </div>

          <div className="status-line">
            <span>API Gateway</span>
            <strong>Online</strong>
          </div>

          <div className="status-line">
            <span>Authentication</span>
            <strong>Protected</strong>
          </div>

          <div className="status-line">
            <span>Employee Intelligence</span>
            <strong>Ready</strong>
          </div>

          <Link href="/employees" className="access-button">
            Open Employee Intelligence
            <span>→</span>
          </Link>

        </div>

      </section>

      {/* CTA */}
      <section className="cta-section">

        <div>
          <span className="eyebrow">GET STARTED</span>

          <h2>
            Ready to enter the
            <span> ITBIS platform?</span>
          </h2>

          <p>
            Sign in to access the platform or create an account to begin.
          </p>
        </div>

        <div className="cta-actions">

          <Link href="/login" className="hero-primary">
            Sign in
            <span>→</span>
          </Link>

          <Link href="/signup" className="hero-secondary">
            Create account
          </Link>

        </div>

      </section>

    </main>
  );
}
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import ThemeToggle from "@/components/ThemeToggle";
import { verifyAuthentication } from "@/lib/auth";

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    verifyAuthentication()
      .then(() => {
        setIsAuthenticated(true);
        window.location.href = "/dashboard";
      })
      .catch(() => {
        setIsAuthenticated(false);
      });
  }, []);

  return (
    <main className="min-h-screen bg-[var(--background)] text-[var(--foreground)] flex flex-col justify-between">
      {/* Top Navbar */}
      <header className="flex h-20 items-center justify-between border-b border-[var(--border)] px-8 max-w-7xl mx-auto w-full">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--primary)] font-bold text-white shadow-md">
            I
          </div>
          <div>
            <h1 className="font-extrabold tracking-tight text-lg">ITBIS</h1>
            <p className="text-[10px] tracking-widest uppercase text-[var(--muted)]">Security Intelligence</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <ThemeToggle />
          <Link
            href="/login"
            className="rounded-xl border border-[var(--border)] px-4 py-2 text-xs font-semibold text-[var(--foreground)] hover:border-[var(--primary)] hover:text-[var(--primary)] transition"
          >
            Sign In
          </Link>
          <Link
            href="/signup"
            className="rounded-xl bg-[var(--primary)] px-4 py-2 text-xs font-semibold text-white shadow-md hover:bg-[var(--primary-hover)] transition"
          >
            Create Account
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <div className="flex-1 flex items-center justify-center py-16 px-6">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          {/* Status Badge */}
          <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-4 py-1 text-xs font-semibold text-emerald-400">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            UEBA Real-Time Behavioral Threat Detection Active
          </div>

          <h1 className="text-4xl md:text-6xl font-black tracking-tight leading-tight">
            AI-Powered Insider Threat & <br />
            <span className="bg-gradient-to-r from-purple-400 via-blue-400 to-indigo-500 bg-clip-text text-transparent">
              Behavioral Security Intelligence
            </span>
          </h1>

          <p className="text-sm md:text-base text-[var(--muted)] max-w-2xl mx-auto leading-relaxed">
            Continuously detect abnormal data exfiltration, privilege misuse, and off-hours access anomalies across your workforce using unsupervised Machine Learning, 5-factor risk scoring, and Explainable AI.
          </p>

          {/* Action CTAs */}
          <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
            <Link
              href={isAuthenticated ? "/dashboard" : "/login"}
              className="rounded-2xl bg-[var(--primary)] px-8 py-3.5 text-sm font-bold text-white shadow-lg shadow-purple-500/25 hover:bg-[var(--primary-hover)] transition"
            >
              Access Security Console →
            </Link>
            <Link
              href="/signup"
              className="rounded-2xl border border-[var(--border)] bg-[var(--card)] px-8 py-3.5 text-sm font-bold text-[var(--foreground)] hover:border-[var(--primary)] transition"
            >
              Deploy Analyst Profile
            </Link>
          </div>

          {/* 4 Pillars Feature Cards */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 pt-12 text-left">
            <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5 space-y-2">
              <span className="text-2xl">🧠</span>
              <h3 className="text-sm font-bold">Unsupervised ML & XAI</h3>
              <p className="text-xs text-[var(--muted)] leading-relaxed">
                Isolation Forest outlier detection with feature attribution breakdown and active learning feedback.
              </p>
            </div>

            <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5 space-y-2">
              <span className="text-2xl">⚡</span>
              <h3 className="text-sm font-bold">5-Factor Risk Scoring</h3>
              <p className="text-xs text-[var(--muted)] leading-relaxed">
                Dynamic risk tiering calibrating behavioral anomalies, privilege, data access, and peer group variance.
              </p>
            </div>

            <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5 space-y-2">
              <span className="text-2xl">🚨</span>
              <h3 className="text-sm font-bold">Incident Investigation</h3>
              <p className="text-xs text-[var(--muted)] leading-relaxed">
                Chronological audit timeline reconstruction with evidence tracking, SLA escalation, and triage queues.
              </p>
            </div>

            <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5 space-y-2">
              <span className="text-2xl">📜</span>
              <h3 className="text-sm font-bold">Compliance Audit Trail</h3>
              <p className="text-xs text-[var(--muted)] leading-relaxed">
                Platform operational action logging and ReportLab PDF risk dossiers aligning with SOC 2 & ISO 27001.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-[var(--border)] py-6 text-center text-xs text-[var(--muted)]">
        <p>ITBIS • Insider Threat Behavioral Intelligence System • Production Operations Console</p>
      </footer>
    </main>
  );
}
"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Shield,
  Lock,
  ArrowRight,
  ChevronDown,
  Activity,
  BrainCircuit,
  TrendingUp,
  AlertTriangle,
  FileSearch,
  ShieldAlert,
  Server,
  Database,
  CheckCircle2,
  Menu,
  X,
  Layers,
  FileText,
  Clock,
  ShieldCheck,
} from "lucide-react";

export default function LandingPage() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#050B14] text-[#F4F8FF] flex flex-col justify-between selection:bg-[#00A8FF]/30 selection:text-[#00E5FF]">
      {/* Background Cyber Grid Lines */}
      <div className="fixed inset-0 pointer-events-none opacity-20 bg-[linear-gradient(to_right,#0B1626_1px,transparent_1px),linear-gradient(to_bottom,#0B1626_1px,transparent_1px)] bg-[size:4rem_4rem]" />

      {/* ========================================================================= */}
      {/* 1. TOP NAVIGATION BAR */}
      {/* ========================================================================= */}
      <header className="sticky top-0 z-50 border-b border-[#132B45] bg-[#0B1626]/90 backdrop-blur-md px-6 py-4 transition-all">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-lg bg-[#050B14] border border-[#00A8FF]/50 flex items-center justify-center text-[#00E5FF] shadow-[0_0_12px_rgba(0,168,255,0.2)] group-hover:border-[#00E5FF] transition">
              <Shield className="w-5 h-5 text-[#00E5FF]" />
            </div>
            <div>
              <span className="font-black tracking-wider text-lg text-[#F4F8FF] leading-none block">
                ITBIS
              </span>
              <span className="text-[10px] text-[#00A8FF] font-mono font-bold tracking-widest uppercase block mt-0.5">
                Behavioral Intel
              </span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-8 text-xs font-semibold tracking-wider text-[#8E9EB5]">
            <a
              href="#pipeline"
              className="hover:text-[#00E5FF] transition duration-150 uppercase"
            >
              Platform
            </a>
            <a
              href="#features"
              className="hover:text-[#00E5FF] transition duration-150 uppercase"
            >
              Capabilities
            </a>
            <a
              href="#architecture"
              className="hover:text-[#00E5FF] transition duration-150 uppercase"
            >
              Security &amp; Architecture
            </a>
          </nav>

          {/* CTA & Mobile Toggle */}
          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="px-5 py-2.5 rounded-lg text-xs font-bold bg-[#00A8FF] hover:bg-[#00E5FF] text-[#050B14] transition duration-200 flex items-center gap-2 shadow-lg shadow-[#00A8FF]/20 cursor-pointer"
            >
              <Lock className="w-3.5 h-3.5" />
              <span>Access SOC Console</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>

            <button
              onClick={() => setMobileNavOpen(!mobileNavOpen)}
              className="md:hidden p-2 rounded-lg bg-[#050B14] border border-[#132B45] text-[#8E9EB5] hover:text-[#00E5FF]"
              aria-label="Toggle Navigation Menu"
            >
              {mobileNavOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Dropdown Menu */}
        {mobileNavOpen && (
          <div className="md:hidden mt-4 pt-4 border-t border-[#132B45] flex flex-col gap-3 text-xs font-semibold uppercase tracking-wider text-[#8E9EB5]">
            <a
              href="#pipeline"
              onClick={() => setMobileNavOpen(false)}
              className="px-3 py-2 rounded-lg hover:bg-[#050B14] hover:text-[#00E5FF] transition"
            >
              Platform
            </a>
            <a
              href="#features"
              onClick={() => setMobileNavOpen(false)}
              className="px-3 py-2 rounded-lg hover:bg-[#050B14] hover:text-[#00E5FF] transition"
            >
              Capabilities
            </a>
            <a
              href="#architecture"
              onClick={() => setMobileNavOpen(false)}
              className="px-3 py-2 rounded-lg hover:bg-[#050B14] hover:text-[#00E5FF] transition"
            >
              Security &amp; Architecture
            </a>
          </div>
        )}
      </header>

      {/* ========================================================================= */}
      {/* 2. HERO SECTION */}
      {/* ========================================================================= */}
      <section className="relative z-10 flex-1 flex flex-col items-center justify-center px-6 pt-20 pb-16 max-w-5xl mx-auto w-full text-center">
        {/* Sub-Header Pill */}
        <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-[#0B1626] border border-[#00A8FF]/40 text-[#00E5FF] text-xs font-mono mb-8 shadow-inner">
          <span className="w-2 h-2 rounded-full bg-[#00E5FF] animate-pulse"></span>
          INSIDER THREAT BEHAVIORAL INTELLIGENCE SYSTEM
        </div>

        {/* Main Heading */}
        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black tracking-tight text-[#F4F8FF] leading-tight uppercase">
          INSIDER THREAT <br />
          <span className="text-[#00E5FF]">BEHAVIORAL INTELLIGENCE</span>
        </h1>

        {/* Subheading */}
        <p className="mt-6 text-base sm:text-xl font-medium text-[#F4F8FF]/90 max-w-2xl leading-relaxed">
          Detect anomalous employee behavior.
          <br className="hidden sm:inline" /> Assess risk. Investigate threats. Respond with confidence.
        </p>

        {/* Short Professional Description */}
        <p className="mt-4 text-xs sm:text-sm text-[#8E9EB5] max-w-2xl leading-relaxed">
          ITBIS is an AI-powered platform designed to monitor employee activity, identify anomalous behavior,
          calculate insider-risk levels, and help SOC operators investigate security incidents before data
          exfiltration occurs.
        </p>

        {/* CTA Buttons */}
        <div className="mt-10 flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto">
          <Link
            href="/login"
            className="w-full sm:w-auto px-8 py-4 bg-[#00A8FF] hover:bg-[#00E5FF] text-[#050B14] font-bold text-sm tracking-wide rounded-lg transition duration-200 flex items-center justify-center gap-2.5 shadow-xl shadow-[#00A8FF]/20 cursor-pointer"
          >
            <Lock className="w-4 h-4" />
            <span>ACCESS SOC CONSOLE</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          <a
            href="#pipeline"
            className="w-full sm:w-auto px-8 py-4 bg-[#0B1626] hover:bg-[#132B45] border border-[#132B45] hover:border-[#00A8FF] text-[#F4F8FF] font-semibold text-sm rounded-lg transition duration-200 flex items-center justify-center gap-2 cursor-pointer"
          >
            <span>Explore Platform</span>
            <ChevronDown className="w-4 h-4 text-[#00A8FF]" />
          </a>
        </div>

        {/* Trust & Readiness Indicators */}
        <div className="mt-14 pt-8 border-t border-[#132B45] w-full grid grid-cols-2 sm:grid-cols-4 gap-4 text-center text-[11px] font-mono text-[#8E9EB5]">
          <div className="p-3 rounded-lg bg-[#0B1626]/50 border border-[#132B45]/60">
            <div className="text-[#00E5FF] font-bold text-sm">Continuous</div>
            <div className="text-[10px] mt-0.5">Telemetry Ingress</div>
          </div>
          <div className="p-3 rounded-lg bg-[#0B1626]/50 border border-[#132B45]/60">
            <div className="text-[#00E5FF] font-bold text-sm">Dynamic</div>
            <div className="text-[10px] mt-0.5">Risk Scoring Model</div>
          </div>
          <div className="p-3 rounded-lg bg-[#0B1626]/50 border border-[#132B45]/60">
            <div className="text-[#00E5FF] font-bold text-sm">Multi-Vector</div>
            <div className="text-[10px] mt-0.5">Anomaly Detection</div>
          </div>
          <div className="p-3 rounded-lg bg-[#0B1626]/50 border border-[#132B45]/60">
            <div className="text-[#00E5FF] font-bold text-sm">End-to-End</div>
            <div className="text-[10px] mt-0.5">Incident Lifecycle</div>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 3. THREAT DETECTION FLOW (PIPELINE ARCHITECTURE) */}
      {/* ========================================================================= */}
      <section id="pipeline" className="relative z-10 px-6 py-20 bg-[#0B1626]/40 border-y border-[#132B45]">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0B1626] border border-[#00A8FF]/30 text-[#00A8FF] text-[11px] font-mono uppercase mb-3">
              Threat Detection Lifecycle
            </div>
            <h2 className="text-2xl sm:text-4xl font-black tracking-tight text-[#F4F8FF] uppercase">
              End-to-End Intelligence Pipeline
            </h2>
            <p className="mt-3 text-xs sm:text-sm text-[#8E9EB5] max-w-xl mx-auto">
              How ITBIS continuously converts raw employee telemetry into actionable security intelligence and incident containment.
            </p>
          </div>

          {/* Pipeline Visual Flow */}
          <div className="grid grid-cols-1 md:grid-cols-7 gap-3 relative">
            {/* Step 1 */}
            <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-4 flex flex-col items-center text-center shadow-lg relative group hover:border-[#00A8FF]/50 transition">
              <div className="w-10 h-10 rounded-lg bg-[#050B14] border border-[#00A8FF]/40 text-[#00E5FF] flex items-center justify-center mb-3">
                <Activity className="w-5 h-5" />
              </div>
              <div className="text-[10px] font-mono text-[#00A8FF] font-bold uppercase">Step 01</div>
              <h3 className="text-xs font-bold text-[#F4F8FF] mt-1 mb-1">Employee Activity</h3>
              <p className="text-[11px] text-[#8E9EB5] leading-snug">
                Telemetry ingestion across logins, downloads, and transfers.
              </p>
            </div>

            {/* Step 2 */}
            <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-4 flex flex-col items-center text-center shadow-lg relative group hover:border-[#00A8FF]/50 transition">
              <div className="w-10 h-10 rounded-lg bg-[#050B14] border border-[#00A8FF]/40 text-[#00E5FF] flex items-center justify-center mb-3">
                <BrainCircuit className="w-5 h-5" />
              </div>
              <div className="text-[10px] font-mono text-[#00A8FF] font-bold uppercase">Step 02</div>
              <h3 className="text-xs font-bold text-[#F4F8FF] mt-1 mb-1">Behavioral Baseline</h3>
              <p className="text-[11px] text-[#8E9EB5] leading-snug">
                Statistical profiling of typical access hours, devices, and volume.
              </p>
            </div>

            {/* Step 3 */}
            <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-4 flex flex-col items-center text-center shadow-lg relative group hover:border-[#00A8FF]/50 transition">
              <div className="w-10 h-10 rounded-lg bg-[#050B14] border border-[#00A8FF]/40 text-[#00E5FF] flex items-center justify-center mb-3">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div className="text-[10px] font-mono text-[#00A8FF] font-bold uppercase">Step 03</div>
              <h3 className="text-xs font-bold text-[#F4F8FF] mt-1 mb-1">Anomaly Detection</h3>
              <p className="text-[11px] text-[#8E9EB5] leading-snug">
                Rule evaluation for off-hours spikes, volume bursts, and privilege drift.
              </p>
            </div>

            {/* Step 4 */}
            <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-4 flex flex-col items-center text-center shadow-lg relative group hover:border-[#00A8FF]/50 transition">
              <div className="w-10 h-10 rounded-lg bg-[#050B14] border border-[#00A8FF]/40 text-[#00E5FF] flex items-center justify-center mb-3">
                <TrendingUp className="w-5 h-5" />
              </div>
              <div className="text-[10px] font-mono text-[#00A8FF] font-bold uppercase">Step 04</div>
              <h3 className="text-xs font-bold text-[#F4F8FF] mt-1 mb-1">Risk Scoring</h3>
              <p className="text-[11px] text-[#8E9EB5] leading-snug">
                Bayesian threat weight calculation mapped from Low to Critical.
              </p>
            </div>

            {/* Step 5 */}
            <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-4 flex flex-col items-center text-center shadow-lg relative group hover:border-[#00A8FF]/50 transition">
              <div className="w-10 h-10 rounded-lg bg-[#050B14] border border-[#00A8FF]/40 text-[#00E5FF] flex items-center justify-center mb-3">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <div className="text-[10px] font-mono text-[#00A8FF] font-bold uppercase">Step 05</div>
              <h3 className="text-xs font-bold text-[#F4F8FF] mt-1 mb-1">Security Alert</h3>
              <p className="text-[11px] text-[#8E9EB5] leading-snug">
                Real-time automated alert dispatch with prioritized risk metrics.
              </p>
            </div>

            {/* Step 6 */}
            <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-4 flex flex-col items-center text-center shadow-lg relative group hover:border-[#00A8FF]/50 transition">
              <div className="w-10 h-10 rounded-lg bg-[#050B14] border border-[#00A8FF]/40 text-[#00E5FF] flex items-center justify-center mb-3">
                <FileSearch className="w-5 h-5" />
              </div>
              <div className="text-[10px] font-mono text-[#00A8FF] font-bold uppercase">Step 06</div>
              <h3 className="text-xs font-bold text-[#F4F8FF] mt-1 mb-1">SOC Investigation</h3>
              <p className="text-[11px] text-[#8E9EB5] leading-snug">
                Forensic timeline drilldown, telemetry audit, and case notes.
              </p>
            </div>

            {/* Step 7 */}
            <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-4 flex flex-col items-center text-center shadow-lg relative group hover:border-[#00A8FF]/50 transition">
              <div className="w-10 h-10 rounded-lg bg-[#050B14] border border-[#00A8FF]/40 text-[#00E5FF] flex items-center justify-center mb-3">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div className="text-[10px] font-mono text-[#00A8FF] font-bold uppercase">Step 07</div>
              <h3 className="text-xs font-bold text-[#F4F8FF] mt-1 mb-1">Incident Resolution</h3>
              <p className="text-[11px] text-[#8E9EB5] leading-snug">
                Workflow stages: Open &rarr; Investigating &rarr; Contained &rarr; Resolved.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 4. FEATURE SECTION */}
      {/* ========================================================================= */}
      <section id="features" className="relative z-10 px-6 py-20 max-w-6xl mx-auto w-full">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0B1626] border border-[#00A8FF]/30 text-[#00A8FF] text-[11px] font-mono uppercase mb-3">
            Core Capabilities
          </div>
          <h2 className="text-2xl sm:text-4xl font-black tracking-tight text-[#F4F8FF] uppercase">
            Comprehensive Insider Threat Intelligence
          </h2>
          <p className="mt-3 text-xs sm:text-sm text-[#8E9EB5] max-w-xl mx-auto">
            Purpose-built modules empowering security operations teams to identify, analyze, and neutralize internal risks.
          </p>
        </div>

        {/* 6 Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Card 1 */}
          <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-6 shadow-xl hover:border-[#00A8FF]/50 transition flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-lg bg-[#050B14] border border-[#132B45] text-[#00E5FF] flex items-center justify-center mb-4">
                <Activity className="w-5 h-5 text-[#00E5FF]" />
              </div>
              <h3 className="text-base font-bold text-[#F4F8FF] mb-2">Behavioral Monitoring</h3>
              <p className="text-xs text-[#8E9EB5] leading-relaxed">
                Continuously tracks workforce activities, endpoint events, and access patterns to establish accurate behavioral baselines.
              </p>
            </div>
            <div className="mt-4 pt-4 border-t border-[#132B45]/60 text-[10px] font-mono text-[#00A8FF]">
              Telemetry Ingestion • 8 Event Types
            </div>
          </div>

          {/* Card 2 */}
          <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-6 shadow-xl hover:border-[#00A8FF]/50 transition flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-lg bg-[#050B14] border border-[#132B45] text-[#00E5FF] flex items-center justify-center mb-4">
                <BrainCircuit className="w-5 h-5 text-[#00E5FF]" />
              </div>
              <h3 className="text-base font-bold text-[#F4F8FF] mb-2">Anomaly Detection</h3>
              <p className="text-xs text-[#8E9EB5] leading-relaxed">
                Flags behavioral deviations such as off-hours logins, unauthorized privilege changes, and abnormal download volumes in real time.
              </p>
            </div>
            <div className="mt-4 pt-4 border-t border-[#132B45]/60 text-[10px] font-mono text-[#00A8FF]">
              Rule Engine • Baseline Variance
            </div>
          </div>

          {/* Card 3 */}
          <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-6 shadow-xl hover:border-[#00A8FF]/50 transition flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-lg bg-[#050B14] border border-[#132B45] text-[#00E5FF] flex items-center justify-center mb-4">
                <TrendingUp className="w-5 h-5 text-[#00E5FF]" />
              </div>
              <h3 className="text-base font-bold text-[#F4F8FF] mb-2">Dynamic Risk Scoring</h3>
              <p className="text-xs text-[#8E9EB5] leading-relaxed">
                Calculates continuous threat scores for every employee, dynamically mapping subjects into Low, Medium, High, and Critical tiers.
              </p>
            </div>
            <div className="mt-4 pt-4 border-t border-[#132B45]/60 text-[10px] font-mono text-[#00A8FF]">
              Bayesian Weighting • 0-100 Score Scale
            </div>
          </div>

          {/* Card 4 */}
          <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-6 shadow-xl hover:border-[#00A8FF]/50 transition flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-lg bg-[#050B14] border border-[#132B45] text-[#00E5FF] flex items-center justify-center mb-4">
                <AlertTriangle className="w-5 h-5 text-[#00E5FF]" />
              </div>
              <h3 className="text-base font-bold text-[#F4F8FF] mb-2">Security Alerts</h3>
              <p className="text-xs text-[#8E9EB5] leading-relaxed">
                Instantly dispatches context-rich alerts with severity scoring and anomaly evidence directly to security operations analysts.
              </p>
            </div>
            <div className="mt-4 pt-4 border-t border-[#132B45]/60 text-[10px] font-mono text-[#00A8FF]">
              Automated Triggers • Severity Prioritization
            </div>
          </div>

          {/* Card 5 */}
          <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-6 shadow-xl hover:border-[#00A8FF]/50 transition flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-lg bg-[#050B14] border border-[#132B45] text-[#00E5FF] flex items-center justify-center mb-4">
                <FileSearch className="w-5 h-5 text-[#00E5FF]" />
              </div>
              <h3 className="text-base font-bold text-[#F4F8FF] mb-2">Investigation Center</h3>
              <p className="text-xs text-[#8E9EB5] leading-relaxed">
                Enables forensic drill-down into chronological audit timelines, suspicious indicators, raw telemetry payloads, and analyst case notes.
              </p>
            </div>
            <div className="mt-4 pt-4 border-t border-[#132B45]/60 text-[10px] font-mono text-[#00A8FF]">
              Chronological Audit • Forensic Dossiers
            </div>
          </div>

          {/* Card 6 */}
          <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-6 shadow-xl hover:border-[#00A8FF]/50 transition flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-lg bg-[#050B14] border border-[#132B45] text-[#00E5FF] flex items-center justify-center mb-4">
                <ShieldAlert className="w-5 h-5 text-[#00E5FF]" />
              </div>
              <h3 className="text-base font-bold text-[#F4F8FF] mb-2">Incident Management</h3>
              <p className="text-xs text-[#8E9EB5] leading-relaxed">
                Provides a structured incident response lifecycle with status transitions from triage and containment to full resolution.
              </p>
            </div>
            <div className="mt-4 pt-4 border-t border-[#132B45]/60 text-[10px] font-mono text-[#00A8FF]">
              Lifecycle Tracking • SOC Containment
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 5. ARCHITECTURE & SECURITY HIGHLIGHTS */}
      {/* ========================================================================= */}
      <section id="architecture" className="relative z-10 px-6 py-20 bg-[#0B1626]/40 border-t border-[#132B45]">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0B1626] border border-[#00A8FF]/30 text-[#00A8FF] text-[11px] font-mono uppercase mb-3">
              Enterprise Architecture
            </div>
            <h2 className="text-2xl sm:text-4xl font-black tracking-tight text-[#F4F8FF] uppercase">
              Engineered for Scalable SOC Operations
            </h2>
            <p className="mt-3 text-xs sm:text-sm text-[#8E9EB5] max-w-xl mx-auto">
              Built on proven zero-trust security standards and dual-store database architecture for resilient threat monitoring.
            </p>
          </div>

          {/* 3 Pillar Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-6 shadow-xl">
              <div className="w-10 h-10 rounded-lg bg-[#050B14] border border-[#132B45] text-[#00E5FF] flex items-center justify-center mb-4">
                <Database className="w-5 h-5 text-[#00E5FF]" />
              </div>
              <h3 className="text-sm font-bold text-[#F4F8FF] mb-2">Dual-Store Architecture</h3>
              <p className="text-xs text-[#8E9EB5] leading-relaxed">
                Structured relational storage for employee registries, incidents, and audit trails, paired with MongoDB for high-throughput activity telemetry.
              </p>
            </div>

            <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-6 shadow-xl">
              <div className="w-10 h-10 rounded-lg bg-[#050B14] border border-[#132B45] text-[#00E5FF] flex items-center justify-center mb-4">
                <Lock className="w-5 h-5 text-[#00E5FF]" />
              </div>
              <h3 className="text-sm font-bold text-[#F4F8FF] mb-2">Zero Trust &amp; RBAC</h3>
              <p className="text-xs text-[#8E9EB5] leading-relaxed">
                Strict cryptographic JWT session management and role-based permissions governing access to telemetry logs, alerts, and administrative controls.
              </p>
            </div>

            <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-6 shadow-xl">
              <div className="w-10 h-10 rounded-lg bg-[#050B14] border border-[#132B45] text-[#00E5FF] flex items-center justify-center mb-4">
                <Server className="w-5 h-5 text-[#00E5FF]" />
              </div>
              <h3 className="text-sm font-bold text-[#F4F8FF] mb-2">SOC Operational Readiness</h3>
              <p className="text-xs text-[#8E9EB5] leading-relaxed">
                Tailored for Tier 1 to Tier 3 SOC operators with complete audit trails, rich telemetry inspector drawers, and streamlined response workflows.
              </p>
            </div>
          </div>

          {/* CTA Banner Box */}
          <div className="mt-14 bg-gradient-to-r from-[#0B1626] via-[#050B14] to-[#0B1626] border border-[#00A8FF]/40 rounded-2xl p-8 sm:p-12 text-center shadow-2xl relative overflow-hidden">
            <div className="relative z-10 max-w-2xl mx-auto">
              <h3 className="text-xl sm:text-3xl font-black text-[#F4F8FF] uppercase tracking-tight">
                Ready to Secure Your Organization?
              </h3>
              <p className="mt-3 text-xs sm:text-sm text-[#8E9EB5] leading-relaxed">
                Enter the ITBIS Security Operations Center console to monitor workforce telemetry, investigate anomalies, and protect critical assets.
              </p>
              <div className="mt-8 flex justify-center">
                <Link
                  href="/login"
                  className="px-8 py-3.5 bg-[#00A8FF] hover:bg-[#00E5FF] text-[#050B14] font-bold text-sm tracking-wide rounded-lg transition duration-200 flex items-center gap-2.5 shadow-xl shadow-[#00A8FF]/25 cursor-pointer"
                >
                  <Lock className="w-4 h-4" />
                  <span>ACCESS SOC CONSOLE</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 6. FOOTER */}
      {/* ========================================================================= */}
      <footer className="relative z-10 border-t border-[#132B45] px-6 py-8 bg-[#0B1626]/90 backdrop-blur-md">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6 text-xs text-[#8E9EB5]">
          {/* Left Brand */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-[#050B14] border border-[#132B45] flex items-center justify-center text-[#00E5FF]">
              <Shield className="w-4 h-4" />
            </div>
            <div>
              <span className="font-bold text-[#F4F8FF] tracking-wider">ITBIS</span>
              <span className="text-[10px] text-[#8E9EB5] block font-mono">
                Insider Threat &amp; Behavioral Intelligence System
              </span>
            </div>
          </div>

          {/* Center Links */}
          <div className="flex items-center gap-6 text-[11px] font-mono">
            <a href="#pipeline" className="hover:text-[#00E5FF] transition">
              Platform
            </a>
            <a href="#features" className="hover:text-[#00E5FF] transition">
              Capabilities
            </a>
            <a href="#architecture" className="hover:text-[#00E5FF] transition">
              Security
            </a>
            <Link href="/login" className="text-[#00A8FF] hover:text-[#00E5FF] transition font-bold">
              SOC Console
            </Link>
          </div>

          {/* Right Compliance */}
          <div className="flex items-center gap-3 text-[11px] font-mono text-[#8E9EB5]">
            <span>SOC 2 Compliant</span>
            <span>•</span>
            <span>Zero Trust</span>
            <span>•</span>
            <span>v1.0.0-PROD</span>
          </div>
        </div>

        <div className="max-w-7xl mx-auto mt-6 pt-4 border-t border-[#132B45]/50 text-center text-[10px] text-[#8E9EB5]/60">
          &copy; 2026 ITBIS Cybersecurity Operations. All rights reserved. Confidential enterprise system.
        </div>
      </footer>
    </div>
  );
}

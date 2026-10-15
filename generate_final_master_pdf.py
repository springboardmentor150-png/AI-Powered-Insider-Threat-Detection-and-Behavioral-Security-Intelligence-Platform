# generate_final_master_pdf.py
"""
Generates the Definitive Master Presentation in PDF Format (16:9 Widescreen)
for the AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform (ITBIS).
Matches the 16 slides of the master deck with dark obsidian styling, rich cards, tables, and exact equations.
"""
import os
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, PageBreak, Spacer, Table, TableStyle, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def build_pdf_presentation(output_path: str):
    PAGE_WIDTH = 13.333 * inch
    PAGE_HEIGHT = 7.5 * inch

    doc = SimpleDocTemplate(
        output_path,
        pagesize=(PAGE_WIDTH, PAGE_HEIGHT),
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.45 * inch,
        bottomMargin=0.45 * inch
    )

    # Dark Obsidian Palette
    C_OBSIDIAN = colors.HexColor("#111317")  # Slide background
    C_CARD = colors.HexColor("#1A1D24")      # Card background
    C_BORDER = colors.HexColor("#2E3442")    # Card outline
    C_EMERALD = colors.HexColor("#10B981")   # Success / Baseline
    C_AMBER = colors.HexColor("#F59E0B")     # Warning / Highlight
    C_CRIMSON = colors.HexColor("#EF4444")   # Threat / Danger
    C_PURPLE = colors.HexColor("#A855F7")    # ML / Intelligence
    C_CYAN = colors.HexColor("#06B6D4")      # Network / Ingestion
    C_WHITE = colors.HexColor("#FFFFFF")
    C_LIGHT = colors.HexColor("#E2E8F0")
    C_MUTED = colors.HexColor("#94A3B8")

    BORDER_EMERALD = C_EMERALD
    BORDER_AMBER = C_AMBER
    BORDER_CRIMSON = C_CRIMSON


    def draw_bg(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(C_OBSIDIAN)
        canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=True, stroke=False)
        # Subtle top accent bar
        canvas.setFillColor(C_CYAN)
        canvas.rect(0.6 * inch, PAGE_HEIGHT - 0.15 * inch, PAGE_WIDTH - 1.2 * inch, 2, fill=True, stroke=False)
        canvas.restoreState()

    base_styles = getSampleStyleSheet()

    # Custom Typography Styles
    s_eyebrow = ParagraphStyle(
        'Eyebrow',
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=C_CYAN,
        spaceAfter=4
    )
    s_title = ParagraphStyle(
        'SlideTitle',
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=C_WHITE,
        spaceAfter=14
    )
    s_card_badge = ParagraphStyle(
        'CardBadge',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=10,
        spaceAfter=4
    )
    s_card_title = ParagraphStyle(
        'CardTitle',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=C_WHITE,
        spaceAfter=8
    )
    s_card_body = ParagraphStyle(
        'CardBody',
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=C_LIGHT,
        spaceAfter=5
    )
    s_card_body_bold = ParagraphStyle(
        'CardBodyBold',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13.5,
        textColor=C_LIGHT,
        spaceAfter=5
    )

    def create_card_flowable(title, bullets, badge=None, badge_color=C_EMERALD, border_color=C_BORDER, width=3.7*inch, height=5.2*inch):
        content = []
        if badge:
            badge_p = Paragraph(badge.upper(), ParagraphStyle('Bdg', parent=s_card_badge, textColor=badge_color))
            content.append(badge_p)
        content.append(Paragraph(title, s_card_title))
        
        for b in bullets:
            p_style = s_card_body_bold if b.startswith("• <b>") or b.startswith("<b>") else s_card_body
            text = b if b.startswith("•") else f"• {b}"
            content.append(Paragraph(text, p_style))

        # Wrap in a Table for visual container card styling
        table = Table([[content]], colWidths=[width])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), C_CARD),
            ('BOX', (0, 0), (-1, -1), 1.2, border_color),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        return table

    story = []

    # =========================================================================
    # SLIDE 1: COVER & EXECUTIVE INTRODUCTION
    # =========================================================================
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph("ENTERPRISE BEHAVIORAL SECURITY INTELLIGENCE PLATFORM (ITBIS)", s_eyebrow))
    story.append(Paragraph("AI-Powered Insider Threat Detection & Behavioral Intelligence", ParagraphStyle('CoverTitle', fontName='Helvetica-Bold', fontSize=28, leading=32, textColor=C_WHITE, spaceAfter=8)))
    story.append(Paragraph("Complete Full-Stack Engineering & Forensic Defense Architecture", ParagraphStyle('CoverSub', fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=C_AMBER, spaceAfter=14)))
    story.append(Paragraph(
        "An end-to-end security operations platform featuring hybrid anomaly detection (Heuristic Rules + Unsupervised Isolation Forest), dynamic 5-factor risk scoring, automated forensic incident synthesis, role-based executive dashboards, and in-memory export engines.",
        ParagraphStyle('CoverDesc', fontName='Helvetica', fontSize=11, leading=16, textColor=C_MUTED, spaceAfter=24)
    ))

    # Candidate Meta Box
    meta_content = [
        Paragraph("PROJECT CANDIDATE & IMPLEMENTATION METADATA:", ParagraphStyle('MetaHead', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=C_AMBER, spaceAfter=4)),
        Paragraph("<b>Done by:</b> Sritha — Final Year Aspiring Student", ParagraphStyle('MetaAuth', fontName='Helvetica-Bold', fontSize=14, leading=17, textColor=C_WHITE, spaceAfter=6)),
        Paragraph("<b>Architecture:</b> FastAPI (Python 3.14) • Next.js 14 App Router • Scikit-Learn Isolation Forest • Dual Storage (SQLite itbis.db & MongoDB) • ReportLab & OpenPyXL", ParagraphStyle('MetaStack', fontName='Helvetica', fontSize=10, leading=14, textColor=C_LIGHT)),
        Paragraph("<b>Milestone Status:</b> Milestones 1, 2, 3 & 4 (Executive Dashboards & Reporting) Built, Tested & Verified (100% Test Pass)", ParagraphStyle('MetaStatus', fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=C_EMERALD))
    ]
    meta_table = Table([[meta_content]], colWidths=[12.133 * inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_CARD),
        ('BOX', (0, 0), (-1, -1), 1.5, C_EMERALD),
        ('TOPPADDING', (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
        ('LEFTPADDING', (0, 0), (-1, -1), 18),
        ('RIGHTPADDING', (0, 0), (-1, -1), 18),
    ]))
    story.append(meta_table)

    # =========================================================================
    # SLIDE 2: THE PROBLEM STATEMENT
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("THE THREAT LANDSCAPE", s_eyebrow))
    story.append(Paragraph("The Problem: Why Traditional Firewalls Fail Against Insiders", s_title))

    c1 = create_card_flowable(
        "1. The Perimeter Blindspot",
        [
            "Traditional perimeter defenses (Firewalls, VPNs, WAFs) monitor north-south ingress/egress from external IP addresses.",
            "Malicious insiders and stolen credentials bypass 100% of perimeter rules because traffic originates from trusted, authenticated sessions.",
            "<b>82% of enterprise breaches</b> involve authorized user credentials or legitimate privileges abused from within (Verizon DBIR).",
            "Firewalls cannot distinguish between an authorized employee generating a routine database report and an employee exfiltrating records."
        ],
        badge="Perimeter Blindness", badge_color=C_CRIMSON, border_color=C_CRIMSON, width=3.85*inch
    )
    c2 = create_card_flowable(
        "2. Log Explosion & Alert Fatigue",
        [
            "Modern enterprise infrastructures generate hundreds of gigabytes of raw logs daily (Active Directory, Kerberos, SSH, file shares).",
            "Traditional SIEM systems rely on static threshold alerts (e.g. 'flag if transfer > 500 MB').",
            "Static thresholds yield <b>>90% false alarms</b>, drowning SOC engineers in alert fatigue while stealthy attackers stay under thresholds.",
            "Without contextual behavioral baselines, insider exfiltration remains undetected for an average of <b>287 days</b>."
        ],
        badge="Information Overload", badge_color=C_AMBER, border_color=C_AMBER, width=3.85*inch
    )
    c3 = create_card_flowable(
        "3. The Disgruntled Insider Profile",
        [
            "Flight-risk employees, resigning staff, and compromised accounts systematically stage corporate data prior to departure.",
            "Attackers leverage low-and-slow data movement, off-hours access, and alternative protocols (SFTP, USB mounts, cloud sync).",
            "Static rules fail to spot contextual deviation—such as an engineer suddenly reading payroll databases at 2:00 AM.",
            "Solution: Continuous behavioral profiling, peer-group benchmarking, and automated digital forensic timelines."
        ],
        badge="Insider Risk Reality", badge_color=C_PURPLE, border_color=C_PURPLE, width=3.85*inch
    )
    row_s2 = Table([[c1, c2, c3]], colWidths=[3.95*inch, 3.95*inch, 3.95*inch])
    row_s2.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(row_s2)

    # =========================================================================
    # SLIDE 3: PROJECT SCOPE & 4-MILESTONE ROADMAP
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("PROJECT ARCHITECTURE", s_eyebrow))
    story.append(Paragraph("Platform Roadmap & Scope: Milestones 1 Through 4", s_title))

    w_m = 2.9*inch
    m1 = create_card_flowable(
        "Milestone 1: Foundations",
        [
            "<b>Role-Based Access Control:</b> 4 distinct roles (Admin, Security Manager, Security Analyst, SOC Engineer).",
            "<b>Stateless JWT Auth:</b> OAuth2 Bearer tokens with 12-round bcrypt password hashing.",
            "<b>Employee Directory:</b> Tracks identity, department, designation, devices, and baseline risk.",
            "<b>SQLite Persistence:</b> Normalized schema with SQLAlchemy 2.0 ORM models."
        ],
        badge="Milestone 1: Days 1–10", badge_color=C_EMERALD, width=w_m
    )
    m2 = create_card_flowable(
        "Milestone 2: Ingestion & AI",
        [
            "<b>Document Telemetry:</b> MongoDB JSON backing store for high-throughput event capture.",
            "<b>Heuristic Engine:</b> Deterministic rules catching off-hours logins, volume spikes, and USB mounts.",
            "<b>Unsupervised ML:</b> Scikit-Learn Isolation Forest with contamination factor c=0.12.",
            "<b>Feature Engineering:</b> Extracts login hour, transfer volume, and failure velocity."
        ],
        badge="Milestone 2: Days 11–20", badge_color=C_PURPLE, width=w_m
    )
    m3 = create_card_flowable(
        "Milestone 3: UEBA & Forensics",
        [
            "<b>5-Factor Risk Scorer:</b> Standardized weighted composite risk equation (0 to 100).",
            "<b>Peer Group UEBA:</b> Statistical Z-score benchmarking against department peers.",
            "<b>Investigation Workbench:</b> Stitched linear chronological telemetry timelines.",
            "<b>Forensic Evidence Ledger:</b> Digital evidence tracking and MITRE ATT&CK framework mapping."
        ],
        badge="Milestone 3: Days 21–30", badge_color=C_AMBER, width=w_m
    )
    m4 = create_card_flowable(
        "Milestone 4: Dashboards & Exports",
        [
            "<b>Manager Compliance View:</b> Resolution rate % and open critical triage.",
            "<b>Accurate MTTR & MTTI:</b> Tracks incident lifecycle and investigation start times.",
            "<b>Admin Health Analytics:</b> Workforce coverage and platform anomaly rates.",
            "<b>In-Memory Exports:</b> ReportLab PDF dossiers and bulk Excel (.xlsx) workbooks."
        ],
        badge="Milestone 4: Days 31–34", badge_color=C_CYAN, width=w_m
    )
    row_s3 = Table([[m1, m2, m3, m4]], colWidths=[2.98*inch, 2.98*inch, 2.98*inch, 2.98*inch])
    row_s3.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(row_s3)

    # =========================================================================
    # SLIDE 4: END-TO-END SYSTEM ARCHITECTURE
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("FULL-STACK PIPELINE", s_eyebrow))
    story.append(Paragraph("End-to-End System Architecture & High-Throughput Data Flow", s_title))

    arch_left = create_card_flowable(
        "Data Pipeline & Service Architecture",
        [
            "<b>1. Client Presentation Layer (Next.js 14):</b>",
            "   Browser communicates with backend via Axios REST API with JWT authorization headers.",
            "<b>2. REST Application Gateway (FastAPI):</b>",
            "   Starlette async engine, Pydantic data validation, and Depends(require_role(...)) guards.",
            "<b>3. Telemetry Ingestion Engine:</b>",
            "   High-throughput ingestion of login, file, USB, and network telemetry into document store.",
            "<b>4. Dual Analytical Processing:</b>",
            "   Simultaneous evaluation by Heuristic Rules and Scikit-Learn Isolation Forest.",
            "<b>5. Dynamic 5-Factor Risk Calculator:</b>",
            "   Synthesizes rule, ML, peer Z-score, role, and privilege sub-scores.",
            "<b>6. Automated Incident & Forensic Synthesizer:</b>",
            "   Generates incident dossiers, MITRE T1048 mapping, and evidence ledger.",
            "<b>7. Dual Storage Tier:</b>",
            "   ACID relational persistence in SQLite (itbis.db) + Document Store in MongoDB."
        ],
        badge="Data Flow Breakdown", badge_color=C_CYAN, width=5.8*inch
    )
    arch_right = create_card_flowable(
        "Key Architectural Invariants",
        [
            "<b>Stateless Authentication:</b> Zero session state maintained on server; JWT claims validated cryptographically per request.",
            "<b>Least-Privilege RBAC:</b> Explicit role checking (Admin, Security Manager, Security Analyst, SOC Engineer) enforced at router level.",
            "<b>Dual-Database Strategy:</b> Strict relational integrity for compliance entities; flexible schema document store for high-volume logs.",
            "<b>In-Memory Export Generation:</b> PDF and Excel streams constructed entirely in RAM (io.BytesIO) to eliminate disk collisions.",
            "<b>Real-Time Event Correlator:</b> Anomaly events linked directly to employee identities and stitched into chronological timelines.",
            "<b>Defensive Error Boundaries:</b> Division-by-zero guards on empty databases and None-safe date formatting on un-resolved records."
        ],
        badge="Engineering Standards", badge_color=C_EMERALD, width=5.8*inch
    )
    row_s4 = Table([[arch_left, arch_right]], colWidths=[5.95*inch, 5.95*inch])
    row_s4.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(row_s4)

    # =========================================================================
    # SLIDE 5: COMPLETE TECHNOLOGY STACK & RATIONALE
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("ENGINEERING CHOICES", s_eyebrow))
    story.append(Paragraph("Technology Stack Breakdown & Architectural Rationale", s_title))

    stk1 = create_card_flowable(
        "Backend: FastAPI (Python 3.14)",
        [
            "<b>Asynchronous Non-Blocking I/O:</b> Starlette + Uvicorn delivers microsecond REST latencies for high-throughput log ingestion.",
            "<b>Pydantic V2 Type Safety:</b> Automated schema validation, serializing, and self-documenting Swagger/OpenAPI docs at /docs.",
            "<b>SQLAlchemy 2.0 ORM:</b> Thread-safe relational abstraction with connection pooling and declarative models.",
            "<b>Dependency Injection Security:</b> Custom require_role(...) dependencies enforce RBAC natively before handler execution.",
            "<b>Native Machine Learning Interop:</b> Direct in-process execution of Scikit-Learn without IPC latency."
        ],
        badge="Application Gateway", badge_color=C_EMERALD, width=3.85*inch
    )
    stk2 = create_card_flowable(
        "Frontend: Next.js 14 & Tailwind",
        [
            "<b>React 18 & App Router:</b> Server and client components with route caching and optimized hydration.",
            "<b>Tailwind Dark Obsidian UI:</b> Cyber-themed interface designed for low eye-strain in 24/7 SOC environments.",
            "<b>Lucide Icons & Chart.js:</b> Interactive radar charts, risk distribution visualizers, and 7-day anomaly trend graphs.",
            "<b>Axios Request Interceptors:</b> Automated JWT header attachment, unified error boundaries, and blob download streaming.",
            "<b>Client-Side Role Switching:</b> Instant evaluation testing across all 4 RBAC personas in live demo."
        ],
        badge="User Interface", badge_color=C_CYAN, width=3.85*inch
    )
    stk3 = create_card_flowable(
        "AI & Data: Isolation Forest & Reports",
        [
            "<b>Scikit-Learn Isolation Forest:</b> Fast recursive partitioning efficient for high-dimensional outlier detection.",
            "<b>ReportLab Platypus:</b> In-memory dynamic PDF compiler producing executive dossiers via io.BytesIO() without disk writes.",
            "<b>Pandas & OpenPyXL:</b> High-speed tabular workbook generator with safe date formatting and custom column sorting.",
            "<b>Dual-Database Strategy:</b> Relational tables for accounts/incidents; document store for unstructured telemetry."
        ],
        badge="Intelligence & Data", badge_color=C_PURPLE, width=3.85*inch
    )
    row_s5 = Table([[stk1, stk2, stk3]], colWidths=[3.95*inch, 3.95*inch, 3.95*inch])
    row_s5.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(row_s5)

    # =========================================================================
    # SLIDE 6: DUAL-DATABASE ARCHITECTURE
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("DATA STORAGE LAYER", s_eyebrow))
    story.append(Paragraph("Dual-Database Architecture: Relational SQLite vs NoSQL MongoDB", s_title))

    db1 = create_card_flowable(
        "Relational Store: SQLite / PostgreSQL (itbis.db)",
        [
            "<b>Role:</b> ACID transaction integrity, relational joins, foreign keys, and audit compliance.",
            "<b>users:</b> id, email, password_hash, full_name, role, is_active, created_at.",
            "<b>employees:</b> id, employee_id, name, department, designation, device_info, access_privileges, status, baseline_risk_score.",
            "<b>incidents:</b> id, incident_code, employee_id, severity, status, title, description, assigned_to, mitre_attack_technique, investigation_started_at, resolved_at.",
            "<b>evidence:</b> id, incident_id, note, added_by (User ID), added_at (foreign key linked).",
            "<b>alerts:</b> id, alert_code, employee_id, severity, message, status, anomaly_type, risk_score, created_at, resolved_at.",
            "<b>audit_logs:</b> id, user_id, user_email, action, target_resource, details, timestamp."
        ],
        badge="Relational ACID Store", badge_color=C_EMERALD, border_color=BORDER_EMERALD, width=5.8*inch
    )
    db2 = create_card_flowable(
        "Document Store: MongoDB / JSON Collections (data/)",
        [
            "<b>Role:</b> High-throughput ingestion of un-structured event streams and anomaly records.",
            "<b>activity_logs.json:</b> Raw audit telemetry events with timestamp, employee_id, event_type (LOGIN, FILE_TRANSFER, USB_MOUNT), bytes_transferred, ip_address, and status.",
            "<b>rule_anomalies.json:</b> Deterministic violations flagged by rule engine with detected_at, severity, rule_name, and employee_id.",
            "<b>ml_anomalies.json:</b> Statistical anomaly entries with is_anomaly (boolean), anomaly_score (float), and feature vectors.",
            "<b>Aggregation Pipeline Support:</b> Uses $match, $group, and $dateToString for 7-day anomaly trend visualizations and department-level aggregations."
        ],
        badge="High-Volume Document Store", badge_color=C_AMBER, border_color=BORDER_AMBER, width=5.8*inch
    )
    row_s6 = Table([[db1, db2]], colWidths=[5.95*inch, 5.95*inch])
    row_s6.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(row_s6)

    # =========================================================================
    # SLIDE 7: TELEMETRY INGESTION & AUDIT LOGGING
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("AUDIT & INGESTION", s_eyebrow))
    story.append(Paragraph("Telemetry Ingestion Pipeline & Platform Audit Logging", s_title))

    ing1 = create_card_flowable(
        "High-Throughput Log Ingestion Pipeline",
        [
            "<b>Endpoint:</b> POST /api/logs/ingest",
            "Validates event schema via Pydantic ActivityLogIngest model.",
            "<b>Supported Telemetry Types:</b>",
            "  • LOGIN: IP address, user agent, workstation hostname, login hour.",
            "  • FILE_ACCESS / FILE_TRANSFER: Source folder, file size, bytes.",
            "  • PRIVILEGE_USE: Sudo, admin impersonation, token generation.",
            "  • USB_DEVICE: Mass storage insertion, device serial.",
            "<b>Automatic Timestamping:</b> Fallback to UTC if client timestamp missing.",
            "<b>Non-Blocking Persistence:</b> Thread-safe in-memory cache synchronized with JSON backing store."
        ],
        badge="Log Ingestion Engine", badge_color=C_CYAN, width=5.8*inch
    )
    ing2 = create_card_flowable(
        "Day 32 Simple Audit Log Implementation",
        [
            "<b>Dedicated Helper Function:</b> log_action(db, user_id, action, details, target_resource)",
            "<b>Retrofitted Across Sensitive Security Endpoints:</b>",
            "  1. Alert Assignment: /api/alerts/{id}/assign -> logs assignee email and assigner user_id.",
            "  2. Alert Resolution: /api/alerts/{id}/resolve -> logs resolving analyst and timestamp.",
            "  3. Incident Creation: /api/incidents -> logs newly generated incident code and target employee.",
            "  4. Status Updates: /api/incidents/{id}/status -> tracks transitions from OPEN to INVESTIGATING or RESOLVED.",
            "  5. User Provisioning: /api/auth/register -> records new account creation and granted RBAC role.",
            "<b>Queryable API:</b> GET /api/dashboard/admin/audit-log and exportable to Excel."
        ],
        badge="Governance Audit Trail", badge_color=C_PURPLE, width=5.8*inch
    )
    row_s7 = Table([[ing1, ing2]], colWidths=[5.95*inch, 5.95*inch])
    row_s7.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(row_s7)

    # =========================================================================
    # SLIDE 8: DETECTION ENGINE 1: HEURISTIC RULES
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("BEHAVIORAL RULE ENGINE", s_eyebrow))
    story.append(Paragraph("Detection Engine 1: Deterministic Heuristic Policy Rules", s_title))

    r1 = create_card_flowable(
        "Rule 1: Off-Hours Access",
        [
            "<b>Trigger:</b> Employee logs in or accesses resources between 22:00 and 05:00 local time.",
            "<b>Context:</b> Checked against department working hours profile.",
            "<b>Severity:</b> HIGH.",
            "<b>Threat Rationale:</b> Disgruntled staff frequently stage exfiltration during night shifts when physical SOC staffing is minimal."
        ],
        badge="Temporal Anomaly", badge_color=C_AMBER, width=w_m
    )
    r2 = create_card_flowable(
        "Rule 2: Volume Spike",
        [
            "<b>Trigger:</b> Single-session file transfer exceeds 1.0 GB or 3.5x normal baseline volume.",
            "<b>Context:</b> Evaluated against 30-day historical transfer rolling average.",
            "<b>Severity:</b> CRITICAL.",
            "<b>Threat Rationale:</b> Mass downloading of source code repositories or sensitive financial exports."
        ],
        badge="Data Exfiltration", badge_color=C_CRIMSON, width=w_m
    )
    r3 = create_card_flowable(
        "Rule 3: Restricted Access",
        [
            "<b>Trigger:</b> Access attempt on classified folders (e.g., /prod/finance_db_backup).",
            "<b>Context:</b> Cross-referenced with employee access_privileges list.",
            "<b>Severity:</b> CRITICAL.",
            "<b>Threat Rationale:</b> Snooping, lateral movement, or privilege abuse across departmental boundaries."
        ],
        badge="Privilege Abuse", badge_color=C_PURPLE, width=w_m
    )
    r4 = create_card_flowable(
        "Rule 4: Multi-Alert Spike",
        [
            "<b>Trigger:</b> More than 3 distinct rule triggers within a rolling 60-minute window.",
            "<b>Context:</b> Aggregated by employee_id.",
            "<b>Severity:</b> CRITICAL.",
            "<b>Threat Rationale:</b> Active, aggressive exfiltration campaign requiring immediate automated quarantine."
        ],
        badge="Heuristic Escalation", badge_color=C_CRIMSON, width=w_m
    )
    row_s8 = Table([[r1, r2, r3, r4]], colWidths=[2.98*inch, 2.98*inch, 2.98*inch, 2.98*inch])
    row_s8.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(row_s8)

    # =========================================================================
    # SLIDE 9: DETECTION ENGINE 2: ISOLATION FOREST ML
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("MACHINE LEARNING", s_eyebrow))
    story.append(Paragraph("Detection Engine 2: Unsupervised Machine Learning (Isolation Forest)", s_title))

    ml1 = create_card_flowable(
        "Algorithm Architecture & Feature Engineering",
        [
            "<b>Why Isolation Forest?</b> Traditional clustering (K-Means, DBSCAN) struggles with high-dimensional sparsity. Isolation Forest isolates anomalies recursively: outliers require fewer random splits to separate.",
            "<b>Trained on 3 Engineered Behavioral Features:</b>",
            "  1. Login Hour Metric: Normalizes access time (0.0 to 23.99).",
            "  2. Data Volume Transferred: Megabytes moved per operation.",
            "  3. Access Failure Velocity: Number of 401/403 errors in session.",
            "<b>Contamination Factor:</b> Configured to c = 0.12 (12%), matching enterprise SOC anomaly expectations.",
            "<b>Mathematical Anomaly Score:</b>",
            "  s(x, n) = 2^(-E(h(x)) / c(n))",
            "  Where E(h(x)) is average path length across 100 decision trees."
        ],
        badge="ML Engine Core", badge_color=C_PURPLE, width=5.8*inch
    )
    ml2 = create_card_flowable(
        "Inference, Decision Boundary & Normalization",
        [
            "<b>Model Output & Scikit-Learn Prediction:</b>",
            "  • Prediction = -1 -> Behavioral Anomaly Flagged.",
            "  • Prediction = +1 -> Normal In-Distribution Activity.",
            "<b>Score Normalization:</b> Raw decision function scores [-0.5, 0.5] mapped linearly to standard [0.0, 1.0] confidence interval.",
            "<b>Zero-Day Threat Detection:</b> Catches multi-dimensional deviations that evade single-variable rule thresholds (e.g., moderate volume transfer paired with unusual hours and elevated failure rate).",
            "<b>Model Persistence:</b> Automatically re-fits and updates dynamic baselines as healthy workforce telemetry accumulates."
        ],
        badge="Scoring & Decision", badge_color=C_CYAN, width=5.8*inch
    )
    row_s9 = Table([[ml1, ml2]], colWidths=[5.95*inch, 5.95*inch])
    row_s9.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(row_s9)

    # =========================================================================
    # SLIDE 10: DYNAMIC 5-FACTOR RISK SCORING ENGINE & UEBA
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("RISK INTELLIGENCE", s_eyebrow))
    story.append(Paragraph("Dynamic 5-Factor Risk Scoring Engine & UEBA Benchmarking", s_title))

    rk1 = create_card_flowable(
        "The 5-Factor Composite Mathematical Formula",
        [
            "<b>Composite Risk Equation:</b>",
            "  Risk Score = 0.35 * R_rule + 0.30 * R_ML + 0.20 * R_peer + 0.10 * R_role + 0.05 * R_priv",
            "<b>1. Rule Violations (35% Weight):</b> Cumulative severity of deterministic triggers.",
            "<b>2. Machine Learning Anomaly (30% Weight):</b> Isolation Forest anomaly probability score.",
            "<b>3. Peer Group Deviation (20% Weight):</b> Statistical Z-score deviation from departmental mean:",
            "   Z = (Employee_Activity - Mean_Dept) / StdDev_Dept",
            "<b>4. Role Sensitivity (10% Weight):</b> Intrinsic sensitivity of role (Finance/DevOps = 85, Sales = 40).",
            "<b>5. Privilege Factor (5% Weight):</b> Access level score (K8s/Prod DB = 90, Standard = 30)."
        ],
        badge="Mathematical Modeling", badge_color=C_AMBER, border_color=BORDER_AMBER, width=5.8*inch
    )
    rk2 = create_card_flowable(
        "Risk Stratification & SOC Action Thresholds",
        [
            "<b>Score Normalization Range:</b> 0.0 to 100.0",
            "<b>1. LOW RISK (Score 0 – 24):</b> Normal baseline operation. No analyst action needed.",
            "<b>2. MEDIUM RISK (Score 25 – 49):</b> Mild anomaly or minor off-hours login. Telemetry logged; system continues passive monitoring.",
            "<b>3. HIGH RISK (Score 50 – 74):</b> Elevated behavioral outlier. Alert dispatched to SOC Analyst queue; single-click incident creation available.",
            "<b>4. CRITICAL RISK (Score 75 – 100):</b> High-confidence malicious insider event. Automated incident generated; immediate credential quarantine recommended."
        ],
        badge="Risk Stratification", badge_color=C_CRIMSON, border_color=BORDER_CRIMSON, width=5.8*inch
    )
    row_s10 = Table([[rk1, rk2]], colWidths=[5.95*inch, 5.95*inch])
    row_s10.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(row_s10)

    # =========================================================================
    # SLIDE 11: CASE STUDY OF DEVON MILLER (EMP1003)
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("CASE STUDY", s_eyebrow))
    story.append(Paragraph("Live Threat Simulation: Case Study of Devon Miller (EMP1003)", s_title))

    cs1 = create_card_flowable(
        "Phase 1: Healthy Baseline State",
        [
            "<b>Subject:</b> Devon Miller (EMP1003)",
            "<b>Department:</b> Cloud Infrastructure / DevOps",
            "<b>Role:</b> Senior Cloud Infrastructure Lead",
            "<b>Initial Baseline Risk Score:</b> 15.2 (Low)",
            "<b>Initial Status:</b> ACTIVE",
            "<b>Normal Behavior:</b> Standard working hours (09:00 - 18:00), average transfer volume < 45 MB, zero policy violations."
        ],
        badge="Baseline Integrity", badge_color=C_EMERALD, width=3.85*inch
    )
    cs2 = create_card_flowable(
        "Phase 2: Attack Simulation Trigger",
        [
            "<b>Attack Scenario:</b> 'mass_exfiltration'",
            "<b>Simulation API:</b> POST /api/simulation/run",
            "<b>Payload:</b> {'scenario': 'mass_exfiltration', 'employee_id': 'EMP1003'}",
            "<b>Injected Telemetry Events:</b>",
            "  • 02:45 AM: Off-hours SSH session opened.",
            "  • 02:50 AM: 8.4 GB sensitive financial backups exported via SFTP.",
            "  • 02:52 AM: Unauthorized token access on /prod/finance_db_backup."
        ],
        badge="Threat Simulation", badge_color=C_CRIMSON, border_color=C_CRIMSON, width=3.85*inch
    )
    cs3 = create_card_flowable(
        "Phase 3: Real-Time AI Detection",
        [
            "<b>Risk Score Jump:</b> 15.2 -> 84.6 (CRITICAL RED ALERT).",
            "<b>UEBA Peer Deviation:</b> Delta = +84.6 above Cloud Ops team mean.",
            "<b>Rule Triggers:</b> Off-hours access + mass transfer spike.",
            "<b>ML Isolation Forest:</b> Anomaly score s = 0.912 (Severe Outlier).",
            "<b>Incident Generated:</b> INC-2026-8841 automatically opened and assigned to SOC triage."
        ],
        badge="Threat Neutralization", badge_color=C_CRIMSON, border_color=C_CRIMSON, width=3.85*inch
    )
    row_s11 = Table([[cs1, cs2, cs3]], colWidths=[3.95*inch, 3.95*inch, 3.95*inch])
    row_s11.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(row_s11)

    # =========================================================================
    # SLIDE 12: INCIDENT WORKBENCH & FORENSIC EVIDENCE LEDGER
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("SOC FORENSICS", s_eyebrow))
    story.append(Paragraph("Incident Investigation Workbench & Forensic Evidence Ledger", s_title))

    wb1 = create_card_flowable(
        "Investigation Workbench Features",
        [
            "<b>Incident Dossier Generation:</b> POST /api/incidents/{id}/generate-ai-report",
            "Automated AI Forensic Brief synthesizing employee profile, event context, and containment playbooks.",
            "<b>Chronological Event Timeline:</b> Stitches raw MongoDB activity logs and anomaly triggers into an interactive linear timeline.",
            "<b>MITRE ATT&CK Mapping:</b>",
            "  • T1048.002: Exfiltration Over Alternative Protocol (SSH/SFTP).",
            "  • T1078.004: Valid Accounts: Cloud Accounts.",
            "  • T1083: File and Directory Discovery.",
            "<b>Recommended SOC Playbooks:</b> Revoke Kerberos session, isolate laptop MAC, notify HR and Legal."
        ],
        badge="Forensic Workbench", badge_color=C_CYAN, width=5.8*inch
    )
    wb2 = create_card_flowable(
        "Digital Evidence Chain of Custody",
        [
            "<b>Relational Table:</b> evidence (linked to incidents via foreign key).",
            "<b>Stored Fields:</b> id, incident_id, note, added_by (User ID), added_at (UTC).",
            "<b>Live Forensic Evidence Captured for EMP1003:</b>",
            "  • EVID-1092: Mass exfiltration of 8.4 GB financial backup files via SFTP at 02:50 UTC.",
            "  • EVID-1093: Isolation Forest peer group deviation exceeded 4.8 standard deviations.",
            "  • EVID-1094: Unauthorized token generation attempt on production financial database.",
            "<b>Immutable Tracking:</b> Analyst attribution logged with tamper-evident audit trail."
        ],
        badge="Chain of Custody", badge_color=C_EMERALD, width=5.8*inch
    )
    row_s12 = Table([[wb1, wb2]], colWidths=[5.95*inch, 5.95*inch])
    row_s12.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(row_s12)

    # =========================================================================
    # SLIDE 13: EXECUTIVE & ADMIN DASHBOARDS (DAYS 31 & 32)
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("MANAGEMENT & HEALTH", s_eyebrow))
    story.append(Paragraph("Executive & Admin Dashboards (Milestone 4 Days 31 & 32)", s_title))

    dsh1 = create_card_flowable(
        "Day 31: Security Manager Compliance View",
        [
            "<b>Endpoint:</b> GET /api/dashboard/manager/compliance",
            "<b>Allowed Roles:</b> admin, security_manager (403 for analysts).",
            "<b>Resolution Rate Calculation:</b>",
            "  Rate % = round((resolved_incidents / total_incidents) * 100, 1)",
            "<b>Zero-Division Guard:</b> Defaults safely to 0.0% on empty database.",
            "<b>Separate Open Critical Metric:</b> Highlights unresolved critical threats regardless of overall percentage.",
            "<b>MTTR (Mean Time to Respond):</b> Average hours between alert created_at and resolved_at.",
            "<b>MTTI (Mean Time to Investigate):</b> Average hours between incident creation and an analyst beginning triage (investigation_started_at)."
        ],
        badge="Executive Compliance", badge_color=C_EMERALD, width=5.8*inch
    )
    dsh2 = create_card_flowable(
        "Day 32: Admin Dashboard & Platform Health",
        [
            "<b>Endpoint:</b> GET /api/dashboard/admin (Strict admin only).",
            "<b>User Governance:</b> Aggregates accounts by role (admin, security_manager, security_analyst, soc_engineer).",
            "<b>Monitored Workforce:</b> Employees tracked & distinct departments count via db.query(Employee.department).distinct().count().",
            "<b>Platform Volume Analytics:</b> GET /api/dashboard/admin/platform-analytics",
            "<b>Calculates Platform Anomaly Rate:</b>",
            "  Anomaly Rate % = round(((rule_anomalies + ml_anomalies) / total_logs) * 100, 2)",
            "<b>Sanity Metric:</b> Verifies detection sensitivity (real-world SOCs aim for single-digit anomaly rates; flags over-tuning)."
        ],
        badge="Platform Governance", badge_color=C_PURPLE, width=5.8*inch
    )
    row_s13 = Table([[dsh1, dsh2]], colWidths=[5.95*inch, 5.95*inch])
    row_s13.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(row_s13)

    # =========================================================================
    # SLIDE 14: REPORTS & EXPORT SYSTEM (DAYS 33 & 34)
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("REPORTING ENGINE", s_eyebrow))
    story.append(Paragraph("Reports & Export System: In-Memory PDF & Excel (Days 33 & 34)", s_title))

    rep1 = create_card_flowable(
        "Day 33: In-Memory PDF Reporting Engine",
        [
            "Built with ReportLab Platypus & io.BytesIO() entirely in RAM.",
            "<b>Zero Temporary Disk Writes:</b> Eliminates server disk accumulation, race conditions, and unneeded disk I/O.",
            "<b>1. Individual Risk Report:</b> GET /api/reports/{employee_id}/pdf",
            "   • Styled 5-factor sub-score table (#7a1f2b crimson header).",
            "   • Capped at 10 recent anomalies; handles 0 total cleanly without crashing.",
            "<b>2. Compliance Summary Report:</b> GET /api/reports/compliance/pdf",
            "   • Reuses Day 31 compliance metrics, SLA benchmarks, and incident audit records.",
            "<b>Headers:</b> Content-Disposition: attachment; filename=... with media_type='application/pdf'."
        ],
        badge="PDF Engine (ReportLab)", badge_color=C_CRIMSON, width=5.8*inch
    )
    rep2 = create_card_flowable(
        "Day 34: Excel Data Exports & Report Catalog",
        [
            "Built with Pandas & OpenPyXL for structured tabular datasets.",
            "<b>MIME Type:</b> application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "<b>1. Bulk Risk Scores:</b> GET /api/reports/export/risk-scores",
            "   • Pre-sorted descending: highest-risk staff appear first.",
            "   • Optional department filter parameter.",
            "<b>2. Incident Export:</b> GET /api/reports/export/incidents",
            "   • Inline date guard: i.resolved_at.strftime(...) if i.resolved_at else 'Not resolved' prevents AttributeError.",
            "<b>3. Report Catalog:</b> GET /api/reports/catalog",
            "   • Single source of truth serving UI with available formats and endpoints."
        ],
        badge="Excel Exports & Catalog", badge_color=C_EMERALD, width=5.8*inch
    )
    row_s14 = Table([[rep1, rep2]], colWidths=[5.95*inch, 5.95*inch])
    row_s14.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(row_s14)

    # =========================================================================
    # SLIDE 15: QUALITY ASSURANCE & TESTING
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("QUALITY ASSURANCE", s_eyebrow))
    story.append(Paragraph("Verification, Testing & Automated Quality Assurance", s_title))

    qa1 = create_card_flowable(
        "Automated TestClient Suite",
        [
            "Executed in test_milestone4_endpoints.py.",
            "<b>100% Pass Rate across all Milestone 4 test suites:</b>",
            "  • Day 31 Compliance View & MTTR/MTTI calculations.",
            "  • Day 32 Admin user counts & platform volume analytics.",
            "  • Audit logging across alert assignment, resolution, and incident creation.",
            "  • PDF generation for both high-anomaly and zero-anomaly employees.",
            "  • Excel risk sorting and unresolved date handling."
        ],
        badge="Test Automation", badge_color=C_EMERALD, width=3.85*inch
    )
    qa2 = create_card_flowable(
        "Defensive Edge-Case Handling",
        [
            "<b>Division-by-Zero Guards:</b> Ensured resolution rate and anomaly rate endpoints never crash on fresh empty databases.",
            "<b>None-Safe Date Formatting:</b> Unresolved incidents gracefully display 'Not resolved' instead of throwing 500 errors.",
            "<b>RAM Buffer Rewind:</b> Enforced buffer.seek(0) across all PDF and Excel streams to eliminate corrupted downloads.",
            "<b>Static Route Precedence:</b> Placed /reports/compliance/pdf before dynamic /reports/{employee_id}/pdf."
        ],
        badge="Edge-Case Resilience", badge_color=C_AMBER, width=3.85*inch
    )
    qa3 = create_card_flowable(
        "Security & RBAC Enforcement",
        [
            "<b>Role Isolation Verified:</b> Non-admin roles (analyst, soc_engineer, manager) correctly receive 403 Forbidden on admin dashboard.",
            "<b>JWT Signature Verification:</b> Cryptographically validates token expiry and subject IDs.",
            "<b>Bcrypt Salted Hashes:</b> 12-round salted hashing protects passwords against rainbow table lookups.",
            "<b>Audit Immutability:</b> Administrative and security actions logged with operator email and timestamp."
        ],
        badge="RBAC Security", badge_color=C_CYAN, width=3.85*inch
    )
    row_s15 = Table([[qa1, qa2, qa3]], colWidths=[3.95*inch, 3.95*inch, 3.95*inch])
    row_s15.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(row_s15)

    # =========================================================================
    # SLIDE 16: CONCLUSION & ATTRIBUTION
    # =========================================================================
    story.append(PageBreak())
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph("PROJECT SUMMARY & DEMONSTRATION COMPLETE", s_eyebrow))
    story.append(Paragraph("Thank You!", ParagraphStyle('ClosingTitle', fontName='Helvetica-Bold', fontSize=36, leading=40, textColor=C_WHITE, spaceAfter=8)))
    story.append(Paragraph("Done by Sritha — Final Year Aspiring Student", ParagraphStyle('ClosingAuthor', fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=C_AMBER, spaceAfter=14)))
    story.append(Paragraph(
        "AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform (ITBIS)\nComplete Full-Stack Implementation: Milestones 1, 2, 3 & 4 (Executive Dashboards & Reporting)",
        ParagraphStyle('ClosingDesc', fontName='Helvetica', fontSize=12, leading=17, textColor=C_LIGHT, spaceAfter=20)
    ))

    summary_content = [
        Paragraph("LIVE DEPLOYMENT & TESTING REFERENCE:", ParagraphStyle('SummHead', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=C_CYAN, spaceAfter=6)),
        Paragraph("• <b>Live Application UI:</b> http://localhost:3000   |   <b>FastAPI Gateway & Swagger Docs:</b> http://127.0.0.1:8000/docs", ParagraphStyle('Summ1', fontName='Helvetica', fontSize=10, leading=15, textColor=C_LIGHT)),
        Paragraph("• <b>Git Remote Branch:</b> origin/student-sritha   |   <b>Database Store:</b> SQLite (backend/itbis.db) & MongoDB (backend/data/)", ParagraphStyle('Summ2', fontName='Helvetica', fontSize=10, leading=15, textColor=C_LIGHT)),
        Paragraph("• <b>Demo Credentials:</b> admin@itbis.security / manager@itbis.security / analyst@itbis.security (Password: Security@123)", ParagraphStyle('Summ3', fontName='Helvetica-Bold', fontSize=10, leading=15, textColor=C_EMERALD))
    ]
    summary_table = Table([[summary_content]], colWidths=[12.133 * inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_CARD),
        ('BOX', (0, 0), (-1, -1), 1.5, C_EMERALD),
        ('TOPPADDING', (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
        ('LEFTPADDING', (0, 0), (-1, -1), 18),
        ('RIGHTPADDING', (0, 0), (-1, -1), 18),
    ]))
    story.append(summary_table)

    # Build the document
    doc.build(story, onFirstPage=draw_bg, onLaterPages=draw_bg)
    print(f"[SUCCESS] PDF Presentation built successfully: {output_path}")

if __name__ == "__main__":
    out_dir = r"C:\Users\ASUS\.gemini\antigravity\scratch\itbis"
    target = os.path.join(out_dir, "ITBIS_Final_Comprehensive_Master_Presentation.pdf")
    build_pdf_presentation(target)

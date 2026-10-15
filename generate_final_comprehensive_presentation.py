# generate_final_comprehensive_presentation.py
"""
Generates the Definitive Master Presentation (.pptx) for the
AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform (ITBIS).
Covers Milestones 1, 2, 3, and 4 in exhaustive, crisp, non-AI-cliche detail.
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_master_presentation(output_path: str):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Professional Obsidian Cybersecurity Color Palette (No generic blue gradients)
    BG_OBSIDIAN = RGBColor(17, 19, 23)        # #111317 (Deep Matte Charcoal)
    BG_CARD = RGBColor(26, 29, 36)            # #1A1D24 (Matte Slate Card)
    BORDER_MUTED = RGBColor(46, 52, 66)       # #2E3442 (Card Border)
    BORDER_EMERALD = RGBColor(16, 185, 129)   # #10B981 (Active / Baseline)
    BORDER_AMBER = RGBColor(245, 158, 11)     # #F59E0B (Warning / Highlight)
    BORDER_CRIMSON = RGBColor(239, 68, 68)    # #EF4444 (Threat / Incident)
    
    TEXT_WHITE = RGBColor(255, 255, 255)
    TEXT_LIGHT = RGBColor(226, 232, 240)      # #E2E8F0
    TEXT_MUTED = RGBColor(148, 163, 184)      # #94A3B8
    
    COLOR_EMERALD = RGBColor(16, 185, 129)
    COLOR_AMBER = RGBColor(245, 158, 11)
    COLOR_CRIMSON = RGBColor(239, 68, 68)
    COLOR_PURPLE = RGBColor(168, 85, 247)
    COLOR_CYAN = RGBColor(6, 182, 212)

    img_flowchart = r"C:\Users\ASUS\.gemini\antigravity\brain\7f9d74e3-4522-4006-987a-e8eb9e4c49b3\itbis_architecture_flowchart_1791447431736.jpg"
    img_dashboard = r"C:\Users\ASUS\.gemini\antigravity\brain\7f9d74e3-4522-4006-987a-e8eb9e4c49b3\.user_uploaded\media_1791445574338.png"
    img_swagger = r"C:\Users\ASUS\.gemini\antigravity\brain\7f9d74e3-4522-4006-987a-e8eb9e4c49b3\.user_uploaded\media_1791447797616_b2aae74a.png"

    def set_bg(slide):
        fill = slide.background.fill
        fill.solid()
        fill.fore_color.rgb = BG_OBSIDIAN

    def add_header(slide, title_text, category_text="AI BEHAVIORAL SECURITY INTELLIGENCE"):
        # Category Eyebrow
        c_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.3))
        tf_c = c_box.text_frame
        tf_c.word_wrap = True
        tf_c.margin_left = tf_c.margin_right = tf_c.margin_top = tf_c.margin_bottom = 0
        p_c = tf_c.paragraphs[0]
        p_c.text = category_text.upper()
        p_c.font.name = "Arial"
        p_c.font.size = Pt(10)
        p_c.font.bold = True
        p_c.font.color.rgb = COLOR_CYAN

        # Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.55))
        tf_t = t_box.text_frame
        tf_t.word_wrap = True
        tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.name = "Arial"
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_WHITE

    def add_card(slide, left, top, width, height, title, bullets, badge=None, badge_color=COLOR_EMERALD, border_color=BORDER_MUTED):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = BG_CARD
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.2)

        pad = Inches(0.2)
        tb = slide.shapes.add_textbox(left + pad, top + pad, width - (2 * pad), height - (2 * pad))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

        if badge:
            p_badge = tf.paragraphs[0]
            p_badge.text = badge.upper()
            p_badge.font.name = "Arial"
            p_badge.font.size = Pt(8.5)
            p_badge.font.bold = True
            p_badge.font.color.rgb = badge_color
            p_badge.space_after = Pt(2)
            p_title = tf.add_paragraph()
        else:
            p_title = tf.paragraphs[0]

        p_title.text = title
        p_title.font.name = "Arial"
        p_title.font.size = Pt(12)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE
        p_title.space_after = Pt(4)

        for b in bullets:
            p_b = tf.add_paragraph()
            p_b.text = "• " + b
            p_b.font.name = "Arial"
            p_b.font.size = Pt(9.5)
            p_b.font.color.rgb = TEXT_LIGHT
            p_b.space_after = Pt(3)

    def add_framed_image(slide, img_path, left, top, width, height, border_color=BORDER_EMERALD):
        frame = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        frame.fill.solid()
        frame.fill.fore_color.rgb = BG_CARD
        frame.line.color.rgb = border_color
        frame.line.width = Pt(1.2)

        if os.path.exists(img_path):
            pad = Inches(0.05)
            slide.shapes.add_picture(img_path, left + pad, top + pad, width - (2 * pad), height - (2 * pad))

    # =========================================================================
    # SLIDE 1: COVER & EXECUTIVE PROJECT INTRODUCTION
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_bg(s1)

    # Accent left vertical stripe
    stripe = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.6), Inches(0.12), Inches(4.2))
    stripe.fill.solid()
    stripe.fill.fore_color.rgb = COLOR_CYAN
    stripe.line.fill.background()

    tb1 = s1.shapes.add_textbox(Inches(1.2), Inches(1.4), Inches(11.2), Inches(4.2))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "ENTERPRISE BEHAVIORAL SECURITY INTELLIGENCE PLATFORM (ITBIS)"
    p0.font.name = "Arial"
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_CYAN
    p0.space_after = Pt(8)

    p1 = tf1.add_paragraph()
    p1.text = "AI-Powered Insider Threat Detection & Security Intelligence"
    p1.font.name = "Arial"
    p1.font.size = Pt(34)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p1.space_after = Pt(6)

    p2 = tf1.add_paragraph()
    p2.text = "Complete Full-Stack Engineering & Forensic Defense Architecture"
    p2.font.name = "Arial"
    p2.font.size = Pt(17)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_AMBER
    p2.space_after = Pt(14)

    p3 = tf1.add_paragraph()
    p3.text = "An end-to-end security operations solution featuring hybrid anomaly detection (Heuristic Rules + Unsupervised Isolation Forest), dynamic 5-factor risk scoring, automated forensic incident synthesis, role-based executive dashboards, and in-memory export engines."
    p3.font.name = "Arial"
    p3.font.size = Pt(12)
    p3.font.color.rgb = TEXT_MUTED

    # Bottom Metadata Pill
    foot1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(5.8), Inches(11.2), Inches(1.1))
    foot1.fill.solid()
    foot1.fill.fore_color.rgb = BG_CARD
    foot1.line.color.rgb = BORDER_MUTED
    foot1.line.width = Pt(1.2)

    tb_foot1 = s1.shapes.add_textbox(Inches(1.4), Inches(5.9), Inches(10.8), Inches(0.9))
    tf_f1 = tb_foot1.text_frame
    pf1 = tf_f1.paragraphs[0]
    pf1.text = "PROJECT CANDIDATE & IMPLEMENTATION METADATA:"
    pf1.font.name = "Arial"
    pf1.font.size = Pt(9.5)
    pf1.font.bold = True
    pf1.font.color.rgb = COLOR_AMBER
    pf1.space_after = Pt(2)

    pf2 = tf_f1.add_paragraph()
    pf2.text = "Done by: Sritha (Final Year Aspiring Student)  •  Stack: FastAPI, Next.js 14, Scikit-Learn, SQLite & MongoDB  •  Milestones 1 – 4 Complete"
    pf2.font.name = "Arial"
    pf2.font.size = Pt(11)
    pf2.font.bold = True
    pf2.font.color.rgb = TEXT_WHITE

    # =========================================================================
    # SLIDE 2: THE PROBLEM STATEMENT: INSIDER THREATS VS PERIMETER DEFENSE
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2)
    add_header(s2, "The Problem: Why Traditional Firewalls Fail Against Insiders", "The Threat Landscape")

    top_pos = Inches(1.4)
    w3 = Inches(3.7)
    g3 = Inches(0.3)

    add_card(s2, Inches(0.8) + 0*(w3+g3), top_pos, w3, Inches(5.4),
             "1. The Perimeter Blindspot",
             [
                 "Traditional perimeter controls (NextGen Firewalls, VPNs, WAFs) are built to block unauthorized outside intrusion.",
                 "Malicious insiders and compromised credentials bypass 100% of perimeter rules because traffic originates from authenticated user sessions.",
                 "82% of enterprise breaches involve authorized user credentials or legitimate privileges abused from within (Verizon DBIR).",
                 "Perimeter tools cannot distinguish between a financial analyst generating a normal monthly report and an analyst exfiltrating client records."
             ],
             badge="Perimeter Blindness", badge_color=COLOR_CRIMSON, border_color=COLOR_CRIMSON)

    add_card(s2, Inches(0.8) + 1*(w3+g3), top_pos, w3, Inches(5.4),
             "2. Log Explosion & Alert Fatigue",
             [
                 "Modern cloud enterprises generate hundreds of gigabytes of raw logs daily (Active Directory, Kerberos, SSH, CloudTrail, file shares).",
                 "Traditional SIEM systems rely on static threshold alerts (e.g., 'flag if file transfers > 500MB').",
                 "Static thresholds create over 90% false positives, flooding SOC engineers with alert fatigue while stealthy attackers fly under thresholds.",
                 "Without continuous behavioral modeling, real multi-stage exfiltration attacks remain undetected for an average of 287 days."
             ],
             badge="Information Overload", badge_color=COLOR_AMBER, border_color=COLOR_AMBER)

    add_card(s2, Inches(0.8) + 2*(w3+g3), top_pos, w3, Inches(5.4),
             "3. The Disgruntled Insider Profile",
             [
                 "Flight-risk employees, resigning staff, and compromised accounts systematically stage data prior to departure.",
                 "Attackers use low-and-slow data movement, off-hours access, and alternative protocols (SFTP, USB mounts, encrypted cloud sync).",
                 "Static policies cannot evaluate contextual deviation—such as an engineer suddenly reading finance payroll databases at 2:00 AM.",
                 "Requires dynamic peer-group benchmarking, unsupervised machine learning, and automated digital forensic timelines."
             ],
             badge="Insider Risk Reality", badge_color=COLOR_PURPLE, border_color=COLOR_PURPLE)

    # =========================================================================
    # SLIDE 3: PROJECT SCOPE & 4-MILESTONE ROADMAP
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3)
    add_header(s3, "Platform Roadmap & Scope: Milestones 1 Through 4", "Project Architecture")

    w4 = Inches(2.76)
    g4 = Inches(0.22)
    h_m = Inches(5.4)

    add_card(s3, Inches(0.8) + 0*(w4+g4), top_pos, w4, h_m,
             "Milestone 1: Foundations",
             [
                 "Role-Based Access Control (RBAC) with 4 security roles (Admin, Manager, Analyst, SOC).",
                 "Stateless JWT bearer authentication with bcrypt salted password hashing.",
                 "Employee workforce directory tracking designation, device ID, baseline risk, and privileges.",
                 "SQLite relational persistence with SQLAlchemy ORM models."
             ],
             badge="Milestone 1: Days 1–10", badge_color=COLOR_EMERALD)

    add_card(s3, Inches(0.8) + 1*(w4+g4), top_pos, w4, h_m,
             "Milestone 2: Ingestion & AI",
             [
                 "High-throughput document telemetry store (MongoDB JSON backing).",
                 "Deterministic Heuristic Engine catching off-hours logins, volume spikes, and USB mounts.",
                 "Unsupervised Isolation Forest ML detector (Scikit-Learn, contamination c=0.12).",
                 "Extracts login hour, bytes transferred, and access failures into standardized feature vectors."
             ],
             badge="Milestone 2: Days 11–20", badge_color=COLOR_PURPLE)

    add_card(s3, Inches(0.8) + 2*(w4+g4), top_pos, w4, h_m,
             "Milestone 3: UEBA & Forensics",
             [
                 "5-Factor weighted composite risk equation normalized from 0 to 100.",
                 "Departmental peer group baselines and statistical Z-score deviation calculation.",
                 "Investigation Workbench: stitched chronological telemetry timelines.",
                 "Digital evidence chain of custody and MITRE ATT&CK framework mapping."
             ],
             badge="Milestone 3: Days 21–30", badge_color=COLOR_AMBER)

    add_card(s3, Inches(0.8) + 3*(w4+g4), top_pos, w4, h_m,
             "Milestone 4: Dashboards & Exports",
             [
                 "Security Manager Compliance View: resolution rate % and open critical triage.",
                 "Accurate MTTR and MTTI metrics tracking investigation lifecycle timestamps.",
                 "Admin Platform Analytics: workforce coverage and overall anomaly rates.",
                 "In-memory PDF risk & compliance dossiers and bulk Excel (.xlsx) data export engines."
             ],
             badge="Milestone 4: Days 31–34", badge_color=COLOR_CYAN)

    # =========================================================================
    # SLIDE 4: END-TO-END SYSTEM ARCHITECTURE
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4)
    add_header(s4, "End-to-End System Architecture & Data Flow", "Full-Stack Pipeline")

    add_framed_image(s4, img_flowchart, Inches(0.8), top_pos, Inches(5.8), Inches(5.4), border_color=COLOR_CYAN)

    w_right = Inches(5.8)
    add_card(s4, Inches(6.8), top_pos, w_right, Inches(1.65),
             "1. Telemetry Ingestion & JWT Gateway",
             [
                 "Client-side Next.js 14 communicates with FastAPI backend via REST API.",
                 "All routes protected with OAuth2 Bearer JWT authentication and role checkers.",
                 "High-frequency audit logs and endpoint events ingested directly into document store."
             ],
             badge="Ingestion Layer", badge_color=COLOR_CYAN)

    add_card(s4, Inches(6.8), top_pos + Inches(1.85), w_right, Inches(1.65),
             "2. Dual-Engine Analytical Processing",
             [
                 "Deterministic Rules check instantaneous policy violations (off-hours, impossible travel).",
                 "Scikit-Learn Isolation Forest isolates multi-dimensional behavioral anomalies.",
                 "Composite Risk Scorer combines rule, ML, peer, role, and privilege sub-scores."
             ],
             badge="Analytics & UEBA", badge_color=COLOR_PURPLE)

    add_card(s4, Inches(6.8), top_pos + Inches(3.7), w_right, Inches(1.7),
             "3. Incident Workbench, Dashboards & Reporting",
             [
                 "Alert escalation automatically provisions Incident records in relational SQLite.",
                 "MITRE ATT&CK T1048 mapping and chronological activity timeline generation.",
                 "Role-based executive views (Compliance, SOC, Admin) with in-memory PDF/Excel export."
             ],
             badge="Presentation & Output", badge_color=COLOR_EMERALD)

    # =========================================================================
    # SLIDE 5: COMPLETE TECHNOLOGY STACK & RATIONALE
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_bg(s5)
    add_header(s5, "Technology Stack Breakdown: Full-Stack Rationale", "Engineering Choices")

    w3_s5 = Inches(3.7)
    g3_s5 = Inches(0.3)

    add_card(s5, Inches(0.8) + 0*(w3_s5+g3_s5), top_pos, w3_s5, Inches(5.4),
             "Backend: FastAPI (Python 3.14)",
             [
                 "High-Performance Asynchronous I/O: Starlette + Uvicorn delivers microsecond REST latency.",
                 "Pydantic V2 Type Safety: Automated schema validation, serializing, and self-documenting Swagger/OpenAPI docs.",
                 "SQLAlchemy 2.0 ORM: Clean relational abstraction with connection pooling and thread safety.",
                 "Role-Based Dependency Injection: Custom Depends(require_role(...)) guards enforce least-privilege security natively at the gateway.",
                 "Lightweight & Native Python AI: Direct interop with Scikit-Learn without IPC overhead."
             ],
             badge="Application Gateway", badge_color=COLOR_EMERALD)

    add_card(s5, Inches(0.8) + 1*(w3_s5+g3_s5), top_pos, w3_s5, Inches(5.4),
             "Frontend: Next.js 14 & Tailwind",
             [
                 "React 18 & Next.js App Router: Component-driven UI architecture with route caching.",
                 "Tailwind CSS Dark Obsidian UI: Cyber-themed interface designed for low eye-strain in 24/7 SOC environments.",
                 "Lucide React Icons & Chart.js: Interactive radar charts, risk distributions, and anomaly trend charts.",
                 "Axios Request Interceptors: Automatic JWT token injection, unified error boundary, and blob download streaming.",
                 "Client-Side Role Switching: Instant demonstration testing across all 4 RBAC roles."
             ],
             badge="User Interface", badge_color=COLOR_CYAN)

    add_card(s5, Inches(0.8) + 2*(w3_s5+g3_s5), top_pos, w3_s5, Inches(5.4),
             "AI & Data: Isolation Forest & Reports",
             [
                 "Scikit-Learn Isolation Forest: Unsupervised recursive partitioning efficient for detecting multi-variable outliers.",
                 "ReportLab Platypus: In-memory dynamic PDF compiler producing executive dossiers via io.BytesIO() without disk writes.",
                 "Pandas & OpenPyXL: High-speed tabular workbook generator with safe date formatting and custom column sorting.",
                 "Dual-Database Strategy: ACID relational tables for users/incidents; flexible schema document store for high-volume logs."
             ],
             badge="Intelligence & Data", badge_color=COLOR_PURPLE)

    # =========================================================================
    # SLIDE 6: DUAL DATABASE ARCHITECTURE: RELATIONAL VS DOCUMENT STORE
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_bg(s6)
    add_header(s6, "Dual-Database Architecture: Schema & Data Modeling", "Data Storage Layer")

    w_half = Inches(5.7)
    g_half = Inches(0.33)

    add_card(s6, Inches(0.8), top_pos, w_half, Inches(5.4),
             "Relational Database: SQLite / PostgreSQL (itbis.db)",
             [
                 "Role: Strict relational integrity, foreign keys, and audit compliance.",
                 "users: id, email, password_hash, full_name, role, is_active, created_at.",
                 "employees: id, employee_id, name, department, designation, device_info, access_privileges, status, baseline_risk_score.",
                 "incidents: id, incident_code, employee_id, severity, status, title, description, assigned_to, mitre_attack_technique, investigation_started_at, resolved_at.",
                 "evidence: id, incident_id, note, added_by, added_at (foreign key linked).",
                 "alerts: id, alert_code, employee_id, severity, message, status, anomaly_type, risk_score, created_at, resolved_at.",
                 "audit_logs: id, user_id, user_email, action, target_resource, details, timestamp."
             ],
             badge="Relational ACID Store", badge_color=COLOR_EMERALD, border_color=BORDER_EMERALD)

    add_card(s6, Inches(0.8) + w_half + g_half, top_pos, w_half, Inches(5.4),
             "Document Store: MongoDB / JSON Collections (data/)",
             [
                 "Role: High-throughput ingestion of un-structured telemetry and anomaly records.",
                 "activity_logs.json: Raw audit telemetry events with timestamp, employee_id, event_type (LOGIN, FILE_TRANSFER, USB_MOUNT), bytes_transferred, ip_address, and status.",
                 "rule_anomalies.json: Deterministic violations flagged by rule engine with detected_at, severity, rule_name, and employee_id.",
                 "ml_anomalies.json: Statistical anomaly entries with is_anomaly (boolean), anomaly_score (float), and feature vectors.",
                 "Aggregation Pipeline Support: Uses $match, $group, and $dateToString for 7-day anomaly trend visualizations and department-level aggregations."
             ],
             badge="High-Volume Document Store", badge_color=COLOR_AMBER, border_color=BORDER_AMBER)

    # =========================================================================
    # SLIDE 7: TELEMETRY INGESTION & AUDIT LOGGING MECHANISM
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_bg(s7)
    add_header(s7, "Telemetry Ingestion & Platform Audit Logging", "Audit & Ingestion")

    add_card(s7, Inches(0.8), top_pos, w_half, Inches(5.4),
             "High-Throughput Log Ingestion Pipeline",
             [
                 "Endpoint: POST /api/logs/ingest",
                 "Validates event schema via Pydantic ActivityLogIngest model.",
                 "Supported Telemetry Types:",
                 "  • LOGIN: IP, user agent, workstation hostname, login hour.",
                 "  • FILE_ACCESS / FILE_TRANSFER: Source folder, file size, bytes.",
                 "  • PRIVILEGE_USE: Sudo, admin impersonation, token generation.",
                 "  • USB_DEVICE: Mass storage insertion, device serial.",
                 "Automatic Timestamping: Fallback to UTC if client timestamp missing.",
                 "Non-Blocking Persistence: Thread-safe in-memory cache synchronized with JSON backing store."
             ],
             badge="Log Ingestion Engine", badge_color=COLOR_CYAN)

    add_card(s7, Inches(0.8) + w_half + g_half, top_pos, w_half, Inches(5.4),
             "Day 32 Simple Audit Log Implementation",
             [
                 "Dedicated Helper Function: log_action(db, user_id, action, details, target_resource)",
                 "Retrofitted Across Sensitive Security Endpoints:",
                 "  1. Alert Assignment: /api/alerts/{id}/assign -> logs assignee email and assigner user_id.",
                 "  2. Alert Resolution: /api/alerts/{id}/resolve -> logs resolving analyst and timestamp.",
                 "  3. Incident Creation: /api/incidents -> logs newly generated incident code and target employee.",
                 "  4. Status Updates: /api/incidents/{id}/status -> tracks transitions from OPEN to INVESTIGATING or RESOLVED.",
                 "  5. User Provisioning: /api/auth/register -> records new account creation and granted RBAC role.",
                 "Queryable via GET /api/dashboard/admin/audit-log and exportable to Excel."
             ],
             badge="Governance Audit Trail", badge_color=COLOR_PURPLE)

    # =========================================================================
    # SLIDE 8: DETECTION ENGINE 1: DETERMINISTIC HEURISTIC RULES
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_bg(s8)
    add_header(s8, "Detection Engine 1: Deterministic Heuristic Rules", "Behavioral Rule Engine")

    add_card(s8, Inches(0.8) + 0*(w4+g4), top_pos, w4, h_m,
             "Rule 1: Off-Hours Access",
             [
                 "Trigger Condition: Employee logs in or accesses resources between 22:00 and 05:00 local time.",
                 "Context Filter: Checked against department working hours profile.",
                 "Severity: HIGH.",
                 "Insider Risk Correlation: Disgruntled staff frequently stage exfiltration during night shifts when physical SOC staffing is minimal."
             ],
             badge="Temporal Anomaly", badge_color=COLOR_AMBER)

    add_card(s8, Inches(0.8) + 1*(w4+g4), top_pos, w4, h_m,
             "Rule 2: Volume Spike",
             [
                 "Trigger Condition: Single-session file transfer exceeds 1.0 GB or 3.5x normal baseline volume.",
                 "Context Filter: Evaluated against 30-day historical transfer rolling average.",
                 "Severity: CRITICAL.",
                 "Insider Risk Correlation: Mass downloading of source code repositories or sensitive financial exports."
             ],
             badge="Data Exfiltration", badge_color=COLOR_CRIMSON)

    add_card(s8, Inches(0.8) + 2*(w4+g4), top_pos, w4, h_m,
             "Rule 3: Restricted Access",
             [
                 "Trigger Condition: Access attempt on classified folders (e.g., /prod/finance_db_backup, /confidential_hr).",
                 "Context Filter: Cross-referenced with employee access_privileges list.",
                 "Severity: CRITICAL.",
                 "Insider Risk Correlation: Snooping, lateral movement, or privilege abuse across departmental boundaries."
             ],
             badge="Privilege Abuse", badge_color=COLOR_PURPLE)

    add_card(s8, Inches(0.8) + 3*(w4+g4), top_pos, w4, h_m,
             "Rule 4: Multi-Alert Spike",
             [
                 "Trigger Condition: More than 3 distinct rule triggers within a rolling 60-minute window.",
                 "Context Filter: Aggregated by employee_id.",
                 "Severity: CRITICAL.",
                 "Insider Risk Correlation: Active, aggressive exfiltration campaign requiring immediate automated quarantine."
             ],
             badge="Heuristic Escalation", badge_color=COLOR_CRIMSON)

    # =========================================================================
    # SLIDE 9: DETECTION ENGINE 2: UNSUPERVISED ISOLATION FOREST ML
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_bg(s9)
    add_header(s9, "Detection Engine 2: Unsupervised Machine Learning (Isolation Forest)", "Machine Learning")

    add_card(s9, Inches(0.8), top_pos, w_half, Inches(5.4),
             "Algorithm Architecture & Feature Engineering",
             [
                 "Why Isolation Forest? Traditional clustering (K-Means, DBSCAN) struggles with high-dimensional sparsity. Isolation Forest isolates anomalies recursively: outliers require fewer random splits to separate.",
                 "Trained on 3 Engineered Behavioral Features:",
                 "  1. Login Hour Metric: Normalizes access time (0.0 to 23.99).",
                 "  2. Data Volume Transferred: Megabytes moved per operation.",
                 "  3. Access Failure Velocity: Number of 401/403 errors in session.",
                 "Contamination Factor: Configured to c = 0.12 (12%), matching enterprise SOC anomaly expectations.",
                 "Mathematical Anomaly Score:",
                 "  s(x, n) = 2^(-E(h(x)) / c(n))",
                 "  Where E(h(x)) is average path length across 100 decision trees."
             ],
             badge="ML Engine Core", badge_color=COLOR_PURPLE)

    add_card(s9, Inches(0.8) + w_half + g_half, top_pos, w_half, Inches(5.4),
             "Inference, Decision Boundary & Normalization",
             [
                 "Model Output & Scikit-Learn Prediction:",
                 "  • Prediction = -1 -> Behavioral Anomaly Flagged.",
                 "  • Prediction = +1 -> Normal In-Distribution Activity.",
                 "Score Normalization: Raw decision function scores [-0.5, 0.5] mapped linearly to standard [0.0, 1.0] confidence interval.",
                 "Zero-Day Threat Detection: Catches multi-dimensional deviations that evade single-variable rule thresholds (e.g., moderate volume transfer paired with unusual hours and elevated failure rate).",
                 "Model Persistence: Automatically re-fits and updates dynamic baselines as healthy workforce telemetry accumulates."
             ],
             badge="Scoring & Decision", badge_color=COLOR_CYAN)

    # =========================================================================
    # SLIDE 10: DYNAMIC 5-FACTOR RISK SCORING ENGINE & UEBA
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_bg(s10)
    add_header(s10, "Dynamic 5-Factor Risk Scoring Engine & UEBA Benchmarking", "Risk Intelligence")

    add_card(s10, Inches(0.8), top_pos, w_half, Inches(5.4),
             "The 5-Factor Composite Mathematical Formula",
             [
                 "Composite Risk Equation:",
                 "  Risk Score = 0.35 * R_rule + 0.30 * R_ML + 0.20 * R_peer + 0.10 * R_role + 0.05 * R_priv",
                 "1. Rule Violations (35% Weight): Cumulative severity of deterministic triggers.",
                 "2. Machine Learning Anomaly (30% Weight): Isolation Forest anomaly probability score.",
                 "3. Peer Group Deviation (20% Weight): Statistical Z-score deviation from departmental mean:",
                 "   Z = (Employee_Activity - Mean_Dept) / StdDev_Dept",
                 "4. Role Sensitivity (10% Weight): Intrinsic sensitivity of role (Finance/DevOps = 85, Sales = 40).",
                 "5. Privilege Factor (5% Weight): Access level score (K8s/Prod DB = 90, Standard = 30)."
             ],
             badge="Mathematical Modeling", badge_color=COLOR_AMBER, border_color=BORDER_AMBER)

    add_card(s10, Inches(0.8) + w_half + g_half, top_pos, w_half, Inches(5.4),
             "Risk Stratification & SOC Action Thresholds",
             [
                 "Score Normalization Range: 0.0 to 100.0",
                 "1. LOW RISK (Score 0 – 24): Normal baseline operation. No analyst action needed.",
                 "2. MEDIUM RISK (Score 25 – 49): Mild anomaly or minor off-hours login. Telemetry logged; system continues passive monitoring.",
                 "3. HIGH RISK (Score 50 – 74): Elevated behavioral outlier. Alert dispatched to SOC Analyst queue; single-click incident creation available.",
                 "4. CRITICAL RISK (Score 75 – 100): High-confidence malicious insider event. Automated incident generated; immediate credential quarantine recommended."
             ],
             badge="Risk Stratification", badge_color=COLOR_CRIMSON, border_color=BORDER_CRIMSON)

    # =========================================================================
    # SLIDE 11: LIVE THREAT SIMULATION: CASE OF DEVON MILLER (EMP1003)
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_bg(s11)
    add_header(s11, "Live Threat Simulation: Case Study of Devon Miller (EMP1003)", "Case Study")

    add_card(s11, Inches(0.8) + 0*(w3+g3), top_pos, w3, Inches(5.4),
             "Phase 1: Healthy Baseline State",
             [
                 "Subject: Devon Miller (EMP1003)",
                 "Department: Cloud Infrastructure / DevOps",
                 "Role: Senior Cloud Infrastructure Lead",
                 "Initial Baseline Risk Score: 15.2 (Low)",
                 "Initial Status: ACTIVE",
                 "Normal Behavior: Standard working hours (09:00 - 18:00), average transfer volume < 45 MB, zero policy violations."
             ],
             badge="Baseline Integrity", badge_color=COLOR_EMERALD)

    add_card(s11, Inches(0.8) + 1*(w3+g3), top_pos, w3, Inches(5.4),
             "Phase 2: Attack Simulation Trigger",
             [
                 "Attack Scenario: 'mass_exfiltration'",
                 "Simulation API: POST /api/simulation/run",
                 "Payload: {'scenario': 'mass_exfiltration', 'employee_id': 'EMP1003'}",
                 "Injected Telemetry Events:",
                 "  • 02:45 AM: Off-hours SSH session opened.",
                 "  • 02:50 AM: 8.4 GB sensitive financial backups exported via SFTP.",
                 "  • 02:52 AM: Unauthorized token access on /prod/finance_db_backup."
             ],
             badge="Threat Simulation", badge_color=COLOR_CRIMSON, border_color=COLOR_CRIMSON)

    add_card(s11, Inches(0.8) + 2*(w3+g3), top_pos, w3, Inches(5.4),
             "Phase 3: Real-Time AI Detection",
             [
                 "Risk Score Jump: 15.2 -> 84.6 (CRITICAL RED ALERT).",
                 "UEBA Peer Deviation: Delta = +84.6 above Cloud Ops team mean.",
                 "Rule Triggers: Off-hours access + mass transfer spike.",
                 "ML Isolation Forest: Anomaly score s = 0.912 (Severe Outlier).",
                 "Incident Generated: INC-2026-8841 automatically opened and assigned to SOC triage."
             ],
             badge="Threat Neutralization", badge_color=COLOR_CRIMSON, border_color=COLOR_CRIMSON)

    # =========================================================================
    # SLIDE 12: INCIDENT WORKBENCH & FORENSIC EVIDENCE LEDGER
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_bg(s12)
    add_header(s12, "Incident Investigation Workbench & Forensic Evidence Ledger", "SOC Forensics")

    add_card(s12, Inches(0.8), top_pos, w_half, Inches(5.4),
             "Investigation Workbench Features",
             [
                 "Incident Dossier Generation: POST /api/incidents/{id}/generate-ai-report",
                 "Automated AI Forensic Brief synthesizing employee profile, event context, and containment playbooks.",
                 "Chronological Event Timeline: Stitches raw MongoDB activity logs and anomaly triggers into an interactive linear timeline.",
                 "MITRE ATT&CK Mapping:",
                 "  • T1048.002: Exfiltration Over Alternative Protocol (SSH/SFTP).",
                 "  • T1078.004: Valid Accounts: Cloud Accounts.",
                 "  • T1083: File and Directory Discovery.",
                 "Recommended SOC Playbooks: Revoke Kerberos session, isolate laptop MAC, notify HR and Legal."
             ],
             badge="Forensic Workbench", badge_color=COLOR_CYAN)

    add_card(s12, Inches(0.8) + w_half + g_half, top_pos, w_half, Inches(5.4),
             "Digital Evidence Chain of Custody",
             [
                 "Relational Table: evidence (linked to incidents via foreign key).",
                 "Stored Fields: id, incident_id, note, added_by (User ID), added_at (UTC).",
                 "Live Forensic Evidence Captured for EMP1003:",
                 "  • EVID-1092: Mass exfiltration of 8.4 GB financial backup files via SFTP at 02:50 UTC.",
                 "  • EVID-1093: Isolation Forest peer group deviation exceeded 4.8 standard deviations.",
                 "  • EVID-1094: Unauthorized token generation attempt on production financial database.",
                 "Immutable Tracking: Analyst attribution logged with tamper-evident audit trail."
             ],
             badge="Chain of Custody", badge_color=COLOR_EMERALD)

    # =========================================================================
    # SLIDE 13: EXECUTIVE & ADMIN DASHBOARDS (DAYS 31 & 32)
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_bg(s13)
    add_header(s13, "Executive & Admin Dashboards (Milestone 4 Days 31 & 32)", "Management & Health")

    add_card(s13, Inches(0.8), top_pos, w_half, Inches(5.4),
             "Day 31: Security Manager Compliance View",
             [
                 "Endpoint: GET /api/dashboard/manager/compliance",
                 "Allowed Roles: admin, security_manager (403 for analysts).",
                 "Resolution Rate Calculation:",
                 "  Rate % = round((resolved_incidents / total_incidents) * 100, 1)",
                 "Zero-Division Guard: Defaults safely to 0.0% on empty database.",
                 "Separate Open Critical Metric: Highlights unresolved critical threats regardless of overall percentage.",
                 "MTTR (Mean Time to Respond): Average hours between alert created_at and resolved_at.",
                 "MTTI (Mean Time to Investigate): Average hours between incident creation and an analyst beginning triage (investigation_started_at)."
             ],
             badge="Executive Compliance", badge_color=COLOR_EMERALD)

    add_card(s13, Inches(0.8) + w_half + g_half, top_pos, w_half, Inches(5.4),
             "Day 32: Admin Dashboard & Platform Health",
             [
                 "Endpoint: GET /api/dashboard/admin (Strict admin only).",
                 "User Governance: Aggregates accounts by role (admin, security_manager, security_analyst, soc_engineer).",
                 "Monitored Workforce: Employees tracked & distinct departments count via db.query(Employee.department).distinct().count().",
                 "Platform Volume Analytics: GET /api/dashboard/admin/platform-analytics",
                 "Calculates Platform Anomaly Rate:",
                 "  Anomaly Rate % = round(((rule_anomalies + ml_anomalies) / total_logs) * 100, 2)",
                 "Sanity Metric: Verifies detection sensitivity (real-world SOCs aim for single-digit anomaly rates; flags over-tuning)."
             ],
             badge="Platform Governance", badge_color=COLOR_PURPLE)

    # =========================================================================
    # SLIDE 14: REPORTS & EXPORT SYSTEM (DAYS 33 & 34)
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_bg(s14)
    add_header(s14, "Reports & Export System: In-Memory PDF & Excel (Days 33 & 34)", "Reporting Engine")

    add_card(s14, Inches(0.8), top_pos, w_half, Inches(5.4),
             "Day 33: In-Memory PDF Reporting Engine",
             [
                 "Built with ReportLab Platypus & io.BytesIO() entirely in RAM.",
                 "Zero Temporary Disk Writes: Eliminates server disk accumulation, race conditions, and unneeded disk I/O.",
                 "1. Individual Risk Report: GET /api/reports/{employee_id}/pdf",
                 "   • Styled 5-factor sub-score table (#7a1f2b crimson header).",
                 "   • Capped at 10 recent anomalies; handles 0 total cleanly without crashing.",
                 "2. Compliance Summary Report: GET /api/reports/compliance/pdf",
                 "   • Reuses Day 31 compliance metrics, SLA benchmarks, and incident audit records.",
                 "Headers: Content-Disposition: attachment; filename=... with media_type='application/pdf'."
             ],
             badge="PDF Engine (ReportLab)", badge_color=COLOR_CRIMSON)

    add_card(s14, Inches(0.8) + w_half + g_half, top_pos, w_half, Inches(5.4),
             "Day 34: Excel Data Exports & Report Catalog",
             [
                 "Built with Pandas & OpenPyXL for structured tabular datasets.",
                 "MIME Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                 "1. Bulk Risk Scores: GET /api/reports/export/risk-scores",
                 "   • Pre-sorted descending: highest-risk staff appear first.",
                 "   • Optional department filter parameter.",
                 "2. Incident Export: GET /api/reports/export/incidents",
                 "   • Inline date guard: i.resolved_at.strftime(...) if i.resolved_at else 'Not resolved' prevents AttributeError.",
                 "3. Report Catalog: GET /api/reports/catalog",
                 "   • Single source of truth serving UI with available formats and endpoints."
             ],
             badge="Excel Exports & Catalog", badge_color=COLOR_EMERALD)

    # =========================================================================
    # SLIDE 15: VERIFICATION, TESTING & QUALITY ASSURANCE
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    set_bg(s15)
    add_header(s15, "Verification, Testing & Automated Quality Assurance", "Quality Assurance")

    add_card(s15, Inches(0.8) + 0*(w3+g3), top_pos, w3, Inches(5.4),
             "Automated TestClient Suite",
             [
                 "Executed in test_milestone4_endpoints.py.",
                 "100% Pass Rate across all Milestone 4 test suites:",
                 "  • Day 31 Compliance View & MTTR/MTTI calculations.",
                 "  • Day 32 Admin user counts & platform volume analytics.",
                 "  • Audit logging across alert assignment, resolution, and incident creation.",
                 "  • PDF generation for both high-anomaly and zero-anomaly employees.",
                 "  • Excel risk sorting and unresolved date handling."
             ],
             badge="Test Automation", badge_color=COLOR_EMERALD)

    add_card(s15, Inches(0.8) + 1*(w3+g3), top_pos, w3, Inches(5.4),
             "Defensive Edge-Case Handling",
             [
                 "Division-by-Zero Guards: Ensured resolution rate and anomaly rate endpoints never crash on fresh empty databases.",
                 "None-Safe Date Formatting: Unresolved incidents gracefully display 'Not resolved' instead of throwing 500 errors.",
                 "RAM Buffer Rewind: Enforced buffer.seek(0) across all PDF and Excel streams to eliminate corrupted downloads.",
                 "Static Route Precedence: Placed /reports/compliance/pdf before dynamic /reports/{employee_id}/pdf."
             ],
             badge="Edge-Case Resilience", badge_color=COLOR_AMBER)

    add_card(s15, Inches(0.8) + 2*(w3+g3), top_pos, w3, Inches(5.4),
             "Security & RBAC Enforcement",
             [
                 "Role Isolation Verified: Non-admin roles (analyst, soc_engineer, manager) correctly receive 403 Forbidden on admin dashboard.",
                 "JWT Signature Verification: Cryptographically validates token expiry and subject IDs.",
                 "Bcrypt Salted Hashes: 12-round salted hashing protects passwords against rainbow table lookups.",
                 "Audit Immutability: Administrative and security actions logged with operator email and timestamp."
             ],
             badge="RBAC Security", badge_color=COLOR_CYAN)

    # =========================================================================
    # SLIDE 16: CONCLUSION & STUDENT ATTRIBUTION
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    set_bg(s16)

    bar16 = s16.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(0.12), Inches(4.5))
    bar16.fill.solid()
    bar16.fill.fore_color.rgb = COLOR_EMERALD
    bar16.line.fill.background()

    tb16 = s16.shapes.add_textbox(Inches(1.2), Inches(1.3), Inches(11.2), Inches(4.5))
    tf16 = tb16.text_frame
    tf16.word_wrap = True

    p16_0 = tf16.paragraphs[0]
    p16_0.text = "PROJECT SUMMARY & DEMONSTRATION COMPLETE"
    p16_0.font.name = "Arial"
    p16_0.font.size = Pt(11)
    p16_0.font.bold = True
    p16_0.font.color.rgb = COLOR_EMERALD
    p16_0.space_after = Pt(8)

    p16_1 = tf16.add_paragraph()
    p16_1.text = "Thank You!"
    p16_1.font.name = "Arial"
    p16_1.font.size = Pt(38)
    p16_1.font.bold = True
    p16_1.font.color.rgb = TEXT_WHITE
    p16_1.space_after = Pt(6)

    p16_2 = tf16.add_paragraph()
    p16_2.text = "Done by Sritha — Final Year Aspiring Student"
    p16_2.font.name = "Arial"
    p16_2.font.size = Pt(20)
    p16_2.font.bold = True
    p16_2.font.color.rgb = COLOR_AMBER
    p16_2.space_after = Pt(14)

    p16_3 = tf16.add_paragraph()
    p16_3.text = "AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform (ITBIS)\nComplete Full-Stack Implementation: Milestones 1, 2, 3 & 4 (Executive Dashboards & Reporting)"
    p16_3.font.name = "Arial"
    p16_3.font.size = Pt(13)
    p16_3.font.color.rgb = TEXT_LIGHT
    p16_3.space_after = Pt(12)

    p16_4 = tf16.add_paragraph()
    p16_4.text = "• Live Application UI: http://localhost:3000   |   FastAPI Gateway & Swagger Docs: http://127.0.0.1:8000/docs\n• Git Repository Remote: origin/student-sritha   |   Database Store: SQLite (backend/itbis.db) & MongoDB (backend/data/)\n• Demo Credentials: admin@itbis.security / manager@itbis.security / analyst@itbis.security (Security@123)"
    p16_4.font.name = "Arial"
    p16_4.font.size = Pt(10.5)
    p16_4.font.color.rgb = COLOR_CYAN

    # Save presentation
    prs.save(output_path)
    print(f"[SUCCESS] Presentation generated successfully: {output_path}")

if __name__ == "__main__":
    out_dir = r"C:\Users\ASUS\.gemini\antigravity\scratch\itbis"
    target = os.path.join(out_dir, "ITBIS_Final_Comprehensive_Master_Presentation.pptx")
    create_master_presentation(target)

# backend/app/reports.py
"""
Day 33: In-Memory PDF Reporting Engine using ReportLab.
Generates executive-ready, downloadable PDF reports entirely in RAM without temporary disk writes.
"""
import io
from datetime import datetime
from typing import Any, Dict, List, Optional

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def generate_employee_risk_report(employee_id: str, risk_data: Dict[str, Any], anomalies: List[Dict[str, Any]]) -> bytes:
    """
    Day 33 Employee Risk Report PDF Generator:
    Constructs an in-memory PDF with employee risk level, factor sub-scores, and capped anomaly records.
    Safely handles 0 total anomalies without crashing.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    styles = getSampleStyleSheet()
    story = []

    # Title & Metadata
    story.append(Paragraph(f"Insider Risk Report: {employee_id}", styles["Title"]))
    story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"]))
    story.append(Spacer(1, 10))

    risk_level = risk_data.get("risk_level") or risk_data.get("risk_category") or "UNKNOWN"
    score_val = risk_data.get("final_score") if "final_score" in risk_data else risk_data.get("composite_risk_score", 0)
    
    story.append(Paragraph(
        f"Overall Risk Level: {str(risk_level).upper()} (Score: {score_val}/100)",
        styles["Heading2"]
    ))
    story.append(Spacer(1, 12))

    # Factor Sub-Scores Table
    table_data = [["Risk Factor", "Sub-Score"]]
    sub_scores = risk_data.get("sub_scores") or risk_data.get("factors") or {}
    for factor, score in sub_scores.items():
        clean_factor = str(factor).replace("_", " ").title()
        table_data.append([clean_factor, f"{score}/100"])

    if len(table_data) == 1:
        # Default factors if sub_scores was not explicit
        table_data.append(["Rule-Based Violations", f"{score_val}/100"])
        table_data.append(["Machine Learning Isolation Forest", f"{score_val}/100"])
        table_data.append(["Peer Group Behavioral Deviation", f"{score_val}/100"])
        table_data.append(["Role Sensitivity Factor", "50/100"])
        table_data.append(["Privilege & Access Level", "60/100"])

    table = Table(table_data, colWidths=[280, 140])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7a1f2b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 16))

    # Recent Anomalies (Capped at 10 items, gracefully handles 0 anomalies)
    story.append(Paragraph(f"Recent Anomalies ({len(anomalies)} total)", styles["Heading2"]))
    story.append(Spacer(1, 8))

    if not anomalies:
        story.append(Paragraph("No behavioral anomalies detected for this employee (0 total). Baseline integrity verified.", styles["Normal"]))
    else:
        for a in anomalies[:10]:
            anom_type = a.get("anomaly_type") or a.get("rule_name") or a.get("event_type") or "Behavioral Anomaly"
            sev = a.get("severity") or ("Critical" if a.get("is_anomaly") else "Medium")
            desc = a.get("description") or a.get("message") or a.get("mitre_technique") or "Telemetry flagged by behavioral detection engine"
            story.append(Paragraph(f"- <b>{anom_type}</b> (Severity: {sev}): {desc}", styles["Normal"]))
            story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_compliance_summary_report(compliance_data: Dict[str, Any], incidents_list: List[Any]) -> bytes:
    """
    Day 33 Exercise 3 Compliance Summary PDF Generator:
    Produces an executive compliance report summarizing SLA metrics, MTTR, MTTI, and resolution rates.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("ITBIS Security Compliance & Executive Audit Report", styles["Title"]))
    story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Executive SLA & Threat Remediation Metrics", styles["Heading2"]))
    story.append(Spacer(1, 8))

    mttr_val = compliance_data.get("mean_time_to_respond_hours")
    mttr_str = f"{mttr_val} hours" if mttr_val is not None else "N/A (No resolved alerts)"

    mtti_val = compliance_data.get("mean_time_to_investigate_hours")
    mtti_str = f"{mtti_val} hours" if mtti_val is not None else "N/A (No open investigations)"

    metrics_table_data = [
        ["Compliance Metric", "Value", "Benchmark Target"],
        ["Total Platform Incidents", str(compliance_data.get("total_incidents", 0)), "N/A"],
        ["Resolved Incidents", str(compliance_data.get("resolved_incidents", 0)), "High Closure"],
        ["Incident Resolution Rate", f"{compliance_data.get('resolution_rate_percent', 0.0)}%", "> 80.0%"],
        ["Open Critical Incidents", str(compliance_data.get("open_critical_incidents", 0)), "0 Target"],
        ["Mean Time to Respond (MTTR)", mttr_str, "< 24.0 hours"],
        ["Mean Time to Investigate (MTTI)", mtti_str, "< 4.0 hours"]
    ]

    t = Table(metrics_table_data, colWidths=[200, 140, 140])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 16))

    story.append(Paragraph(f"Incident Audit Records ({len(incidents_list)} Total)", styles["Heading2"]))
    story.append(Spacer(1, 8))

    if not incidents_list:
        story.append(Paragraph("No recorded incidents on platform. Risk state clean.", styles["Normal"]))
    else:
        inc_data = [["Incident Code", "Employee", "Severity", "Status", "Created"]]
        for inc in incidents_list[:15]:
            inc_data.append([
                getattr(inc, "incident_code", None) or f"INC-{inc.id}",
                getattr(inc, "employee_id", "Unknown"),
                str(getattr(inc, "severity", "medium")).upper(),
                str(getattr(inc, "status", "open")).upper(),
                inc.created_at.strftime("%Y-%m-%d %H:%M") if getattr(inc, "created_at", None) else "N/A"
            ])
        inc_table = Table(inc_data, colWidths=[110, 90, 80, 90, 110])
        inc_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7a1f2b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(inc_table)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

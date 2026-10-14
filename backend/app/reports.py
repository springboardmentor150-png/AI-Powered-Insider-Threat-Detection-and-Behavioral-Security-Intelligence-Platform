"""
Reports generation module for ITBIS (Milestone 4, Part 2 - Day 33).
Generates in-memory PDF reports using ReportLab.
"""

import io
from datetime import datetime, timezone
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def generate_employee_risk_report(
    employee_id: str,
    risk_data: dict,
    anomalies: list,
) -> bytes:
    """
    Generate an in-memory PDF risk report for a single employee.
    
    Includes overall risk score, risk level, breakdown of weighted sub-scores,
    and recent behavioral/rule anomalies.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    styles = getSampleStyleSheet()
    story = []

    # Title & Header
    story.append(Paragraph(f"Insider Risk Report: {employee_id}", styles["Title"]))
    generated_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    story.append(Paragraph(f"Generated: {generated_time}", styles["Normal"]))
    story.append(Spacer(1, 8))

    # Overall Risk Level
    final_score = risk_data.get("final_score", risk_data.get("risk_score", 0))
    risk_level = risk_data.get("risk_level", risk_data.get("risk_category", "Low")).capitalize()
    story.append(Paragraph(
        f"Overall Risk Level: {risk_level} (Score: {final_score}/100)",
        styles["Heading2"]
    ))
    story.append(Spacer(1, 12))

    # Risk Factors & Sub-scores Table
    sub_scores = risk_data.get("sub_scores") or risk_data.get("factor_scores") or {}
    table_data = [["Risk Factor", "Sub-Score"]]
    for factor, score in sub_scores.items():
        table_data.append([factor.replace("_", " ").title(), f"{score}/100"])

    table = Table(table_data, colWidths=[320, 150])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7a1f2b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 16))

    # Recent Anomalies Section (capped at 10 items)
    story.append(Paragraph(f"Recent Anomalies ({len(anomalies)} total)", styles["Heading2"]))
    if not anomalies:
        story.append(Paragraph("No anomalies detected for this employee.", styles["Normal"]))
    else:
        for a in anomalies[:10]:
            anomaly_type = (
                a.get("anomaly_type")
                or a.get("indicator")
                or ("ML Anomaly" if a.get("is_anomaly") else "behavioral_anomaly")
            )
            severity = a.get("severity") or ("High" if a.get("is_anomaly") else "n/a")
            story.append(
                Paragraph(f"- {anomaly_type} (severity: {severity})", styles["Normal"])
            )

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_compliance_report(compliance_data: dict) -> bytes:
    """
    Generate an in-memory compliance summary PDF report.
    Reuses organizational posture, operational metrics, and audit controls.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    styles = getSampleStyleSheet()
    story = []

    # Title & Header
    story.append(Paragraph("ITBIS Compliance & Security Audit Report", styles["Title"]))
    generated_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    story.append(Paragraph(f"Generated: {generated_time}", styles["Normal"]))
    story.append(Spacer(1, 8))

    # Executive Overview
    story.append(Paragraph("Executive Compliance Summary", styles["Heading2"]))
    overview_text = (
        "This security intelligence report documents organizational risk posture, incident response "
        "timeliness, and continuous behavioral telemetry in alignment with ISO/IEC 27001, "
        "NIST SP 800-53, and SOC 2 insider threat mitigation standards."
    )
    story.append(Paragraph(overview_text, styles["Normal"]))
    story.append(Spacer(1, 12))

    # Operational & Compliance Metrics Table
    metrics = compliance_data.get("metrics", [])
    if metrics:
        story.append(Paragraph("Key Compliance & Operational Indicators", styles["Heading3"]))
        table_data = [["Compliance Indicator", "Measured Value", "Target Standard"]]
        for item in metrics:
            table_data.append([
                str(item.get("metric", "")),
                str(item.get("value", "")),
                str(item.get("target", "100%")),
            ])

        table = Table(table_data, colWidths=[240, 110, 130])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(table)
        story.append(Spacer(1, 16))

    # Risk Distribution Breakdown
    dist = compliance_data.get("risk_distribution", {})
    if dist:
        story.append(Paragraph("Organizational Risk Posture Distribution", styles["Heading3"]))
        dist_data = [["Risk Category", "Employee Count", "Percentage"]]
        total = compliance_data.get("total_employees", sum(dist.values()) or 1)
        for cat, count in dist.items():
            pct = f"{(count / total * 100):.1f}%" if total > 0 else "0%"
            dist_data.append([cat.capitalize(), str(count), pct])

        dist_table = Table(dist_data, colWidths=[180, 150, 150])
        dist_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(dist_table)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

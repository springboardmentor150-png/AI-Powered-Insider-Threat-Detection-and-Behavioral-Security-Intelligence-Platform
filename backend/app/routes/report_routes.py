# backend/app/routes/report_routes.py
"""
Day 33 & Day 34: Reports & Export System Route Handlers.
Implements in-memory PDF risk & compliance reports, Excel data exports (.xlsx), and report catalog.
"""
import io
from typing import Optional
from datetime import datetime

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db, mongo_db
from app.models import Employee, Incident, Alert, AuditLog
from app.auth import get_current_user, require_role
from app.risk_scoring import calculate_risk_score
from app.reports import generate_employee_risk_report, generate_compliance_summary_report
from app.routes.dashboard_routes import calculate_mttr, calculate_mtti

router = APIRouter(tags=["Reports & Export System"])


# =========================================================================
# Day 33: PDF Reports
# =========================================================================

@router.get("/reports/compliance/pdf")
def download_compliance_pdf_report(
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "security_manager"))
):
    """
    Day 33 Exercise 3: Compliance Summary PDF Report:
    Generates an executive SLA compliance report summarizing incident resolution rate, MTTR, and MTTI.
    """
    total_incidents = db.query(Incident).count()
    resolved_incidents = db.query(Incident).filter(
        func.lower(Incident.status).in_(["resolved", "closed"])
    ).count()
    resolution_rate = round((resolved_incidents / total_incidents) * 100, 1) if total_incidents else 0.0

    open_critical = db.query(Incident).filter(
        func.lower(Incident.status) == "open",
        func.lower(Incident.severity) == "critical"
    ).count()

    compliance_data = {
        "total_incidents": total_incidents,
        "resolved_incidents": resolved_incidents,
        "resolution_rate_percent": resolution_rate,
        "open_critical_incidents": open_critical,
        "mean_time_to_respond_hours": calculate_mttr(db),
        "mean_time_to_investigate_hours": calculate_mtti(db)
    }

    incidents = db.query(Incident).order_by(Incident.created_at.desc()).all()
    pdf_bytes = generate_compliance_summary_report(compliance_data, incidents)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=compliance_summary_report.pdf"}
    )


@router.get("/reports/{employee_id}/pdf")
def download_employee_risk_report(
    employee_id: str,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "security_analyst", "security_manager"))
):
    """
    Day 33 In-Memory PDF Risk Report:
    Generates and downloads a dedicated executive PDF dossier for an individual employee.
    Safely handles 0 anomalies cleanly without crashing.
    """
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee '{employee_id}' not found")

    risk = calculate_risk_score(employee_id)
    anomalies = list(mongo_db["rule_anomalies"].find({"employee_id": employee_id}))

    pdf_bytes = generate_employee_risk_report(employee_id, risk, anomalies)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={employee_id}_risk_report.pdf"}
    )



# =========================================================================
# Day 34: Excel Data Exports (.xlsx)
# =========================================================================

@router.get("/reports/export/risk-scores")
def export_risk_scores_excel(
    department: Optional[str] = Query(None, description="Optional department filter"),
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "security_manager"))
):
    """
    Day 34 Bulk Risk Scores Excel Export:
    Exports all employee behavioral risk scores into an Excel workbook.
    Sorted by 'Risk Score' descending so riskiest personnel appear first.
    """
    query = db.query(Employee)
    if department:
        query = query.filter(func.lower(Employee.department) == department.lower())

    employees = query.all()
    rows = []
    for emp in employees:
        risk = calculate_risk_score(emp.employee_id)
        score_val = risk.get("final_score") if "final_score" in risk else risk.get("composite_risk_score", 0.0)
        level_val = risk.get("risk_level") if "risk_level" in risk else risk.get("risk_category", "LOW").upper()
        
        rows.append({
            "Employee ID": emp.employee_id,
            "Name": emp.name,
            "Department": emp.department,
            "Designation": emp.designation,
            "Risk Score": score_val,
            "Risk Level": level_val
        })

    df = pd.DataFrame(rows)
    if not df.empty and "Risk Score" in df.columns:
        df = df.sort_values("Risk Score", ascending=False)

    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl", sheet_name="Risk Scores")
    buffer.seek(0)

    filename = f"risk_scores_{department.lower()}_export.xlsx" if department else "risk_scores_export.xlsx"

    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/reports/export/incidents")
def export_incidents_excel(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (open, investigating, resolved)"),
    severity: Optional[str] = Query(None, description="Filter by severity (low, medium, high, critical)"),
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "security_manager"))
):
    """
    Day 34 Incident Report Excel Export:
    Exports tabular incident history with safe inline formatting for un-resolved records.
    """
    query = db.query(Incident)
    if status_filter:
        query = query.filter(func.lower(Incident.status) == status_filter.lower())
    if severity:
        query = query.filter(func.lower(Incident.severity) == severity.lower())

    incidents = query.order_by(Incident.created_at.desc()).all()

    rows = [{
        "Incident ID": i.incident_code or f"INC-{i.id}",
        "Employee ID": i.employee_id,
        "Severity": (i.severity or "medium").upper(),
        "Status": (i.status or "open").upper(),
        "Assigned To": i.assigned_to or "Unassigned",
        "MITRE Technique": i.mitre_attack_technique or "T1078",
        "Created": i.created_at.strftime("%Y-%m-%d %H:%M") if i.created_at else "N/A",
        # Safe inline conditional preventing AttributeError on None
        "Resolved": i.resolved_at.strftime("%Y-%m-%d %H:%M") if i.resolved_at else "Not resolved"
    } for i in incidents]

    df = pd.DataFrame(rows)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl", sheet_name="Incidents")
    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=incidents_export.xlsx"}
    )


@router.get("/reports/export/audit-logs")
def export_audit_logs_excel(
    db: Session = Depends(get_db),
    user=Depends(require_role("admin"))
):
    """
    Day 34 Administrator Audit Log Excel Export:
    Exports immutable audit logs for compliance officers and external security auditors.
    """
    entries = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(1000).all()
    rows = [{
        "Log ID": e.id,
        "User ID": e.user_id,
        "User Email": e.user_email or "system",
        "Action": e.action,
        "Target Resource": e.target_resource or "N/A",
        "Details": e.details or "N/A",
        "Timestamp": e.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC") if e.timestamp else "N/A"
    } for e in entries]

    df = pd.DataFrame(rows)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl", sheet_name="Audit Logs")
    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=audit_logs_export.xlsx"}
    )


# =========================================================================
# Day 34: Report Catalog Endpoint
# =========================================================================

@router.get("/reports/catalog")
def list_available_reports(
    user=Depends(require_role("admin", "security_analyst", "security_manager"))
):
    """
    Day 34 Report Catalog:
    Single source of truth providing the UI and external integrators with all available reports.
    """
    return {
        "reports": [
            {
                "name": "Employee Risk Report",
                "format": "PDF",
                "endpoint": "/api/reports/{employee_id}/pdf",
                "description": "Comprehensive individual risk assessment with sub-score radar breakdown and anomaly timeline.",
                "allowed_roles": ["admin", "security_analyst", "security_manager"]
            },
            {
                "name": "Compliance Summary Report",
                "format": "PDF",
                "endpoint": "/api/reports/compliance/pdf",
                "description": "Executive compliance audit summary with SLA metrics, MTTR, MTTI, and resolution rates.",
                "allowed_roles": ["admin", "security_manager"]
            },
            {
                "name": "All Risk Scores",
                "format": "Excel",
                "endpoint": "/api/reports/export/risk-scores",
                "description": "Bulk tabular spreadsheet of all employee risk scores, sorted highest-risk first, with optional department filter.",
                "allowed_roles": ["admin", "security_manager"]
            },
            {
                "name": "Incident Report",
                "format": "Excel",
                "endpoint": "/api/reports/export/incidents",
                "description": "Full tabular audit list of all security incidents, status, severity, and resolution timestamps.",
                "allowed_roles": ["admin", "security_manager"]
            },
            {
                "name": "Platform Audit Logs",
                "format": "Excel",
                "endpoint": "/api/reports/export/audit-logs",
                "description": "Administrative audit trail containing sensitive actions, user attributions, and timestamps.",
                "allowed_roles": ["admin"]
            }
        ]
    }

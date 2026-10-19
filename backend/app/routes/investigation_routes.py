import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee, Alert, Incident, RiskScoreHistory, InvestigationNote, AuditLog, User
from app.schemas import (
    FullInvestigationDossier,
    InvestigationNoteCreate,
    InvestigationNoteResponse,
    InvestigationTimelineItem,
    EmployeeActivityProfile,
    AlertResponse,
    IncidentResponse,
    RiskScoreHistoryResponse,
    EmployeeResponse,
)
from app.security import get_current_user, require_role
from sqlalchemy import or_
from app.mongodb import mongo_service

logger = logging.getLogger("itbis.investigation")
router = APIRouter(prefix="/investigations", tags=["Investigation Center"])


@router.get("/{employee_id}", response_model=FullInvestigationDossier)
def get_investigation_dossier(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves full unified security investigation dossier for an employee:
    - PostgreSQL: Employee profile, alerts, incidents, risk history, analyst notes.
    - MongoDB: Telemetry activity profile & time-series event details.
    - Chronological Threat Story Timeline.
    """
    emp = db.query(Employee).filter(
        (Employee.employee_id == employee_id) | (Employee.id == employee_id)
    ).first()
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found.")

    # 1. Fetch Relational Data from PostgreSQL
    alerts = db.query(Alert).filter(Alert.employee_id == emp.id).order_by(Alert.created_at.desc()).all()
    incidents = db.query(Incident).filter(Incident.employee_id == emp.id).order_by(Incident.created_at.desc()).all()
    risk_history = db.query(RiskScoreHistory).filter(RiskScoreHistory.employee_id == emp.id).order_by(RiskScoreHistory.calculated_at.desc()).all()
    notes = db.query(InvestigationNote).filter(InvestigationNote.employee_id == emp.id).order_by(InvestigationNote.created_at.desc()).all()

    # 2. Fetch Telemetry Data from MongoDB
    activity_profile_raw = mongo_service.get_employee_activity_profile(emp.employee_id)
    activity_profile = EmployeeActivityProfile(**activity_profile_raw)
    mongo_logs = mongo_service.query_activity_logs(employee_id=emp.employee_id, limit=100)["items"]

    # 3. Construct Unified Chronological Threat Story Timeline
    timeline_items: List[InvestigationTimelineItem] = []

    # Add Activities
    for log in mongo_logs:
        ts = log.get("timestamp", datetime.utcnow().isoformat())
        et = log.get("event_type", "activity")
        is_susp = log.get("is_suspicious") or log.get("risk_weight", 0) >= 30
        timeline_items.append(InvestigationTimelineItem(
            id=f"act-{log.get('id', '0')}",
            timestamp=ts,
            event_type=et,
            source="TELEMETRY",
            title=f"{et.replace('_', ' ').title()}: {log.get('action', '')}",
            description=log.get("resource", "Internal Asset"),
            severity="HIGH" if is_susp else "LOW",
            employee_id=emp.employee_id,
            risk_impact=log.get("risk_weight", 0),
            related_id=log.get("id"),
            metadata=log.get("details", {}),
        ))

    # Add Risk Score Updates
    for rh in risk_history:
        timeline_items.append(InvestigationTimelineItem(
            id=f"risk-{rh.id}",
            timestamp=rh.calculated_at.isoformat(),
            event_type="risk_score_update",
            source="RISK_CHANGE",
            title=f"Risk Score Escalated to {rh.score}/100 ({rh.risk_level})",
            description=f"Contributing factors: {rh.contributing_factors or 'Statistical model evaluation'}",
            severity="CRITICAL" if rh.score >= 80 else ("HIGH" if rh.score >= 60 else "MEDIUM"),
            employee_id=emp.employee_id,
            risk_impact=rh.score,
            related_id=str(rh.id),
        ))

    # Add Alerts
    for al in alerts:
        timeline_items.append(InvestigationTimelineItem(
            id=f"alert-{al.id}",
            timestamp=al.created_at.isoformat(),
            event_type="security_alert",
            source="ALERT",
            title=f"SOC Alert Triggered: {al.title}",
            description=al.message,
            severity=al.severity,
            employee_id=emp.employee_id,
            risk_impact=al.risk_score,
            related_id=str(al.id),
        ))

    # Add Incidents
    for inc in incidents:
        timeline_items.append(InvestigationTimelineItem(
            id=f"inc-{inc.id}",
            timestamp=inc.created_at.isoformat(),
            event_type="incident_created",
            source="INCIDENT",
            title=f"Security Incident INC-{inc.id}: {inc.title}",
            description=inc.description or "Investigation initiated by SOC analyst.",
            severity=inc.severity,
            employee_id=emp.employee_id,
            related_id=str(inc.id),
        ))

    # Add Analyst Notes
    for n in notes:
        timeline_items.append(InvestigationTimelineItem(
            id=f"note-{n.id}",
            timestamp=n.created_at.isoformat(),
            event_type="analyst_note",
            source="ANALYST_NOTE",
            title=f"Case Note by {n.author_email}",
            description=n.note_text,
            severity="LOW",
            employee_id=emp.employee_id,
            related_id=str(n.id),
        ))

    # Sort timeline newest-first or chronologically
    timeline_items.sort(key=lambda x: x.timestamp, reverse=True)

    user_email = current_user.get("email", "analyst@itbis.cyber") if isinstance(current_user, dict) else current_user.email

    # Log SOC Analyst Audit Trail
    audit = AuditLog(
        user_email=user_email,
        action="VIEW_INVESTIGATION",
        target_type="EMPLOYEE",
        target_id=emp.employee_id,
        details=f"Analyst {user_email} inspected full investigation timeline for {emp.name} ({emp.employee_id})."
    )
    db.add(audit)
    db.commit()

    return FullInvestigationDossier(
        employee=EmployeeResponse.model_validate(emp),
        activity_profile=activity_profile,
        active_alerts=[AlertResponse.model_validate(a) for a in alerts],
        active_incidents=[IncidentResponse.model_validate(i) for i in incidents],
        risk_history=[RiskScoreHistoryResponse.model_validate(r) for r in risk_history],
        notes=[InvestigationNoteResponse.model_validate(n) for n in notes],
        timeline=timeline_items,
    )


@router.post("/{employee_id}/notes", response_model=InvestigationNoteResponse, status_code=status.HTTP_201_CREATED)
def add_investigation_note(
    employee_id: str,
    payload: InvestigationNoteCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Adds a persistent SOC analyst investigation case note in PostgreSQL."""
    emp = db.query(Employee).filter(
        (Employee.employee_id == employee_id) | (Employee.id == employee_id)
    ).first()
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found.")

    user_email = current_user.get("email", "analyst@itbis.cyber") if isinstance(current_user, dict) else current_user.email

    note = InvestigationNote(
        employee_id=emp.id,
        incident_id=payload.incident_id,
        author_email=user_email,
        note_text=payload.note_text,
    )
    db.add(note)

    # Audit Trail
    audit = AuditLog(
        user_email=user_email,
        action="ADD_INVESTIGATION_NOTE",
        target_type="EMPLOYEE",
        target_id=emp.employee_id,
        details=f"Added case note: {payload.note_text[:60]}..."
    )
    db.add(audit)
    db.commit()
    db.refresh(note)
    return InvestigationNoteResponse.model_validate(note)



@router.get("/{employee_id}/export")
def export_investigation_summary(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Generates an exportable forensic investigation brief for executive/compliance review."""
    emp = db.query(Employee).filter(
        (Employee.employee_id == employee_id) | (Employee.id == employee_id)
    ).first()
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found.")

    alerts = db.query(Alert).filter(Alert.employee_id == emp.id).all()
    incidents = db.query(Incident).filter(Incident.employee_id == emp.id).all()
    notes = db.query(InvestigationNote).filter(InvestigationNote.employee_id == emp.id).all()
    activity_profile = mongo_service.get_employee_activity_profile(emp.employee_id)

    user_email = current_user.get("email", "analyst@itbis.cyber") if isinstance(current_user, dict) else current_user.email
    audit = AuditLog(
        user_email=user_email,
        action="EXPORT_INVESTIGATION_SUMMARY",
        target_type="EMPLOYEE",
        target_id=emp.employee_id,
        details=f"Exported forensic investigation summary report for {emp.name} ({emp.employee_id})."
    )
    db.add(audit)
    db.commit()

    return {
        "report_id": f"ITBIS-EXP-{emp.employee_id}-{int(datetime.utcnow().timestamp())}",
        "generated_at": datetime.utcnow().isoformat(),
        "generated_by": user_email,
        "subject": {
            "employee_id": emp.employee_id,
            "name": emp.name,
            "department": emp.department,
            "designation": emp.designation,
            "email": emp.email,
            "risk_score": emp.risk_score,
            "risk_level": emp.risk_level,
            "status": emp.status,
            "device_info": emp.device_info,
            "access_privileges": emp.access_privileges,
        },
        "telemetry_summary": activity_profile,
        "security_events": {
            "total_alerts": len(alerts),
            "alerts": [
                {
                    "id": a.id,
                    "title": a.title,
                    "category": a.category,
                    "severity": a.severity,
                    "risk_score": a.risk_score,
                    "status": a.status,
                    "created_at": a.created_at.isoformat(),
                }
                for a in alerts
            ],
            "total_incidents": len(incidents),
            "incidents": [
                {
                    "id": i.id,
                    "title": i.title,
                    "severity": i.severity,
                    "status": i.status,
                    "created_at": i.created_at.isoformat(),
                }
                for i in incidents
            ],
        },
        "analyst_notes": [
            {
                "author": n.author_email,
                "note": n.note_text,
                "created_at": n.created_at.isoformat(),
            }
            for n in notes
        ],
        "compliance_signoff": "SOC Operations Forensic Verification — Classification: RESTRICTED",
    }


@router.get("/{employee_id}/timeline")
def get_activity_timeline(
    employee_id: str,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin", "security_analyst", "soc_engineer", "security_manager")),
):
    """
    Merges and normalizes raw activity logs, rule anomalies, and ML anomalies
    into a unified chronological timeline (newest-first) for security investigations (Day 26).
    """
    emp = db.query(Employee).filter(
        or_(
            Employee.employee_id == employee_id,
            Employee.id == int(employee_id) if str(employee_id).isdigit() else False,
        )
    ).first()

    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee '{employee_id}' not found")

    emp_code = emp.employee_id

    # 1. Raw activity logs
    logs_result = mongo_service.query_activity_logs(employee_id=emp_code, limit=100)
    logs = logs_result.get("items", [])

    # 2. Anomaly records
    all_anomalies = mongo_service.get_anomalies(employee_id=emp_code, limit=300)

    timeline = []

    for log in logs:
        ts = log.get("timestamp") or ""
        timeline.append({
            "time": ts,
            "source": "activity",
            "detail": log.get("event_type", "activity"),
            "severity": "LOW",
        })

    for a in all_anomalies:
        anom_type = str(a.get("anomaly_type") or "").strip()
        ts = a.get("detected_at") or a.get("detection_timestamp") or a.get("timestamp") or a.get("date") or ""

        if anom_type == "ML_ISOLATION_FOREST" or a.get("source") == "ml_anomaly" or a.get("indicator") == "isolation_forest":
            score_val = a.get("anomaly_score")
            score_str = f"{score_val:.2f}" if score_val is not None else "N/A"
            timeline.append({
                "time": str(ts),
                "source": "ml_anomaly",
                "detail": f"ML flagged day (score: {score_str})",
                "severity": a.get("severity", "MEDIUM"),
            })
        else:
            timeline.append({
                "time": str(ts),
                "source": "rule_anomaly",
                "detail": anom_type or "Rule Anomaly",
                "severity": a.get("severity", "MEDIUM"),
            })

    # Sort descending (newest first)
    timeline.sort(key=lambda x: str(x.get("time") or ""), reverse=True)

    return {
        "employee_id": emp_code,
        "event_count": len(timeline),
        "timeline": timeline[:limit],
    }

"""
ITBIS Threat Investigation API Routes.

Day 25:
- Create incidents
- Add investigation notes
- Retrieve investigation notes

Day 26:
- Unified investigation timeline
- Resolve incidents
- List active incidents
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db, mongo_db
from app.models import Employee, Incident, InvestigationNote
from app.schemas import (
    IncidentCreate,
    InvestigationNoteCreate,
    IncidentResolveRequest,
)
from app.security import require_role


router = APIRouter(tags=["investigations"])


ALLOWED_ROLES = (
    "admin",
    "security_analyst",
    "soc_engineer",
)


# =========================================================
# DAY 25 — CREATE INCIDENT
# =========================================================

@router.post("/incidents", status_code=201)
def create_incident(
    incident_data: IncidentCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role(*ALLOWED_ROLES)),
):
    employee = (
        db.query(Employee)
        .filter(Employee.id == incident_data.employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    incident = Incident(
        employee_id=employee.id,
        status=incident_data.status,
        severity=incident_data.severity,
        summary=incident_data.summary,
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    return {
        "id": incident.id,
        "employee_id": employee.id,
        "status": incident.status,
        "severity": incident.severity,
        "summary": incident.summary,
        "created_at": incident.created_at,
        "resolved_at": incident.resolved_at,
    }


# =========================================================
# DAY 25 — ADD INVESTIGATION NOTE
# =========================================================

@router.post("/incidents/{incident_id}/notes")
def add_investigation_note(
    incident_id: int,
    note_data: InvestigationNoteCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role(*ALLOWED_ROLES)),
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    note = InvestigationNote(
        incident_id=incident.id,
        author_user_id=int(user["sub"]),
        note=note_data.note,
        evidence_reference=note_data.evidence_reference,
    )

    db.add(note)

    # First investigation note changes
    # the incident from open to investigating.
    if incident.status == "open":
        incident.status = "investigating"

    db.commit()
    db.refresh(note)

    return {
        "message": "Investigation note added successfully",
        "note_id": note.id,
        "incident_id": incident.id,
        "status": incident.status,
        "author_user_id": note.author_user_id,
        "note": note.note,
        "evidence_reference": note.evidence_reference,
        "created_at": note.created_at,
    }


# =========================================================
# DAY 25 — GET INVESTIGATION NOTES
# =========================================================

@router.get("/incidents/{incident_id}/notes")
def get_investigation_notes(
    incident_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role(*ALLOWED_ROLES)),
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    notes = (
        db.query(InvestigationNote)
        .filter(
            InvestigationNote.incident_id == incident_id
        )
        .order_by(InvestigationNote.created_at.asc())
        .all()
    )

    return {
        "incident_id": incident_id,
        "notes": [
            {
                "id": note.id,
                "author_user_id": note.author_user_id,
                "note": note.note,
                "evidence_reference": note.evidence_reference,
                "created_at": note.created_at,
            }
            for note in notes
        ],
    }


# =========================================================
# DAY 26 — UNIFIED INVESTIGATION TIMELINE
# =========================================================

@router.get("/investigations/{employee_id}/timeline")
def get_investigation_timeline(
    employee_id: str,
    db: Session = Depends(get_db),
    user=Depends(require_role(*ALLOWED_ROLES)),
):
    employee = (
        db.query(Employee)
        .filter(Employee.employee_id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    timeline = []

    # -----------------------------------------------------
    # Activity Logs
    # -----------------------------------------------------

    activity_logs = mongo_db["activity_logs"].find({
        "employee_id": employee_id
    })

    for log in activity_logs:
        timestamp = log.get("timestamp")

        timeline.append({
            "time": timestamp,
            "source": "activity_log",
            "detail": {
                "event_type": log.get("event_type"),
                "details": log.get("details", {}),
            },
        })

    # -----------------------------------------------------
    # Rule Anomalies
    # -----------------------------------------------------

    rule_anomalies = mongo_db["rule_anomalies"].find({
        "employee_id": employee_id
    })

    for anomaly in rule_anomalies:
        timeline.append({
            "time": anomaly.get("detected_at"),
            "source": "rule_anomaly",
            "detail": {
                "indicator": anomaly.get("indicator"),
                "anomaly_type": anomaly.get("anomaly_type"),
            },
            "severity": anomaly.get("severity"),
        })

    # -----------------------------------------------------
    # ML Anomalies
    # IMPORTANT:
    # Your existing ML schema uses prediction == -1.
    # -----------------------------------------------------

    ml_anomalies = mongo_db["ml_anomalies"].find({
        "employee_id": employee_id,
        "prediction": -1,
    })

    for anomaly in ml_anomalies:
        timestamp = (
            anomaly.get("timestamp")
            or anomaly.get("date")
            or anomaly.get("detected_at")
        )

        timeline.append({
            "time": timestamp,
            "source": "ml_anomaly",
            "detail": {
                "prediction": anomaly.get("prediction"),
                "details": anomaly.get("details", {}),
            },
            "severity": anomaly.get("severity"),
        })

    # -----------------------------------------------------
    # Sort newest first
    # -----------------------------------------------------

    timeline.sort(
        key=lambda item: str(item.get("time") or ""),
        reverse=True,
    )

    return {
        "employee_id": employee_id,
        "total_events": len(timeline),
        "timeline": timeline,
    }


# =========================================================
# DAY 26 — RESOLVE INCIDENT
# =========================================================

@router.patch("/incidents/{incident_id}/resolve")
def resolve_incident(
    incident_id: int,
    resolution_data: IncidentResolveRequest,
    db: Session = Depends(get_db),
    user=Depends(require_role(*ALLOWED_ROLES)),
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    if incident.status == "resolved":
        raise HTTPException(
            status_code=400,
            detail="Incident is already resolved",
        )

    incident.status = "resolved"
    incident.summary = resolution_data.resolution_summary
    incident.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(incident)

    return {
        "message": "Incident resolved successfully",
        "incident_id": incident.id,
        "employee_id": incident.employee_id,
        "status": incident.status,
        "summary": incident.summary,
        "resolved_at": incident.resolved_at,
    }


# =========================================================
# DAY 26 — LIST ACTIVE INCIDENTS
# =========================================================

@router.get("/incidents")
def get_incidents(
    db: Session = Depends(get_db),
    user=Depends(require_role(*ALLOWED_ROLES)),
):
    incidents = (
        db.query(Incident)
        .filter(Incident.status != "resolved")
        .order_by(Incident.created_at.desc())
        .all()
    )

    return {
        "total": len(incidents),
        "incidents": [
            {
                "id": incident.id,
                "employee_id": incident.employee_id,
                "status": incident.status,
                "severity": incident.severity,
                "summary": incident.summary,
                "created_at": incident.created_at,
                "resolved_at": incident.resolved_at,
            }
            for incident in incidents
        ],
    }
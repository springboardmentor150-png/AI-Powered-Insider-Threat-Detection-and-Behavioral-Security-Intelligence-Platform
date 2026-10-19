from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import Incident, Employee, InvestigationNote, User
from app.schemas import (
    IncidentCreate,
    IncidentResponse,
    IncidentStatusUpdate,
    PaginatedIncidentsResponse,
)
from app.security import get_current_user, require_role
from app.risk_scoring import calculate_risk_score
from app.audit import log_action

router = APIRouter(prefix="/incidents", tags=["Incidents (Days 25-26)"])


def to_incident_response(incident: Incident) -> IncidentResponse:
    emp_name = incident.employee.name if incident.employee else None
    emp_identifier = incident.employee.employee_id if incident.employee else None
    return IncidentResponse(
        id=incident.id,
        employee_id=incident.employee_id,
        employee_name=emp_name,
        employee_identifier=emp_identifier,
        alert_id=incident.alert_id,
        title=incident.title or f"Incident INC-{incident.id}",
        description=incident.description or incident.summary,
        status=incident.status,
        severity=incident.severity,
        assigned_to=incident.assigned_to,
        resolved_at=incident.resolved_at,
        created_at=incident.created_at,
    )


@router.get("", response_model=PaginatedIncidentsResponse)
def get_incidents(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    employee_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "security_analyst", "soc_engineer", "security_manager")),
):
    query = db.query(Incident)

    if status and status.upper() != "ALL":
        query = query.filter(or_(Incident.status == status, Incident.status == status.lower(), Incident.status == status.upper()))

    if severity and severity.upper() != "ALL":
        query = query.filter(or_(Incident.severity == severity, Incident.severity == severity.lower(), Incident.severity == severity.upper()))

    if employee_id:
        emp = db.query(Employee).filter(
            or_(
                Employee.employee_id == employee_id,
                Employee.id == int(employee_id) if str(employee_id).isdigit() else False,
            )
        ).first()
        if emp:
            query = query.filter(Incident.employee_id == emp.id)
        else:
            return PaginatedIncidentsResponse(items=[], page=page, limit=limit, total=0)

    total = query.count()
    offset = (page - 1) * limit
    raw_items = query.order_by(Incident.created_at.desc(), Incident.id.desc()).offset(offset).limit(limit).all()

    items = [to_incident_response(inc) for inc in raw_items]

    return PaginatedIncidentsResponse(
        items=items,
        page=page,
        limit=limit,
        total=total,
    )


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident_by_id(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "security_analyst", "soc_engineer", "security_manager")),
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID {incident_id} not found"
        )
    return to_incident_response(incident)


@router.post("")
def create_incident(
    employee_id: Optional[str] = Query(None),
    data: Optional[Dict[str, Any]] = Body(None),
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin", "security_analyst")),
):
    """
    Creates an incident from a risk score or manual escalation (Day 25).
    Guarantees: Rejects Low-risk employees with HTTP 400.
    """
    target_emp_id = employee_id
    if target_emp_id is None and isinstance(data, dict):
        target_emp_id = data.get("employee_id")

    if not target_emp_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required field 'employee_id'",
        )

    str_emp_id = str(target_emp_id)
    employee = db.query(Employee).filter(
        or_(
            Employee.employee_id == str_emp_id,
            Employee.id == int(str_emp_id) if str_emp_id.isdigit() else False,
        )
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    # Evaluate risk score to enforce business rule: only Medium+ can generate incident
    risk = calculate_risk_score(employee.employee_id, db)
    if risk["risk_level"] == "Low":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee risk level is Low - incident creation is reserved for Medium risk and above",
        )

    summary_text = f"Auto-generated from risk score {risk['final_score']} ({risk['risk_level']})"
    if isinstance(data, dict) and data.get("summary"):
        summary_text = data.get("summary")

    incident = Incident(
        employee_id=employee.id,
        title=f"Security Incident for {employee.name} ({risk['risk_level']})",
        description=summary_text,
        summary=summary_text,
        status="open",
        severity=risk["risk_level"].lower(),
        assigned_to=int(user["sub"]) if user and str(user.get("sub", "")).isdigit() else None,
        created_at=datetime.now(timezone.utc),
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    caller_id = int(user["sub"]) if user and str(user.get("sub", "")).isdigit() else None
    log_action(
        db=db,
        user_id=caller_id,
        action="CREATE_INCIDENT",
        details=f"Created incident INC-{incident.id} for employee {employee.employee_id} ({incident.severity})",
        target_type="INCIDENT",
        target_id=str(incident.id),
    )

    return {
        "incident_id": incident.id,
        "severity": incident.severity,
        "summary": incident.summary,
        "status": incident.status,
    }


@router.post("/create-from-risk/{employee_id}")
def create_incident_from_risk(
    employee_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin", "security_analyst", "security_manager")),
):
    """
    Handout route specification: creates an incident directly from an employee's risk score.
    """
    return create_incident(employee_id=employee_id, data=None, db=db, user=user)


@router.post("/{incident_id}/notes")
def add_investigation_note(
    incident_id: int,
    note_text: Optional[str] = Query(None),
    data: Optional[Dict[str, Any]] = Body(None),
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin", "security_analyst", "soc_engineer")),
):
    """
    Appends an investigation note to an incident (Day 25/26).
    Automatically transitions incident status from 'open' to 'investigating'.
    Supports linking evidence references.
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    text_to_save = note_text
    evidence_ref = None
    if text_to_save is None and isinstance(data, dict):
        text_to_save = data.get("note_text") or data.get("note")
        evidence_ref = data.get("evidence_reference")

    if not text_to_save:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Note text cannot be empty")

    author_id = 1
    if user and str(user.get("sub", "")).isdigit():
        author_id = int(user["sub"])

    author_email = None
    if author_id:
        db_user = db.query(User).filter(User.id == author_id).first()
        if db_user and db_user.email:
            author_email = db_user.email
    if not author_email:
        author_email = user.get("email") if isinstance(user, dict) and user.get("email") else f"analyst_{author_id}@itbis.cyber"

    note = InvestigationNote(
        employee_id=incident.employee_id or 1,
        incident_id=incident_id,
        author_user_id=author_id,
        author_email=author_email,
        note=text_to_save,
        note_text=text_to_save,
        evidence_reference=evidence_ref,
        created_at=datetime.now(timezone.utc),
    )
    db.add(note)

    if incident.status.lower() == "open":
        incident.status = "investigating"
        if not incident.investigation_started_at:
            incident.investigation_started_at = datetime.now(timezone.utc)

    db.commit()
    return {"message": "Note added", "incident_status": incident.status}


@router.get("/{incident_id}/notes")
def get_investigation_notes(
    incident_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin", "security_analyst", "soc_engineer", "security_manager")),
):
    """
    Retrieves investigation notes in chronological (ascending) order (Day 26).
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    notes = db.query(InvestigationNote).filter(
        InvestigationNote.incident_id == incident_id
    ).order_by(InvestigationNote.created_at.asc()).all()

    return {
        "incident_id": incident_id,
        "notes": [
            {
                "note": n.note or n.note_text,
                "evidence_reference": n.evidence_reference,
                "created_at": n.created_at,
            }
            for n in notes
        ],
    }


@router.patch("/{incident_id}/resolve")
def resolve_incident(
    incident_id: int,
    resolution_summary: Optional[str] = Query(None),
    data: Optional[Dict[str, Any]] = Body(None),
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin", "security_analyst", "security_manager")),
):
    """
    Resolves an ongoing security incident with resolution notes and records resolved_at (Day 26).
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    res_text = resolution_summary
    if res_text is None and isinstance(data, dict):
        res_text = data.get("resolution_summary") or data.get("summary") or data.get("resolution_notes")

    incident.status = "resolved"
    incident.summary = res_text or "Incident resolved by security analyst."
    incident.resolved_at = datetime.now(timezone.utc)
    db.commit()

    caller_id = int(user["sub"]) if user and str(user.get("sub", "")).isdigit() else None
    log_action(
        db=db,
        user_id=caller_id,
        action="RESOLVE_INCIDENT",
        details=f"Resolved incident INC-{incident.id}: {incident.summary}",
        target_type="INCIDENT",
        target_id=str(incident.id),
    )

    return {"message": "Incident resolved", "incident_id": incident.id, "status": incident.status}


@router.get("/{incident_id}/timeline")
def get_incident_timeline(
    incident_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin", "security_analyst", "soc_engineer", "security_manager")),
):
    """
    Handout route specification: combines activity logs and anomalies in chronological order for an incident.
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID {incident_id} not found",
        )
    from app.routes.investigation_routes import get_activity_timeline
    emp_code = incident.employee.employee_id if incident.employee else str(incident.employee_id)
    return get_activity_timeline(employee_id=emp_code, db=db, user=user)


@router.patch("/{incident_id}/status", response_model=IncidentResponse)
def update_incident_status(
    incident_id: int,
    data: IncidentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "security_analyst", "soc_engineer", "security_manager")),
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID {incident_id} not found"
        )

    new_status = data.status.upper()
    incident.status = new_status
    if new_status in ["INVESTIGATING", "CONTAINED"] and not incident.investigation_started_at:
        incident.investigation_started_at = datetime.now(timezone.utc)
    if data.resolution_notes:
        incident.description = f"{incident.description or ''}\n\n[Update {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}]: {data.resolution_notes}"

    if new_status in ["RESOLVED", "CLOSED"]:
        incident.resolved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(incident)
    return to_incident_response(incident)

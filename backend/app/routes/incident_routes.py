# backend/app/routes/incident_routes.py
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db, doc_db
from app.models import Incident, Employee, Alert, User, AuditLog
from app.schemas import IncidentCreate, IncidentStatusUpdate, IncidentOut
from app.auth import get_current_user, require_role
from app.ml_engine.threat_explainer import threat_explainer

router = APIRouter(prefix="/incidents", tags=["Incidents & Investigation Workbench"])

@router.get("", response_model=List[IncidentOut])
def list_incidents(
    status_filter: Optional[str] = Query(None, alias="status"),
    severity: Optional[str] = None,
    employee_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Incident)
    if status_filter:
        query = query.filter(Incident.status == status_filter.upper())
    if severity:
        query = query.filter(Incident.severity == severity.upper())
    if employee_id:
        query = query.filter(Incident.employee_id == employee_id)

    return query.order_by(Incident.created_at.desc()).all()

@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return incident

@router.post("", response_model=IncidentOut, status_code=status.HTTP_201_CREATED)
def create_incident(
    inc_in: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "security_manager", "security_analyst", "soc_engineer"))
):
    emp = db.query(Employee).filter(Employee.employee_id == inc_in.employee_id).first()
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee {inc_in.employee_id} not found")

    inc_code = f"INC-{uuid.uuid4().hex[:6].upper()}"
    new_incident = Incident(
        incident_code=inc_code,
        employee_id=inc_in.employee_id,
        title=inc_in.title,
        description=inc_in.description,
        severity=inc_in.severity.upper(),
        status="OPEN",
        assigned_to=inc_in.assigned_to or current_user.email,
        mitre_attack_technique=inc_in.mitre_attack_technique or "T1078 - Valid Accounts"
    )
    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)

    return new_incident

@router.patch("/{incident_id}/status", response_model=IncidentOut)
def update_incident_status(
    incident_id: int,
    update_in: IncidentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "security_manager", "security_analyst", "soc_engineer"))
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    incident.status = update_in.status.upper()
    if update_in.assigned_to:
        incident.assigned_to = update_in.assigned_to
    if update_in.ai_summary:
        incident.ai_summary = update_in.ai_summary

    db.commit()
    db.refresh(incident)

    # Audit trail
    audit = AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action="UPDATE_INCIDENT_STATUS",
        target_resource=f"Incident:{incident.incident_code}",
        details=f"Status changed to {incident.status} by {current_user.email}"
    )
    db.add(audit)
    db.commit()

    return incident

@router.post("/{incident_id}/generate-ai-report")
def generate_ai_incident_report(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    AI synthesizes telemetry evidence, employee profile, and MITRE classification
    into a comprehensive forensic incident dossier.
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    employee = incident.employee
    logs = doc_db.activity_logs.find(query={"employee_id": incident.employee_id}, limit=30)
    
    explanation = threat_explainer.generate_explanation(
        employee_name=employee.name if employee else "Unknown",
        employee_id=incident.employee_id,
        department=employee.department if employee else "General",
        risk_score=employee.baseline_risk_score if employee else 75.0,
        threat_level=incident.severity,
        indicators=["Observed pattern flagged by behavioral engine"],
        logs=logs
    )

    dossier = (
        f"### AI FORENSIC INCIDENT BRIEF — {incident.incident_code}\n\n"
        f"**Subject:** {employee.name if employee else 'N/A'} ({incident.employee_id}) — {employee.designation if employee else 'N/A'}\n"
        f"**Severity Classification:** {incident.severity} | **Current Status:** {incident.status}\n\n"
        f"#### 1. Executive Summary\n{explanation['narrative']}\n\n"
        f"#### 2. MITRE ATT&CK Framework Mapping\n"
    )
    for m in explanation["mitre_mapping"]:
        dossier += f"- **{m['technique_id']} - {m['name']}**: {m['description']}\n"

    dossier += f"\n#### 3. Recommended SOC Containment Playbook\n"
    for action in explanation["recommended_actions"]:
        dossier += f"- [ ] {action}\n"

    incident.ai_summary = dossier
    db.commit()

    return {
        "incident_code": incident.incident_code,
        "ai_report": dossier,
        "mitre_mapping": explanation["mitre_mapping"],
        "recommended_actions": explanation["recommended_actions"]
    }

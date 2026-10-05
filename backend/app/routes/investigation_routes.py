# backend/app/routes/investigation_routes.py
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db, mongo_db
from app.models import Incident, Evidence, Employee, User
from app.auth import get_current_user, require_role
from app.risk_scoring import calculate_risk_score

router = APIRouter(tags=["Threat Investigation & Incidents"])

class EvidenceCreate(BaseModel):
    note: str

@router.post("/incidents/create-from-risk/{employee_id}")
def create_incident_from_risk(
    employee_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "security_analyst", "security_manager", "soc_engineer"))
):
    """
    Creates an incident automatically from a high-risk finding.
    Rejects low/medium risk employees, only allowing high/critical per SOC workflow.
    """
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")

    risk = calculate_risk_score(employee_id)
    if risk["risk_category"] not in ("high", "critical"):
        raise HTTPException(status_code=400, detail="Risk level too low to warrant an incident")

    code = f"INC-{uuid.uuid4().hex[:6].upper()}"
    incident = Incident(
        incident_code=code,
        employee_id=employee_id,
        title=f"Elevated Threat Investigation: {emp.name}",
        severity=risk["risk_category"],
        status="open",
        summary=f"Auto-created from risk score {risk['risk_score']}",
        assigned_to=user.email,
        mitre_attack_technique="T1078 - Insider Behavior"
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident

@router.get("/incidents/{incident_id}/timeline")
def get_incident_timeline(
    incident_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "security_analyst", "security_manager", "soc_engineer"))
):
    """
    Merges raw activity logs and detected anomalies into one chronological timeline sorted descending.
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    raw_logs = list(mongo_db["activity_logs"].find({"employee_id": incident.employee_id}, limit=50))
    raw_anomalies = list(mongo_db["rule_anomalies"].find({"employee_id": incident.employee_id}))

    timeline = []
    for l in raw_logs:
        ts = l.get("timestamp")
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts)
            except Exception:
                ts = datetime.utcnow()
        timeline.append({
            "type": "activity",
            "timestamp": ts.isoformat() if isinstance(ts, datetime) else str(ts),
            "detail": l.get("event_type", "activity"),
            "raw_timestamp": ts
        })

    for a in raw_anomalies:
        ts = a.get("detected_at") or a.get("timestamp")
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts)
            except Exception:
                ts = datetime.utcnow()
        timeline.append({
            "type": "anomaly",
            "timestamp": ts.isoformat() if isinstance(ts, datetime) else str(ts),
            "detail": a.get("anomaly_type", "behavioral_anomaly"),
            "raw_timestamp": ts
        })

    timeline.sort(key=lambda x: x.get("raw_timestamp", datetime.min), reverse=True)
    # Remove raw datetime object before returning JSON
    for item in timeline:
        item.pop("raw_timestamp", None)

    return {"incident_id": incident_id, "timeline": timeline}

@router.post("/incidents/{incident_id}/evidence")
def add_incident_evidence(
    incident_id: int,
    evidence_in: EvidenceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "security_analyst", "security_manager"))
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    evidence = Evidence(
        incident_id=incident_id,
        note=evidence_in.note,
        added_by=user.id
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    return {
        "id": evidence.id,
        "incident_id": evidence.incident_id,
        "note": evidence.note,
        "added_by": user.email,
        "added_at": evidence.added_at.isoformat()
    }

@router.get("/incidents/{incident_id}/evidence")
def list_incident_evidence(
    incident_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    evidence_list = db.query(Evidence).filter(Evidence.incident_id == incident_id).order_by(Evidence.added_at.desc()).all()
    return [
        {
            "id": e.id,
            "incident_id": e.incident_id,
            "note": e.note,
            "added_by": e.author.email if e.author else "System",
            "added_at": e.added_at.isoformat()
        }
        for e in evidence_list
    ]
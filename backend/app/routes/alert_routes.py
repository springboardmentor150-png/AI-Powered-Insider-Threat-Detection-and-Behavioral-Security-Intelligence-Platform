# backend/app/routes/alert_routes.py
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Alert, Incident, Employee, User, AuditLog
from app.schemas import AlertOut
from app.auth import get_current_user, require_role

router = APIRouter(prefix="/alerts", tags=["Alerts & Triage Center"])

@router.get("", response_model=List[AlertOut])
def list_alerts(
    severity: Optional[str] = None,
    employee_id: Optional[str] = None,
    is_acknowledged: Optional[bool] = None,
    is_escalated: Optional[bool] = None,
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Alert)
    if severity:
        query = query.filter(Alert.severity == severity.upper())
    if employee_id:
        query = query.filter(Alert.employee_id == employee_id)
    if is_acknowledged is not None:
        query = query.filter(Alert.is_acknowledged == is_acknowledged)
    if is_escalated is not None:
        query = query.filter(Alert.is_escalated == is_escalated)

    return query.order_by(Alert.created_at.desc()).limit(limit).all()

@router.post("/{alert_id}/acknowledge", response_model=AlertOut)
def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    alert.is_acknowledged = True
    db.commit()
    db.refresh(alert)

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action="ACKNOWLEDGE_ALERT",
        target_resource=f"Alert:{alert.alert_code}",
        details=f"Acknowledged alert for {alert.employee_id}"
    )
    db.add(audit)
    db.commit()

    return alert

@router.post("/{alert_id}/escalate")
def escalate_alert_to_incident(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "security_manager", "security_analyst", "soc_engineer"))
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    if alert.is_escalated and alert.incident_id:
        return {"message": "Alert already escalated", "incident_id": alert.incident_id}

    inc_code = f"INC-{uuid.uuid4().hex[:6].upper()}"
    new_incident = Incident(
        incident_code=inc_code,
        employee_id=alert.employee_id,
        title=f"Escalated from {alert.alert_code}: {alert.title}",
        description=alert.message,
        severity=alert.severity,
        status="OPEN",
        assigned_to=current_user.email,
        mitre_attack_technique=alert.anomaly_type or "T1078 - Insider Activity",
        ai_summary=f"Automated escalation from SOC Alert {alert.alert_code}. Risk score evaluation: {alert.risk_score}."
    )
    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)

    alert.is_escalated = True
    alert.is_acknowledged = True
    alert.incident_id = new_incident.id
    db.commit()

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action="ESCALATE_ALERT_TO_INCIDENT",
        target_resource=f"Incident:{new_incident.incident_code}",
        details=f"Escalated Alert {alert.alert_code} to Incident {new_incident.incident_code}"
    )
    db.add(audit)
    db.commit()

    return {
        "message": f"Successfully escalated alert to Incident {new_incident.incident_code}",
        "incident_id": new_incident.id,
        "incident_code": new_incident.incident_code
    }

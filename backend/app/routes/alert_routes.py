# backend/app/routes/alert_routes.py
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Alert, Incident, Employee, User, AuditLog
from app.schemas import AlertOut
from app.auth import get_current_user, require_role
from app.risk_scoring import calculate_risk_score

router = APIRouter(tags=["Alerts & Risk Analytics"])

@router.get("/alerts", response_model=List[AlertOut])
def list_alerts(
    severity: Optional[str] = None,
    employee_id: Optional[str] = None,
    is_acknowledged: Optional[bool] = None,
    is_escalated: Optional[bool] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Alert)
    if severity:
        query = query.filter(Alert.severity == severity.lower())
    if employee_id:
        query = query.filter(Alert.employee_id == employee_id)
    if status_filter:
        query = query.filter(Alert.status == status_filter.lower())
    if is_acknowledged is not None:
        query = query.filter(Alert.is_acknowledged == is_acknowledged)
    if is_escalated is not None:
        query = query.filter(Alert.is_escalated == is_escalated)

    return query.order_by(Alert.created_at.desc()).limit(limit).all()

@router.post("/alerts/{alert_id}/assign")
def assign_alert(
    alert_id: int,
    analyst_user_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "security_manager"))
):
    """
    Assign an alert to a specific analyst (Admin / Security Manager only).
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    analyst = db.query(User).filter(User.id == analyst_user_id).first()
    if not analyst:
        raise HTTPException(status_code=404, detail="Analyst user not found")

    alert.assigned_to = analyst_user_id
    alert.status = "assigned"
    db.commit()
    return {"message": f"Alert {alert_id} assigned to {analyst.email}", "status": alert.status}

@router.patch("/alerts/{alert_id}/resolve")
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "security_analyst", "security_manager", "soc_engineer"))
):
    """
    Resolve an alert (Security Analysts / Admin).
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = "resolved"
    alert.is_acknowledged = True
    db.commit()
    return {"message": f"Alert {alert_id} resolved", "status": alert.status}

@router.post("/alerts/{alert_id}/acknowledge", response_model=AlertOut)
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
    return alert

@router.post("/alerts/{alert_id}/escalate")
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
        title=f"Escalated from {alert.alert_code or f'ALT-{alert.id}'}: {alert.title or alert.message}",
        description=alert.message,
        severity=alert.severity,
        status="open",
        summary=f"Escalated from alert {alert.id}",
        assigned_to=current_user.email,
        mitre_attack_technique=alert.anomaly_type or "T1078 - Insider Activity"
    )
    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)

    alert.is_escalated = True
    alert.is_acknowledged = True
    alert.incident_id = new_incident.id
    db.commit()

    return {
        "message": f"Successfully escalated alert to Incident {new_incident.incident_code}",
        "incident_id": new_incident.id,
        "incident_code": new_incident.incident_code
    }

@router.get("/analytics/risk-distribution")
def get_risk_distribution(
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "security_manager"))
):
    """
    Organizational risk posture view for Security Managers.
    """
    employees = db.query(Employee).all()
    distribution = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for emp in employees:
        risk = calculate_risk_score(emp.employee_id)
        distribution[risk["risk_category"]] += 1

    return {"total_employees": len(employees), "distribution": distribution}
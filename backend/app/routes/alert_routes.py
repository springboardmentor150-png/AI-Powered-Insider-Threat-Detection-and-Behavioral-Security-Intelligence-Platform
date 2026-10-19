from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Alert, Employee, Incident
from app.schemas import (
    AlertCreate,
    AlertResponse,
    PaginatedAlertsResponse,
    IncidentResponse,
)
from app.security import get_current_user, require_role
from app.alerting import (
    generate_alerts_from_anomalies,
    escalate_stale_alerts,
    get_risk_overview_analytics,
)
from app.audit import log_action
from app.notifications import notify_on_critical_alert

router = APIRouter(prefix="/alerts", tags=["Alerts"])


def to_alert_response(alert: Alert) -> AlertResponse:
    emp_name = alert.employee.name if alert.employee else None
    emp_identifier = alert.employee.employee_id if alert.employee else None
    return AlertResponse(
        id=alert.id,
        employee_id=alert.employee_id,
        employee_name=emp_name,
        employee_identifier=emp_identifier,
        title=alert.title,
        message=alert.message,
        category=alert.category or "DATA_EXFILTRATION",
        severity=alert.severity,
        status=alert.status,
        risk_score=alert.risk_score or 0,
        assigned_to=alert.assigned_to,
        acknowledged_at=alert.acknowledged_at,
        resolved_at=alert.resolved_at,
        created_at=alert.created_at,
    )


@router.get("", response_model=PaginatedAlertsResponse)
def get_alerts(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    employee_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Alert)

    if severity and severity != "ALL":
        query = query.filter(Alert.severity == severity)

    if status and status != "ALL":
        query = query.filter(Alert.status == status)

    if category and category != "ALL":
        query = query.filter(Alert.category == category)

    if employee_id:
        query = query.filter(Alert.employee_id == employee_id)

    total = query.count()
    offset = (page - 1) * limit
    raw_items = query.order_by(Alert.created_at.desc(), Alert.id.desc()).offset(offset).limit(limit).all()

    items = [to_alert_response(a) for a in raw_items]

    return PaginatedAlertsResponse(
        items=items,
        page=page,
        limit=limit,
        total=total,
    )


@router.get("/my")
def get_my_alerts(
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin", "security_analyst", "soc_engineer", "security_manager")),
):
    """
    Returns alerts assigned to the currently logged in analyst (using user['sub'] from JWT).
    """
    try:
        user_id = int(user.get("sub", 0))
    except (ValueError, TypeError):
        user_id = 0

    alerts = db.query(Alert).filter(Alert.assigned_to == user_id).order_by(Alert.created_at.desc()).all()
    return [to_alert_response(a) for a in alerts]


@router.post("/generate")
def generate_alerts(
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin", "security_analyst", "soc_engineer", "security_manager")),
):
    """
    Scans unalerted anomalies and generates corresponding security alerts.
    """
    count = generate_alerts_from_anomalies(db)
    return {"message": "Alert generation completed", "alerts_created": count}


@router.post("/escalate")
def escalate_alerts(
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin", "security_manager", "soc_engineer")),
):
    """
    Evaluates open alerts against SLA escalation thresholds and escalates stale alerts.
    """
    escalated_ids = escalate_stale_alerts(db)
    return {"message": "Alert escalation completed", "escalated_alerts": len(escalated_ids), "escalated_ids": escalated_ids}


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert_by_id(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    return to_alert_response(alert)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=AlertResponse)
def create_alert(
    data: AlertCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    employee = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee ID {data.employee_id} not found"
        )

    alert = Alert(
        employee_id=data.employee_id,
        title=data.title,
        message=data.message,
        category=data.category or "DATA_EXFILTRATION",
        severity=data.severity,
        status=getattr(data, "status", None) or "OPEN",
        risk_score=data.risk_score or employee.risk_score,
        assigned_to=getattr(data, "assigned_to", None),
        created_at=datetime.now(timezone.utc),
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    if str(alert.severity).lower() == "critical":
        notify_on_critical_alert(alert, db)

    return to_alert_response(alert)


@router.patch("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )

    alert.status = "ACKNOWLEDGED"
    alert.acknowledged_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)
    return to_alert_response(alert)


@router.patch("/{alert_id}/assign")
def assign_alert(
    alert_id: int,
    analyst_user_id: Optional[int] = Query(None),
    data: Optional[Dict[str, Any]] = Body(None),
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin", "security_manager", "soc_engineer", "security_analyst")),
):
    """
    Assigns an alert to an analyst and updates status to 'in_progress'.
    """
    target_analyst_id = analyst_user_id
    if target_analyst_id is None and isinstance(data, dict):
        target_analyst_id = data.get("analyst_user_id") or data.get("assigned_to")

    if target_analyst_id is None:
        try:
            target_analyst_id = int(user.get("sub", 0))
        except (ValueError, TypeError):
            target_analyst_id = None

    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

    alert.assigned_to = target_analyst_id
    alert.status = "in_progress"
    db.commit()
    db.refresh(alert)

    caller_id = int(user["sub"]) if user and str(user.get("sub", "")).isdigit() else None
    log_action(
        db=db,
        user_id=caller_id,
        action="ASSIGN_ALERT",
        details=f"Alert #{alert.id} ({alert.title}) assigned to analyst ID {target_analyst_id}",
        target_type="ALERT",
        target_id=str(alert.id),
    )

    return {
        "message": "Alert assigned",
        "alert_id": alert.id,
        "assigned_to": alert.assigned_to,
        "status": alert.status,
    }


@router.patch("/{alert_id}/resolve")
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin", "security_analyst", "security_manager", "soc_engineer")),
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

    now = datetime.now(timezone.utc)
    alert.status = "resolved"
    alert.resolved_at = now
    db.commit()
    db.refresh(alert)

    created_dt = alert.created_at
    if created_dt and created_dt.tzinfo is None:
        created_dt = created_dt.replace(tzinfo=timezone.utc)
    res_minutes = int(max(0, (now - created_dt).total_seconds() // 60)) if created_dt else 0

    caller_id = int(user["sub"]) if user and str(user.get("sub", "")).isdigit() else None
    log_action(
        db=db,
        user_id=caller_id,
        action="RESOLVE_ALERT",
        details=f"Alert #{alert.id} ({alert.title}) resolved in {res_minutes} minutes",
        target_type="ALERT",
        target_id=str(alert.id),
    )

    return {
        "message": "Alert resolved",
        "alert_id": alert.id,
        "resolution_time_minutes": res_minutes,
        "status": alert.status,
    }


analytics_router = APIRouter(prefix="/analytics", tags=["Risk Analytics (Day 28)"])


@analytics_router.get("/risk-overview")
def risk_overview(
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin", "security_manager", "security_analyst", "soc_engineer")),
):
    return get_risk_overview_analytics(db)


@router.post("/{alert_id}/create-incident", response_model=IncidentResponse)
def escalate_alert_to_incident(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )

    # Check if incident already exists for this alert
    existing_incident = db.query(Incident).filter(Incident.alert_id == alert.id).first()
    if existing_incident:
        emp_name = existing_incident.employee.name if existing_incident.employee else None
        emp_id = existing_incident.employee.employee_id if existing_incident.employee else None
        return IncidentResponse(
            id=existing_incident.id,
            employee_id=existing_incident.employee_id,
            employee_name=emp_name,
            employee_identifier=emp_id,
            alert_id=existing_incident.alert_id,
            title=existing_incident.title,
            description=existing_incident.description,
            status=existing_incident.status,
            severity=existing_incident.severity,
            assigned_to=existing_incident.assigned_to,
            resolved_at=existing_incident.resolved_at,
            created_at=existing_incident.created_at,
        )

    # Create new Incident
    incident = Incident(
        employee_id=alert.employee_id,
        alert_id=alert.id,
        title=f"Incident Escalation: {alert.title}",
        description=f"Automated incident created from Alert #{alert.id} ({alert.category}).\n\nTrigger Details:\n{alert.message}",
        severity=alert.severity,
        status="OPEN",
        created_at=datetime.now(timezone.utc),
    )
    db.add(incident)

    alert.status = "ACKNOWLEDGED"
    alert.acknowledged_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(incident)

    emp_name = incident.employee.name if incident.employee else None
    emp_id = incident.employee.employee_id if incident.employee else None

    return IncidentResponse(
        id=incident.id,
        employee_id=incident.employee_id,
        employee_name=emp_name,
        employee_identifier=emp_id,
        alert_id=incident.alert_id,
        title=incident.title,
        description=incident.description,
        status=incident.status,
        severity=incident.severity,
        assigned_to=incident.assigned_to,
        resolved_at=incident.resolved_at,
        created_at=incident.created_at,
    )

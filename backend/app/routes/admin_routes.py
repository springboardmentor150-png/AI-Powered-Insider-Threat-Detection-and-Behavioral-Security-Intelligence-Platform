"""
Day 6 RBAC examples, turned into real working endpoints:
- /admin/users            (admin only)
- /reports/risk-posture   (admin, security_manager)
- /alerts/my              (any logged-in role)

Incident/Alert CREATE endpoints are added here too. The Day 2 schema defines
the `incidents` and `alerts` tables, and Day 6 shows a reader for /alerts/my,
but no guide yet supplies a writer for them - without one there's no way to
put data in those tables to test against. These are a minimal, clearly-scoped
addition on top of what the guides specify.
"""

from collections import Counter

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Employee, Incident, Alert
from app.schemas import (
    UserResponse,
    IncidentCreate,
    IncidentResponse,
    AlertCreate,
    AlertResponse,
    RiskPostureResponse,
)
from app.security import require_role

router = APIRouter(tags=["admin"])


@router.get("/admin/users", response_model=list[UserResponse])
def list_all_users(
    db: Session = Depends(get_db),
    user=Depends(require_role("admin")),
):
    return db.query(User).all()


@router.get("/reports/risk-posture", response_model=RiskPostureResponse)
def get_risk_posture(
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "security_manager")),
):
    total_employees = db.query(Employee).count()
    open_incidents = db.query(Incident).filter(Incident.status == "open").count()

    incidents_by_severity = Counter(
        row.severity for row in db.query(Incident.severity).all()
    )
    alerts_by_severity = Counter(row.severity for row in db.query(Alert.severity).all())

    return RiskPostureResponse(
        total_employees=total_employees,
        open_incidents=open_incidents,
        incidents_by_severity=dict(incidents_by_severity),
        alerts_by_severity=dict(alerts_by_severity),
    )


@router.get("/alerts/my", response_model=list[AlertResponse])
def get_my_alerts(
    db: Session = Depends(get_db),
    user=Depends(
        require_role("admin", "security_analyst", "soc_engineer", "security_manager")
    ),
):
    current_user_id = int(user["sub"])
    return db.query(Alert).filter(Alert.assigned_to == current_user_id).all()


@router.post("/incidents", response_model=IncidentResponse, status_code=201)
def create_incident(
    data: IncidentCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "security_manager", "soc_engineer")),
):
    employee = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not employee:
        raise HTTPException(status_code=400, detail="employee_id does not exist")

    incident = Incident(**data.dict())
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@router.post("/alerts", response_model=AlertResponse, status_code=201)
def create_alert(
    data: AlertCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "security_manager", "soc_engineer")),
):
    employee = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not employee:
        raise HTTPException(status_code=400, detail="employee_id does not exist")

    if data.assigned_to is not None:
        assignee = db.query(User).filter(User.id == data.assigned_to).first()
        if not assignee:
            raise HTTPException(status_code=400, detail="assigned_to does not match any existing user")

    alert = Alert(**data.dict())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert

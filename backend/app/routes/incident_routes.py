from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Incident, Alert
from app.schemas import Incident as IncidentSchema, IncidentBase
from app.models import Employee
from app.auth import require_role, decode_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/incidents", tags=["incidents"])
security = HTTPBearer()

from app.audit import log_audit

@router.post("", response_model=IncidentSchema, status_code=status.HTTP_201_CREATED)
def create_incident(incident: IncidentBase, db: Session = Depends(get_db), current_user: dict = Depends(require_role("admin", "soc_engineer", "security_analyst", "security_manager"))):
    alert = db.query(Alert).filter(Alert.id == incident.alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    new_incident = Incident(**incident.dict())
    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)
    log_audit(db, int(current_user.get("sub", 0)), "CREATED_INCIDENT", str(new_incident.id), f"Escalated from alert {incident.alert_id}")
    return new_incident

@router.get("", response_model=List[IncidentSchema])
def list_incidents(db: Session = Depends(get_db), credentials: dict = Depends(require_role("admin", "security_manager", "soc_engineer", "security_analyst"))):
    role = credentials.get("role", "").upper()
    if role == "SECURITY_MANAGER":
        user_id = credentials.get("sub")
        employees = db.query(Employee).filter(Employee.manager_id == int(user_id)).all()
        emp_ids = [e.employee_id for e in employees]
        alerts = db.query(Alert).filter(Alert.employee_id.in_(emp_ids)).all()
        alert_ids = [a.id for a in alerts]
        return db.query(Incident).filter(Incident.alert_id.in_(alert_ids)).all()
    return db.query(Incident).all()

@router.put("/{incident_id}", response_model=IncidentSchema)
def update_incident(incident_id: int, status: str, notes: str = None, db: Session = Depends(get_db), current_user: dict = Depends(require_role("admin", "soc_engineer", "security_manager", "security_analyst"))):
    db_incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not db_incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    db_incident.status = status
    if notes:
        db_incident.notes = notes
    db.commit()
    db.refresh(db_incident)
    log_audit(db, int(current_user.get("sub", 0)), "UPDATED_INCIDENT", str(incident_id), f"Changed status to {status}")
    return db_incident

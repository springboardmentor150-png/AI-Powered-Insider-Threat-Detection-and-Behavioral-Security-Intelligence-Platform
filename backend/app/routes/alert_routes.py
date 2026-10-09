from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Alert
from app.schemas import Alert as AlertSchema, AlertBase
from app.models import Employee
from app.auth import require_role

router = APIRouter(prefix="/alerts", tags=["alerts"])

from app.models import User

@router.get("", response_model=List[AlertSchema])
def list_alerts(db: Session = Depends(get_db), credentials: dict = Depends(require_role("ADMIN", "SECURITY_MANAGER", "SOC_ENGINEER", "SECURITY_ANALYST"))):
    role = credentials.get("role", "").upper()
    if role == "SECURITY_MANAGER":
        user_id = credentials.get("sub")
        employees = db.query(Employee).filter(Employee.manager_id == int(user_id)).all()
        emp_ids = [e.employee_id for e in employees]
        return db.query(Alert).filter(Alert.employee_id.in_(emp_ids)).all()
    # For privileged roles return all
    return db.query(Alert).all()

from app.audit import log_audit

@router.put("/{alert_id}/status")
def update_alert_status(alert_id: int, status: str, db: Session = Depends(get_db), current_user: dict = Depends(require_role("admin", "soc_engineer", "security_analyst", "security_manager"))):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = status
    db.commit()
    log_audit(db, int(current_user.get("sub", 0)), "UPDATED_ALERT", str(alert_id), f"Changed status to {status}")
    return {"message": "Status updated successfully"}

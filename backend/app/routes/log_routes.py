from fastapi import APIRouter, status, Depends
from typing import List
from app.schemas import ActivityLogCreate
from app.log_ingestion import ingest_activity_log, get_activity_logs
from app.auth import require_role
from app.models import Employee

router = APIRouter(prefix="/logs", tags=["logs"])

@router.post("/ingest", status_code=status.HTTP_201_CREATED)
def ingest_log(log: ActivityLogCreate, _: dict = Depends(require_role("ADMIN", "SOC_ENGINEER", "SECURITY_ANALYST", "SECURITY_MANAGER"))):
    inserted_id = ingest_activity_log(
        employee_id=log.employee_id,
        event_type=log.event_type,
        details=log.details
    )
    return {"message": "Activity log ingested successfully", "id": inserted_id}

from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

@router.get("/")
def list_logs(db: Session = Depends(get_db), credentials: dict = Depends(require_role("ADMIN", "SECURITY_ANALYST", "SOC_ENGINEER", "SECURITY_MANAGER"))):
    role = credentials.get("role", "").upper()
    if role == "SECURITY_MANAGER":
        user_id = credentials.get("sub")
        employees = db.query(Employee).filter(Employee.manager_id == int(user_id)).all()
        emp_ids = [e.employee_id for e in employees]
        logs = get_activity_logs()
        return [l for l in logs if l.get("employee_id") in emp_ids]
        
    return get_activity_logs()

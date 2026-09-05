# backend/app/routes/employee_routes.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database import get_db, doc_db
from app.models import Employee, User, AuditLog
from app.schemas import EmployeeCreate, EmployeeUpdate, EmployeeOut
from app.auth import get_current_user, require_role

router = APIRouter(prefix="/employees", tags=["Employee Profiles & Identity"])

@router.get("", response_model=List[EmployeeOut])
def list_employees(
    department: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Employee)
    if department:
        query = query.filter(Employee.department.ilike(f"%{department}%"))
    if search:
        query = query.filter(
            (Employee.name.ilike(f"%{search}%")) |
            (Employee.employee_id.ilike(f"%{search}%")) |
            (Employee.designation.ilike(f"%{search}%"))
        )
    return query.order_by(Employee.baseline_risk_score.desc()).all()

@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee {employee_id} not found")
    return employee

@router.post("", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
def create_employee(
    emp_in: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "security_manager"))
):
    existing = db.query(Employee).filter(Employee.employee_id == emp_in.employee_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Employee ID {emp_in.employee_id} already exists")

    new_emp = Employee(**emp_in.model_dump())
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)

    # Initialize behavioral baseline in document database
    doc_db.behavioral_baselines.insert_one({
        "employee_id": new_emp.employee_id,
        "avg_daily_events": 25,
        "avg_daily_download_mb": 18.5,
        "allowed_devices": [new_emp.device_info or "Standard Corporate Laptop"],
        "typical_work_hours": "09:00 - 18:00 UTC",
        "last_updated": datetime.now(timezone.utc).isoformat()
    })

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action="CREATE_EMPLOYEE",
        target_resource=f"Employee:{new_emp.employee_id}",
        details=f"Onboarded employee {new_emp.name} in department {new_emp.department}"
    )
    db.add(audit)
    db.commit()

    return new_emp

@router.put("/{employee_id}", response_model=EmployeeOut)
def update_employee(
    employee_id: str,
    emp_in: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "security_manager"))
):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee {employee_id} not found")

    update_data = emp_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(employee, field, val)

    db.commit()
    db.refresh(employee)

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action="UPDATE_EMPLOYEE",
        target_resource=f"Employee:{employee.employee_id}",
        details=f"Updated profile: {list(update_data.keys())}"
    )
    db.add(audit)
    db.commit()

    return employee

@router.delete("/{employee_id}")
def delete_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee {employee_id} not found")

    db.delete(employee)
    db.commit()
    doc_db.activity_logs.delete_many({"employee_id": employee_id})
    doc_db.behavioral_baselines.delete_many({"employee_id": employee_id})

    return {"message": f"Employee {employee_id} and associated telemetry deleted successfully"}

@router.get("/{employee_id}/baseline")
def get_employee_baseline(
    employee_id: str,
    current_user: User = Depends(get_current_user)
):
    baseline = doc_db.behavioral_baselines.find_one({"employee_id": employee_id})
    if not baseline:
        return {
            "employee_id": employee_id,
            "avg_daily_events": 20,
            "avg_daily_download_mb": 15.0,
            "allowed_devices": ["Corporate Workstation"],
            "typical_work_hours": "09:00 - 18:00 UTC",
            "is_default": True
        }
    baseline["_id"] = str(baseline.get("_id", ""))
    return baseline

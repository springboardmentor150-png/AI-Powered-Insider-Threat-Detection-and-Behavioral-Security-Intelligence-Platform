from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Employee
from app.schemas import EmployeeCreate, Employee as EmployeeSchema
from app.auth import require_role
from app.audit import log_audit

router = APIRouter(prefix="/employees", tags=["employees"])

@router.post("", response_model=EmployeeSchema, status_code=status.HTTP_201_CREATED)
def create_employee(
    employee: EmployeeCreate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(require_role("admin", "security_manager"))
):
    db_employee = db.query(Employee).filter(Employee.employee_id == employee.employee_id).first()
    if db_employee:
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    
    new_employee = Employee(**employee.dict())
    
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    
    log_audit(db, int(current_user.get("sub", 0)), "CREATED_EMPLOYEE", new_employee.employee_id, f"Created {new_employee.name}")
    return new_employee

@router.get("/{employee_id}", response_model=EmployeeSchema)
def get_employee(
    employee_id: str, 
    db: Session = Depends(get_db), 
    _: dict = Depends(require_role("admin", "security_analyst", "soc_engineer", "security_manager"))
):
    db_employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@router.get("")
def list_employees(
    db: Session = Depends(get_db), 
    _: dict = Depends(require_role("admin", "security_analyst", "soc_engineer", "security_manager"))
):
    from app.mongo_database import db as mongo_db
    employees = db.query(Employee).all()
    scores_cur = list(mongo_db.risk_scores.find({}, {"_id": 0}))
    scores_map = {s["employee_id"]: s for s in scores_cur}
    
    result = []
    for emp in employees:
        emp_dict = {
            "id": emp.id,
            "employee_id": emp.employee_id,
            "name": emp.name,
            "department": emp.department,
            "designation": emp.designation,
            "manager_id": emp.manager_id,
            "device_info": emp.device_info,
            "access_privileges": emp.access_privileges
        }
        score_data = scores_map.get(emp.employee_id)
        if score_data:
            score = score_data.get("score", 0)
            emp_dict["risk_score"] = score
            emp_dict["risk_level"] = "Critical" if score >= 75 else "High" if score >= 50 else "Medium" if score >= 25 else "Low"
            emp_dict["last_activity"] = score_data.get("last_updated")
        else:
            emp_dict["risk_score"] = 0
            emp_dict["risk_level"] = "Low"
            emp_dict["last_activity"] = None
        result.append(emp_dict)
    return result

@router.put("/{employee_id}", response_model=EmployeeSchema)
def update_employee(
    employee_id: str,
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "security_manager"))
):
    db_emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not db_emp:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    db_emp.name = employee.name
    db_emp.department = employee.department
    db_emp.designation = employee.designation
    db_emp.manager_id = employee.manager_id
    db_emp.device_info = employee.device_info
    db_emp.access_privileges = employee.access_privileges
    db.commit()
    db.refresh(db_emp)
    log_audit(db, int(current_user.get("sub", 0)), "UPDATED_EMPLOYEE", employee_id, f"Updated designation/department")
    return db_emp

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    db_emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not db_emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(db_emp)
    db.commit()
    log_audit(db, int(current_user.get("sub", 0)), "DELETED_EMPLOYEE", employee_id, "Removed from registry")
    return

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from ..database import get_db
from ..models import Employee
from ..security import require_role

router = APIRouter(prefix="/employees", tags=["Employees"])


class EmployeeCreate(BaseModel):
    employee_id: str
    name: str
    department: Optional[str] = None
    designation: Optional[str] = None
    manager_id: Optional[int] = None
    device_info: Optional[str] = None
    access_privileges: Optional[str] = None


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    manager_id: Optional[int] = None
    device_info: Optional[str] = None
    access_privileges: Optional[str] = None


@router.post("")
def create_employee(
    request: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin", "security_manager")),
):
    existing = db.query(Employee).filter(Employee.employee_id == request.employee_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee ID already exists",
        )

    employee = Employee(**request.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return {"message": "Employee created", "employee_id": employee.employee_id}


@router.get("")
def list_employees(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin", "security_analyst", "soc_engineer")),
):
    employees = db.query(Employee).all()
    return {"employees": [{"id": e.id, "employee_id": e.employee_id, "name": e.name, "department": e.department} for e in employees]}


@router.get("/{employee_id}")
def get_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin", "security_analyst", "soc_engineer")),
):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {
        "id": employee.id,
        "employee_id": employee.employee_id,
        "name": employee.name,
        "department": employee.department,
        "designation": employee.designation,
        "manager_id": employee.manager_id,
        "device_info": employee.device_info,
        "access_privileges": employee.access_privileges,
    }


@router.put("/{employee_id}")
def update_employee(
    employee_id: str,
    request: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin", "security_manager")),
):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(employee, key, value)

    db.commit()
    db.refresh(employee)
    return {"message": "Employee updated", "employee_id": employee.employee_id}


@router.delete("/{employee_id}")
def delete_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin", "security_manager")),
):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(employee)
    db.commit()
    return {"message": "Employee deleted", "employee_id": employee_id}

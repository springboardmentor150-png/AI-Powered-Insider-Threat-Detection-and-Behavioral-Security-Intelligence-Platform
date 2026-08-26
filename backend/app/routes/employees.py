from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee
from app.auth import require_role

router = APIRouter(tags=["Employees"])


class EmployeeCreate(BaseModel):
    employee_id: str
    name: str
    department: str
    designation: str
    manager_id: int | None = None
    device_info: str | None = None
    access_privileges: str | None = None


@router.post("/employees")
def create_employee(
    data: EmployeeCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "security_manager"))
):
    existing = db.query(Employee).filter(
        Employee.employee_id == data.employee_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Employee ID already exists"
        )

    employee = Employee(
        employee_id=data.employee_id,
        name=data.name,
        department=data.department,
        designation=data.designation,
        manager_id=data.manager_id,
        device_info=data.device_info,
        access_privileges=data.access_privileges
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return {
        "message": "Employee onboarded",
        "employee_id": employee.employee_id
    }


@router.get("/employees/{employee_id}")
def get_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    user=Depends(
        require_role(
            "admin",
            "security_analyst",
            "soc_engineer"
        )
    )
):
    employee = db.query(Employee).filter(
        Employee.employee_id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return employee
@router.get("/employees")
def list_employees(
    db: Session = Depends(get_db),
    user=Depends(
        require_role(
            "admin",
            "security_analyst",
            "security_manager",
            "soc_engineer"
        )
    )
):
    employees = db.query(Employee).all()
    return employees
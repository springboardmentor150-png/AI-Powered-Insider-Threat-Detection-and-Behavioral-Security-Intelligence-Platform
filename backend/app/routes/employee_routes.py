from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models import Employee

router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)


@router.get("/")
def get_employees(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    employees = db.query(Employee).all()
    return employees


@router.post("/")
def create_employee(
    employee_id: str,
    name: str,
    department: str,
    designation: str,
    manager_id: int = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role not in ["admin", "security_manager"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to create employees"
        )

    employee = Employee(
        employee_id=employee_id,
        name=name,
        department=department,
        designation=designation,
        manager_id=manager_id
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return {
        "message": "Employee created successfully",
        "employee_id": employee.id,
        "name": employee.name
    }

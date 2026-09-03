from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import Employee
from .auth import require_roles


router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Request body
class EmployeeCreate(BaseModel):
    name: str
    department: str
    role: str


# Create employee
# Only admin and security_manager can create employees
@router.post("/")
def create_employee(
    data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("admin", "security_manager")
    )
):
    employee = Employee(
        name=data.name,
        department=data.department,
        role=data.role
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return {
        "message": "Employee created successfully",
        "employee_id": employee.id,
        "name": employee.name,
        "department": employee.department,
        "role": employee.role
    }


# Get all employees
# All authenticated roles can view employees
@router.get("/")
def get_employees(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "admin",
            "security_manager",
            "security_analyst",
            "soc_engineer"
        )
    )
):
    employees = db.query(Employee).all()

    return employees


# Get employee by ID
# All authenticated roles can view an employee
@router.get("/{employee_id}")
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "admin",
            "security_manager",
            "security_analyst",
            "soc_engineer"
        )
    )
):
    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return employee
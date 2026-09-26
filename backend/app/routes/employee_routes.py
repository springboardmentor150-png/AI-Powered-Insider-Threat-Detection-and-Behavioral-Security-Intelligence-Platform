from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee
from app.auth import get_current_user


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

    return {
        "employees": employees
    }


@router.post("/")
def add_employee(
    employee_id: str,
    name: str,
    email: str,
    department: str = "",
    role: str = "",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    existing_employee = db.query(Employee).filter(
        Employee.employee_id == employee_id
    ).first()

    if existing_employee:
        raise HTTPException(
            status_code=400,
            detail="Employee ID already exists"
        )

    existing_email = db.query(Employee).filter(
        Employee.email == email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Employee email already exists"
        )

    employee = Employee(
        employee_id=employee_id,
        name=name,
        email=email,
        department=department,
        role=role,
        status="Active"
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return {
        "message": "Employee added successfully",
        "employee": {
            "id": employee.id,
            "employee_id": employee.employee_id,
            "name": employee.name,
            "email": employee.email,
            "department": employee.department,
            "role": employee.role,
            "status": employee.status
        }
    }


@router.delete("/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    db.delete(employee)
    db.commit()

    return {
        "message": "Employee deleted successfully"
    }
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Employee
from app.schemas import EmployeeCreate, Employee as EmployeeSchema
from app.auth import require_role

router = APIRouter(prefix="/employees", tags=["employees"])

@router.post("", response_model=EmployeeSchema, status_code=status.HTTP_201_CREATED)
def create_employee(
    employee: EmployeeCreate, 
    db: Session = Depends(get_db), 
    _: dict = Depends(require_role("admin", "security_manager"))
):
    db_employee = db.query(Employee).filter(Employee.employee_id == employee.employee_id).first()
    if db_employee:
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    
    new_employee = Employee(**employee.dict())
    
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    
    return new_employee

@router.get("/{employee_id}", response_model=EmployeeSchema)
def get_employee(
    employee_id: str, 
    db: Session = Depends(get_db), 
    _: dict = Depends(require_role("admin", "security_analyst", "soc_engineer"))
):
    db_employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@router.get("", response_model=List[EmployeeSchema])
def list_employees(
    db: Session = Depends(get_db), 
    _: dict = Depends(require_role("admin", "security_analyst", "soc_engineer", "security_manager"))
):
    employees = db.query(Employee).all()
    return employees

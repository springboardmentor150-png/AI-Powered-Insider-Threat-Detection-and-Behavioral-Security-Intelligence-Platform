"""
Days 7-8: Employee onboarding, profile management, department mapping.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee
from app.schemas import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    DirectReportsResponse,
)
from app.security import require_role

router = APIRouter(tags=["employees"])


@router.post("/employees", response_model=EmployeeResponse, status_code=201)
def onboard_employee(
    data: EmployeeCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "security_manager")),
):
    existing = db.query(Employee).filter(Employee.employee_id == data.employee_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Employee ID already exists")

    if data.manager_id:
        manager = db.query(Employee).filter(Employee.id == data.manager_id).first()
        if not manager:
            raise HTTPException(
                status_code=400,
                detail="manager_id does not match any existing employee",
            )

    employee = Employee(**data.dict())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    user=Depends(
        require_role("admin", "security_analyst", "soc_engineer", "security_manager")
    ),
):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.get("/employees", response_model=list[EmployeeResponse])
def list_employees(
    department: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(
        require_role("admin", "security_analyst", "soc_engineer", "security_manager")
    ),
):
    query = db.query(Employee)
    if department:
        query = query.filter(Employee.department == department)
    return query.all()


@router.patch("/employees/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: str,
    data: EmployeeUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "security_manager")),
):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    updates = data.dict(exclude_unset=True)

    if "manager_id" in updates and updates["manager_id"] is not None:
        manager = db.query(Employee).filter(Employee.id == updates["manager_id"]).first()
        if not manager:
            raise HTTPException(
                status_code=400,
                detail="manager_id does not match any existing employee",
            )

    for field, value in updates.items():
        setattr(employee, field, value)

    db.commit()
    db.refresh(employee)
    return employee


@router.get("/employees/{employee_id}/reports", response_model=DirectReportsResponse)
def get_direct_reports(
    employee_id: str,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "security_manager")),
):
    manager = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not manager:
        raise HTTPException(status_code=404, detail="Employee not found")

    reports = db.query(Employee).filter(Employee.manager_id == manager.id).all()
    return DirectReportsResponse(
        manager=manager.name, direct_reports=[r.name for r in reports]
    )


@router.get("/departments/{department}/employees", response_model=list[EmployeeResponse])
def get_department_employees(
    department: str,
    db: Session = Depends(get_db),
    user=Depends(
        require_role("admin", "security_analyst", "soc_engineer", "security_manager")
    ),
):
    return db.query(Employee).filter(Employee.department == department).all()

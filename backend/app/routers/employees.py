"""
/employees router

GET    /employees              — list all (or filter by dept)
POST   /employees              — create (Admin / Security Manager)
GET    /employees/{emp_id}     — single employee
PATCH  /employees/{emp_id}     — update (Admin / Security Manager)
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models import Employee
from app.schemas import EmployeeCreate, EmployeeOut, EmployeeUpdate

router = APIRouter(prefix="/employees", tags=["employees"])

_MANAGERS = ["Administrator", "Security Manager"]


def _next_employee_id(count: int) -> str:
    return f"EMP-{1000 + count + 1}"


@router.get("", response_model=list[EmployeeOut])
async def list_employees(
    department: str | None = Query(default=None, description="Filter by department name"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _current=Depends(get_current_user),
):
    """Return all active employees, optionally filtered by department."""
    q = select(Employee).where(Employee.is_active == True)  # noqa: E712
    if department:
        q = q.where(Employee.department == department)
    q = q.order_by(Employee.name).offset(skip).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
async def create_employee(
    body: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    _current=Depends(require_role(*_MANAGERS)),
):
    """Create a new monitored employee. Requires Administrator or Security Manager role."""
    # Email uniqueness check
    dup = await db.execute(select(Employee).where(Employee.email == body.email))
    if dup.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An employee with that email already exists.",
        )

    # Auto-generate employee_id
    count_result = await db.execute(select(func.count()).select_from(Employee))
    count = count_result.scalar_one()

    emp = Employee(
        employee_id=_next_employee_id(count),
        name=body.name,
        email=body.email,
        department=body.department,
        designation=body.designation,
        manager=body.manager,
        risk_level=body.risk_level,  # type: ignore[arg-type]
        risk_score=body.risk_score,
        location=body.location,
        joined_at=datetime.now(timezone.utc),
        is_active=True,
    )
    db.add(emp)
    await db.flush()
    await db.refresh(emp)
    return emp


@router.get("/{emp_id}", response_model=EmployeeOut)
async def get_employee(
    emp_id: str,
    db: AsyncSession = Depends(get_db),
    _current=Depends(get_current_user),
):
    result = await db.execute(
        select(Employee).where(Employee.employee_id == emp_id)
    )
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee '{emp_id}' not found.")
    return emp


@router.patch("/{emp_id}", response_model=EmployeeOut)
async def update_employee(
    emp_id: str,
    body: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
    _current=Depends(require_role(*_MANAGERS)),
):
    """Update employee fields. Requires Administrator or Security Manager role."""
    result = await db.execute(
        select(Employee).where(Employee.employee_id == emp_id)
    )
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee '{emp_id}' not found.")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(emp, field, value)

    await db.flush()
    await db.refresh(emp)
    return emp

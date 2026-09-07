"""
/alerts router

GET   /alerts             — list (filter by severity / status / employee)
POST  /alerts             — create
GET   /alerts/{alert_id}  — single alert with correlated logs
PATCH /alerts/{alert_id}  — update status / severity / narrative
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models import Alert, Employee
from app.mongo import get_logs_for_employee
from app.schemas import AlertCreate, AlertOut, AlertUpdate

router = APIRouter(prefix="/alerts", tags=["alerts"])

_MANAGERS = ["Administrator", "Security Manager"]


def _enrich(alert: Alert, employee_name: str) -> dict:
    """Convert ORM Alert + employee name to a dict matching AlertOut."""
    d = {
        "id": alert.id,
        "alert_id": alert.alert_id,
        "employee_id": alert.employee_id,
        "severity": alert.severity.value,
        "message": alert.message,
        "status": alert.status.value,
        "rule": alert.rule,
        "narrative": alert.narrative,
        "assigned_to": alert.assigned_to.value,
        "created_at": alert.created_at,
        "employee_name": employee_name,
    }
    return d


@router.get("", response_model=list[AlertOut])
async def list_alerts(
    severity: str | None = Query(default=None),
    status: str | None = Query(default=None),
    employee_id: str | None = Query(default=None),
    assigned_to: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _current=Depends(get_current_user),
):
    q = select(Alert).order_by(Alert.created_at.desc()).offset(skip).limit(limit)
    if severity:
        q = q.where(Alert.severity == severity)
    if status:
        q = q.where(Alert.status == status)
    if employee_id:
        q = q.where(Alert.employee_id == employee_id)
    if assigned_to:
        q = q.where(Alert.assigned_to == assigned_to)

    result = await db.execute(q)
    alerts = result.scalars().all()

    # Bulk-load employee names
    emp_ids = {a.employee_id for a in alerts}
    emp_result = await db.execute(
        select(Employee).where(Employee.employee_id.in_(emp_ids))
    )
    emp_map = {e.employee_id: e.name for e in emp_result.scalars().all()}

    return [_enrich(a, emp_map.get(a.employee_id, "")) for a in alerts]


@router.post("", response_model=AlertOut, status_code=201)
async def create_alert(
    body: AlertCreate,
    db: AsyncSession = Depends(get_db),
    _current=Depends(require_role(*_MANAGERS, "Security Analyst", "SOC Engineer")),
):
    # Verify employee exists
    emp_result = await db.execute(
        select(Employee).where(Employee.employee_id == body.employee_id)
    )
    emp = emp_result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee '{body.employee_id}' not found.")

    # Generate alert_id
    count_result = await db.execute(select(Alert))
    count = len(count_result.scalars().all())

    alert = Alert(
        alert_id=f"ALR-{4400 + count + 1}",
        employee_id=body.employee_id,
        severity=body.severity,  # type: ignore[arg-type]
        message=body.message,
        status="Open",  # type: ignore[arg-type]
        rule=body.rule,
        narrative=body.narrative,
        assigned_to=body.assigned_to,  # type: ignore[arg-type]
    )
    db.add(alert)
    await db.flush()
    await db.refresh(alert)
    return _enrich(alert, emp.name)


@router.get("/{alert_id}", response_model=AlertOut)
async def get_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    _current=Depends(get_current_user),
):
    result = await db.execute(select(Alert).where(Alert.alert_id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found.")

    emp_result = await db.execute(
        select(Employee).where(Employee.employee_id == alert.employee_id)
    )
    emp = emp_result.scalar_one_or_none()
    return _enrich(alert, emp.name if emp else "")


@router.patch("/{alert_id}", response_model=AlertOut)
async def update_alert(
    alert_id: str,
    body: AlertUpdate,
    db: AsyncSession = Depends(get_db),
    _current=Depends(get_current_user),
):
    result = await db.execute(select(Alert).where(Alert.alert_id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found.")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(alert, field, value)

    await db.flush()
    await db.refresh(alert)

    emp_result = await db.execute(
        select(Employee).where(Employee.employee_id == alert.employee_id)
    )
    emp = emp_result.scalar_one_or_none()
    return _enrich(alert, emp.name if emp else "")


@router.get("/{alert_id}/logs")
async def get_alert_correlated_logs(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    _current=Depends(get_current_user),
):
    """Return activity logs correlated to the employee on this alert."""
    result = await db.execute(select(Alert).where(Alert.alert_id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found.")

    logs = await get_logs_for_employee(alert.employee_id, limit=10)
    return logs

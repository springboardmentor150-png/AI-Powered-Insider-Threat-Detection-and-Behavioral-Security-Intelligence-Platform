"""
/activity-logs router  (MongoDB-backed)

GET  /activity-logs            — list with filters
POST /activity-logs            — ingest a new event
GET  /activity-logs/{emp_id}   — all logs for one employee
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_current_user, require_role
from app.mongo import ALLOWED_EVENT_TYPES, get_logs, get_logs_for_employee, insert_log
from app.schemas import ActivityLogCreate, ActivityLogOut

router = APIRouter(prefix="/activity-logs", tags=["activity-logs"])


@router.get("", response_model=list[ActivityLogOut])
async def list_logs(
    employee_id: str | None = Query(default=None, description="Partial match on employee_id"),
    event_type: str | None = Query(default=None, description="Exact event type"),
    date_from: str | None = Query(default=None, description="YYYY-MM-DD"),
    date_to: str | None = Query(default=None, description="YYYY-MM-DD"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=200, ge=1, le=500),
    _current=Depends(get_current_user),
):
    if event_type and event_type not in ALLOWED_EVENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid event_type. Allowed: {sorted(ALLOWED_EVENT_TYPES)}",
        )

    logs = await get_logs(
        employee_id=employee_id,
        event_type=event_type,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )
    return logs


@router.post("", response_model=ActivityLogOut, status_code=status.HTTP_201_CREATED)
async def ingest_log(
    body: ActivityLogCreate,
    _current=Depends(require_role("Administrator", "SOC Engineer")),
):
    """Ingest a single activity log event into MongoDB."""
    try:
        inserted = await insert_log(body.model_dump())
        return inserted
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get("/employee/{emp_id}", response_model=list[ActivityLogOut])
async def logs_for_employee(
    emp_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    _current=Depends(get_current_user),
):
    """Return recent activity logs for a specific employee."""
    return await get_logs_for_employee(emp_id, limit=limit)

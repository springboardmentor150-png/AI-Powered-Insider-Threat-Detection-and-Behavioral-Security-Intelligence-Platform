"""
ITBIS UEBA API Routes.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.security import require_role
from app.ueba import (
    get_peer_group_comparison,
    get_trend_direction,
    get_risk_trend,
)
from app.models import Employee
from app.risk_scoring import calculate_risk_score


router = APIRouter(tags=["UEBA"])


ALLOWED_ROLES = (
    "admin",
    "security_analyst",
    "soc_engineer",
    "security_manager",
)


@router.get("/ueba/peer-comparison/{employee_id}")
def peer_comparison(
    employee_id: str,
    db: Session = Depends(get_db),
    user=Depends(require_role(*ALLOWED_ROLES)),
):
    result = get_peer_group_comparison(
        employee_id,
        db
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return result


@router.get("/ueba/trend/{employee_id}")
def risk_trend(
    employee_id: str,
    days: int = 30,
    db: Session = Depends(get_db),
    user=Depends(require_role(*ALLOWED_ROLES)),
):
    employee = (
        db.query(Employee)
        .filter(Employee.employee_id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    if days < 1 or days > 90:
        raise HTTPException(
            status_code=400,
            detail="days must be between 1 and 90"
        )

    return {
        "employee_id": employee_id,
        "days": days,
        "trend": get_risk_trend(
            employee_id,
            days
        ),
    }


@router.get("/ueba/trend-direction/{employee_id}")
def trend_direction(
    employee_id: str,
    db: Session = Depends(get_db),
    user=Depends(require_role(*ALLOWED_ROLES)),
):
    employee = (
        db.query(Employee)
        .filter(Employee.employee_id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return get_trend_direction(employee_id)


@router.get("/ueba/profile/{employee_id}")
def ueba_profile(
    employee_id: str,
    db: Session = Depends(get_db),
    user=Depends(require_role(*ALLOWED_ROLES)),
):
    employee = (
        db.query(Employee)
        .filter(Employee.employee_id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return {
        "risk_score": calculate_risk_score(
            employee_id,
            db
        ),
        "peer_comparison": get_peer_group_comparison(
            employee_id,
            db
        ),
        "trend": get_trend_direction(
            employee_id
        ),
    }
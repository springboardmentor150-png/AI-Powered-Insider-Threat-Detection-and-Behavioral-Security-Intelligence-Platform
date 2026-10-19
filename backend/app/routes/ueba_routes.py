"""
ITBIS UEBA Intelligence Workflow Routes (Milestone 3: Days 23-24)
Endpoints:
1. GET /ueba/peer-comparison/{employee_id} (Day 23)
   - Compares employee against coworkers in the same department
   - Returns PeerGroupComparisonResponse
   - 404 if employee does not exist, 200 with note if no peers
2. GET /ueba/trend/{employee_id} (Day 24)
   - Evaluates short-term behavioral acceleration
   - Returns trend direction and chronological anomaly series
3. GET /ueba/profile/{employee_id} (Day 24)
   - Unified UEBA profile combining risk_score, peer_comparison, and trend
   - Returns UEBAProfileResponse
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import Employee
from app.schemas import (
    PeerGroupComparisonResponse,
    TrendDirectionResponse,
    UEBAProfileResponse,
)
from app.security import require_role
from app.ueba import (
    get_peer_group_comparison,
    get_risk_trend,
    get_trend_direction,
    get_ueba_profile,
)

router = APIRouter(prefix="/ueba", tags=["UEBA Intelligence Workflows (Days 23-24)"])


@router.get("/peer-comparison/{employee_id}", response_model=PeerGroupComparisonResponse)
def peer_comparison(
    employee_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin", "security_analyst", "soc_engineer", "security_manager")),
):
    result = get_peer_group_comparison(employee_id, db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{employee_id}' not found",
        )
    return result


@router.get("/trend/{employee_id}")
def trend_analysis(
    employee_id: str,
    days: int = Query(14, ge=1, le=90),
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin", "security_analyst", "soc_engineer", "security_manager")),
):
    employee = db.query(Employee).filter(
        or_(
            Employee.employee_id == employee_id,
            Employee.id == int(employee_id) if employee_id.isdigit() else False,
        )
    ).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{employee_id}' not found",
        )

    direction_info = get_trend_direction(employee.employee_id)
    time_series = get_risk_trend(employee.employee_id, days=days)
    return {
        "employee_id": employee.employee_id,
        "direction": direction_info["direction"],
        "first_week_avg": direction_info["first_week_avg"],
        "second_week_avg": direction_info["second_week_avg"],
        "trend_days": days,
        "trend": time_series,
    }


@router.get("/profile/{employee_id}", response_model=UEBAProfileResponse)
def ueba_profile(
    employee_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin", "security_analyst", "soc_engineer", "security_manager")),
):
    result = get_ueba_profile(employee_id, db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{employee_id}' not found",
        )
    return result

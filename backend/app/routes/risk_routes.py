import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import Employee, RiskScoreHistory
from app.schemas import (
    EmployeeRiskItem,
    PaginatedRiskScoresResponse,
    RiskScoreHistoryResponse,
    RiskScoreResponse,
)
from app.security import get_current_user, require_role
from app.risk_scoring import calculate_risk_score

router = APIRouter(prefix="/risk-scores", tags=["Risk Scores"])


@router.get("", response_model=PaginatedRiskScoresResponse)
def get_risk_scores(
    risk_level: Optional[str] = None,
    department: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Employee)

    if risk_level and risk_level != "ALL":
        query = query.filter(Employee.risk_level == risk_level)

    if department and department != "ALL":
        query = query.filter(Employee.department == department)

    total = query.count()
    offset = (page - 1) * limit
    employees = query.order_by(Employee.risk_score.desc(), Employee.id.asc()).offset(offset).limit(limit).all()

    items = []
    for emp in employees:
        last_hist = db.query(RiskScoreHistory).filter(
            RiskScoreHistory.employee_id == emp.id
        ).order_by(RiskScoreHistory.calculated_at.desc()).first()

        top_factor = None
        if last_hist and last_hist.contributing_factors:
            try:
                factors = json.loads(last_hist.contributing_factors)
                top_factor = factors[0] if factors else None
            except Exception:
                top_factor = last_hist.contributing_factors

        if not top_factor:
            top_factor = "Operational Baseline Monitoring" if emp.risk_score < 30 else "Elevated Anomaly Triggers"

        items.append(EmployeeRiskItem(
            employee_id=emp.employee_id,
            name=emp.name,
            department=emp.department,
            risk_score=emp.risk_score,
            risk_level=emp.risk_level,
            status=emp.status,
            top_factor=top_factor,
            last_calculated=last_hist.calculated_at if last_hist else emp.created_at,
        ))

    return PaginatedRiskScoresResponse(
        items=items,
        page=page,
        limit=limit,
        total=total,
    )


@router.get("/{employee_id}/history", response_model=List[RiskScoreHistoryResponse])
def get_employee_risk_history(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
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
            detail=f"Employee '{employee_id}' not found"
        )

    history = db.query(RiskScoreHistory).filter(
        RiskScoreHistory.employee_id == employee.id
    ).order_by(RiskScoreHistory.calculated_at.asc()).all()

    return history


@router.get("/{employee_id}", response_model=RiskScoreResponse)
def get_employee_risk_score(
    employee_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin", "security_analyst", "soc_engineer", "security_manager")),
):
    """
    Computes and returns the 5-factor normalized composite insider risk score
    for a specific employee (Day 22).
    """
    employee = db.query(Employee).filter(
        or_(
            Employee.employee_id == employee_id,
            Employee.id == int(employee_id) if employee_id.isdigit() else False,
        )
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{employee_id}' not found"
        )

    return calculate_risk_score(employee.employee_id, db)


# Singular route router matching Day 22 guide specification: GET /risk-score/{employee_id}
singular_risk_router = APIRouter(prefix="/risk-score", tags=["Insider Risk Scoring Engine (Day 22)"])


@singular_risk_router.get("/{employee_id}", response_model=RiskScoreResponse)
def get_risk_score(
    employee_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin", "security_analyst", "soc_engineer", "security_manager")),
):
    return get_employee_risk_score(employee_id=employee_id, db=db, user=user)


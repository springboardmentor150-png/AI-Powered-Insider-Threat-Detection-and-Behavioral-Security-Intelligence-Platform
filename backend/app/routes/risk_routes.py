"""
ITBIS Risk Scoring API Routes.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee
from app.risk_scoring import calculate_risk_score
from app.security import require_role


router = APIRouter(
    tags=["risk scoring"]
)


@router.get("/risk-score/{employee_id}")
def get_risk_score(
    employee_id: str,
    db: Session = Depends(get_db),
    user=Depends(
        require_role(
            "admin",
            "security_analyst",
            "soc_engineer",
            "security_manager"
        )
    ),
):
    """
    Return the insider risk score for an employee.
    """

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

    return calculate_risk_score(
        employee_id,
        db
    )
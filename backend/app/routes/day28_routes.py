"""
ITBIS Day 28 API Routes.

Day 28:
- Alert escalation
- Organization-wide risk analytics
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Alert, Employee
from app.security import require_role
from app.escalation import escalate_stale_alerts
from app.risk_scoring import calculate_risk_score


router = APIRouter(tags=["Day 28 - Escalation & Analytics"])


# =========================================================
# Escalate Stale Alerts
# =========================================================

@router.post("/alerts/escalate")
def escalate_alerts(
    db: Session = Depends(get_db),
    user=Depends(
        require_role(
            "admin",
            "security_manager",
        )
    ),
):
    escalated_ids = escalate_stale_alerts(db)

    return {
        "message": "Alert escalation completed",
        "escalated_count": len(escalated_ids),
        "escalated_alert_ids": escalated_ids,
    }


# =========================================================
# Risk Overview
# =========================================================

@router.get("/analytics/risk-overview")
def risk_overview(
    db: Session = Depends(get_db),
    user=Depends(
        require_role(
            "admin",
            "security_manager",
        )
    ),
):
    employees = db.query(Employee).all()

    level_counts = {
        "Low": 0,
        "Medium": 0,
        "High": 0,
        "Critical": 0,
    }

    for employee in employees:

        risk = calculate_risk_score(
            employee.employee_id,
            db,
        )

        level_counts[risk["risk_level"]] += 1

    open_alerts = (
        db.query(Alert)
        .filter(Alert.status == "open")
        .count()
    )

    escalated_alerts = (
        db.query(Alert)
        .filter(Alert.status == "escalated")
        .count()
    )

    return {
        "total_employees": len(employees),
        "risk_level_distribution": level_counts,
        "open_alerts": open_alerts,
        "escalated_alerts": escalated_alerts,
    }
from fastapi import APIRouter
from app.database import SessionLocal
from app.models import Employee, Alert, Incident
from app.risk_scoring import calculate_risk_score

router = APIRouter(prefix="/analytics", tags=["Risk Analytics"])

@router.get("/risk-distribution")
def get_risk_distribution():
    db = SessionLocal()
    try:
        employees = db.query(Employee).all()
        distribution = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for emp in employees:
            category = calculate_risk_score(emp.employee_id)["risk_category"]
            distribution[category] += 1
        return {"total_employees": len(employees), "distribution": distribution}
    finally:
        db.close()

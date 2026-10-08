from fastapi import APIRouter
from app.risk_scoring import calculate_risk_score

router = APIRouter(prefix="/risk", tags=["Risk Scoring"])

@router.get("/{employee_id}")
def get_employee_risk(employee_id: str):
    return calculate_risk_score(employee_id)

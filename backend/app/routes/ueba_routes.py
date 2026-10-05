# backend/app/routes/ueba_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.risk_scoring import calculate_risk_score
from app.ueba import compare_to_peers, get_risk_trend

router = APIRouter(prefix="/ueba", tags=["UEBA & Risk Intelligence"])

@router.get("/risk-score/{employee_id}")
def get_employee_risk_score(employee_id: str, user=Depends(get_current_user)):
    return calculate_risk_score(employee_id)

@router.get("/peer-comparison/{employee_id}")
def get_employee_peer_comparison(
    employee_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return compare_to_peers(db, employee_id)

@router.get("/risk-trend/{employee_id}")
def get_employee_risk_trend(
    employee_id: str,
    days: int = 30,
    user=Depends(get_current_user)
):
    return get_risk_trend(employee_id, days=days)
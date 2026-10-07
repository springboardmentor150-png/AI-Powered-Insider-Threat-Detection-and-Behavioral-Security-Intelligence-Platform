from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.ueba import compare_to_peers, get_risk_trend

router = APIRouter(prefix="/ueba", tags=["UEBA"])

@router.get("/peer/{employee_id}")
def peer_comparison(employee_id: str, db: Session = Depends(get_db)):
    return compare_to_peers(db, employee_id)

@router.get("/trend/{employee_id}")
def risk_trend(employee_id: str, days: int = 30):
    return {"employee_id": employee_id, "days": days, "trend": get_risk_trend(employee_id, days)}

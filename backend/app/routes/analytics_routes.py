from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.analytics import generate_baseline, detect_anomalies, calculate_risk_score, get_dashboard_stats
from app.auth import require_role
from app.mongo_database import db

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/dashboard-stats")
def get_stats(db: Session = Depends(get_db), _: dict = Depends(require_role("admin", "security_manager", "soc_engineer", "security_analyst"))):
    return get_dashboard_stats(db)

@router.post("/baseline/{employee_id}")
def create_baseline(employee_id: str, _: dict = Depends(require_role("admin", "security_manager", "security_analyst", "soc_engineer"))):
    return generate_baseline(employee_id)
    
@router.post("/anomalies/{employee_id}")
def trigger_anomaly_detection(employee_id: str, db: Session = Depends(get_db), _: dict = Depends(require_role("admin", "security_manager", "soc_engineer", "security_analyst"))):
    anomalies = detect_anomalies(employee_id, db)
    return {"message": "Anomaly detection complete", "anomalies": anomalies}

@router.post("/risk-score/{employee_id}")
def generate_risk_score(employee_id: str, _: dict = Depends(require_role("admin", "security_manager", "security_analyst", "soc_engineer"))):
    result = calculate_risk_score(employee_id)
    return result

@router.get("/anomalies/{employee_id}")
def get_anomaly_evidence(employee_id: str, _: dict = Depends(require_role("admin", "security_manager", "soc_engineer", "security_analyst"))):
    docs = list(db.anomalies.find({"employee_id": employee_id}, {"_id": 0}).sort("detected_at", -1))
    return docs

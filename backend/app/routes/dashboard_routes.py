from fastapi import APIRouter
from app.database import SessionLocal
from app.models import Employee, Alert, Incident
from app.risk_scoring import calculate_risk_score

router = APIRouter(prefix="/dashboard", tags=["Dashboards"])

@router.get("/analyst")
def analyst_dashboard():
    db = SessionLocal()
    try:
        open_alerts = db.query(Alert).filter(Alert.status == "open").count()
        active = db.query(Incident).filter(Incident.status == "investigating").count()
        high_risk = [
            e.employee_id for e in db.query(Employee).all()
            if calculate_risk_score(e.employee_id)["risk_category"] in ("high", "critical")
        ]
        return {
            "open_alerts": open_alerts,
            "active_investigations": active,
            "high_risk_employees": high_risk[:10],
        }
    finally:
        db.close()

@router.get("/soc")
def soc_dashboard():
    db = SessionLocal()
    try:
        return {
            "security_events": 1248,
            "behavioral_anomalies": 86,
            "active_investigations": db.query(Incident).filter(Incident.status != "resolved").count(),
            "threat_intelligence_notes": [
                "Suspicious login detected",
                "Abnormal download activity",
                "Privilege escalation observed"
            ]
        }
    finally:
        db.close()

@router.get("/manager")
def manager_dashboard():
    db = SessionLocal()
    try:
        distribution = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for e in db.query(Employee).all():
            distribution[calculate_risk_score(e.employee_id)["risk_category"]] += 1
        return {
            "total_employees": db.query(Employee).count(),
            "risk_distribution": distribution,
            "risk_trend": [35, 38, 42, 48, 55, 62, 68],
            "compliance_metrics": {
                "policy_compliance": 94,
                "open_findings": 6,
                "resolved_findings": 28
            }
        }
    finally:
        db.close()

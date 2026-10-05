# backend/app/routes/dashboard_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db, mongo_db
from app.models import Alert, Incident, Employee, User
from app.auth import get_current_user, require_role
from app.risk_scoring import calculate_risk_score

router = APIRouter(tags=["Security Dashboards"])

@router.get("/dashboard/analyst")
def analyst_dashboard(
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "security_analyst", "soc_engineer"))
):
    """
    Security Analyst Dashboard: Open alerts, active investigations, and high-risk employees.
    """
    open_alerts = db.query(Alert).filter(Alert.status == "open").count()
    my_incidents = db.query(Incident).filter(Incident.status == "investigating").count()
    
    high_risk_employees = [
        emp.employee_id for emp in db.query(Employee).all()
        if calculate_risk_score(emp.employee_id)["risk_category"] in ("high", "critical")
    ]
    
    return {
        "open_alerts": open_alerts,
        "active_investigations": my_incidents,
        "high_risk_employees": high_risk_employees[:10]
    }

@router.get("/dashboard/soc")
def soc_dashboard(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    SOC Dashboard: Security events, behavioral anomalies count, active investigations, recent threat notes.
    """
    events_count = mongo_db["activity_logs"].count_documents()
    rule_anomalies_count = mongo_db["rule_anomalies"].count_documents()
    ml_anomalies_count = mongo_db["ml_anomalies"].count_documents({"is_anomaly": True})
    active_incidents = db.query(Incident).filter(Incident.status.in_(["open", "investigating"])).count()
    
    recent_alerts = db.query(Alert).order_by(Alert.created_at.desc()).limit(5).all()

    return {
        "total_security_events": events_count,
        "behavioral_anomalies_count": rule_anomalies_count + ml_anomalies_count,
        "active_investigations": active_incidents,
        "threat_intelligence_notes": [
            f"{a.severity.upper()}: {a.title or a.message} ({a.employee_id})"
            for a in recent_alerts
        ]
    }

@router.get("/dashboard/manager")
def manager_dashboard(
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "security_manager"))
):
    """
    Security Manager Dashboard: Organizational risk posture, risk distribution, compliance metrics.
    """
    employees = db.query(Employee).all()
    distribution = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for emp in employees:
        risk = calculate_risk_score(emp.employee_id)
        distribution[risk["risk_category"]] += 1

    total_incidents = db.query(Incident).count()
    resolved_incidents = db.query(Incident).filter(Incident.status == "resolved").count()
    resolution_rate = round((resolved_incidents / max(total_incidents, 1)) * 100, 1)

    return {
        "total_employees": len(employees),
        "distribution": distribution,
        "compliance_score": 96.5,
        "incident_resolution_rate": resolution_rate
    }
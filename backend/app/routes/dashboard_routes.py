from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import User, Employee, Alert, Incident
from app.auth import require_role
from app.mongo_database import db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary")
def get_dashboard_summary(db_session: Session = Depends(get_db), _: dict = Depends(require_role("ADMIN", "SECURITY_MANAGER", "SECURITY_ANALYST", "SOC_ENGINEER"))):
    total_users = db_session.query(User).count()
    monitored_employees = db_session.query(Employee).count()
    active_alerts = db_session.query(Alert).filter(Alert.status == "open").count()
    open_incidents = db_session.query(Incident).filter(Incident.status.in_(["open", "investigating"])).count()
    
    telemetry_events = db.activity_logs.count_documents({})
    
    # Calculate high risk employees from Mongo
    risk_scores = list(db.risk_scores.find({}, {"_id": 0}))
    high_risk_count = sum(1 for r in risk_scores if r.get("score", 0) >= 50)
    
    # Risk distribution
    low = sum(1 for r in risk_scores if r.get("score", 0) < 25)
    medium = sum(1 for r in risk_scores if 25 <= r.get("score", 0) < 50)
    high = sum(1 for r in risk_scores if 50 <= r.get("score", 0) < 75)
    critical = sum(1 for r in risk_scores if r.get("score", 0) >= 75)
    
    # Recent alerts
    recent_alerts = db_session.query(Alert).order_by(Alert.created_at.desc()).limit(10).all()
    
    # Alert severity distribution
    severities = db_session.query(Alert.severity, func.count(Alert.id)).group_by(Alert.severity).all()
    severity_dist = {s.lower(): c for s, c in severities}
    
    # Events today
    from datetime import datetime, timezone, timedelta
    start_of_today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    events_today = db.activity_logs.count_documents({"timestamp": {"$gte": start_of_today}})

    # Recent incidents
    recent_incidents = db_session.query(Incident).order_by(Incident.created_at.desc()).limit(5).all()

    return {
        "total_users": total_users,
        "monitored_employees": monitored_employees,
        "active_alerts": active_alerts,
        "open_incidents": open_incidents,
        "telemetry_events": telemetry_events,
        "events_today": events_today,
        "high_risk_employees": high_risk_count,
        "risk_distribution": {
            "low": low,
            "medium": medium,
            "high": high,
            "critical": critical
        },
        "severity_distribution": severity_dist,
        "recent_alerts": [
            {
                "id": a.id,
                "employee_id": a.employee_id,
                "severity": a.severity,
                "message": a.message,
                "status": a.status,
                "created_at": a.created_at
            } for a in recent_alerts
        ],
        "recent_incidents": [
            {
                "id": i.id,
                "alert_id": i.alert_id,
                "status": i.status,
                "created_at": i.created_at
            } for i in recent_incidents
        ]
    }

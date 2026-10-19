from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.database import get_db
from app.models import Employee, Alert, Incident, RiskScoreHistory, ActivityLog, User, AuditLog
from app.schemas import (
    DashboardSummaryResponse,
    DashboardTrendResponse,
    DashboardTrendPoint,
    ThreatDistributionResponse,
    ThreatCategoryCount,
)
from app.security import get_current_user, require_role
from app.risk_scoring import calculate_risk_score
from app.mongodb import mongo_service
from app.compliance import get_compliance_metrics

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    from app.mongodb import mongo_service
    total_employees = db.query(Employee).count()
    active_monitoring = db.query(Employee).filter(Employee.status == "ACTIVE").count()
    high_risk_employees = db.query(Employee).filter(Employee.risk_score >= 60).count()
    critical_risk_employees = db.query(Employee).filter(Employee.risk_score >= 80).count()
    open_alerts = db.query(Alert).filter(Alert.status == "OPEN").count()
    critical_alerts = db.query(Alert).filter(Alert.status == "OPEN", Alert.severity == "CRITICAL").count()
    total_incidents = db.query(Incident).filter(Incident.status.in_(["OPEN", "INVESTIGATING"])).count()
    total_activities = mongo_service.query_activity_logs(limit=1)["total"]

    return {
        "total_employees": total_employees,
        "active_monitoring": active_monitoring,
        "high_risk_employees": high_risk_employees,
        "critical_risk_employees": critical_risk_employees,
        "open_alerts": open_alerts,
        "critical_alerts": critical_alerts,
        "total_incidents": total_incidents,
        "total_activities_ingested": total_activities,
        "system_status": "OPERATIONAL",
    }


@router.get("/trend", response_model=DashboardTrendResponse)
def get_risk_trend(
    timeframe: str = "7d",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    points = []
    now = datetime.now(timezone.utc)

    if timeframe == "24h":
        # 6 buckets of 4 hours
        for i in range(5, -1, -1):
            bucket_start = now - timedelta(hours=(i + 1) * 4)
            bucket_end = now - timedelta(hours=i * 4)
            label = bucket_end.strftime("%H:%M") if i > 0 else "Live"

            scores = db.query(RiskScoreHistory.score).filter(
                RiskScoreHistory.calculated_at >= bucket_start,
                RiskScoreHistory.calculated_at <= bucket_end,
            ).all()

            if scores:
                avg_score = sum(s[0] for s in scores) / len(scores)
            else:
                emp_scores = [e.risk_score for e in db.query(Employee.risk_score).all()]
                avg_score = (sum(emp_scores) / len(emp_scores)) if emp_scores else 22.0

            alert_count = db.query(Alert).filter(
                Alert.created_at >= bucket_start,
                Alert.created_at <= bucket_end,
            ).count()

            points.append(DashboardTrendPoint(
                date=label,
                avg_risk=round(avg_score, 1),
                alert_count=alert_count,
            ))

    elif timeframe == "30d":
        # 6 buckets of 5 days
        for i in range(5, -1, -1):
            bucket_start = now - timedelta(days=(i + 1) * 5)
            bucket_end = now - timedelta(days=i * 5)
            label = f"-{i*5}d" if i > 0 else "Live"

            scores = db.query(RiskScoreHistory.score).filter(
                RiskScoreHistory.calculated_at >= bucket_start,
                RiskScoreHistory.calculated_at <= bucket_end,
            ).all()

            if scores:
                avg_score = sum(s[0] for s in scores) / len(scores)
            else:
                emp_scores = [e.risk_score for e in db.query(Employee.risk_score).all()]
                avg_score = (sum(emp_scores) / len(emp_scores)) if emp_scores else 22.0

            alert_count = db.query(Alert).filter(
                Alert.created_at >= bucket_start,
                Alert.created_at <= bucket_end,
            ).count()

            points.append(DashboardTrendPoint(
                date=label,
                avg_risk=round(avg_score, 1),
                alert_count=alert_count,
            ))

    else:
        # Default 7d
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i in range(6, -1, -1):
            day_date = now - timedelta(days=i)
            day_label = day_names[day_date.weekday()]
            if i == 0:
                day_label = f"{day_label} (Live)"

            start_of_day = day_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = day_date.replace(hour=23, minute=59, second=59, microsecond=999999)

            scores = db.query(RiskScoreHistory.score).filter(
                RiskScoreHistory.calculated_at >= start_of_day,
                RiskScoreHistory.calculated_at <= end_of_day,
            ).all()

            if scores:
                score_vals = [s[0] for s in scores]
                avg_score = sum(score_vals) / len(score_vals)
            else:
                emp_scores = [e.risk_score for e in db.query(Employee.risk_score).all()]
                avg_score = (sum(emp_scores) / len(emp_scores)) if emp_scores else 22.0

            alert_count = db.query(Alert).filter(
                Alert.created_at >= start_of_day,
                Alert.created_at <= end_of_day,
            ).count()

            points.append(DashboardTrendPoint(
                date=day_label,
                avg_risk=round(avg_score, 1),
                alert_count=alert_count,
            ))

    return DashboardTrendResponse(points=points)


@router.get("/public-overview")
def get_public_telemetry_overview(db: Session = Depends(get_db)):
    """Public unauthenticated telemetry summary for landing page live graph and security posture."""
    from app.mongodb import mongo_service
    total_employees = db.query(Employee).count()
    active_monitoring = db.query(Employee).filter(Employee.status == "ACTIVE").count()
    high_risk_count = db.query(Employee).filter(Employee.risk_score >= 60).count()
    total_activities = mongo_service.query_activity_logs(limit=1)["total"]
    
    # 7-day trend
    now = datetime.now(timezone.utc)
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    points = []
    for i in range(6, -1, -1):
        day_date = now - timedelta(days=i)
        day_label = day_names[day_date.weekday()]
        if i == 0:
            day_label = f"{day_label} (Live)"
        start_of_day = day_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = day_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        scores = db.query(RiskScoreHistory.score).filter(
            RiskScoreHistory.calculated_at >= start_of_day,
            RiskScoreHistory.calculated_at <= end_of_day,
        ).all()

        if scores:
            avg_score = sum(s[0] for s in scores) / len(scores)
        else:
            emp_scores = [e.risk_score for e in db.query(Employee.risk_score).all()]
            avg_score = (sum(emp_scores) / len(emp_scores)) if emp_scores else 22.0

        alert_count = db.query(Alert).filter(
            Alert.created_at >= start_of_day,
            Alert.created_at <= end_of_day,
        ).count()

        points.append({
            "date": day_label,
            "avg_risk": round(avg_score, 1),
            "alert_count": alert_count,
        })

    return {
        "status": "ONLINE",
        "total_employees": total_employees,
        "active_monitoring": active_monitoring,
        "high_risk_count": high_risk_count,
        "total_activities": total_activities,
        "trend_points": points,
    }



@router.get("/threat-distribution", response_model=ThreatDistributionResponse)
def get_threat_distribution(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    categories = [
        "DATA_EXFILTRATION",
        "PRIVILEGE_ESCALATION",
        "OFF_HOURS_ACCESS",
        "MASS_DOWNLOAD",
        "UNUSUAL_LOGIN",
        "SENSITIVE_RESOURCE_ACCESS",
    ]

    total_alerts = db.query(Alert).count()
    results = []

    for cat in categories:
        count = db.query(Alert).filter(Alert.category == cat).count()
        pct = round((count / total_alerts) * 100, 1) if total_alerts > 0 else 0.0
        results.append(ThreatCategoryCount(
            category=cat.replace("_", " ").title(),
            count=count,
            percentage=pct,
        ))

    return ThreatDistributionResponse(categories=results)


@router.get("/analyst")
def analyst_dashboard(
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin", "security_analyst")),
):
    """
    Security Analyst Operational Dashboard (Day 29).
    Returns open alerts count, personal investigation queue, open incidents,
    and top-risk employees with calculated risk score breakdowns.
    """
    my_id = 1
    if user and str(user.get("sub", "")).isdigit():
        my_id = int(user["sub"])

    open_alerts = db.query(Alert).filter(Alert.status.in_(["open", "OPEN"])).count()
    my_queue = db.query(Alert).filter(
        Alert.assigned_to == my_id,
        Alert.status.in_(["in_progress", "IN_PROGRESS", "open", "OPEN"])
    ).count()
    open_incidents = db.query(Incident).filter(
        Incident.status.in_(["open", "OPEN", "investigating", "INVESTIGATING"])
    ).count()

    # Aggregate top flagged employees from anomaly telemetry
    all_anomalies = mongo_service.get_anomalies(limit=3000)
    emp_flags: Dict[str, int] = defaultdict(int)
    for a in all_anomalies:
        emp_code = a.get("employee_id")
        if emp_code:
            emp_flags[emp_code] += 1

    top_flagged = sorted(emp_flags.items(), key=lambda x: x[1], reverse=True)[:5]

    top_risk = []
    for emp_id, count in top_flagged:
        emp_record = db.query(Employee).filter(Employee.employee_id == emp_id).first()
        top_risk.append({
            "employee_id": emp_id,
            "employee_name": emp_record.name if emp_record else emp_id,
            "department": emp_record.department if emp_record else "General",
            "flags": count,
            "risk": calculate_risk_score(emp_id, db),
        })

    return {
        "open_alerts": open_alerts,
        "my_investigation_queue": my_queue,
        "open_incidents": open_incidents,
        "top_risk_employees": top_risk,
    }


@router.get("/soc")
def soc_dashboard(
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin", "soc_engineer")),
):
    """
    SOC Operational Engineering Dashboard (Day 29).
    Returns alerts grouped by severity, 7-day anomaly activity trend,
    and count of active investigations.
    Restricted to SOC Engineers and Administrators (Analysts blocked with 403).
    """
    raw_sev = db.query(Alert.severity, func.count(Alert.id)).filter(
        ~Alert.status.in_(["resolved", "RESOLVED", "closed", "CLOSED"])
    ).group_by(Alert.severity).all()

    severities = ["informational", "low", "medium", "high", "critical"]
    alerts_by_severity = {s: 0 for s in severities}
    for sev, count in raw_sev:
        if sev:
            alerts_by_severity[str(sev).lower()] = count

    # Anomaly trend for the last 7 calendar days
    now = datetime.now(timezone.utc)
    all_anomalies = mongo_service.get_anomalies(limit=5000)
    daily_counts: Dict[str, int] = defaultdict(int)

    for a in all_anomalies:
        details = a.get("details") if isinstance(a.get("details"), dict) else {}
        d_str = details.get("date") or a.get("date")
        if not d_str:
            ts = str(a.get("detected_at") or a.get("detection_timestamp") or a.get("timestamp") or "").strip()
            if len(ts) >= 10:
                d_str = ts[:10]
        if d_str:
            daily_counts[str(d_str)[:10]] += 1

    anomalies_last_7_days = []
    for day_offset in range(6, -1, -1):
        target_date = (now - timedelta(days=day_offset)).strftime("%Y-%m-%d")
        anomalies_last_7_days.append({
            "date": target_date,
            "count": daily_counts.get(target_date, 0),
        })

    active_investigations = db.query(Incident).filter(
        Incident.status.in_(["investigating", "INVESTIGATING", "open", "OPEN"])
    ).count()

    return {
        "alerts_by_severity": alerts_by_severity,
        "anomalies_last_7_days": anomalies_last_7_days,
        "active_investigations": active_investigations,
    }


@router.get("/manager/compliance")
def get_manager_compliance_dashboard(
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin", "security_manager")),
):
    """
    Security Manager Compliance Dashboard (Day 31-32).
    Returns SLA metrics, MTTR, MTTI, incident resolution rate, and compliance posture.
    Restricted to Admins and Security Managers (Analysts and SOC Engineers receive 403).
    """
    return get_compliance_metrics(db)


@router.get("/admin")
def get_admin_dashboard(
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin")),
):
    """
    Administrator Platform Overview (Day 31-32).
    Returns platform user distribution, monitored employee metrics, and departments.
    Strictly restricted to Admin role.
    """
    total_platform_users = db.query(User).count()
    roles = db.query(User.role, func.count(User.id)).group_by(User.role).all()
    users_by_role = {str(r[0]): r[1] for r in roles if r[0]}
    employees_monitored = db.query(Employee).count()
    distinct_departments = db.query(func.distinct(Employee.department)).filter(
        Employee.department.isnot(None),
        Employee.department != "",
    ).count()

    return {
        "total_platform_users": total_platform_users,
        "users_by_role": users_by_role,
        "employees_monitored": employees_monitored,
        "distinct_departments_count": distinct_departments,
    }


@router.get("/admin/platform-analytics")
def get_admin_platform_analytics(
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin")),
):
    """
    Platform Data Analytics & Ingestion Health (Day 31-32).
    Returns telemetry ingestion totals, rule vs ML anomalies breakdown,
    and zero-guarded overall anomaly rate.
    Strictly restricted to Admin role.
    """
    total_logs = mongo_service.query_activity_logs(limit=1).get("total", 0)
    anomalies = mongo_service.get_anomalies(limit=10000)

    rule_anomalies = 0
    ml_anomalies = 0
    for a in anomalies:
        method = str(a.get("detection_method") or "").lower()
        atype = str(a.get("anomaly_type") or "").upper()
        if method == "machine_learning" or atype in ["ML_ANOMALY", "ISOLATION_FOREST_OUTLIER"]:
            ml_anomalies += 1
        else:
            rule_anomalies += 1

    total_anomalies = rule_anomalies + ml_anomalies
    overall_anomaly_rate = round((total_anomalies / total_logs) * 100.0, 2) if total_logs > 0 else 0.0

    return {
        "total_logs": total_logs,
        "rule_anomalies": rule_anomalies,
        "ml_anomalies": ml_anomalies,
        "total_anomalies": total_anomalies,
        "overall_anomaly_rate_percent": overall_anomaly_rate,
        "status": "HEALTHY" if overall_anomaly_rate < 15.0 else "ELEVATED_RISK",
    }


@router.get("/admin/audit-log")
def get_admin_audit_log(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin")),
):
    """
    Administrator Audit Log Feed (Day 31-32).
    Returns system action audit trail in reverse chronological order.
    Strictly restricted to Admin role.
    """
    logs = db.query(AuditLog).order_by(
        AuditLog.timestamp.desc(),
        AuditLog.id.desc(),
    ).offset(offset).limit(limit).all()

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "user_email": log.user_email,
            "action": log.action,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "details": log.details,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
        }
        for log in logs
    ]


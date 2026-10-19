"""
ITBIS Alert Management & Escalation Engine (Milestone 3: Days 27-28)
AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform.

Capabilities:
1. Alert Generation from Anomalies:
   - Scans unalerted high-confidence anomalies (severity in ["critical", "high", "medium"]).
   - Auto-generates formal Alert records linked to the corresponding employee.
   - Sets 'alert_generated': True to prevent duplicate alerts on repeated execution runs.
2. Escalation Workflow:
   - Evaluates aging open alerts against severity-based SLA thresholds (critical: 2h, high: 8h, medium: 24h).
   - Automatically escalates stale alerts to 'escalated' status and 'critical' severity.
   - Records escalated_at timestamp for SLA tracking and MTTR metrics.
3. Organization-wide Risk Analytics:
   - Aggregates employee risk distributions and alert statuses across the enterprise.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.models import Alert, Employee, Incident
from app.mongodb import mongo_service
from app.risk_scoring import calculate_risk_score
from app.notifications import notify_on_critical_alert

logger = logging.getLogger("itbis.alerting")

SEVERITY_MESSAGES = {
    "critical": "Critical insider risk detected - immediate review required",
    "high": "High-severity anomaly detected requiring analyst attention",
    "medium": "Moderate anomaly detected - review recommended",
}

ESCALATION_THRESHOLDS_HOURS = {
    "critical": 2,
    "high": 8,
    "medium": 24,
}


def generate_alerts_from_anomalies(db: Session) -> int:
    """
    Scans for high-severity anomalies that have not yet generated a formal alert.
    Ensures idempotency using the 'alert_generated' flag so repeated calls create 0 duplicates.
    """
    created_count = 0
    now = datetime.now(timezone.utc)
    new_alerts = []

    # Fetch anomalies across storage tiers
    all_anomalies = mongo_service.get_anomalies(limit=5000)

    for anomaly in all_anomalies:
        sev = str(anomaly.get("severity") or "").strip().lower()
        if sev not in {"critical", "high", "medium"}:
            continue

        # Skip if an alert has already been generated
        if anomaly.get("alert_generated") is True:
            continue

        emp_code = str(anomaly.get("employee_id") or "").strip()
        if not emp_code:
            continue

        employee = db.query(Employee).filter(
            or_(
                Employee.employee_id == emp_code,
                Employee.id == int(emp_code) if emp_code.isdigit() else False,
            )
        ).first()

        if not employee:
            continue

        anom_type = str(anomaly.get("anomaly_type") or "ANOMALY_DETECTION").strip()
        msg = SEVERITY_MESSAGES.get(sev, f"Anomaly detected: {anom_type}")
        if anomaly.get("description"):
            msg = f"{msg} — {anomaly.get('description')}"

        alert = Alert(
            employee_id=employee.id,
            title=f"Anomaly Alert: {anom_type.replace('_', ' ').title()}",
            message=msg,
            category=anom_type,
            severity=sev,
            status="open",
            risk_score=employee.risk_score or 50,
            created_at=now,
        )
        db.add(alert)
        new_alerts.append(alert)

        # Mark anomaly document as alerted in MongoDB / persistent dev file
        anomaly_id = anomaly.get("_id") or anomaly.get("id")
        anomaly["alert_generated"] = True
        mongo_service.mark_anomaly_alerted(anomaly_id=anomaly_id, anomaly_doc=anomaly)

        created_count += 1

    if created_count > 0:
        db.commit()
        for a in new_alerts:
            if str(a.severity).lower() == "critical":
                notify_on_critical_alert(a, db)

    return created_count


def escalate_stale_alerts(db: Session, thresholds: Optional[Dict[str, float]] = None) -> List[int]:
    """
    Finds open alerts exceeding SLA thresholds and escalates them to 'critical' and 'escalated' status.
    """
    threshold_map = thresholds or ESCALATION_THRESHOLDS_HOURS
    escalated_ids: List[int] = []
    now = datetime.now(timezone.utc)
    escalated_alerts = []

    for severity, hours in threshold_map.items():
        cutoff = now - timedelta(hours=hours)

        stale_alerts = db.query(Alert).filter(
            Alert.status.in_(["open", "OPEN"]),
            Alert.severity.ilike(severity),
            Alert.created_at < cutoff,
        ).all()

        for alert in stale_alerts:
            alert.status = "escalated"
            if alert.severity.lower() != "critical":
                alert.severity = "critical"
            alert.escalated_at = now
            escalated_ids.append(alert.id)
            escalated_alerts.append(alert)

    if escalated_ids:
        db.commit()
        for a in escalated_alerts:
            notify_on_critical_alert(a, db)

    return escalated_ids


def get_risk_overview_analytics(db: Session) -> Dict[str, Any]:
    """
    Aggregates organization-wide security risk posture and alert statistics.
    """
    employees = db.query(Employee).all()
    level_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}

    for emp in employees:
        risk = calculate_risk_score(emp.employee_id, db)
        lvl = risk.get("risk_level", "Low")
        if lvl in level_counts:
            level_counts[lvl] += 1
        else:
            level_counts["Low"] += 1

    open_alerts = db.query(Alert).filter(Alert.status.in_(["open", "OPEN"])).count()
    escalated_alerts = db.query(Alert).filter(Alert.status.in_(["escalated", "ESCALATED"])).count()

    return {
        "total_employees": len(employees),
        "risk_level_distribution": level_counts,
        "open_alerts": open_alerts,
        "escalated_alerts": escalated_alerts,
    }

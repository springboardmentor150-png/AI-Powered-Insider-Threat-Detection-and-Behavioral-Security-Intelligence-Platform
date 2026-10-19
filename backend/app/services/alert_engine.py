from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import Employee, ActivityLog, Alert, Notification, User


def evaluate_and_trigger_alerts(
    db: Session,
    employee: Employee,
    activity: ActivityLog,
    anomalies: List[Dict[str, Any]],
    risk_score: int,
) -> Optional[Alert]:
    if not anomalies or risk_score < 60:
        return None

    # Determine primary category and title
    categories = [a.get("category", "ANOMALOUS_BEHAVIOR") for a in anomalies]
    primary_category = categories[0] if categories else "ANOMALOUS_BEHAVIOR"

    if any(a.get("anomaly_type") == "MASS_DOWNLOAD_EXFILTRATION" for a in anomalies):
        primary_category = "DATA_EXFILTRATION"
        title = f"Mass data exfiltration trigger: {activity.action} on {activity.resource}"
    elif any(a.get("anomaly_type") == "PRIVILEGE_ESCALATION" for a in anomalies):
        primary_category = "PRIVILEGE_ESCALATION"
        title = f"Privilege escalation vector: {activity.action}"
    elif any(a.get("anomaly_type") == "OFF_HOURS_ACCESS" for a in anomalies) and any(a.get("anomaly_type") == "UNUSUAL_DEVICE" for a in anomalies):
        primary_category = "OFF_HOURS_ACCESS"
        title = f"Off-hours untrusted node access by {employee.name}"
    elif any(a.get("anomaly_type") == "SENSITIVE_RESOURCE_ACCESS" for a in anomalies):
        primary_category = "SENSITIVE_RESOURCE_ACCESS"
        title = f"Sensitive repository access anomaly: {activity.resource}"
    else:
        title = f"Behavioral anomaly threshold breached by {employee.name} ({risk_score}/100)"

    severity = "CRITICAL" if risk_score >= 80 or any(a.get("severity") == "CRITICAL" for a in anomalies) else "HIGH"

    # Detail composite message
    anomaly_bullets = "\n".join([f"• [{a.get('severity')}] {a.get('description')}" for a in anomalies])
    message = (
        f"Automated behavioral sensor detected high-risk activity for monitored subject {employee.name} ({employee.employee_id}).\n"
        f"Activity: {activity.action} targeting '{activity.resource}' (Type: {activity.activity_type}).\n"
        f"Risk Score: {risk_score}/100 ({employee.risk_level}).\n"
        f"Detected Signals:\n{anomaly_bullets}"
    )

    # Deduplication check: check if an identical open alert for this employee and category exists in the last 15 minutes
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=15)
    existing_alert = db.query(Alert).filter(
        Alert.employee_id == employee.id,
        Alert.category == primary_category,
        Alert.status == "OPEN",
        Alert.created_at >= cutoff,
    ).first()

    if existing_alert:
        existing_alert.risk_score = max(existing_alert.risk_score, risk_score)
        existing_alert.message = message
        db.commit()
        db.refresh(existing_alert)
        return existing_alert

    # Create new Alert
    alert = Alert(
        employee_id=employee.id,
        title=title,
        message=message,
        category=primary_category,
        severity=severity,
        status="OPEN",
        risk_score=risk_score,
        created_at=datetime.now(timezone.utc),
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    # Create SOC Notification
    analysts = db.query(User).all()
    for user in analysts:
        notif = Notification(
            user_id=user.id,
            title=f"[{severity}] {title}",
            message=f"Subject {employee.name} ({employee.employee_id}) generated risk score {risk_score}.",
            alert_id=alert.id,
            is_read=False,
            created_at=datetime.now(timezone.utc),
        )
        db.add(notif)
    db.commit()

    return alert


def trigger_automated_alert_if_warranted(
    db: Session,
    employee_id: int,
    title: str,
    message: str,
    category: str = "DATA_EXFILTRATION",
    severity: str = "HIGH",
    risk_score: int = 70,
) -> Optional[Alert]:
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=15)
    existing_alert = db.query(Alert).filter(
        Alert.employee_id == employee_id,
        Alert.category == category,
        Alert.status == "OPEN",
        Alert.created_at >= cutoff,
    ).first()

    if existing_alert:
        existing_alert.risk_score = max(existing_alert.risk_score, risk_score)
        existing_alert.message = message
        db.commit()
        db.refresh(existing_alert)
        return existing_alert

    alert = Alert(
        employee_id=employee_id,
        title=title,
        message=message,
        category=category,
        severity=severity,
        status="OPEN",
        risk_score=risk_score,
        created_at=datetime.now(timezone.utc),
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    # Notify analysts
    analysts = db.query(User).all()
    for user in analysts:
        notif = Notification(
            user_id=user.id,
            title=f"[{severity}] {title}",
            message=message[:150],
            alert_id=alert.id,
            is_read=False,
            created_at=datetime.now(timezone.utc),
        )
        db.add(notif)
    db.commit()

    return alert


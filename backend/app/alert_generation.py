"""
ITBIS Alert Generation Engine.

Day 27:
- Generate alerts from rule anomalies
- Generate alerts from ML anomalies
- Prevent duplicate alerts
"""

from datetime import datetime

from app.database import mongo_db
from app.models import Alert, Employee


def create_alert_if_new(
    db,
    employee_id: str,
    severity: str,
    message: str,
    incident_id: int | None = None,
):
    """
    Create an alert only when an equivalent unresolved alert
    does not already exist.

    Returns:
        (alert, created)
    """

    employee = (
        db.query(Employee)
        .filter(Employee.employee_id == employee_id)
        .first()
    )

    if not employee:
        return None, False

    existing = (
        db.query(Alert)
        .filter(
            Alert.employee_id == employee.id,
            Alert.message == message,
            Alert.status != "resolved",
        )
        .first()
    )

    if existing:
        return existing, False

    alert = Alert(
        employee_id=employee.id,
        incident_id=incident_id,
        severity=severity,
        message=message,
        status="open",
        created_at=datetime.utcnow(),
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return alert, True


def generate_alerts_from_anomalies(db):
    """
    Scan MongoDB anomaly collections and generate PostgreSQL alerts.
    """

    generated = 0
    skipped = 0

    # ==================================================
    # Rule-based anomalies
    # ==================================================

    rule_anomalies = mongo_db["rule_anomalies"].find({})

    for anomaly in rule_anomalies:

        employee_id = anomaly.get("employee_id")

        if not employee_id:
            continue

        severity = anomaly.get(
            "severity",
            "medium"
        )

        indicator = anomaly.get(
            "indicator",
            anomaly.get(
                "anomaly_type",
                "rule anomaly"
            )
        )

        message = (
            f"Rule anomaly detected: {indicator}"
        )

        _, created = create_alert_if_new(
            db=db,
            employee_id=employee_id,
            severity=severity,
            message=message,
        )

        if created:
            generated += 1
        else:
            skipped += 1

    # ==================================================
    # ML anomalies
    # ==================================================

    ml_anomalies = mongo_db["ml_anomalies"].find({
        "prediction": -1
    })

    for anomaly in ml_anomalies:

        employee_id = anomaly.get("employee_id")

        if not employee_id:
            continue

        message = (
            "ML anomaly detected by behavioral model"
        )

        _, created = create_alert_if_new(
            db=db,
            employee_id=employee_id,
            severity="high",
            message=message,
        )

        if created:
            generated += 1
        else:
            skipped += 1

    return {
        "generated": generated,
        "skipped": skipped,
        "message": "Alert generation completed",
    }
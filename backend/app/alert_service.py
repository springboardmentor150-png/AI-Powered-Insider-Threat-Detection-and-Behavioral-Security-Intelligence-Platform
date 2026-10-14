
"""Automatic alert generation from existing ML anomaly records."""

from sqlalchemy.orm import Session

from app.models import Alert, Employee, Incident
from app.mongo import ml_anomalies, rule_anomalies
from app.risk_scoring import calculate_risk_score


def generate_alerts(db: Session) -> dict:
    """Create incidents and alerts for qualifying, unduplicated anomalies.

    An incident and its alert are created only when the employee's
    current risk level is High or Critical.
    """

    created_incidents = 0
    created_alerts = 0
    skipped_not_anomaly = 0
    skipped_low_risk = 0
    skipped_duplicate = 0
    skipped_unknown_employee = 0

    # Read both anomaly sources using their actual employee_code field.
    sources = [
        ("ml", ml_anomalies),
        ("rule", rule_anomalies),
    ]

    for source_name, collection in sources:
        records = collection.find({"is_anomaly": True})

        for record in records:
            employee_code = record.get("employee_code")

            if not employee_code:
                skipped_unknown_employee += 1
                continue

            employee = (
                db.query(Employee)
                .filter(Employee.employee_code == employee_code)
                .first()
            )

            if employee is None:
                skipped_unknown_employee += 1
                continue

            # Identify this specific anomaly using its source and date.
            anomaly_date = str(
                record.get("date")
                or record.get("detected_at")
                or "unknown"
            )
            incident_type = f"AUTO_{source_name.upper()}_ANOMALY"

            description = (
                f"Automatically generated from {source_name} anomaly "
                f"data for {employee_code} on {anomaly_date}. "
                "Review the anomaly evidence before taking action."
            )

            # Deduplicate by employee, anomaly type, and date.
            existing_incident = (
                db.query(Incident)
                .filter(
                    Incident.employee_id == employee.id,
                    Incident.incident_type == incident_type,
                    Incident.description == description,
                )
                .first()
            )

            if existing_incident:
                skipped_duplicate += 1
                continue

            try:
                risk_result = calculate_risk_score(employee_code, db)
            except ValueError:
                skipped_unknown_employee += 1
                continue

            risk_level = risk_result["risk_level"]

            if risk_level not in {"High", "Critical"}:
                skipped_low_risk += 1
                continue

            incident = Incident(
                employee_id=employee.id,
                incident_type=incident_type,
                description=description,
                severity=risk_level.lower(),
                status="open",
            )

            try:
                db.add(incident)
                db.flush()

                alert = Alert(
                    incident_id=incident.id,
                    employee_id=employee.id,
                    alert_type=incident_type,
                    message=(
                        f"{risk_level} risk employee {employee_code} "
                        f"has a qualifying {source_name} anomaly "
                        f"dated {anomaly_date}."
                    ),
                    severity=risk_level.lower(),
                    status="open",
                )

                db.add(alert)
                db.commit()

                created_incidents += 1
                created_alerts += 1

            except Exception:
                db.rollback()
                raise

    return {
        "created_incidents": created_incidents,
        "created_alerts": created_alerts,
        "skipped_not_anomaly": skipped_not_anomaly,
        "skipped_low_risk": skipped_low_risk,
        "skipped_duplicate": skipped_duplicate,
        "skipped_unknown_employee": skipped_unknown_employee,
        "message": (
            "Alert generation completed. Review generated incidents "
            "and alerts before taking action."
        ),
    }


from datetime import datetime, timezone
from typing import Any

from .models import Employee, Incident
from .mongo import activity_logs, rule_anomalies, ml_anomalies


def _to_iso(value: Any) -> str | None:
    """Convert datetime values into ISO 8601 strings."""
    if value is None:
        return None

    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()

    return str(value)


def _timestamp_key(value: Any) -> float:
    """Return a sortable Unix timestamp; unknown dates sort last."""
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.timestamp()

    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.timestamp()
        except ValueError:
            pass

    return float("-inf")


def get_incident_timeline(employee_code: str, db) -> dict:
    """
    Combine an employee's activity, rule anomalies, ML anomalies,
    and PostgreSQL incidents into one chronological timeline.
    """
    employee = (
        db.query(Employee)
        .filter(Employee.employee_code == employee_code)
        .first()
    )

    if employee is None:
        raise ValueError(f"Employee '{employee_code}' was not found")

    timeline = []

    # Activity logs from MongoDB.
    for document in activity_logs.find(
        {"employee_code": employee_code}
    ):
        timestamp = document.get("timestamp")
        timeline.append(
            {
                "event_id": str(document.get("_id")),
                "event_type": "activity",
                "timestamp": _to_iso(timestamp),
                "severity": None,
                "title": str(document.get("event_type", "Activity")),
                "description": (
                    f"Source: {document.get('source', 'Unknown')}; "
                    f"Application: {document.get('application') or 'N/A'}"
                ),
                "details": {
                    key: value
                    for key, value in document.items()
                    if key != "_id"
                },
                "_sort_timestamp": _timestamp_key(timestamp),
            }
        )

    # Rule-based anomalies from MongoDB.
    for document in rule_anomalies.find(
        {"employee_code": employee_code}
    ):
        timestamp = document.get("detected_at")
        indicator = document.get("indicator", "Anomaly")

        timeline.append(
            {
                "event_id": str(document.get("_id")),
                "event_type": "rule_anomaly",
                "timestamp": _to_iso(timestamp),
                "severity": document.get("severity"),
                "title": str(indicator),
                "description": (
                    f"Rule-based anomaly detected for indicator: {indicator}"
                ),
                "details": {
                    key: value
                    for key, value in document.items()
                    if key != "_id"
                },
                "_sort_timestamp": _timestamp_key(timestamp),
            }
        )

    # ML anomaly documents represent employee-day results.
    for document in ml_anomalies.find(
        {"employee_code": employee_code, "is_anomaly": True}
    ):
        timestamp = document.get("detected_at") or document.get("date")

        timeline.append(
            {
                "event_id": str(document.get("_id")),
                "event_type": "ml_anomaly",
                "timestamp": _to_iso(timestamp),
                "severity": None,
                "title": "Isolation Forest anomaly",
                "description": (
                    "Machine-learning model flagged an unusual employee-day pattern."
                ),
                "details": {
                    key: value
                    for key, value in document.items()
                    if key != "_id"
                },
                "_sort_timestamp": _timestamp_key(timestamp),
            }
        )

    # Incidents from PostgreSQL.
    incidents = (
        db.query(Incident)
        .filter(Incident.employee_id == employee.id)
        .all()
    )

    for incident in incidents:
        timestamp = incident.created_at

        timeline.append(
            {
                "event_id": str(incident.id),
                "event_type": "incident",
                "timestamp": _to_iso(timestamp),
                "severity": incident.severity,
                "title": incident.incident_type,
                "description": incident.description or "",
                "details": {
                    "status": incident.status,
                    "incident_id": incident.id,
                },
                "_sort_timestamp": _timestamp_key(timestamp),
            }
        )

    # Newest events first. The internal sort key is not returned.
    timeline.sort(
        key=lambda item: item["_sort_timestamp"],
        reverse=True,
    )

    for item in timeline:
        item.pop("_sort_timestamp", None)

    return {
        "employee_code": employee.employee_code,
        "employee_name": employee.name,
        "total_events": len(timeline),
        "timeline": timeline,
    }

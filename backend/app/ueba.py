
"""User and Entity Behavior Analytics (UEBA) services for ITBIS."""

from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import Employee
from app.mongo import ml_anomalies, rule_anomalies
from app.risk_scoring import calculate_risk_score


def get_peer_group_comparison(
    employee_code: str,
    db: Session,
) -> dict | None:
    """Compare an employee's risk score with others in their department."""
    employee = (
        db.query(Employee)
        .filter(Employee.employee_code == employee_code)
        .first()
    )

    if employee is None:
        return None

    employee_score = calculate_risk_score(employee_code, db)["risk_score"]

    peers = (
        db.query(Employee)
        .filter(
            Employee.department == employee.department,
            Employee.employee_code != employee_code,
        )
        .all()
    )

    if not peers:
        return {
            "employee_code": employee_code,
            "department": employee.department,
            "employee_score": employee_score,
            "peer_count": 0,
            "department_avg_score": None,
            "deviation_from_peers": None,
            "peer_percentile": None,
            "note": "No peers found in this department for comparison.",
        }

    peer_scores = [
        calculate_risk_score(peer.employee_code, db)["risk_score"]
        for peer in peers
    ]

    peer_average = sum(peer_scores) / len(peer_scores)
    percentile = (
        sum(score < employee_score for score in peer_scores)
        / len(peer_scores)
        * 100
    )

    return {
        "employee_code": employee_code,
        "department": employee.department,
        "employee_score": employee_score,
        "peer_count": len(peer_scores),
        "department_avg_score": round(peer_average, 2),
        "deviation_from_peers": round(employee_score - peer_average, 2),
        "peer_percentile": round(percentile, 2),
        "interpretation": (
            "A positive deviation means this employee's risk score is "
            "above the department average. Peer comparison alone does "
            "not establish malicious behavior."
        ),
    }


def compare_to_peers(db: Session, employee_id: str) -> dict:
    """Compare employee risk to department peers matching Milestone 3 handout."""
    res = get_peer_group_comparison(employee_id, db)
    if res is None:
        return {"employee_id": employee_id, "note": "Employee not found"}
    if res.get("peer_count", 0) == 0:
        return {"employee_id": employee_id, "note": "No peers in department for comparison"}
    return {
        "employee_id": employee_id,
        "employee_score": res["employee_score"],
        "department_avg_score": res["department_avg_score"],
        "deviation_from_peers": res["deviation_from_peers"],
        "peer_count": res["peer_count"],
    }


def get_risk_trend(
    employee_code: str,
    days: int = 30,
) -> list[dict]:
    """Return a complete daily anomaly-count series, including zero days."""
    if days < 1 or days > 365:
        raise ValueError("days must be between 1 and 365")

    today = datetime.now(timezone.utc).date()
    start_day = today - timedelta(days=days - 1)

    # Use UTC day boundaries for MongoDB datetime fields.
    start_datetime = datetime.combine(
        start_day, datetime.min.time(), tzinfo=timezone.utc
    )
    end_datetime = datetime.combine(
        today + timedelta(days=1),
        datetime.min.time(),
        tzinfo=timezone.utc,
    )

    daily_counts: dict[str, int] = {}

    for offset in range(days):
        day = start_day + timedelta(days=offset)
        daily_counts[day.isoformat()] = 0

    # Rule anomalies use detected_at, a BSON datetime field.
    rule_records = rule_anomalies.find(
        {
            "employee_code": employee_code,
            "detected_at": {
                "$gte": start_datetime,
                "$lt": end_datetime,
            },
        },
        {"_id": 0, "detected_at": 1},
    )

    for record in rule_records:
        timestamp = record.get("detected_at")
        if isinstance(timestamp, datetime):
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            day_key = timestamp.astimezone(timezone.utc).date().isoformat()
            if day_key in daily_counts:
                daily_counts[day_key] += 1

    # ML anomalies use date as YYYY-MM-DD and store detection time separately.
    ml_records = ml_anomalies.find(
        {
            "employee_code": employee_code,
            "date": {
                "$gte": start_day.isoformat(),
                "$lte": today.isoformat(),
            },
            "is_anomaly": True,
        },
        {"_id": 0, "date": 1},
    )

    for record in ml_records:
        event_date = record.get("date")
        if isinstance(event_date, str) and event_date in daily_counts:
            daily_counts[event_date] += 1
        elif isinstance(event_date, date):
            day_key = event_date.isoformat()
            if day_key in daily_counts:
                daily_counts[day_key] += 1

    return [
        {"date": day, "anomaly_count": count}
        for day, count in daily_counts.items()
    ]


def get_trend_direction(employee_code: str) -> dict:
    """Compare two seven-day windows to classify a 14-day trend."""
    trend = get_risk_trend(employee_code, days=14)

    first_week = trend[:7]
    second_week = trend[7:]

    first_average = sum(
        item["anomaly_count"] for item in first_week
    ) / len(first_week)

    second_average = sum(
        item["anomaly_count"] for item in second_week
    ) / len(second_week)

    if second_average > first_average * 1.3:
        direction = "increasing"
    elif (
        first_average > 0
        and second_average < first_average * 0.7
    ):
        direction = "decreasing"
    elif first_average == 0 and second_average > 0:
        direction = "increasing"
    else:
        direction = "stable"

    return {
        "employee_code": employee_code,
        "period_days": 14,
        "first_week_average": round(first_average, 2),
        "second_week_average": round(second_average, 2),
        "direction": direction,
        "interpretation": (
            "This direction describes changes in recorded anomaly counts; "
            "it is not a prediction that an employee will commit a threat."
        ),
    }

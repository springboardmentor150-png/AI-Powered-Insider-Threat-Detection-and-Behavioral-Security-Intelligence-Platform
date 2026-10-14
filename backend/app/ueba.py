"""
ITBIS UEBA Intelligence Workflows.

Day 23:
- Peer group comparison
- Department average
- Deviation from peers

Day 24:
- Day-by-day anomaly trend
- Trend direction
"""

from datetime import datetime, timedelta

from app.database import mongo_db
from app.models import Employee
from app.risk_scoring import calculate_risk_score


def get_peer_group_comparison(employee_id: str, db) -> dict | None:
    """
    Compare an employee's risk score with employees
    from the same department.
    """

    employee = (
        db.query(Employee)
        .filter(Employee.employee_id == employee_id)
        .first()
    )

    if not employee:
        return None

    peers = (
        db.query(Employee)
        .filter(
            Employee.department == employee.department,
            Employee.employee_id != employee_id,
        )
        .all()
    )

    employee_score = calculate_risk_score(employee_id, db)["final_score"]

    if not peers:
        return {
            "employee_id": employee_id,
            "employee_score": employee_score,
            "peer_count": 0,
            "department_avg_score": None,
            "deviation_from_peers": None,
            "note": "No peers found in this department for comparison",
        }

    peer_scores = [
        calculate_risk_score(
            peer.employee_id,
            db
        )["final_score"]
        for peer in peers
    ]

    peer_avg = sum(peer_scores) / len(peer_scores)

    return {
        "employee_id": employee_id,
        "employee_score": employee_score,
        "peer_count": len(peers),
        "department_avg_score": round(peer_avg, 1),
        "deviation_from_peers": round(
            employee_score - peer_avg,
            1
        ),
    }


def get_risk_trend(
    employee_id: str,
    days: int = 30
) -> list[dict]:
    """
    Return one anomaly-count entry for every day
    in the requested period.
    """

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    trend = []

    current = start_date

    while current < end_date:
        next_day = current + timedelta(days=1)

        # Rule-based anomalies use detected_at.
        rule_count = mongo_db["rule_anomalies"].count_documents({
            "employee_id": employee_id,
            "detected_at": {
                "$gte": current,
                "$lt": next_day,
            },
        })

        # Existing ITBIS ML anomaly records use prediction == -1.
        # Also support is_anomaly=True if older/test records contain it.
        ml_count = mongo_db["ml_anomalies"].count_documents({
            "employee_id": employee_id,
            "date": current.date().isoformat(),
            "$or": [
                {"prediction": -1},
                {"is_anomaly": True},
            ],
        })

        trend.append({
            "date": current.date().isoformat(),
            "anomaly_count": rule_count + ml_count,
        })

        current = next_day

    return trend


def get_trend_direction(employee_id: str) -> dict:
    """
    Compare the first 7 days with the second 7 days
    of the latest 14-day anomaly trend.
    """

    trend = get_risk_trend(employee_id, days=14)

    first_week = trend[:7]
    second_week = trend[7:]

    first_week_avg = (
        sum(item["anomaly_count"] for item in first_week)
        / len(first_week)
    )

    second_week_avg = (
        sum(item["anomaly_count"] for item in second_week)
        / len(second_week)
    )

    if second_week_avg > first_week_avg * 1.3:
        direction = "increasing"

    elif second_week_avg < first_week_avg * 0.7:
        direction = "decreasing"

    else:
        direction = "stable"

    return {
        "employee_id": employee_id,
        "first_week_avg": round(first_week_avg, 2),
        "second_week_avg": round(second_week_avg, 2),
        "direction": direction,
    }
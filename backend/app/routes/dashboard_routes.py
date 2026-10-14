"""
ITBIS Dashboard Routes.

Day 29:
- Security Analyst Dashboard
- SOC Dashboard
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db, mongo_db
from app.models import Alert, Incident
from app.risk_scoring import calculate_risk_score
from app.security import require_role


router = APIRouter(tags=["Dashboards"])


# =========================================================
# SECURITY ANALYST DASHBOARD
# =========================================================

@router.get("/dashboard/analyst")
def analyst_dashboard(
    db: Session = Depends(get_db),
    user=Depends(
        require_role(
            "admin",
            "security_analyst"
        )
    ),
):
    """
    Dashboard for Security Analysts.

    Returns:
    - Open alerts
    - Current analyst investigation queue
    - Open/investigating incidents
    - Top 5 risk employees
    """

    # JWT subject is stored as a string.
    # assigned_to is an integer in PostgreSQL.
    my_id = int(user["sub"])

    # -----------------------------------------------------
    # Open alerts
    # -----------------------------------------------------

    open_alerts = (
        db.query(Alert)
        .filter(Alert.status == "open")
        .count()
    )

    # -----------------------------------------------------
    # My investigation queue
    # -----------------------------------------------------

    my_queue = (
        db.query(Alert)
        .filter(
            Alert.assigned_to == my_id,
            Alert.status == "in_progress"
        )
        .count()
    )

    # -----------------------------------------------------
    # Open incidents
    # -----------------------------------------------------

    open_incidents = (
        db.query(Incident)
        .filter(
            Incident.status.in_(
                ["open", "investigating"]
            )
        )
        .count()
    )

    # -----------------------------------------------------
    # Top 5 flagged employees
    # -----------------------------------------------------

    pipeline = [
        {
            "$group": {
                "_id": "$employee_id",
                "flag_count": {"$sum": 1},
            }
        },
        {
            "$sort": {
                "flag_count": -1
            }
        },
        {
            "$limit": 5
        },
    ]

    top_flagged = list(
        mongo_db["rule_anomalies"].aggregate(
            pipeline
        )
    )

    top_risk = []

    for row in top_flagged:

        employee_id = row["_id"]

        risk = calculate_risk_score(
            employee_id,
            db
        )

        top_risk.append(
            {
                "employee_id": employee_id,
                "flags": row["flag_count"],
                "risk": risk,
            }
        )

    return {
        "open_alerts": open_alerts,
        "my_investigation_queue": my_queue,
        "open_incidents": open_incidents,
        "top_risk_employees": top_risk,
    }


# =========================================================
# SOC DASHBOARD
# =========================================================

@router.get("/dashboard/soc")
def soc_dashboard(
    db: Session = Depends(get_db),
    user=Depends(
        require_role(
            "admin",
            "soc_engineer"
        )
    ),
):
    """
    Dashboard for SOC Engineers.

    Returns:
    - Open alerts grouped by severity
    - Rule anomalies from the last 7 days
    - Active investigations
    """

    # -----------------------------------------------------
    # Alerts by severity
    # -----------------------------------------------------

    alerts_by_severity = dict(
        db.query(
            Alert.severity,
            func.count(Alert.id)
        )
        .filter(
            Alert.status != "resolved"
        )
        .group_by(
            Alert.severity
        )
        .all()
    )

    # -----------------------------------------------------
    # Rule anomalies - last 7 days
    # -----------------------------------------------------

    since = (
        datetime.utcnow()
        - timedelta(days=7)
    )

    daily = list(
        mongo_db["rule_anomalies"].aggregate(
            [
                {
                    "$match": {
                        "detected_at": {
                            "$gte": since
                        }
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$detected_at",
                            }
                        },
                        "count": {
                            "$sum": 1
                        },
                    }
                },
                {
                    "$sort": {
                        "_id": 1
                    }
                },
            ]
        )
    )

    # -----------------------------------------------------
    # Active investigations
    # -----------------------------------------------------

    active_investigations = (
        db.query(Incident)
        .filter(
            Incident.status == "investigating"
        )
        .count()
    )

    return {
        "alerts_by_severity": alerts_by_severity,

        "anomalies_last_7_days": [
            {
                "date": item["_id"],
                "count": item["count"],
            }
            for item in daily
        ],

        "active_investigations": active_investigations,
    }
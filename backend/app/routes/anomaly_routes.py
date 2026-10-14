"""
Anomaly Detection API routes for ITBIS.

Milestone 2 - Day 19–20

Endpoints:

GET /anomalies/summary
    Returns an overall anomaly summary.

GET /anomalies/{employee_id}
    Returns combined rule-based and ML anomalies
    for a specific employee.
"""

from fastapi import APIRouter, Depends

from app.database import (
    rule_anomalies_collection,
    ml_anomalies_collection,
)

from app.security import require_role


# =========================================================
# Router
# =========================================================

router = APIRouter(
    prefix="/anomalies",
    tags=["Anomalies"],
)


# =========================================================
# GET overall anomaly summary
# =========================================================

@router.get("/summary")
def get_anomaly_summary(
    current_user: dict = Depends(
        require_role(
            "admin",
            "security_analyst",
            "soc_engineer",
        )
    ),
):
    """
    Return an overall summary of detected anomalies.
    """

    # -----------------------------------------------------
    # Total rule-based anomalies
    # -----------------------------------------------------

    total_rule_anomalies = (
        rule_anomalies_collection.count_documents({})
    )

    # -----------------------------------------------------
    # Total ML anomalies
    # -----------------------------------------------------

    total_ml_anomalies = (
        ml_anomalies_collection.count_documents({})
    )

    # -----------------------------------------------------
    # Rule anomalies by severity
    # -----------------------------------------------------

    critical_count = (
        rule_anomalies_collection.count_documents(
            {
                "severity": "critical"
            }
        )
    )

    high_count = (
        rule_anomalies_collection.count_documents(
            {
                "severity": "high"
            }
        )
    )

    medium_count = (
        rule_anomalies_collection.count_documents(
            {
                "severity": "medium"
            }
        )
    )

    # -----------------------------------------------------
    # Top employees by rule anomalies
    # -----------------------------------------------------

    top_rule_employees = list(
        rule_anomalies_collection.aggregate(
            [
                {
                    "$group": {
                        "_id": "$employee_id",
                        "anomaly_count": {
                            "$sum": 1
                        },
                    }
                },
                {
                    "$sort": {
                        "anomaly_count": -1
                    }
                },
                {
                    "$limit": 10
                },
            ]
        )
    )

    # -----------------------------------------------------
    # Convert aggregation results
    # -----------------------------------------------------

    top_employees = []

    for item in top_rule_employees:

        top_employees.append(
            {
                "employee_id": item["_id"],
                "anomaly_count": item[
                    "anomaly_count"
                ],
            }
        )

    # -----------------------------------------------------
    # Return summary
    # -----------------------------------------------------

    return {
        "total_rule_anomalies": (
            total_rule_anomalies
        ),
        "total_ml_anomalies": (
            total_ml_anomalies
        ),
        "total_anomalies": (
            total_rule_anomalies
            + total_ml_anomalies
        ),
        "rule_anomalies_by_severity": {
            "critical": critical_count,
            "high": high_count,
            "medium": medium_count,
        },
        "top_rule_anomaly_employees": (
            top_employees
        ),
    }


# =========================================================
# GET anomalies for a specific employee
# =========================================================

@router.get("/{employee_id}")
def get_employee_anomalies(
    employee_id: str,
    current_user: dict = Depends(
        require_role(
            "admin",
            "security_analyst",
            "soc_engineer",
        )
    ),
):
    """
    Return rule-based and ML anomalies
    for a specific employee.
    """

    # -----------------------------------------------------
    # Rule-based anomalies
    # -----------------------------------------------------

    rule_anomalies = list(
        rule_anomalies_collection.find(
            {
                "employee_id": employee_id
            }
        )
    )

    # -----------------------------------------------------
    # ML anomalies
    # -----------------------------------------------------

    ml_anomalies = list(
        ml_anomalies_collection.find(
            {
                "employee_id": employee_id
            }
        )
    )

    # -----------------------------------------------------
    # Convert MongoDB ObjectId to string
    # -----------------------------------------------------

    for anomaly in rule_anomalies:

        if "_id" in anomaly:

            anomaly["_id"] = str(
                anomaly["_id"]
            )

    for anomaly in ml_anomalies:

        if "_id" in anomaly:

            anomaly["_id"] = str(
                anomaly["_id"]
            )

    # -----------------------------------------------------
    # Combined response
    # -----------------------------------------------------

    return {
        "employee_id": employee_id,

        "rule_anomalies": rule_anomalies,

        "ml_anomalies": ml_anomalies,

        "total_rule_anomalies": len(
            rule_anomalies
        ),

        "total_ml_anomalies": len(
            ml_anomalies
        ),

        "total_anomalies": (
            len(rule_anomalies)
            + len(ml_anomalies)
        ),
    }
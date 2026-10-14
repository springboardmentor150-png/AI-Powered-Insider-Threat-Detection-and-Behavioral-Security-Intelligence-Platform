"""
ITBIS Insider Risk Scoring Engine.

Day 21-22:
- Five normalized 0-100 sub-scores
- Weighted final risk score
- Risk levels: Low / Medium / High / Critical
"""

from app.database import mongo_db
from app.models import Employee, Incident


# =========================================================
# Weights
# =========================================================

WEIGHTS = {
    "behavioral_anomalies": 0.35,
    "privilege_misuse": 0.25,
    "data_access_violations": 0.20,
    "access_pattern_deviations": 0.10,
    "historical_events": 0.10,
}


# =========================================================
# Behavioral Anomalies - 35%
# =========================================================

def score_behavioral_anomalies(employee_id: str) -> float:
    """
    Score combined rule-based and ML anomalies.

    Existing ITBIS rule anomalies are stored in the
    rule_anomalies collection.

    ML anomalies are stored in ml_anomalies.
    In the existing ITBIS ML schema, prediction == -1
    represents an anomaly.
    """

    # Rule-based anomalies
    rule_count = mongo_db["rule_anomalies"].count_documents({
        "employee_id": employee_id
    })

    # ML anomalies
    # Existing ML anomaly records use prediction == -1
    ml_count = mongo_db["ml_anomalies"].count_documents({
        "employee_id": employee_id,
        "prediction": -1
    })

    return min((rule_count + ml_count) * 10, 100)


# =========================================================
# Privilege Misuse - 25%
# =========================================================

def score_privilege_misuse(employee_id: str) -> float:
    """
    Score explicit privilege-change anomalies.

    The Day 21 design uses privilege_change as a
    high-impact security signal.
    """

    count = mongo_db["rule_anomalies"].count_documents({
        "employee_id": employee_id,
        "anomaly_type": "privilege_change"
    })

    return min(count * 25, 100)


# =========================================================
# Data Access Violations - 20%
# =========================================================

def score_data_access_violations(employee_id: str) -> float:
    """
    Score explicit data-exfiltration-risk anomalies.

    These are intentionally kept separate from ordinary
    data-transfer-volume anomalies.
    """

    count = mongo_db["rule_anomalies"].count_documents({
        "employee_id": employee_id,
        "anomaly_type": "data_exfiltration_risk"
    })

    return min(count * 40, 100)


# =========================================================
# Access Pattern Deviations - 10%
# =========================================================

def score_access_pattern_deviations(employee_id: str) -> float:
    """
    Score unknown device/application patterns.

    Supports the Day 21 anomaly_type convention and
    the existing Day 15-16 indicator convention.
    """

    count = mongo_db["rule_anomalies"].count_documents({
        "employee_id": employee_id,
        "$or": [
            {
                "anomaly_type": {
                    "$regex": "^unknown_"
                }
            },
            {
                "indicator": {
                    "$in": [
                        "device_usage",
                        "application_usage"
                    ]
                }
            }
        ]
    })

    return min(count * 15, 100)


# =========================================================
# Historical Security Events - 10%
# =========================================================

def score_historical_events(employee_id: str, db) -> float:
    """
    Score previous incidents stored in PostgreSQL.

    Incident records use the internal numeric employee
    primary key, so employee_id must first be resolved
    to the Employee row.
    """

    employee = (
        db.query(Employee)
        .filter(Employee.employee_id == employee_id)
        .first()
    )

    if not employee:
        return 0.0

    count = (
        db.query(Incident)
        .filter(Incident.employee_id == employee.id)
        .count()
    )

    return min(count * 20, 100)


# =========================================================
# Final Risk Score
# =========================================================

def calculate_risk_score(employee_id: str, db) -> dict:
    """
    Calculate the complete insider risk score.

    Returns:
        employee_id
        sub_scores
        final_score
        risk_level
    """

    sub_scores = {
        "behavioral_anomalies": score_behavioral_anomalies(
            employee_id
        ),
        "privilege_misuse": score_privilege_misuse(
            employee_id
        ),
        "data_access_violations": score_data_access_violations(
            employee_id
        ),
        "access_pattern_deviations": score_access_pattern_deviations(
            employee_id
        ),
        "historical_events": score_historical_events(
            employee_id,
            db
        ),
    }

    # Weighted final score
    final_score = sum(
        sub_scores[key] * WEIGHTS[key]
        for key in WEIGHTS
    )

    # Safety clamp
    final_score = max(0.0, min(final_score, 100.0))

    # Risk levels
    if final_score >= 75:
        risk_level = "Critical"
    elif final_score >= 50:
        risk_level = "High"
    elif final_score >= 25:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "employee_id": employee_id,
        "sub_scores": sub_scores,
        "final_score": round(final_score, 1),
        "risk_level": risk_level,
    }
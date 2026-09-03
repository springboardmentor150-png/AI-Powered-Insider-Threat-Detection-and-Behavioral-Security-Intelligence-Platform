from .mongo_database import (
    activity_logs_collection,
    behavioral_baselines_collection
)


def detect_anomaly(employee_id: int, action: str, resource: str | None = None):
    # Get employee's behavioral baseline
    baseline = behavioral_baselines_collection.find_one(
        {"employee_id": employee_id}
    )

    if not baseline:
        return {
            "employee_id": employee_id,
            "anomaly": False,
            "risk_score": 0,
            "threat_level": "UNKNOWN",
            "message": "No behavioral baseline found for this employee."
        }

    risk_score = 0
    reasons = []

    # Check whether the action is unusual
    if action != baseline["common_action"]:
        risk_score += 40
        reasons.append("Unusual activity type")

    # Check whether the resource is unusual
    common_resource = baseline.get("common_resource")

    if common_resource and resource and resource != common_resource:
        risk_score += 30
        reasons.append("Unusual resource accessed")

    # Limit risk score to 100
    risk_score = min(risk_score, 100)

    # Determine threat level
    if risk_score >= 70:
        threat_level = "HIGH"
    elif risk_score >= 40:
        threat_level = "MEDIUM"
    else:
        threat_level = "LOW"

    anomaly = risk_score >= 40

    return {
        "employee_id": employee_id,
        "anomaly": anomaly,
        "risk_score": risk_score,
        "threat_level": threat_level,
        "reasons": reasons
    }
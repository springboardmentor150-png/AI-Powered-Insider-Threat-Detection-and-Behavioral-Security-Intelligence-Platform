from .database import mongo_db

WEIGHTS = {
    "behavioral_anomalies": 0.35,
    "privilege_misuse": 0.25,
    "data_access_violations": 0.20,
    "access_pattern_deviations": 0.10,
    "historical_security_events": 0.10,
}

def calculate_risk_score(employee_id: str) -> dict:
    anomalies = list(mongo_db["rule_anomalies"].find({"employee_id": employee_id}))
    ml_flags = list(mongo_db["ml_anomalies"].find({
        "employee_id": employee_id,
        "is_anomaly": True
    }))
    factor_scores = {
        "behavioral_anomalies": min(len(anomalies) * 10 + len(ml_flags) * 15, 100),
        "privilege_misuse": min(sum(1 for a in anomalies if a.get("anomaly_type") == "privilege_change") * 40, 100),
        "data_access_violations": min(sum(1 for a in anomalies if "exfiltration" in a.get("anomaly_type", "")) * 50, 100),
        "access_pattern_deviations": min(sum(1 for a in anomalies if "unusual" in a.get("anomaly_type", "")) * 15, 100),
        "historical_security_events": min(len(anomalies) * 2, 100),
    }
    weighted_total = sum(factor_scores[k] * WEIGHTS[k] for k in WEIGHTS)
    if weighted_total >= 75:
        category = "critical"
    elif weighted_total >= 50:
        category = "high"
    elif weighted_total >= 25:
        category = "medium"
    else:
        category = "low"
    return {
        "employee_id": employee_id,
        "factor_scores": factor_scores,
        "risk_score": round(weighted_total, 1),
        "risk_category": category,
    }

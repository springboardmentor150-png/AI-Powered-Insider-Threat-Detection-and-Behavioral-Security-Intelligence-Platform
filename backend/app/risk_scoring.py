from app.database import mongo_db


WEIGHTS = {
    "behavioral_anomalies": 0.35,
    "privilege_misuse": 0.25,
    "data_access_violations": 0.20,
    "access_pattern_deviations": 0.10,
    "historical_security_events": 0.10,
}


# Demo fallback data lets M3 run even when MongoDB/M2 data is not available.
DEMO_ANOMALIES = {
    "EMP-1001": [
        {"anomaly_type": "privilege_change"},
        {"anomaly_type": "data_exfiltration"},
        {"anomaly_type": "unusual_download"},
        {"anomaly_type": "unusual_login"},
    ],
    "EMP-1002": [
        {"anomaly_type": "unusual_download"},
        {"anomaly_type": "unusual_login"},
    ],
    "EMP-1003": [],
    "EMP-1004": [
        {"anomaly_type": "privilege_change"},
        {"anomaly_type": "unusual_download"},
    ],
    "EMP-1005": [
        {"anomaly_type": "data_exfiltration"},
        {"anomaly_type": "unusual_download"},
        {"anomaly_type": "unusual_login"},
    ],
}


DEMO_ML = {
    "EMP-1001": 3,
    "EMP-1002": 1,
    "EMP-1003": 0,
    "EMP-1004": 1,
    "EMP-1005": 2,
}


def _get_anomalies(employee_id):
    if mongo_db is not None:
        try:
            data = list(
                mongo_db["rule_anomalies"].find(
                    {"employee_id": employee_id}
                )
            )

            # Use MongoDB data only when records exist.
            if data:
                return data

        except Exception:
            pass

    # Otherwise use demo fallback data.
    return DEMO_ANOMALIES.get(employee_id, [])


def _get_ml_count(employee_id):
    if mongo_db is not None:
        try:
            count = mongo_db["ml_anomalies"].count_documents(
                {
                    "employee_id": employee_id,
                    "is_anomaly": True
                }
            )

            # Use MongoDB count only when records exist.
            if count > 0:
                return count

        except Exception:
            pass

    # Otherwise use demo fallback data.
    return DEMO_ML.get(employee_id, 0)


def calculate_risk_score(employee_id: str) -> dict:
    anomalies = _get_anomalies(employee_id)
    ml_count = _get_ml_count(employee_id)

    factor_scores = {
        "behavioral_anomalies": min(
            len(anomalies) * 10 + ml_count * 15,
            100
        ),

        "privilege_misuse": min(
            sum(
                1
                for a in anomalies
                if a.get("anomaly_type") == "privilege_change"
            ) * 40,
            100
        ),

        "data_access_violations": min(
            sum(
                1
                for a in anomalies
                if "exfiltration" in a.get("anomaly_type", "")
            ) * 50,
            100
        ),

        "access_pattern_deviations": min(
            sum(
                1
                for a in anomalies
                if "unusual" in a.get("anomaly_type", "")
            ) * 15,
            100
        ),

        "historical_security_events": min(
            len(anomalies) * 2,
            100
        ),
    }

    weighted_total = sum(
        factor_scores[k] * WEIGHTS[k]
        for k in WEIGHTS
    )

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
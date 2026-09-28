from .database import mongo_db

def check_login_time_anomaly(employee_id: str, login_hour: float) -> dict:
    baseline = mongo_db["behavioral_baselines"].find_one({
        "employee_id": employee_id,
        "indicator": "avg_login_hour"
    })
    if not baseline:
        return {"anomaly": False, "reason": "No baseline yet"}
    typical = baseline["typical_value"]
    deviation = baseline.get("std_deviation") or 0.5
    z_score = abs(login_hour - typical) / deviation
    is_anomaly = z_score > 2.5
    result = {
        "employee_id": employee_id,
        "anomaly": is_anomaly,
        "z_score": round(z_score, 2),
        "typical_login_hour": typical,
        "actual_login_hour": login_hour,
        "category": "Unusual Login Time" if is_anomaly else None,
    }
    if is_anomaly:
        mongo_db["rule_anomalies"].insert_one({
            "employee_id": employee_id,
            "anomaly_type": "unusual_login_time",
            "detected_at": __import__("datetime").datetime.utcnow(),
            "details": result,
        })
    return result

def check_resource_access_anomaly(employee_id: str, actual_count: float) -> dict:
    baseline = mongo_db["behavioral_baselines"].find_one({
        "employee_id": employee_id,
        "indicator": "resource_access_frequency"
    })
    if not baseline:
        return {"anomaly": False, "reason": "No baseline yet"}
    typical = baseline["typical_value"]
    deviation = baseline.get("std_deviation") or 1
    z = abs(actual_count - typical) / deviation
    result = {
        "employee_id": employee_id,
        "anomaly": z > 2.5,
        "z_score": round(z, 2),
        "typical_value": typical,
        "actual_value": actual_count,
        "category": "Unusual Resource Access" if z > 2.5 else None,
    }
    if result["anomaly"]:
        mongo_db["rule_anomalies"].insert_one({
            "employee_id": employee_id,
            "anomaly_type": "unusual_resource_access",
            "detected_at": __import__("datetime").datetime.utcnow(),
            "details": result,
        })
    return result

def check_data_transfer_anomaly(employee_id: str, actual_mb: float) -> dict:
    baseline = mongo_db["behavioral_baselines"].find_one({
        "employee_id": employee_id,
        "indicator": "data_transfer_volume"
    })
    if not baseline:
        return {"anomaly": False, "reason": "No baseline yet"}
    typical = baseline["typical_value"]
    deviation = baseline.get("std_deviation") or max(1, typical * 0.1)
    z = abs(actual_mb - typical) / deviation
    result = {
        "employee_id": employee_id,
        "anomaly": z > 2.5,
        "z_score": round(z, 2),
        "typical_value": typical,
        "actual_value": actual_mb,
        "category": "Data Exfiltration Risk" if z > 2.5 else None,
    }
    if result["anomaly"]:
        mongo_db["rule_anomalies"].insert_one({
            "employee_id": employee_id,
            "anomaly_type": "data_exfiltration",
            "detected_at": __import__("datetime").datetime.utcnow(),
            "details": result,
        })
    return result

def check_privilege_abuse(employee_id: str, requested_privilege: str, allowed_privileges: list[str]) -> dict:
    is_anomaly = requested_privilege not in allowed_privileges
    result = {
        "employee_id": employee_id,
        "anomaly": is_anomaly,
        "requested_privilege": requested_privilege,
        "allowed_privileges": allowed_privileges,
        "category": "Privilege Abuse" if is_anomaly else None,
    }
    if is_anomaly:
        mongo_db["rule_anomalies"].insert_one({
            "employee_id": employee_id,
            "anomaly_type": "privilege_change",
            "detected_at": __import__("datetime").datetime.utcnow(),
            "details": result,
        })
    return result

def check_suspicious_device(employee_id: str, device: str, known_devices: list[str]) -> dict:
    is_anomaly = device not in known_devices
    result = {
        "employee_id": employee_id,
        "anomaly": is_anomaly,
        "device": device,
        "known_devices": known_devices,
        "category": "Suspicious Device Usage" if is_anomaly else None,
    }
    if is_anomaly:
        mongo_db["rule_anomalies"].insert_one({
            "employee_id": employee_id,
            "anomaly_type": "suspicious_device",
            "detected_at": __import__("datetime").datetime.utcnow(),
            "details": result,
        })
    return result

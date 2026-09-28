import statistics
from collections import Counter
from datetime import datetime
from .database import mongo_db

def _numeric_details(log, keys):
    details = log.get("details") or {}
    for key in keys:
        value = details.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return None

def calculate_login_time_baseline(employee_id: str):
    logs = list(mongo_db["activity_logs"].find({
        "employee_id": employee_id,
        "event_type": "login"
    }))
    if len(logs) < 5:
        return None
    values = [
        log["timestamp"].hour + log["timestamp"].minute / 60
        for log in logs if log.get("timestamp")
    ]
    if len(values) < 5:
        return None
    baseline = {
        "employee_id": employee_id,
        "indicator": "avg_login_hour",
        "typical_value": round(statistics.mean(values), 2),
        "std_deviation": round(statistics.stdev(values), 2) if len(values) > 1 else 0,
        "sample_size": len(values),
        "last_updated": datetime.utcnow(),
    }
    mongo_db["behavioral_baselines"].update_one(
        {"employee_id": employee_id, "indicator": "avg_login_hour"},
        {"$set": baseline},
        upsert=True,
    )
    return baseline

def calculate_resource_access_baseline(employee_id: str):
    logs = list(mongo_db["activity_logs"].find({"employee_id": employee_id}))
    values = []
    for log in logs:
        if log.get("event_type") in {"resource_access", "file_access"}:
            value = _numeric_details(log, ["count", "access_count"])
            values.append(value if value is not None else 1.0)
    if len(values) < 5:
        return None
    baseline = {
        "employee_id": employee_id,
        "indicator": "resource_access_frequency",
        "typical_value": round(statistics.mean(values), 2),
        "std_deviation": round(statistics.stdev(values), 2) if len(values) > 1 else 0,
        "sample_size": len(values),
        "last_updated": datetime.utcnow(),
    }
    mongo_db["behavioral_baselines"].update_one(
        {"employee_id": employee_id, "indicator": baseline["indicator"]},
        {"$set": baseline}, upsert=True
    )
    return baseline

def calculate_data_transfer_baseline(employee_id: str):
    logs = list(mongo_db["activity_logs"].find({"employee_id": employee_id}))
    values = []
    for log in logs:
        if log.get("event_type") in {"upload", "download", "data_transfer"}:
            value = _numeric_details(log, ["mb", "data_mb", "volume_mb", "size_mb"])
            if value is not None:
                values.append(value)
    if len(values) < 5:
        return None
    baseline = {
        "employee_id": employee_id,
        "indicator": "data_transfer_volume",
        "typical_value": round(statistics.mean(values), 2),
        "std_deviation": round(statistics.stdev(values), 2) if len(values) > 1 else 0,
        "sample_size": len(values),
        "last_updated": datetime.utcnow(),
    }
    mongo_db["behavioral_baselines"].update_one(
        {"employee_id": employee_id, "indicator": baseline["indicator"]},
        {"$set": baseline}, upsert=True
    )
    return baseline

def calculate_device_usage_baseline(employee_id: str):
    logs = list(mongo_db["activity_logs"].find({"employee_id": employee_id}))
    devices = []
    for log in logs:
        device = (log.get("details") or {}).get("device") or (log.get("details") or {}).get("device_id")
        if device:
            devices.append(str(device))
    if len(devices) < 5:
        return None
    typical = Counter(devices).most_common(1)[0][0]
    baseline = {
        "employee_id": employee_id,
        "indicator": "device_usage",
        "typical_value": typical,
        "std_deviation": 0,
        "sample_size": len(devices),
        "last_updated": datetime.utcnow(),
    }
    mongo_db["behavioral_baselines"].update_one(
        {"employee_id": employee_id, "indicator": "device_usage"},
        {"$set": baseline}, upsert=True
    )
    return baseline

def calculate_all_baselines(employee_id: str):
    return [
        b for b in [
            calculate_login_time_baseline(employee_id),
            calculate_resource_access_baseline(employee_id),
            calculate_data_transfer_baseline(employee_id),
            calculate_device_usage_baseline(employee_id),
        ] if b is not None
    ]

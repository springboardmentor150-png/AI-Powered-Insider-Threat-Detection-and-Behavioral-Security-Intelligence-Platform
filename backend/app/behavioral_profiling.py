from statistics import mean, stdev
from datetime import datetime

from app.database import get_mongo_db


MINIMUM_SAMPLES = 5


def calculate_baseline(values):
    if values is None or len(values) < MINIMUM_SAMPLES:
        return None

    return {
        "typical_value": round(mean(values), 3),
        "std_deviation": round(stdev(values), 3),
        "sample_size": len(values),
        "last_updated": datetime.now().isoformat()
    }


def calculate_login_time_baseline(values):
    return calculate_baseline(values)


def calculate_resource_access_baseline(values):
    return calculate_baseline(values)


def calculate_device_usage_baseline(values):
    return calculate_baseline(values)


def calculate_application_usage_baseline(values):
    return calculate_baseline(values)


def calculate_data_transfer_baseline(values):
    return calculate_baseline(values)


def calculate_communication_pattern_baseline(values):
    return calculate_baseline(values)


def save_baseline(employee_id, indicator, baseline):
    if baseline is None:
        return None

    db = get_mongo_db()

    baseline_data = {
        "employee_id": employee_id,
        "indicator": indicator,
        "typical_value": baseline["typical_value"],
        "std_deviation": baseline["std_deviation"],
        "sample_size": baseline["sample_size"],
        "last_updated": baseline["last_updated"]
    }

    db.behavioral_baselines.update_one(
        {
            "employee_id": employee_id,
            "indicator": indicator
        },
        {
            "$set": baseline_data
        },
        upsert=True
    )

    return baseline_data


def generate_employee_baselines(employee_id):

    db = get_mongo_db()

    logs = list(
        db.activity_logs.find(
            {"employee_id": employee_id}
        )
    )

    if len(logs) < MINIMUM_SAMPLES:
        return {
            "employee_id": employee_id,
            "message": "Not enough logs to create baseline",
            "sample_size": len(logs)
        }

    login_hours = []
    file_access_counts = []
    data_transfer_values = []
    communication_counts = []

    for log in logs:

        if "timestamp" in log:
            try:
                timestamp = datetime.fromisoformat(
                    log["timestamp"]
                )
                login_hours.append(timestamp.hour)
            except (ValueError, TypeError):
                pass

        details = log.get("details", {})

        if not isinstance(details, dict):
            details = {}

        if "file_access_count" in details:
            file_access_counts.append(
                details["file_access_count"]
            )

        if "data_transfer_mb" in details:
            data_transfer_values.append(
                details["data_transfer_mb"]
            )

        if "communication_count" in details:
            communication_counts.append(
                details["communication_count"]
            )

    baselines = {}

    baseline = calculate_login_time_baseline(login_hours)
    if baseline:
        baselines["login_time"] = save_baseline(
            employee_id,
            "login_time",
            baseline
        )

    baseline = calculate_resource_access_baseline(
        file_access_counts
    )
    if baseline:
        baselines["resource_access"] = save_baseline(
            employee_id,
            "resource_access",
            baseline
        )

    baseline = calculate_data_transfer_baseline(
        data_transfer_values
    )
    if baseline:
        baselines["data_transfer"] = save_baseline(
            employee_id,
            "data_transfer",
            baseline
        )

    baseline = calculate_communication_pattern_baseline(
        communication_counts
    )
    if baseline:
        baselines["communication_pattern"] = save_baseline(
            employee_id,
            "communication_pattern",
            baseline
        )

    return {
        "employee_id": employee_id,
        "sample_size": len(logs),
        "baselines_created": baselines
    }

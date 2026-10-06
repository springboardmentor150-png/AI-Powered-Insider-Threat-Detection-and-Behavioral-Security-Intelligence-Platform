"""
ITBIS Milestone 2 - Behavioral Profiling Engine

Day 13:
    Builds numeric behavioral baselines for each employee.

Numeric indicators:
    1. Login Time
    2. Resource Access Frequency
    3. Data Transfer Volume

Only controlled Milestone 2 seed data is used for baseline training.
This keeps the original Milestone 1 activity records from contaminating
the Milestone 2 behavioral baselines.

Baselines are stored in MongoDB collection:
    behavioral_baselines
"""

from collections import defaultdict
from datetime import datetime, timezone
from statistics import mean, stdev
from zoneinfo import ZoneInfo

from app.mongo import activity_logs, behavioral_baselines


MIN_SAMPLE_SIZE = 5
INDIA_TIMEZONE = ZoneInfo("Asia/Kolkata")

# Milestone 2 controlled training dataset.
# We intentionally exclude legacy Milestone 1 activity records.
TRAINING_DATA_FILTER = {
    "dataset_source": "milestone_2_seed"
}


def save_numeric_baseline(
    employee_code: str,
    indicator: str,
    values: list[float],
) -> dict | None:
    """
    Calculate and save a numeric behavioral baseline.

    A baseline is created only when enough observations are available.
    """
    if len(values) < MIN_SAMPLE_SIZE:
        return None

    typical_value = mean(values)
    normal_range = stdev(values) if len(values) > 1 else 0.0

    baseline = {
        "employee_code": employee_code,
        "indicator": indicator,
        "typical_value": round(typical_value, 2),
        "normal_range": round(normal_range, 2),
        "sample_size": len(values),
        "last_updated": datetime.now(timezone.utc),
    }

    behavioral_baselines.update_one(
        {
            "employee_code": employee_code,
            "indicator": indicator,
        },
        {
            "$set": baseline,
        },
        upsert=True,
    )

    return baseline


def _to_india_time(timestamp: datetime) -> datetime:
    """
    Convert an activity timestamp to Indian Standard Time.

    MongoDB timestamps are stored in UTC.
    """
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    return timestamp.astimezone(INDIA_TIMEZONE)


def _employee_training_filter(employee_code: str) -> dict:
    """
    Return the MongoDB filter for one employee's Milestone 2
    controlled training records.
    """
    return {
        **TRAINING_DATA_FILTER,
        "employee_code": employee_code,
    }


def calculate_login_time_baseline(
    employee_code: str,
) -> dict | None:
    """
    Calculate the employee's typical login time.

    Login time is represented as decimal hours in IST.

    Example:
        08:30 -> 8.5
        09:15 -> 9.25
    """
    query = {
        **_employee_training_filter(employee_code),
        "event_type": "login",
    }

    logs = activity_logs.find(query)

    login_hours = []

    for log in logs:
        timestamp = log.get("timestamp")

        if not timestamp:
            continue

        india_time = _to_india_time(timestamp)

        login_hour = (
            india_time.hour
            + india_time.minute / 60
            + india_time.second / 3600
        )

        login_hours.append(login_hour)

    return save_numeric_baseline(
        employee_code,
        "login_time",
        login_hours,
    )


def calculate_access_frequency_baseline(
    employee_code: str,
) -> dict | None:
    """
    Calculate the employee's typical daily resource access frequency.

    Related file-access events are grouped by calendar day in IST.
    The resulting daily counts are used to calculate the baseline.
    """
    query = {
        **_employee_training_filter(employee_code),
        "event_type": "file_access",
    }

    logs = activity_logs.find(query)

    daily_counts = defaultdict(int)

    for log in logs:
        timestamp = log.get("timestamp")

        if not timestamp:
            continue

        india_time = _to_india_time(timestamp)
        day_key = india_time.date()

        daily_counts[day_key] += 1

    counts_per_day = list(daily_counts.values())

    return save_numeric_baseline(
        employee_code,
        "resource_access_frequency",
        counts_per_day,
    )


def calculate_data_transfer_baseline(
    employee_code: str,
) -> dict | None:
    """
    Calculate the employee's typical daily data transfer volume.

    Both file_access and data_transfer events are considered when
    data_volume_mb is available.
    """
    query = {
        **_employee_training_filter(employee_code),
        "event_type": {
            "$in": [
                "file_access",
                "data_transfer",
            ]
        },
    }

    logs = activity_logs.find(query)

    daily_volume = defaultdict(float)

    for log in logs:
        timestamp = log.get("timestamp")

        if not timestamp:
            continue

        data_volume = log.get("data_volume_mb")

        if data_volume is None:
            continue

        try:
            data_volume = float(data_volume)
        except (TypeError, ValueError):
            continue

        india_time = _to_india_time(timestamp)
        day_key = india_time.date()

        daily_volume[day_key] += data_volume

    volumes_per_day = list(daily_volume.values())

    return save_numeric_baseline(
        employee_code,
        "data_transfer_volume",
        volumes_per_day,
    )

def calculate_device_usage_baseline(
    employee_code: str,
) -> dict | None:
    """
    Build a set-membership baseline for devices used by an employee.

    The baseline stores all known device IDs observed in the
    Milestone 2 training dataset.
    """
    query = {
        **_employee_training_filter(employee_code),
        "device_id": {
            "$exists": True,
            "$ne": None,
        },
    }

    logs = activity_logs.find(query)

    devices = set()

    for log in logs:
        device_id = log.get("device_id")

        if not device_id:
            continue

        device_id = str(device_id).strip()

        if device_id:
            devices.add(device_id)

    if len(devices) == 0:
        return None

    baseline = {
        "employee_code": employee_code,
        "indicator": "device_usage",
        "known_values": sorted(devices),
        "sample_size": len(devices),
        "last_updated": datetime.now(timezone.utc),
    }

    behavioral_baselines.update_one(
        {
            "employee_code": employee_code,
            "indicator": "device_usage",
        },
        {
            "$set": baseline,
        },
        upsert=True,
    )

    return baseline


def calculate_application_usage_baseline(
    employee_code: str,
) -> dict | None:
    """
    Build a set-membership baseline for applications used by an employee.

    The baseline stores all known application names observed in the
    Milestone 2 training dataset.
    """
    query = {
        **_employee_training_filter(employee_code),
        "application": {
            "$exists": True,
            "$ne": None,
        },
    }

    logs = activity_logs.find(query)

    applications = set()

    for log in logs:
        application = log.get("application")

        if not application:
            continue

        application = str(application).strip()

        if application:
            applications.add(application)

    if len(applications) == 0:
        return None

    baseline = {
        "employee_code": employee_code,
        "indicator": "application_usage",
        "known_values": sorted(applications),
        "sample_size": len(applications),
        "last_updated": datetime.now(timezone.utc),
    }

    behavioral_baselines.update_one(
        {
            "employee_code": employee_code,
            "indicator": "application_usage",
        },
        {
            "$set": baseline,
        },
        upsert=True,
    )

    return baseline
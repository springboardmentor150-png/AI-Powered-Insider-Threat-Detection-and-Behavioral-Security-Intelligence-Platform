"""
ITBIS - Behavioral Profiling

Milestone 2 - Day 13 & Day 14

Builds per-employee behavioral baselines from
historical activity logs stored in MongoDB.
"""

from datetime import datetime, timedelta
from statistics import mean, stdev

from app.database import (
    activity_logs_collection,
    behavioral_baselines_collection,
)


# Minimum number of observations required before
# creating a reliable baseline.
MIN_SAMPLE_SIZE = 5


# ============================================================
# Fetch Employee Logs
# ============================================================

def get_employee_logs(
    employee_id: str,
    event_type: str,
    days_back: int = 90
) -> list:
    """
    Fetch recent activity logs for one employee
    and one event type.

    Only logs within the requested number of days
    are considered.
    """

    cutoff_time = datetime.utcnow() - timedelta(
        days=days_back
    )

    logs = list(
        activity_logs_collection.find(
            {
                "employee_id": employee_id,
                "event_type": event_type,
                "timestamp": {
                    "$gte": cutoff_time
                },
            }
        ).sort(
            "timestamp",
            1
        )
    )

    return logs


# ============================================================
# Generic Numeric Baseline Helper
# ============================================================

def save_numeric_baseline(
    employee_id: str,
    indicator: str,
    values: list
) -> dict | None:
    """
    Calculate and save a numeric behavioral baseline.

    Returns the baseline dictionary, or None if there
    are not enough observations.
    """

    if len(values) < MIN_SAMPLE_SIZE:
        return None

    typical_value = mean(values)

    if len(values) > 1:
        normal_range = stdev(values)
    else:
        normal_range = 0.0

    baseline = {
        "employee_id": employee_id,
        "indicator": indicator,
        "typical_value": typical_value,
        "normal_range": normal_range,
        "sample_size": len(values),
        "last_updated": datetime.utcnow(),
    }

    save_baseline(baseline)

    return baseline


# ============================================================
# Login Time Baseline
# ============================================================

def calculate_login_time_baseline(
    employee_id: str
) -> dict | None:
    """
    Calculate the employee's typical login hour.

    Login time is converted into decimal hours.

    Example:
        09:30 -> 9.5
    """

    logs = get_employee_logs(
        employee_id,
        "login"
    )

    login_hours = []

    for log in logs:

        timestamp = log.get("timestamp")

        if not timestamp:
            continue

        hour = timestamp.hour
        minute = timestamp.minute

        decimal_hour = hour + (minute / 60)

        login_hours.append(decimal_hour)

    return save_numeric_baseline(
        employee_id=employee_id,
        indicator="login_time",
        values=login_hours,
    )


# ============================================================
# Resource Access Frequency Baseline
# ============================================================

def calculate_resource_access_baseline(
    employee_id: str
) -> dict | None:
    """
    Calculate the employee's typical number of
    resource-access events per day.

    Relevant events:
        file_download
        file_upload
        application_usage
    """

    event_types = {
        "file_download",
        "file_upload",
        "application_usage",
    }

    cutoff_time = datetime.utcnow() - timedelta(
        days=90
    )

    logs = list(
        activity_logs_collection.find(
            {
                "employee_id": employee_id,
                "event_type": {
                    "$in": list(event_types)
                },
                "timestamp": {
                    "$gte": cutoff_time
                },
            }
        )
    )

    daily_counts = {}

    for log in logs:

        timestamp = log.get("timestamp")

        if not timestamp:
            continue

        day = timestamp.date()

        daily_counts[day] = (
            daily_counts.get(day, 0) + 1
        )

    daily_values = list(
        daily_counts.values()
    )

    return save_numeric_baseline(
        employee_id=employee_id,
        indicator="resource_access_frequency",
        values=daily_values,
    )


# ============================================================
# Data Transfer Volume Baseline
# ============================================================

def calculate_data_transfer_baseline(
    employee_id: str
) -> dict | None:
    """
    Calculate the employee's typical daily
    data-transfer volume in MB.

    Relevant events:
        file_download
        file_upload
        data_transfer
    """

    event_types = {
        "file_download",
        "file_upload",
        "data_transfer",
    }

    cutoff_time = datetime.utcnow() - timedelta(
        days=90
    )

    logs = list(
        activity_logs_collection.find(
            {
                "employee_id": employee_id,
                "event_type": {
                    "$in": list(event_types)
                },
                "timestamp": {
                    "$gte": cutoff_time
                },
            }
        )
    )

    daily_transfer = {}

    for log in logs:

        timestamp = log.get("timestamp")

        if not timestamp:
            continue

        details = log.get("details") or {}

        size_mb = details.get(
            "size_mb",
            0
        )

        # Ignore malformed/non-numeric sizes.
        if not isinstance(
            size_mb,
            (int, float)
        ):
            continue

        day = timestamp.date()

        daily_transfer[day] = (
            daily_transfer.get(day, 0)
            + size_mb
        )

    daily_values = list(
        daily_transfer.values()
    )

    return save_numeric_baseline(
        employee_id=employee_id,
        indicator="data_transfer_volume",
        values=daily_values,
    )


# ============================================================
# Set-Based Baseline Helper
# ============================================================

def save_set_baseline(
    employee_id: str,
    indicator: str,
    values: list
) -> dict | None:
    """
    Save a set-membership baseline.

    Used for:
        device_usage
        application_usage
    """

    unique_values = sorted(
        {
            value
            for value in values
            if value
        }
    )

    if len(unique_values) == 0:
        return None

    baseline = {
        "employee_id": employee_id,
        "indicator": indicator,
        "known_values": unique_values,
        "sample_size": len(values),
        "last_updated": datetime.utcnow(),
    }

    save_baseline(baseline)

    return baseline


# ============================================================
# Device Usage Baseline
# ============================================================

def calculate_device_usage_baseline(
    employee_id: str
) -> dict | None:
    """
    Determine which devices the employee normally uses.
    """

    logs = list(
        activity_logs_collection.find(
            {
                "employee_id": employee_id,
                "details.device": {
                    "$exists": True
                },
            }
        )
    )

    devices = []

    for log in logs:

        details = log.get("details") or {}

        device = details.get("device")

        if device:
            devices.append(device)

    return save_set_baseline(
        employee_id=employee_id,
        indicator="device_usage",
        values=devices,
    )


# ============================================================
# Application Usage Baseline
# ============================================================

def calculate_application_usage_baseline(
    employee_id: str
) -> dict | None:
    """
    Determine which applications the employee
    normally uses.
    """

    logs = get_employee_logs(
        employee_id,
        "application_usage"
    )

    applications = []

    for log in logs:

        details = log.get("details") or {}

        application = details.get(
            "application"
        )

        if application:
            applications.append(
                application
            )

    return save_set_baseline(
        employee_id=employee_id,
        indicator="application_usage",
        values=applications,
    )


# ============================================================
# Save / Upsert Baseline
# ============================================================

def save_baseline(
    baseline: dict
) -> None:
    """
    Upsert a baseline document into MongoDB.

    One baseline exists for each:
        employee_id + indicator
    """

    behavioral_baselines_collection.update_one(
        {
            "employee_id": baseline["employee_id"],
            "indicator": baseline["indicator"],
        },
        {
            "$set": baseline
        },
        upsert=True,
    )


# ============================================================
# Build All Baselines For One Employee
# ============================================================

def build_employee_baselines(
    employee_id: str
) -> list:
    """
    Build all five behavioral baselines
    for one employee.
    """

    baselines = []

    baseline_functions = [
        calculate_login_time_baseline,
        calculate_resource_access_baseline,
        calculate_device_usage_baseline,
        calculate_application_usage_baseline,
        calculate_data_transfer_baseline,
    ]

    for function in baseline_functions:

        baseline = function(employee_id)

        if baseline is not None:
            baselines.append(baseline)

    return baselines


# ============================================================
# Build Baselines For All Employees
# ============================================================

def build_all_baselines(
    employee_ids: list
) -> dict:
    """
    Build behavioral baselines for every employee.
    """

    results = {}

    for employee_id in employee_ids:

        baselines = build_employee_baselines(
            employee_id
        )

        results[employee_id] = baselines

    return results
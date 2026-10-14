"""
Rule-Based Anomaly Detection for ITBIS.

Milestone 2 - Day 15–16

This module compares new employee activity against
employee-specific behavioral baselines.

Numeric indicators:
- login_time
- resource_access_frequency
- data_transfer_volume

Set-based indicators:
- device_usage
- application_usage

Detected anomalies are stored in MongoDB collection:
- rule_anomalies
"""

from datetime import datetime

from app.database import (
    activity_logs_collection,
    behavioral_baselines_collection,
    rule_anomalies_collection,
)


# =========================================================
# Constants
# =========================================================

MIN_SPREAD = 0.1

SEVERITY_MEDIUM = "medium"
SEVERITY_HIGH = "high"
SEVERITY_CRITICAL = "critical"


# =========================================================
# Get employee baseline
# =========================================================

def get_baseline(employee_id: str, indicator: str):
    """
    Get the behavioral baseline for a specific employee
    and indicator.
    """

    return behavioral_baselines_collection.find_one(
        {
            "employee_id": employee_id,
            "indicator": indicator,
        }
    )


# =========================================================
# Numeric anomaly detection
# =========================================================

def check_numeric_anomaly(
    employee_id: str,
    indicator: str,
    new_value: float,
):
    """
    Compare a new numeric value against the employee baseline.

    deviation_ratio =
        abs(new_value - typical_value)
        / max(normal_range, 0.1)

    Rules:

    deviation <= 2
        Normal

    deviation > 2 and <= 3
        Medium

    deviation > 3 and <= 5
        High

    deviation > 5
        Critical
    """

    baseline = get_baseline(
        employee_id,
        indicator
    )

    # No baseline available
    if not baseline:
        return {
            "anomaly": False,
            "reason": "No baseline found",
        }

    typical_value = baseline.get("typical_value")

    normal_range = baseline.get(
        "normal_range",
        MIN_SPREAD
    )

    # Baseline is incomplete
    if typical_value is None:
        return {
            "anomaly": False,
            "reason": "Baseline does not contain typical_value",
        }

    # Convert values safely
    try:
        new_value = float(new_value)
        typical_value = float(typical_value)
        normal_range = float(
            normal_range or MIN_SPREAD
        )

    except (TypeError, ValueError):
        return {
            "anomaly": False,
            "reason": "Invalid numeric value",
        }

    # Prevent zero/negative spread problems
    spread = max(
        abs(normal_range),
        MIN_SPREAD
    )

    deviation_ratio = (
        abs(new_value - typical_value)
        / spread
    )

    # -----------------------------------------------------
    # Normal behavior
    # -----------------------------------------------------

    if deviation_ratio <= 2:

        return {
            "anomaly": False,
            "deviation_ratio": deviation_ratio,
            "severity": None,
            "typical_value": typical_value,
            "normal_range": normal_range,
        }

    # -----------------------------------------------------
    # Determine severity
    # -----------------------------------------------------

    if deviation_ratio > 5:

        severity = SEVERITY_CRITICAL

    elif deviation_ratio > 3:

        severity = SEVERITY_HIGH

    else:

        severity = SEVERITY_MEDIUM

    return {
        "anomaly": True,
        "employee_id": employee_id,
        "indicator": indicator,
        "new_value": new_value,
        "typical_value": typical_value,
        "normal_range": normal_range,
        "deviation_ratio": deviation_ratio,
        "severity": severity,
    }


# =========================================================
# Set-based anomaly detection
# =========================================================

def check_set_anomaly(
    employee_id: str,
    indicator: str,
    new_value: str,
):
    """
    Check whether a device or application is known
    for the specific employee.
    """

    baseline = get_baseline(
        employee_id,
        indicator
    )

    # No baseline
    if not baseline:

        return {
            "anomaly": False,
            "reason": "No baseline found",
        }

    known_values = baseline.get(
        "known_values",
        []
    )

    # Missing value
    if not new_value:

        return {
            "anomaly": False,
            "reason": "Missing value",
        }

    # Known value
    if new_value in known_values:

        return {
            "anomaly": False,
            "known_value": True,
            "known_values": known_values,
        }

    # Unknown value
    return {
        "anomaly": True,
        "employee_id": employee_id,
        "indicator": indicator,
        "new_value": new_value,
        "known_values": known_values,
        "severity": SEVERITY_HIGH,
        "reason": "Unknown value for this employee",
    }


# =========================================================
# Save rule anomaly
# =========================================================

def save_rule_anomaly(anomaly: dict):
    """
    Save a detected rule-based anomaly into MongoDB.
    """

    document = {
        **anomaly,
        "detected_at": datetime.utcnow(),
    }

    result = rule_anomalies_collection.insert_one(
        document
    )

    document["_id"] = str(
        result.inserted_id
    )

    return document


# =========================================================
# Login time
# =========================================================

def check_login_time(
    employee_id: str,
    login_hour: float,
):
    """
    Check whether login time is abnormal.
    """

    result = check_numeric_anomaly(
        employee_id,
        "login_time",
        login_hour,
    )

    if result.get("anomaly"):

        return save_rule_anomaly(result)

    return result


# =========================================================
# Resource access frequency
# =========================================================

def check_resource_access_frequency(
    employee_id: str,
    access_count: float,
):
    """
    Check whether daily resource access frequency
    is abnormal.
    """

    result = check_numeric_anomaly(
        employee_id,
        "resource_access_frequency",
        access_count,
    )

    if result.get("anomaly"):

        return save_rule_anomaly(result)

    return result


# =========================================================
# Data transfer volume
# =========================================================

def check_data_transfer_volume(
    employee_id: str,
    transfer_volume: float,
):
    """
    Check whether daily data transfer volume
    is abnormal.
    """

    result = check_numeric_anomaly(
        employee_id,
        "data_transfer_volume",
        transfer_volume,
    )

    if result.get("anomaly"):

        return save_rule_anomaly(result)

    return result


# =========================================================
# Device usage
# =========================================================

def check_device_usage(
    employee_id: str,
    device: str,
):
    """
    Check whether the device is known
    for the employee.
    """

    result = check_set_anomaly(
        employee_id,
        "device_usage",
        device,
    )

    if result.get("anomaly"):

        return save_rule_anomaly(result)

    return result


# =========================================================
# Application usage
# =========================================================

def check_application_usage(
    employee_id: str,
    application: str,
):
    """
    Check whether the application is known
    for the employee.
    """

    result = check_set_anomaly(
        employee_id,
        "application_usage",
        application,
    )

    if result.get("anomaly"):

        return save_rule_anomaly(result)

    return result


# =========================================================
# Today's resource access count
# =========================================================

def get_today_resource_access_count(
    employee_id: str,
    timestamp: datetime,
):
    """
    Calculate the employee's resource/application
    access count for the same calendar day.
    """

    start_of_day = timestamp.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    end_of_day = timestamp.replace(
        hour=23,
        minute=59,
        second=59,
        microsecond=999999,
    )

    relevant_event_types = [
        "file_download",
        "file_upload",
        "application_usage",
    ]

    logs = activity_logs_collection.find(
        {
            "employee_id": employee_id,
            "event_type": {
                "$in": relevant_event_types
            },
            "timestamp": {
                "$gte": start_of_day,
                "$lte": end_of_day,
            },
        }
    )

    return sum(
        1
        for _ in logs
    )


# =========================================================
# Today's data transfer volume
# =========================================================

def get_today_data_transfer_volume(
    employee_id: str,
    timestamp: datetime,
):
    """
    Calculate total data transferred by the employee
    during the same calendar day.
    """

    start_of_day = timestamp.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    end_of_day = timestamp.replace(
        hour=23,
        minute=59,
        second=59,
        microsecond=999999,
    )

    logs = activity_logs_collection.find(
        {
            "employee_id": employee_id,
            "event_type": {
                "$in": [
                    "file_download",
                    "file_upload",
                    "data_transfer",
                ]
            },
            "timestamp": {
                "$gte": start_of_day,
                "$lte": end_of_day,
            },
        }
    )

    total_mb = 0.0

    for log in logs:

        details = log.get(
            "details"
        ) or {}

        size_mb = details.get(
            "size_mb",
            0
        )

        try:

            total_mb += float(
                size_mb
            )

        except (TypeError, ValueError):

            continue

    return total_mb


# =========================================================
# Check activity log
# =========================================================

def check_activity_log(log: dict):
    """
    Automatically select the appropriate behavioral
    rule for an activity log.
    """

    employee_id = log.get(
        "employee_id"
    )

    event_type = log.get(
        "event_type"
    )

    details = log.get(
        "details"
    ) or {}

    timestamp = log.get(
        "timestamp"
    )

    # -----------------------------------------------------
    # Validate employee
    # -----------------------------------------------------

    if not employee_id:

        return {
            "anomaly": False,
            "reason": "Missing employee_id",
        }

    # -----------------------------------------------------
    # Validate timestamp
    # -----------------------------------------------------

    if not timestamp:

        return {
            "anomaly": False,
            "reason": "Missing timestamp",
        }

    # =====================================================
    # LOGIN
    # =====================================================

    if event_type == "login":

        login_hour = (
            timestamp.hour
            + (
                timestamp.minute / 60
            )
        )

        return check_login_time(
            employee_id,
            login_hour,
        )

    # =====================================================
    # DEVICE USAGE
    # =====================================================

    device = details.get(
        "device"
    )

    if device:

        device_result = check_device_usage(
            employee_id,
            device,
        )

        if device_result.get("anomaly"):

            return device_result

    # =====================================================
    # APPLICATION USAGE
    # =====================================================

    application = details.get(
        "application"
    )

    if application:

        application_result = check_application_usage(
            employee_id,
            application,
        )

        if application_result.get("anomaly"):

            return application_result

    # =====================================================
    # RESOURCE ACCESS
    # =====================================================

    if event_type in {
        "file_download",
        "file_upload",
        "application_usage",
    }:

        access_count = (
            get_today_resource_access_count(
                employee_id,
                timestamp,
            )
        )

        return check_resource_access_frequency(
            employee_id,
            access_count,
        )

    # =====================================================
    # DATA TRANSFER
    # =====================================================

    if event_type == "data_transfer":

        total_transfer_mb = (
            get_today_data_transfer_volume(
                employee_id,
                timestamp,
            )
        )

        return check_data_transfer_volume(
            employee_id,
            total_transfer_mb,
        )

    # =====================================================
    # Unknown/unmapped event
    # =====================================================

    return {
        "anomaly": False,
        "reason": "Event type not mapped to a rule",
    }


# =========================================================
# Ingest log + anomaly check
# =========================================================

def ingest_log_and_check(log: dict):
    """
    Insert an activity log into MongoDB and immediately
    check it against the employee's behavioral baseline.
    """

    log_document = {
        **log,
        "created_at": datetime.utcnow(),
    }

    # -----------------------------------------------------
    # Insert activity log
    # -----------------------------------------------------

    result = activity_logs_collection.insert_one(
        log_document
    )

    log_document["_id"] = str(
        result.inserted_id
    )

    # -----------------------------------------------------
    # Check activity against baseline
    # -----------------------------------------------------

    anomaly = check_activity_log(
        log_document
    )

    return {
        "activity_log": log_document,
        "anomaly": anomaly,
    }
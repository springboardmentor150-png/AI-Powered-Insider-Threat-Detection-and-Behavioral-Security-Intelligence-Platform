"""
ITBIS Milestone 2 - Rule-Based Anomaly Detection

Day 15:
    Numeric anomaly detection using employee behavioral baselines.

Detection flow:
    1. Retrieve the employee baseline.
    2. Compare the new observation with the typical value.
    3. Calculate the deviation ratio.
    4. Apply the specified thresholds.
    5. Persist anomalies to MongoDB.

Numeric indicators supported:
    - login_time
    - resource_access_frequency
    - data_transfer_volume
"""

from datetime import datetime, timezone

from app.mongo import behavioral_baselines, activity_logs, rule_anomalies


MIN_SPREAD = 0.1
ANOMALY_THRESHOLD = 2.0
HIGH_SEVERITY_THRESHOLD = 3.0
CRITICAL_SEVERITY_THRESHOLD = 5.0


def check_numeric_anomaly(
    employee_code: str,
    indicator: str,
    new_value: float,
    activity_id=None,
) -> dict | None:
    """
    Compare a new numeric observation against an employee baseline.

    Returns:
        None when the observation is normal or no baseline exists.

        A dictionary containing anomaly details when an anomaly
        is detected.
    """

    baseline = behavioral_baselines.find_one(
        {
            "employee_code": employee_code,
            "indicator": indicator,
        }
    )

    # No baseline means the employee does not have enough
    # historical data for this indicator yet.
    if baseline is None:
        return None

    typical_value = float(baseline["typical_value"])
    normal_range = float(baseline.get("normal_range", 0.0))

    # Prevent zero or extremely small standard deviation from
    # creating unstable or infinite deviation ratios.
    spread = max(normal_range, MIN_SPREAD)

    deviation_ratio = abs(new_value - typical_value) / spread

    # Values within 2 standard deviations are considered normal.
    if deviation_ratio <= ANOMALY_THRESHOLD:
        return None

    if deviation_ratio > CRITICAL_SEVERITY_THRESHOLD:
        severity = "critical"
    elif deviation_ratio > HIGH_SEVERITY_THRESHOLD:
        severity = "high"
    else:
        severity = "medium"

    anomaly = {
        "employee_code": employee_code,
        "indicator": indicator,
        "observed_value": float(new_value),
        "typical_value": typical_value,
        "normal_range": normal_range,
        "deviation_ratio": round(deviation_ratio, 2),
        "severity": severity,
        "detection_type": "rule_based",
        "activity_id": activity_id,
        "detected_at": datetime.now(timezone.utc),
    }

    rule_anomalies.insert_one(anomaly)

    return anomaly


def check_unusual_login_time(
    employee_code: str,
    login_hour: float,
    activity_id=None,
) -> dict | None:
    """
    Check whether a login time is unusual for the employee.
    """
    return check_numeric_anomaly(
        employee_code=employee_code,
        indicator="login_time",
        new_value=login_hour,
        activity_id=activity_id,
    )


def check_abnormal_data_transfer(
    employee_code: str,
    data_volume_mb: float,
    activity_id=None,
) -> dict | None:
    """
    Check whether data transfer volume is unusual for the employee.
    """
    return check_numeric_anomaly(
        employee_code=employee_code,
        indicator="data_transfer_volume",
        new_value=data_volume_mb,
        activity_id=activity_id,
    )


def check_excessive_resource_access(
    employee_code: str,
    access_count: float,
    activity_id=None,
) -> dict | None:
    """
    Check whether resource access frequency is unusual.
    """
    return check_numeric_anomaly(
        employee_code=employee_code,
        indicator="resource_access_frequency",
        new_value=access_count,
        activity_id=activity_id,
    )

def check_set_membership_anomaly(
    employee_code: str,
    indicator: str,
    observed_value: str,
    activity_id=None,
) -> dict | None:
    """
    Check whether an observed device or application is known
    for the employee.

    Known value:
        No anomaly.

    Unknown value:
        High-severity rule-based anomaly.

    No baseline:
        No anomaly.
    """

    baseline = behavioral_baselines.find_one(
        {
            "employee_code": employee_code,
            "indicator": indicator,
        }
    )

    # No behavioral baseline exists yet.
    # Therefore, there is not enough historical information
    # to classify the observation as anomalous.
    if baseline is None:
        return None

    known_values = baseline.get("known_values", [])

    observed_value = str(observed_value).strip()

    # Known device/application is normal.
    if observed_value in known_values:
        return None

    anomaly = {
        "employee_code": employee_code,
        "indicator": indicator,
        "observed_value": observed_value,
        "known_values": known_values,
        "severity": "high",
        "detection_type": "rule_based",
        "activity_id": activity_id,
        "detected_at": datetime.now(timezone.utc),
    }

    rule_anomalies.insert_one(anomaly)

    return anomaly


def check_unknown_device(
    employee_code: str,
    device_id: str,
    activity_id=None,
) -> dict | None:
    """
    Check whether a device is known for the employee.
    """
    return check_set_membership_anomaly(
        employee_code=employee_code,
        indicator="device_usage",
        observed_value=device_id,
        activity_id=activity_id,
    )


def check_unknown_application(
    employee_code: str,
    application: str,
    activity_id=None,
) -> dict | None:
    """
    Check whether an application is known for the employee.
    """
    return check_set_membership_anomaly(
        employee_code=employee_code,
        indicator="application_usage",
        observed_value=application,
        activity_id=activity_id,
    )
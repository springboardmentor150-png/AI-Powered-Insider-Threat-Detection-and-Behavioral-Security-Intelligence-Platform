"""
Rule-Based Anomaly Detection Engine (Milestone 2: Day 15-16)
ITBIS: AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform.

Phase 2 (Day 15): Numeric Anomaly Detection
- check_numeric_anomaly(employee_id, indicator, new_value, anomaly_type)
- detect_login_anomaly: compares login hour against baseline 'avg_login_hour'
- detect_download_anomaly: compares data transfer size against baseline 'data_transfer_volume'
- detect_transfer_frequency_anomaly: compares transfer frequency against baseline 'resource_access_frequency'

Phase 3 (Day 16): Set-Membership Anomaly Detection
- check_set_anomaly(employee_id, indicator, new_value, anomaly_type)
- detect_device_anomaly: compares hardware against baseline 'device_usage'
- detect_unauthorized_access: compares app/service against baseline 'application_usage'

Architectural Principles:
- Enforces documented minimum spread (0.1) to protect against zero-variance division by zero.
- Configurable default threshold (2.0 standard deviation ratios).
- Classified into 'medium', 'high', and 'critical' severities.
- Unknown devices and applications classified as 'high' severity.
- Safe handling of missing baselines, None/invalid measurements (returns None).
- Persistent storage through MongoDBService (MongoDB or persistent JSON fallback).
"""

import math
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Union

from app.mongodb import mongo_service
from app.behavioral_profiling import (
    parse_timestamp,
    timestamp_to_decimal_hour,
    extract_app_identifier,
)

logger = logging.getLogger("itbis.anomaly_detection")

# Configurable detection parameters
DEFAULT_NUMERIC_THRESHOLD = 2.0
MIN_SPREAD = 0.1

# Documented severity classification thresholds
SEVERITY_MEDIUM_MAX = 3.0
SEVERITY_HIGH_MAX = 5.0


# =====================================================================
# Phase 2: Numeric Anomaly Detection (Day 15)
# =====================================================================

def check_numeric_anomaly(
    employee_id: str,
    indicator: str,
    new_value: Any,
    anomaly_type: str,
    threshold: float = DEFAULT_NUMERIC_THRESHOLD,
    min_spread: float = MIN_SPREAD,
) -> Optional[Dict[str, Any]]:
    """
    Evaluates a new numeric observation against the employee's empirical baseline.
    
    Requirements:
    1. Retrieve the employee's actual baseline using existing storage service.
    2. Read baseline typical_value (mean) and spread (sample std_deviation).
    3. Return None when no baseline exists or the observation is invalid.
    4. Protect against zero or near-zero spread using min_spread (default: 0.1).
    5. Calculate absolute deviation ratio: |new_value - typical_value| / effective_spread.
    6. Return None when ratio <= threshold (default threshold: 2.0).
    7. Classify detected anomalies as medium, high, or critical:
       - threshold < ratio <= 3.0: 'medium'
       - 3.0 < ratio <= 5.0:       'high'
       - ratio > 5.0:              'critical'
    8. Record detected anomalies persistently in storage (MongoDB or dev store).
    9. Return anomaly dictionary including all audit fields.
    """
    if not employee_id or not indicator or new_value is None:
        return None

    # Safe numeric conversion
    try:
        obs_val = float(new_value)
        if math.isnan(obs_val) or math.isinf(obs_val):
            return None
    except (ValueError, TypeError):
        logger.debug("Invalid numeric value '%s' for indicator %s", new_value, indicator)
        return None

    # Retrieve baseline
    baseline = mongo_service.get_baseline(employee_id=employee_id, indicator=indicator)
    if not baseline:
        logger.debug("No baseline found for employee %s on indicator %s. Skipping anomaly check.", employee_id, indicator)
        return None

    typical_value = baseline.get("typical_value")
    if typical_value is None:
        return None

    try:
        typ_val = float(typical_value)
    except (ValueError, TypeError):
        return None

    # Spread protection (Bessel's std dev with min_spread safeguard)
    raw_spread = baseline.get("std_deviation")
    try:
        spread = float(raw_spread) if raw_spread is not None else 0.0
    except (ValueError, TypeError):
        spread = 0.0

    effective_spread = max(spread, min_spread)

    # Calculate absolute deviation ratio
    abs_diff = abs(obs_val - typ_val)
    deviation_ratio = abs_diff / effective_spread

    # Check against threshold
    if deviation_ratio <= threshold:
        return None

    # Classify severity
    if deviation_ratio <= SEVERITY_MEDIUM_MAX:
        severity = "medium"
    elif deviation_ratio <= SEVERITY_HIGH_MAX:
        severity = "high"
    else:
        severity = "critical"

    # Construct anomaly record
    anomaly_record: Dict[str, Any] = {
        "employee_id": employee_id,
        "anomaly_type": anomaly_type,
        "indicator": indicator,
        "severity": severity,
        "observed_value": round(obs_val, 2),
        "typical_value": round(typ_val, 2),
        "deviation_ratio": round(deviation_ratio, 2),
        "detection_timestamp": datetime.now(timezone.utc).isoformat(),
        "details": {
            "threshold": threshold,
            "raw_spread": round(spread, 2),
            "effective_spread": round(effective_spread, 2),
            "sample_size": baseline.get("sample_size", 0),
        },
    }

    # Persist in storage
    saved = mongo_service.record_anomaly(anomaly_record)
    logger.info(
        "Detected numeric anomaly [%s] for %s (%s): observed=%.2f, typical=%.2f, ratio=%.2f, severity=%s",
        anomaly_type, employee_id, indicator, obs_val, typ_val, deviation_ratio, severity
    )
    return saved


def detect_login_anomaly(
    employee_id: str,
    login_time: Union[datetime, str, float, int],
    threshold: float = DEFAULT_NUMERIC_THRESHOLD,
    min_spread: float = MIN_SPREAD,
) -> Optional[Dict[str, Any]]:
    """
    Wrapper: detects unusual login time against baseline 'avg_login_hour'.
    Accepts datetime objects, ISO strings, or numeric decimal hours.
    """
    if login_time is None:
        return None

    decimal_hour: Optional[float] = None
    if isinstance(login_time, (int, float)):
        decimal_hour = float(login_time)
    elif isinstance(login_time, datetime):
        decimal_hour = timestamp_to_decimal_hour(login_time)
    elif isinstance(login_time, str):
        # Could be an ISO timestamp or a decimal string
        try:
            decimal_hour = float(login_time)
        except ValueError:
            dt = parse_timestamp(login_time)
            if dt is not None:
                decimal_hour = timestamp_to_decimal_hour(dt)

    if decimal_hour is None or decimal_hour < 0.0 or decimal_hour >= 24.0:
        logger.debug("Invalid login time '%s' for employee %s", login_time, employee_id)
        return None

    return check_numeric_anomaly(
        employee_id=employee_id,
        indicator="avg_login_hour",
        new_value=decimal_hour,
        anomaly_type="UNUSUAL_LOGIN_TIME",
        threshold=threshold,
        min_spread=min_spread,
    )


def detect_download_anomaly(
    employee_id: str,
    download_size_mb: Any,
    threshold: float = DEFAULT_NUMERIC_THRESHOLD,
    min_spread: float = MIN_SPREAD,
) -> Optional[Dict[str, Any]]:
    """
    Wrapper: detects abnormal data transfer volume against baseline 'data_transfer_volume'.
    """
    return check_numeric_anomaly(
        employee_id=employee_id,
        indicator="data_transfer_volume",
        new_value=download_size_mb,
        anomaly_type="ABNORMAL_DATA_TRANSFER",
        threshold=threshold,
        min_spread=min_spread,
    )


def detect_transfer_frequency_anomaly(
    employee_id: str,
    daily_transfers_count: Any,
    threshold: float = DEFAULT_NUMERIC_THRESHOLD,
    min_spread: float = MIN_SPREAD,
) -> Optional[Dict[str, Any]]:
    """
    Wrapper: detects excessive transfer frequency against baseline 'resource_access_frequency'.
    """
    return check_numeric_anomaly(
        employee_id=employee_id,
        indicator="resource_access_frequency",
        new_value=daily_transfers_count,
        anomaly_type="EXCESSIVE_TRANSFER_FREQUENCY",
        threshold=threshold,
        min_spread=min_spread,
    )


# =====================================================================
# Phase 3: Set-Membership Anomaly Detection (Day 16)
# =====================================================================

def check_set_anomaly(
    employee_id: str,
    indicator: str,
    new_value: Any,
    anomaly_type: str,
) -> Optional[Dict[str, Any]]:
    """
    Evaluates whether an entity (device, app) belongs to the employee's known values set.
    
    Requirements:
    1. Compare against employee's observed known_values.
    2. Return None for known values (case-insensitive normalized).
    3. Record unknown values as high-severity anomalies.
    4. Return None when no baseline exists.
    5. Persist anomalies in storage so they remain available after restarts.
    """
    if not employee_id or not indicator or new_value is None:
        return None

    val_str = str(new_value).strip()
    if not val_str or val_str.upper() in ("NONE", "NULL", "N/A", "UNKNOWN", ""):
        return None

    # Retrieve baseline
    baseline = mongo_service.get_baseline(employee_id=employee_id, indicator=indicator)
    if not baseline:
        logger.debug("No baseline found for employee %s on indicator %s. Skipping set anomaly check.", employee_id, indicator)
        return None

    known_values = baseline.get("known_values")
    if known_values is None:
        return None

    # Case-insensitive membership verification
    known_set = {str(k).strip().lower() for k in known_values}
    if val_str.lower() in known_set:
        # Known value -> normal, no anomaly
        return None

    # Unknown value -> High-severity anomaly
    anomaly_record: Dict[str, Any] = {
        "employee_id": employee_id,
        "anomaly_type": anomaly_type,
        "indicator": indicator,
        "severity": "high",
        "observed_value": val_str,
        "typical_value": known_values,
        "deviation_ratio": None,
        "detection_timestamp": datetime.now(timezone.utc).isoformat(),
        "details": {
            "known_values_count": len(known_values),
            "status": "UNRECOGNIZED_ENTITY",
        },
    }

    saved = mongo_service.record_anomaly(anomaly_record)
    logger.info(
        "Detected set-membership anomaly [%s] for %s (%s): observed='%s', not in known values (%d registered)",
        anomaly_type, employee_id, indicator, val_str, len(known_values)
    )
    return saved


def detect_device_anomaly(
    employee_id: str,
    device: Any,
) -> Optional[Dict[str, Any]]:
    """
    Wrapper: detects unrecognized device hardware against baseline 'device_usage'.
    """
    if device is None:
        return None
    normalized_device = str(device).strip()
    return check_set_anomaly(
        employee_id=employee_id,
        indicator="device_usage",
        new_value=normalized_device,
        anomaly_type="SUSPICIOUS_DEVICE",
    )


def detect_unauthorized_access(
    employee_id: str,
    resource_or_app: Any,
    details: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Wrapper: detects unauthorized application or resource access against baseline 'application_usage'.
    Normalizes resource using extract_app_identifier consistently with baseline builder.
    """
    if resource_or_app is None and not details:
        return None

    normalized_app = extract_app_identifier(resource_or_app, details)
    if not normalized_app:
        normalized_app = str(resource_or_app).strip() if resource_or_app else None

    if not normalized_app:
        return None

    return check_set_anomaly(
        employee_id=employee_id,
        indicator="application_usage",
        new_value=normalized_app,
        anomaly_type="UNAUTHORIZED_APPLICATION_ACCESS",
    )

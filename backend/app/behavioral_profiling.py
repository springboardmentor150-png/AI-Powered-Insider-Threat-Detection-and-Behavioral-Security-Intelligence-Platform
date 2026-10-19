"""
Behavioral Profiling Engine (Milestone 2: Day 11-14)
ITBIS: AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform.

Calculates employee-specific behavioral baselines across six key indicators:
1. Login Times (avg_login_hour) - Numeric: mean decimal hour, sample std dev
2. Resource Access Frequency (resource_access_frequency) - Numeric: mean daily accesses, sample std dev
3. Device Usage (device_usage) - Categorical / Set-membership: known_values, sample_size
4. Application Usage (application_usage) - Categorical / Set-membership: known_values, sample_size
5. Data Transfer Volume (data_transfer_volume) - Numeric: mean daily transfer MB, sample std dev
6. Communication Patterns (communication_patterns) - Numeric: mean daily email communications, sample std dev

Requirements:
- Configurable recent window (default: 90 days).
- Minimum sample size of 5 observations for numeric baselines.
- Bessel's correction (N - 1) for sample standard deviation.
- Zero standard deviation is preserved as a valid measure (not missing data).
- Robust handling of missing, malformed, or out-of-range logs.
- Safe upsert operations to prevent duplicate baseline records.
"""

import math
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple, Set
from collections import defaultdict

from app.mongodb import mongo_service

logger = logging.getLogger("itbis.behavioral_profiling")

MIN_SAMPLE_SIZE = 5
DEFAULT_LOOKBACK_DAYS = 90


# =====================================================================
# Reusable Mathematical and Utility Helpers
# =====================================================================

def calculate_mean(values: List[float]) -> float:
    """Calculates the arithmetic mean of a list of numeric values."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def calculate_sample_std_dev(values: List[float], mean: Optional[float] = None) -> float:
    """
    Calculates sample standard deviation using Bessel's correction (N - 1).
    - If N < 2: returns 0.0.
    - If spread is 0 (all values identical): returns 0.0 (preserved, not treated as missing).
    """
    n = len(values)
    if n < 2:
        return 0.0
    if mean is None:
        mean = calculate_mean(values)
    sum_sq_diff = sum((x - mean) ** 2 for x in values)
    variance = sum_sq_diff / (n - 1)
    return math.sqrt(max(0.0, variance))


def parse_timestamp(ts: Any) -> Optional[datetime]:
    """
    Parses ISO-8601 or datetime objects safely into UTC-aware datetime.
    Returns None if malformed or missing.
    """
    if ts is None:
        return None
    if isinstance(ts, datetime):
        if ts.tzinfo is None:
            return ts.replace(tzinfo=timezone.utc)
        return ts
    try:
        ts_str = str(ts).strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def timestamp_to_decimal_hour(dt: datetime) -> float:
    """
    Converts a datetime object into decimal hours (0.0 to 23.999...).
    Example: 08:30:00 -> 8.5, 14:15:00 -> 14.25
    """
    return dt.hour + (dt.minute / 60.0) + (dt.second / 3600.0)


def extract_app_identifier(resource: Optional[str], details: Optional[Dict[str, Any]]) -> Optional[str]:
    """
    Extracts a normalized application or service identifier from resource URI and details dict.
    Examples:
    - s3://vault/... -> 'S3_Storage'
    - SharePoint://HR/... -> 'SharePoint'
    - Exchange://Mailbox/... -> 'Exchange_Mail'
    - k8s://prod-cluster-01.corp -> 'Kubernetes'
    - ActiveDirectory://DC-01/... -> 'ActiveDirectory'
    - USB://Kingston... -> 'USB_Storage'
    - https://grc.enterprise.corp -> 'GRC_Portal'
    - details.tool == 'PowerShell_AD_Module' -> 'PowerShell_AD_Module'
    """
    if isinstance(details, dict):
        if details.get("tool"):
            return str(details["tool"]).strip()
        if details.get("vpn_client"):
            return f"VPN_{str(details['vpn_client']).strip()}"
        if details.get("audit_module"):
            return str(details["audit_module"]).strip()
        if details.get("source_system"):
            return str(details["source_system"]).strip()
        if details.get("application"):
            return str(details["application"]).strip()
        if details.get("app"):
            return str(details["app"]).strip()

    if not resource:
        return None

    res_str = str(resource).strip()
    if "://" in res_str:
        scheme, remainder = res_str.split("://", 1)
        scheme_upper = scheme.upper()
        if scheme_upper == "S3":
            return "S3_Storage"
        if scheme_upper in ("SHAREPOINT", "ONEDRIVE"):
            return "SharePoint"
        if scheme_upper in ("EXCHANGE", "MAILBOX", "SMTP"):
            return "Exchange_Mail"
        if scheme_upper in ("K8S", "KUBERNETES"):
            return "Kubernetes"
        if scheme_upper in ("ACTIVEDIRECTORY", "LDAP", "AD"):
            return "ActiveDirectory"
        if scheme_upper == "USB":
            return "USB_Storage"
        if scheme_upper in ("HTTP", "HTTPS"):
            # Extract domain/host from URL
            host = remainder.split("/")[0].split(":")[0]
            if host:
                return f"Web_{host}"
            return "Web_Portal"
        return scheme

    if res_str.startswith("http://") or res_str.startswith("https://"):
        host = res_str.split("//", 1)[1].split("/")[0].split(":")[0]
        return f"Web_{host}" if host else "Web_Portal"

    if res_str.lower().endswith(".tar.gz") or res_str.lower().endswith(".zip"):
        return "Archive_Vault"
    if res_str.lower().endswith(".pdf") or res_str.lower().endswith(".docx"):
        return "Document_Store"

    return res_str.split("/")[0] if "/" in res_str else res_str


# =====================================================================
# Individual Indicator Calculation Engines
# =====================================================================

def calculate_login_time_baseline(
    logs: List[Dict[str, Any]],
    employee_id: str,
    min_samples: int = MIN_SAMPLE_SIZE,
) -> Optional[Dict[str, Any]]:
    """
    Indicator 1: Login Times (avg_login_hour).
    Converts timestamps of 'login' events to decimal hours and computes
    mean and sample standard deviation.
    Enforces minimum sample size (default: 5).
    """
    login_hours: List[float] = []

    for log in logs:
        if str(log.get("event_type", "")).lower() != "login":
            continue
        dt = parse_timestamp(log.get("timestamp"))
        if dt is None:
            continue
        login_hours.append(timestamp_to_decimal_hour(dt))

    sample_size = len(login_hours)
    if sample_size < min_samples:
        logger.debug(
            "Employee %s skipped for avg_login_hour: %d/%d observations.",
            employee_id, sample_size, min_samples
        )
        return None

    mean_val = round(calculate_mean(login_hours), 2)
    std_val = round(calculate_sample_std_dev(login_hours, mean=mean_val), 2)

    return {
        "employee_id": employee_id,
        "indicator": "avg_login_hour",
        "typical_value": mean_val,
        "std_deviation": std_val,
        "sample_size": sample_size,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }


def calculate_resource_access_frequency_baseline(
    logs: List[Dict[str, Any]],
    employee_id: str,
    min_samples: int = MIN_SAMPLE_SIZE,
) -> Optional[Dict[str, Any]]:
    """
    Indicator 2: Resource Access Frequency (resource_access_frequency).
    Groups non-login operational access events by calendar day and calculates
    the mean daily access count and sample standard deviation.
    Enforces minimum sample size of 5 active access days.
    """
    # Group relevant operational events by day (YYYY-MM-DD)
    daily_counts: Dict[str, int] = defaultdict(int)

    for log in logs:
        et = str(log.get("event_type", "")).lower()
        if et in ("login",):  # Logins are tracked separately in login baseline
            continue
        dt = parse_timestamp(log.get("timestamp"))
        if dt is None:
            continue
        date_key = dt.strftime("%Y-%m-%d")
        daily_counts[date_key] += 1

    sample_size = len(daily_counts)
    if sample_size < min_samples:
        logger.debug(
            "Employee %s skipped for resource_access_frequency: %d/%d active days.",
            employee_id, sample_size, min_samples
        )
        return None

    counts_list = [float(c) for c in daily_counts.values()]
    mean_val = round(calculate_mean(counts_list), 2)
    std_val = round(calculate_sample_std_dev(counts_list, mean=mean_val), 2)

    return {
        "employee_id": employee_id,
        "indicator": "resource_access_frequency",
        "typical_value": mean_val,
        "std_deviation": std_val,
        "sample_size": sample_size,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }


def calculate_device_usage_baseline(
    logs: List[Dict[str, Any]],
    employee_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Indicator 3: Device Usage (device_usage).
    Set-membership indicator: extracts unique device identifiers.
    Does not force meaningless numeric averages or std deviations.
    """
    known_devices: Set[str] = set()
    valid_observations = 0

    for log in logs:
        dev = log.get("device") or log.get("device_id")
        if not dev and isinstance(log.get("details"), dict):
            dev = log["details"].get("device") or log["details"].get("device_id")
        if dev and str(dev).strip().upper() not in ("N/A", "NONE", "NULL", ""):
            known_devices.add(str(dev).strip())
            valid_observations += 1

    if not known_devices:
        logger.debug("Employee %s has no device observations.", employee_id)
        return None

    return {
        "employee_id": employee_id,
        "indicator": "device_usage",
        "known_values": sorted(list(known_devices)),
        "sample_size": valid_observations,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }


def calculate_application_usage_baseline(
    logs: List[Dict[str, Any]],
    employee_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Indicator 4: Application Usage (application_usage).
    Set-membership indicator: extracts unique application and service identifiers
    from resources and event details.
    """
    known_apps: Set[str] = set()
    valid_observations = 0

    for log in logs:
        app_id = extract_app_identifier(log.get("resource"), log.get("details"))
        if app_id and str(app_id).strip().upper() not in ("N/A", "NONE", "NULL", ""):
            known_apps.add(str(app_id).strip())
            valid_observations += 1

    if not known_apps:
        logger.debug("Employee %s has no application observations.", employee_id)
        return None

    return {
        "employee_id": employee_id,
        "indicator": "application_usage",
        "known_values": sorted(list(known_apps)),
        "sample_size": valid_observations,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }


def calculate_data_transfer_volume_baseline(
    logs: List[Dict[str, Any]],
    employee_id: str,
    min_samples: int = MIN_SAMPLE_SIZE,
) -> Optional[Dict[str, Any]]:
    """
    Indicator 5: Data Transfer Volume (data_transfer_volume).
    Aggregates valid file upload, download, and data transfer sizes by day in MB.
    Calculates mean daily volume and sample standard deviation.
    Enforces minimum sample size of 5 transfer days.
    """
    daily_mb: Dict[str, float] = defaultdict(float)

    for log in logs:
        et = str(log.get("event_type", "")).lower()
        if et not in ("file_download", "file_upload", "data_transfer"):
            continue

        details = log.get("details")
        size_mb = 0.0
        if isinstance(details, dict):
            raw_size = (
                details.get("size_mb")
                or details.get("download_size_mb")
                or details.get("file_size_mb")
                or details.get("size")
            )
            if raw_size is not None:
                try:
                    size_mb = float(raw_size)
                except (ValueError, TypeError):
                    size_mb = 0.0

        if size_mb <= 0.0:
            continue

        dt = parse_timestamp(log.get("timestamp"))
        if dt is None:
            continue

        date_key = dt.strftime("%Y-%m-%d")
        daily_mb[date_key] += size_mb

    sample_size = len(daily_mb)
    if sample_size < min_samples:
        logger.debug(
            "Employee %s skipped for data_transfer_volume: %d/%d transfer days.",
            employee_id, sample_size, min_samples
        )
        return None

    daily_totals = list(daily_mb.values())
    mean_val = round(calculate_mean(daily_totals), 2)
    std_val = round(calculate_sample_std_dev(daily_totals, mean=mean_val), 2)

    return {
        "employee_id": employee_id,
        "indicator": "data_transfer_volume",
        "typical_value": mean_val,
        "std_deviation": std_val,
        "sample_size": sample_size,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }


def calculate_communication_patterns_baseline(
    logs: List[Dict[str, Any]],
    employee_id: str,
    min_samples: int = MIN_SAMPLE_SIZE,
) -> Optional[Dict[str, Any]]:
    """
    Indicator 6: Communication Patterns (communication_patterns).
    Measures email activity frequency by day for supported 'email_activity' events.
    Calculates mean daily email communication count and sample standard deviation.
    Enforces minimum sample size of 5 active communication days.
    """
    daily_email_counts: Dict[str, int] = defaultdict(int)

    for log in logs:
        if str(log.get("event_type", "")).lower() != "email_activity":
            continue
        dt = parse_timestamp(log.get("timestamp"))
        if dt is None:
            continue
        date_key = dt.strftime("%Y-%m-%d")
        daily_email_counts[date_key] += 1

    sample_size = len(daily_email_counts)
    if sample_size < min_samples:
        logger.debug(
            "Employee %s skipped for communication_patterns: %d/%d active days.",
            employee_id, sample_size, min_samples
        )
        return None

    counts_list = [float(c) for c in daily_email_counts.values()]
    mean_val = round(calculate_mean(counts_list), 2)
    std_val = round(calculate_sample_std_dev(counts_list, mean=mean_val), 2)

    return {
        "employee_id": employee_id,
        "indicator": "communication_patterns",
        "typical_value": mean_val,
        "std_deviation": std_val,
        "sample_size": sample_size,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }


# =====================================================================
# Profile Engine Orchestrator & Persistence
# =====================================================================

def fetch_employee_activity_logs(
    employee_id: str,
    lookback_days: Optional[int] = DEFAULT_LOOKBACK_DAYS,
    limit: int = 5000,
) -> List[Dict[str, Any]]:
    """
    Retrieves activity logs for a specific employee within the lookback window.
    Defaults to 90 days.
    """
    res = mongo_service.query_activity_logs(employee_id=employee_id, limit=limit)
    all_logs = res.get("items", [])

    if not lookback_days or lookback_days <= 0:
        return all_logs

    cutoff_dt = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    filtered = []
    for log in all_logs:
        dt = parse_timestamp(log.get("timestamp"))
        if dt is not None and dt >= cutoff_dt:
            filtered.append(log)

    return filtered


def build_employee_profile(
    employee_id: str,
    lookback_days: Optional[int] = DEFAULT_LOOKBACK_DAYS,
    logs: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Computes all six behavioral indicators for a given employee.
    Returns:
    {
        "employee_id": employee_id,
        "generated": { indicator: baseline_doc, ... },
        "skipped": { indicator: reason, ... },
        "total_logs_analyzed": count,
    }
    """
    if logs is None:
        logs = fetch_employee_activity_logs(employee_id, lookback_days=lookback_days)

    generated: Dict[str, Dict[str, Any]] = {}
    skipped: Dict[str, str] = {}

    # 1. Login Times
    login_b = calculate_login_time_baseline(logs, employee_id)
    if login_b:
        generated["avg_login_hour"] = login_b
    else:
        login_count = sum(1 for l in logs if str(l.get("event_type", "")).lower() == "login")
        skipped["avg_login_hour"] = f"Insufficient observations ({login_count}/{MIN_SAMPLE_SIZE} logins)"

    # 2. Resource Access Frequency
    raf_b = calculate_resource_access_frequency_baseline(logs, employee_id)
    if raf_b:
        generated["resource_access_frequency"] = raf_b
    else:
        distinct_days = len(set(
            parse_timestamp(l.get("timestamp")).strftime("%Y-%m-%d")
            for l in logs
            if parse_timestamp(l.get("timestamp")) and str(l.get("event_type", "")).lower() != "login"
        ))
        skipped["resource_access_frequency"] = f"Insufficient active days ({distinct_days}/{MIN_SAMPLE_SIZE} days)"

    # 3. Device Usage (Categorical)
    dev_b = calculate_device_usage_baseline(logs, employee_id)
    if dev_b:
        generated["device_usage"] = dev_b
    else:
        skipped["device_usage"] = "No device identifiers recorded in activity logs"

    # 4. Application Usage (Categorical)
    app_b = calculate_application_usage_baseline(logs, employee_id)
    if app_b:
        generated["application_usage"] = app_b
    else:
        skipped["application_usage"] = "No application or service identifiers recorded"

    # 5. Data Transfer Volume
    dtv_b = calculate_data_transfer_volume_baseline(logs, employee_id)
    if dtv_b:
        generated["data_transfer_volume"] = dtv_b
    else:
        transfer_days = len(set(
            parse_timestamp(l.get("timestamp")).strftime("%Y-%m-%d")
            for l in logs
            if parse_timestamp(l.get("timestamp")) and str(l.get("event_type", "")).lower() in ("file_download", "file_upload", "data_transfer")
        ))
        skipped["data_transfer_volume"] = f"Insufficient transfer days ({transfer_days}/{MIN_SAMPLE_SIZE} days)"

    # 6. Communication Patterns
    comm_b = calculate_communication_patterns_baseline(logs, employee_id)
    if comm_b:
        generated["communication_patterns"] = comm_b
    else:
        email_days = len(set(
            parse_timestamp(l.get("timestamp")).strftime("%Y-%m-%d")
            for l in logs
            if parse_timestamp(l.get("timestamp")) and str(l.get("event_type", "")).lower() == "email_activity"
        ))
        skipped["communication_patterns"] = f"Insufficient email communication days ({email_days}/{MIN_SAMPLE_SIZE} days)"

    return {
        "employee_id": employee_id,
        "generated": generated,
        "skipped": skipped,
        "total_logs_analyzed": len(logs),
    }


def save_employee_baselines(
    employee_id: str,
    lookback_days: Optional[int] = DEFAULT_LOOKBACK_DAYS,
) -> Dict[str, Any]:
    """
    Computes and upserts all eligible behavioral baselines for an employee
    into MongoDB collection 'behavioral_baselines' (or persistent dev store).
    Prevents duplicates through upsert operations.
    """
    profile = build_employee_profile(employee_id, lookback_days=lookback_days)
    saved: Dict[str, Dict[str, Any]] = {}

    for indicator, baseline_data in profile["generated"].items():
        doc = mongo_service.upsert_baseline(baseline_data)
        saved[indicator] = doc

    return {
        "employee_id": employee_id,
        "saved_count": len(saved),
        "skipped_count": len(profile["skipped"]),
        "saved": saved,
        "skipped": profile["skipped"],
        "total_logs_analyzed": profile["total_logs_analyzed"],
    }


def get_employee_baselines(employee_id: str) -> List[Dict[str, Any]]:
    """Retrieves all stored baselines for a specific employee."""
    return mongo_service.get_baselines(employee_id=employee_id)

"""
ITBIS Behavioral Intelligence Platform - Machine Learning Feature Engineering
Milestone 2: Days 17-18

Builds standardized daily behavioral feature vectors per employee per UTC day
from activity telemetry logs.

Features extracted per (employee_id, UTC date):
1. avg_login_hour: Average decimal hour (0.0 - 23.999) of login events in UTC.
2. download_count: Total count of file download events.
3. total_download_mb: Total volume in megabytes transferred across download events.
4. unique_devices: Count of distinct hardware devices utilized.
5. total_events: Total count of valid, deduplicated telemetry events.

Missing Measurement Policy:
- avg_login_hour: When an employee records activity on a given day but has NO login
  events, avg_login_hour is recorded as None (missing measurement). It is NOT set
  to 0.0, because 0.0 represents a midnight login (00:00 UTC) which would fabricate
  an artificial off-hours anomaly. For dense matrix ML preparation, an explicit
  imputation policy replaces None with a configured default (default: 12.0 UTC / midday).
- download_count & total_download_mb: If an employee performed zero downloads on an
  active day, these are recorded as 0 and 0.0 respectively (true observed absence of downloads).
- unique_devices: Recorded as 0 if no device identifiers were logged, or the count of
  distinct non-empty device names.
"""

import json
import logging
import math
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple, Union

logger = logging.getLogger("itbis.ml_features")

FEATURE_NAMES = [
    "avg_login_hour",
    "download_count",
    "total_download_mb",
    "unique_devices",
    "total_events",
]


def parse_utc_timestamp(ts: Any) -> Optional[datetime]:
    """
    Parses diverse timestamp representations into a timezone-aware UTC datetime.
    Handles ISO-8601 strings, 'Z' suffixes, epoch numbers, and datetime objects.
    Returns None if malformed or missing, without raising exceptions.
    """
    if ts is None:
        return None

    if isinstance(ts, datetime):
        if ts.tzinfo is None:
            return ts.replace(tzinfo=timezone.utc)
        return ts.astimezone(timezone.utc)

    if isinstance(ts, (int, float)):
        try:
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        except (ValueError, OverflowError, OSError):
            return None

    if isinstance(ts, str):
        cleaned = ts.strip()
        if not cleaned:
            return None
        # Handle trailing Z
        if cleaned.endswith("Z") or cleaned.endswith("z"):
            cleaned = cleaned[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(cleaned)
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except (ValueError, TypeError):
            # Attempt alternative common format parsing
            for fmt in (
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%d",
            ):
                try:
                    dt = datetime.strptime(cleaned, fmt)
                    return dt.replace(tzinfo=timezone.utc)
                except ValueError:
                    continue
            logger.debug("Failed to parse timestamp string: %s", ts)
            return None

    return None


def extract_daily_features(
    activity_logs: List[Dict[str, Any]],
    deduplicate: bool = True,
) -> List[Dict[str, Any]]:
    """
    Aggregates activity telemetry logs into daily feature records per employee per UTC day.

    Args:
        activity_logs: List of activity log dictionaries.
        deduplicate: Whether to filter out duplicate log records.

    Returns:
        List of daily feature dictionaries sorted by (employee_id, date).
        Each record contains:
          - employee_id: str
          - date: str (YYYY-MM-DD in UTC)
          - avg_login_hour: Optional[float] (None if no login occurred)
          - download_count: int
          - total_download_mb: float
          - unique_devices: int
          - total_events: int
    """
    if not activity_logs:
        return []

    # Step 1: Filter and optionally deduplicate events
    valid_events = []
    seen_ids: Set[str] = set()
    seen_tuples: Set[Tuple] = set()

    for log in activity_logs:
        if not isinstance(log, dict):
            continue

        emp_id = str(log.get("employee_id") or "").strip()
        if not emp_id:
            continue

        raw_ts = log.get("timestamp")
        dt_utc = parse_utc_timestamp(raw_ts)
        if dt_utc is None:
            # Skip records with unparseable or missing timestamps
            logger.debug("Skipping event with invalid timestamp: %s", raw_ts)
            continue

        if deduplicate:
            log_id = str(log.get("id") or log.get("_id") or "")
            if log_id:
                if log_id in seen_ids:
                    continue
                seen_ids.add(log_id)
            else:
                event_type = str(log.get("event_type") or "").strip().lower()
                action = str(log.get("action") or "").strip()
                device = str(log.get("device") or "").strip()
                details_repr = json.dumps(log.get("details") or {}, sort_keys=True)
                sig = (emp_id, dt_utc.isoformat(), event_type, action, device, details_repr)
                if sig in seen_tuples:
                    continue
                seen_tuples.add(sig)

        valid_events.append((emp_id, dt_utc, log))

    if not valid_events:
        return []

    # Step 2: Group events by (employee_id, UTC_day)
    # Using strict UTC day boundary formatted as YYYY-MM-DD
    grouped_events: Dict[Tuple[str, str], List[Tuple[datetime, Dict[str, Any]]]] = defaultdict(list)
    for emp_id, dt_utc, log in valid_events:
        utc_date_str = dt_utc.strftime("%Y-%m-%d")
        grouped_events[(emp_id, utc_date_str)].append((dt_utc, log))

    # Step 3: Compute daily feature aggregations
    daily_records: List[Dict[str, Any]] = []

    for (emp_id, date_str), day_events in sorted(grouped_events.items()):
        total_events = len(day_events)

        # 1. Login hour tracking
        login_hours: List[float] = []
        # 2. Downloads tracking
        download_count = 0
        total_download_mb = 0.0
        # 3. Unique devices tracking
        devices_set: Set[str] = set()

        for dt_utc, log in day_events:
            et = str(log.get("event_type") or "").strip().lower()
            action = str(log.get("action") or "").strip().lower()
            details = log.get("details") if isinstance(log.get("details"), dict) else {}

            # Device collection
            dev = (
                log.get("device")
                or log.get("device_id")
                or details.get("device")
                or details.get("device_id")
            )
            if dev and isinstance(dev, str) and dev.strip():
                devices_set.add(dev.strip())

            # Login detection
            if et == "login":
                decimal_hour = dt_utc.hour + (dt_utc.minute / 60.0) + (dt_utc.second / 3600.0)
                login_hours.append(decimal_hour)

            # Download detection
            if et in ("file_download", "data_transfer") or "download" in action:
                download_count += 1
                # Extract file size in MB
                raw_size = (
                    details.get("size_mb")
                    or details.get("file_size_mb")
                    or details.get("download_size_mb")
                    or details.get("size")
                )
                if raw_size is not None:
                    try:
                        size_f = float(raw_size)
                        if math.isfinite(size_f) and size_f > 0:
                            total_download_mb += size_f
                    except (ValueError, TypeError):
                        pass

        # Calculate average login hour (None if no login occurred on this day)
        avg_login_hour: Optional[float] = None
        if login_hours:
            avg_login_hour = round(sum(login_hours) / len(login_hours), 4)

        daily_records.append({
            "employee_id": emp_id,
            "date": date_str,
            "avg_login_hour": avg_login_hour,
            "download_count": download_count,
            "total_download_mb": round(total_download_mb, 4),
            "unique_devices": len(devices_set),
            "total_events": total_events,
        })

    return daily_records


def prepare_feature_matrix(
    daily_records: List[Dict[str, Any]],
    default_login_hour: float = 12.0,
    feature_names: Optional[List[str]] = None,
) -> Tuple[Any, List[Dict[str, Any]], List[str]]:
    """
    Transforms daily feature dictionaries into a 2D numeric matrix ready for
    scikit-learn models like IsolationForest.

    Policy on missing login measurements:
    Scikit-learn tree estimators require finite numeric entries. When avg_login_hour
    is None (indicating no logins occurred on that day), it is imputed with
    default_login_hour (default: 12.0 UTC / midday). It is NOT imputed with 0.0
    to prevent fabricating midnight login anomalies.

    Args:
        daily_records: List of feature dictionaries from extract_daily_features.
        default_login_hour: Decimal hour to impute when avg_login_hour is None.
        feature_names: List of numeric feature keys to extract (default: FEATURE_NAMES).

    Returns:
        (numpy.ndarray of shape (N, D), valid_records, feature_names)
    """
    import numpy as np

    features_to_use = feature_names or FEATURE_NAMES

    if not daily_records:
        return np.empty((0, len(features_to_use)), dtype=np.float64), [], features_to_use

    rows = []
    valid_records = []

    for rec in daily_records:
        row_vals = []
        is_valid = True
        for feat in features_to_use:
            val = rec.get(feat)
            if feat == "avg_login_hour":
                if val is None:
                    # Impute missing login hour with midday baseline
                    val = float(default_login_hour)
                else:
                    try:
                        val = float(val)
                    except (ValueError, TypeError):
                        val = float(default_login_hour)
            else:
                if val is None:
                    val = 0.0
                else:
                    try:
                        val = float(val)
                    except (ValueError, TypeError):
                        is_valid = False
                        break

            if not math.isfinite(val):
                is_valid = False
                break

            row_vals.append(val)

        if is_valid and len(row_vals) == len(features_to_use):
            rows.append(row_vals)
            valid_records.append(rec)

    if not rows:
        return np.empty((0, len(features_to_use)), dtype=np.float64), [], features_to_use

    X = np.array(rows, dtype=np.float64)
    return X, valid_records, features_to_use


def build_features_from_storage(
    mongo_service: Optional[Any] = None,
    employee_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieves activity logs from persistent storage (MongoDB or fallback JSON)
    and extracts daily feature rows.
    """
    if mongo_service is None:
        from app.mongodb import mongo_service as default_service
        mongo_service = default_service

    # Query activity telemetry logs
    if employee_id:
        result = mongo_service.query_activity_logs(employee_id=employee_id, limit=2000)
    else:
        result = mongo_service.query_activity_logs(limit=5000)

    logs = result.get("items", [])
    return extract_daily_features(logs)

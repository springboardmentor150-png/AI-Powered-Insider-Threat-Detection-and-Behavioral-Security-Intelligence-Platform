"""
Combined Anomaly Report Routes (Milestone 2: Days 19-20)
ITBIS: AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform.

Endpoints:
1. GET /anomalies/summary (Day 20)
   - High-level enterprise summary of detected behavioral anomalies.
   - Total rule-based vs ML anomalies, severity distribution, top anomalous employees,
     and temporal volume breakdown over time.
   - Deterministic ordering and empty-data resilience.

2. GET /anomalies/{employee_id} (Day 19)
   - Employee-specific unified behavioral threat intelligence report.
   - Severity-sorted rule-based anomalies (critical -> high -> medium -> low).
   - Score-sorted ML Isolation Forest anomalies (most anomalous negative score first).
   - Safe deduplication and distinct evidence preservation.
"""

import math
import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import Employee, User
from app.mongodb import mongo_service
from app.schemas import (
    EmployeeAnomalyReportResponse,
    AnomalySummaryResponse,
    TopEmployeeAnomalyItem,
    DailyAnomalyCountItem,
)
from app.security import get_current_user

logger = logging.getLogger("itbis.anomaly_routes")

router = APIRouter(prefix="/anomalies", tags=["Combined Anomaly Intelligence (Days 19-20)"])

SEVERITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "informational": 4,
    "info": 4,
}


def _extract_ml_score(item: Dict[str, Any]) -> float:
    """
    Extracts the numeric Isolation Forest decision_function anomaly score.
    In ml_anomaly.py, lower / more negative values indicate greater outlier severity.
    """
    details = item.get("details")
    if isinstance(details, dict):
        score_val = details.get("anomaly_score")
        if score_val is not None:
            try:
                return float(score_val)
            except (ValueError, TypeError):
                pass

    obs = item.get("observed_value")
    if isinstance(obs, (int, float)):
        return float(obs)
    if isinstance(obs, str) and "Score:" in obs:
        try:
            part = obs.split("Score:")[1].split()[0].strip()
            return float(part)
        except Exception:
            pass

    return 999.0


def _parse_timestamp_for_sorting(ts_str: Optional[str]) -> float:
    """Converts ISO timestamp string into a float epoch for reverse chronological sorting."""
    if not ts_str:
        return 0.0
    try:
        clean = ts_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean)
        return dt.timestamp()
    except Exception:
        return 0.0


# =====================================================================
# Day 20: GET /anomalies/summary
# Note: Defined before /{employee_id} so '/summary' is not captured as an employee ID.
# =====================================================================

@router.get("/summary", response_model=AnomalySummaryResponse)
def get_anomaly_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Returns an enterprise-wide summary based on actual persisted anomaly records:
    - Total rule-based anomalies
    - Total ML anomalies
    - Counts by severity for rule-based anomalies
    - Top employees by anomaly count (deterministically sorted)
    - Anomaly counts over time (deterministically sorted by UTC date)
    - Distinct count of unique employees affected
    """
    # Retrieve all persisted anomaly records from mongo_service (using dev buffer or MongoDB)
    all_anomalies = mongo_service.get_anomalies(limit=10000)

    # Optional MongoDB aggregation when connected
    if mongo_service.is_connected and mongo_service._anomalies_collection is not None:
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$employee_id",
                        "rule_count": {
                            "$sum": {
                                "$cond": [
                                    {"$and": [
                                        {"$ne": ["$anomaly_type", "ML_ISOLATION_FOREST"]},
                                        {"$ne": ["$indicator", "isolation_forest"]}
                                    ]},
                                    1,
                                    0
                                ]
                            }
                        },
                        "ml_count": {
                            "$sum": {
                                "$cond": [
                                    {"$or": [
                                        {"$eq": ["$anomaly_type", "ML_ISOLATION_FOREST"]},
                                        {"$eq": ["$indicator", "isolation_forest"]}
                                    ]},
                                    1,
                                    0
                                ]
                            }
                        },
                        "total_count": {"$sum": 1}
                    }
                },
                {"$sort": {"rule_count": -1, "total_count": -1, "_id": 1}},
                {"$limit": 10}
            ]
            mongo_service._anomalies_collection.aggregate(pipeline)
        except Exception as e:
            logger.warning("MongoDB aggregation error: %s. Using persistent storage aggregation.", e)

    total_rule = 0
    total_ml = 0
    severity_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "informational": 0,
    }

    # Tracking per employee: emp_id -> {"rule": int, "ml": int, "highest_sev": str, "highest_order": int}
    emp_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "rule": 0,
        "ml": 0,
        "highest_sev": None,
        "highest_order": 99,
    })

    # Tracking per date: date_str -> {"total": int, "rule": int, "ml": int}
    daily_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {
        "total": 0,
        "rule": 0,
        "ml": 0,
    })

    unique_employees_set = set()

    for item in all_anomalies:
        emp_id = str(item.get("employee_id") or "").strip()
        if not emp_id:
            continue

        unique_employees_set.add(emp_id)

        anom_type = str(item.get("anomaly_type") or "").strip()
        indicator = str(item.get("indicator") or "").strip()
        is_ml = (anom_type == "ML_ISOLATION_FOREST" or indicator == "isolation_forest")

        # Extract date for temporal aggregation
        ts_str = item.get("detection_timestamp") or item.get("timestamp") or ""
        details = item.get("details") if isinstance(item.get("details"), dict) else {}
        date_str = details.get("date")

        if not date_str and ts_str:
            try:
                date_str = ts_str[:10]  # YYYY-MM-DD
            except Exception:
                date_str = "Unknown"
        if not date_str:
            date_str = "Unknown"

        daily_stats[date_str]["total"] += 1

        if is_ml:
            total_ml += 1
            emp_stats[emp_id]["ml"] += 1
            daily_stats[date_str]["ml"] += 1
        else:
            total_rule += 1
            emp_stats[emp_id]["rule"] += 1
            daily_stats[date_str]["rule"] += 1

            raw_sev = str(item.get("severity") or "").lower().strip()
            if raw_sev in severity_counts:
                severity_counts[raw_sev] += 1

            # Update highest severity for this employee
            order = SEVERITY_ORDER.get(raw_sev, 99)
            if order < emp_stats[emp_id]["highest_order"]:
                emp_stats[emp_id]["highest_order"] = order
                emp_stats[emp_id]["highest_sev"] = raw_sev

    # Resolve employee metadata from PostgreSQL / SQLite database
    emp_records = db.query(Employee).all()
    emp_meta = {e.employee_id: (e.name, e.department) for e in emp_records}

    top_employees_list: List[TopEmployeeAnomalyItem] = []
    for emp_id, st in emp_stats.items():
        tot = st["rule"] + st["ml"]
        name, dept = emp_meta.get(emp_id, (None, None))
        top_employees_list.append(TopEmployeeAnomalyItem(
            employee_id=emp_id,
            employee_name=name or emp_id,
            department=dept,
            total_anomalies=tot,
            rule_anomalies=st["rule"],
            ml_anomalies=st["ml"],
            anomaly_count=st["rule"],
            highest_severity=st["highest_sev"],
        ))

    # Deterministic sorting for top 10 employees ranked by rule-based anomaly count:
    # Primary: rule_anomalies descending
    # Secondary: total_anomalies descending
    # Tertiary: employee_id ascending
    top_employees_list.sort(key=lambda x: (-x.rule_anomalies, -x.total_anomalies, x.employee_id))
    top_10 = top_employees_list[:10]

    # Deterministic sorting for anomalies over time:
    anomalies_over_time: List[DailyAnomalyCountItem] = []
    for d_str, counts in sorted(daily_stats.items()):
        if d_str != "Unknown":
            anomalies_over_time.append(DailyAnomalyCountItem(
                date=d_str,
                total=counts["total"],
                rule_count=counts["rule"],
                ml_count=counts["ml"],
            ))

    return AnomalySummaryResponse(
        total_anomalies=total_rule + total_ml,
        total_rule_anomalies=total_rule,
        total_ml_anomalies=total_ml,
        unique_employees=len(unique_employees_set),
        counts_by_severity=severity_counts,
        top_employees=top_10,
        top_10_employees=top_10,
        anomalies_over_time=anomalies_over_time,
    )


# =====================================================================
# Day 19: GET /anomalies/{employee_id}
# =====================================================================

@router.get("/{employee_id}", response_model=EmployeeAnomalyReportResponse)
def get_employee_anomaly_report(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Returns a unified anomaly intelligence report for a specific employee:
    - Validates employee existence in the database (404 if not found).
    - Returns empty lists and zero counts if employee has no recorded anomalies (200 OK).
    - Rule-based anomalies sorted by severity: critical -> high -> medium -> low.
    - ML anomalies sorted by most anomalous score first (ascending decision_function score).
    - Safe deduplication of duplicate records while preserving distinct detector evidence.
    """
    # Verify employee exists in registry
    is_numeric = employee_id.isdigit()
    employee = db.query(Employee).filter(
        or_(
            Employee.employee_id == employee_id,
            Employee.id == int(employee_id) if is_numeric else False,
        )
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{employee_id}' not found in registry"
        )

    emp_code = employee.employee_id

    # Retrieve all anomalies for this employee from persistent storage
    raw_anomalies = mongo_service.get_anomalies(employee_id=emp_code, limit=2000)

    rule_anomalies: List[Dict[str, Any]] = []
    ml_anomalies: List[Dict[str, Any]] = []

    seen_rule_sigs = set()
    seen_ml_sigs = set()

    severity_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "informational": 0,
    }

    for item in raw_anomalies:
        anom_type = str(item.get("anomaly_type") or "").strip()
        indicator = str(item.get("indicator") or "").strip()
        details = item.get("details") if isinstance(item.get("details"), dict) else {}
        ts = str(item.get("detection_timestamp") or item.get("timestamp") or "")

        is_ml = (anom_type == "ML_ISOLATION_FOREST" or indicator == "isolation_forest")

        if is_ml:
            # ML Anomaly
            ml_date = str(details.get("date") or ts[:10])
            score = _extract_ml_score(item)
            ml_sig = (emp_code, ml_date, round(score, 4))
            if ml_sig in seen_ml_sigs:
                continue
            seen_ml_sigs.add(ml_sig)

            feature_vals = details.get("features") if isinstance(details.get("features"), dict) else item.get("feature_values")

            ml_anomalies.append({
                "id": str(item.get("id") or item.get("_id") or ""),
                "employee_id": emp_code,
                "anomaly_type": "ML_ISOLATION_FOREST",
                "indicator": "isolation_forest",
                "anomaly_score": score,
                "anomaly_flag": int(details.get("anomaly_flag", -1)),
                "date": ml_date,
                "detection_timestamp": ts or None,
                "observed_value": item.get("observed_value"),
                "expected_baseline": item.get("expected_baseline") or "Normal operational behavior (score >= 0.0)",
                "feature_values": feature_vals,
                "details": details,
            })
        else:
            # Rule-Based Anomaly
            obs_repr = str(item.get("observed_value"))
            rule_sig = (emp_code, anom_type, indicator, obs_repr, ts[:16])
            if rule_sig in seen_rule_sigs:
                continue
            seen_rule_sigs.add(rule_sig)

            sev = str(item.get("severity") or "medium").lower().strip()
            if sev in severity_counts:
                severity_counts[sev] += 1

            rule_anomalies.append({
                "id": str(item.get("id") or item.get("_id") or ""),
                "employee_id": emp_code,
                "anomaly_type": anom_type,
                "indicator": indicator,
                "severity": sev,
                "observed_value": item.get("observed_value"),
                "typical_value": item.get("typical_value"),
                "expected_baseline": item.get("expected_baseline"),
                "deviation_ratio": item.get("deviation_ratio"),
                "detection_timestamp": ts or None,
                "details": details,
            })

    # Sort Rule-Based Anomalies by severity: critical -> high -> medium -> low
    # Within same severity, sort newest first
    rule_anomalies.sort(
        key=lambda x: (
            SEVERITY_ORDER.get(str(x.get("severity", "")).lower(), 99),
            -_parse_timestamp_for_sorting(x.get("detection_timestamp")),
        )
    )

    # Sort ML Anomalies by most anomalous score first
    # In Isolation Forest decision_function, lower / more negative indicates greater outlier severity
    ml_anomalies.sort(
        key=lambda x: (
            x.get("anomaly_score", 999.0),
            -_parse_timestamp_for_sorting(x.get("detection_timestamp")),
        )
    )

    tot = len(rule_anomalies) + len(ml_anomalies)
    return EmployeeAnomalyReportResponse(
        employee_id=emp_code,
        employee_name=employee.name,
        department=employee.department,
        total_flags=tot,
        total_anomalies=tot,
        total_rule_anomalies=len(rule_anomalies),
        total_ml_anomalies=len(ml_anomalies),
        severity_counts=severity_counts,
        rule_based_anomalies=rule_anomalies,
        ml_anomalies=ml_anomalies,
    )

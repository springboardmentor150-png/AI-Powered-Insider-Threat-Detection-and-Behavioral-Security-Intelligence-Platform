"""
ITBIS Insider Risk Scoring Engine (Milestone 3: Days 21-22)
AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform.

Calculates a normalized 0-100 composite insider risk score for an employee
by evaluating 5 standardized risk factors:
1. Behavioral Anomalies (35%): Broadest signal covering login, device, and ML anomalies.
2. Privilege Misuse (25%): High-impact unauthorized escalation or privilege modifications.
3. Data Access Violations (20%): Data exfiltration risk, excessive transfer volume or frequency.
4. Access Pattern Deviations (10%): Unrecognized hardware, unapproved applications, or unknown IPs.
5. Historical Security Events (10%): Prior verified security incidents from relational store.

Normalized Sub-Score Conversion:
- Each raw factor count is converted to a 0-100 scale using an empirical multiplier
  before applying executive weights, ensuring severe rare events are not overwhelmed
  by frequent benign fluctuations.
- All sub-scores are capped at min(..., 100.0).
- Final score lands strictly within 0.0 - 100.0.
"""

import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models import Employee, Incident
from app.mongodb import mongo_service

logger = logging.getLogger("itbis.risk_scoring")

# Standardized Executive Weights (Sum = 1.00 / 100%)
WEIGHTS = {
    "behavioral_anomalies": 0.35,
    "privilege_misuse": 0.25,
    "data_access_violations": 0.20,
    "access_pattern_deviations": 0.10,
    "historical_events": 0.10,
}

# Thresholds for converting raw counts into 0-100 sub-scores:
# - behavioral_anomalies: 10 occurrences -> 100 (multiplier: 10.0)
# - privilege_misuse: 4 occurrences -> 100 (multiplier: 25.0)
# - data_access_violations: 2.5 occurrences -> 100 (multiplier: 40.0)
# - access_pattern_deviations: 6.67 occurrences -> 100 (multiplier: 15.0)
# - historical_events: 5 incidents -> 100 (multiplier: 20.0)
FACTOR_MULTIPLIERS = {
    "behavioral_anomalies": 10.0,
    "privilege_misuse": 25.0,
    "data_access_violations": 40.0,
    "access_pattern_deviations": 15.0,
    "historical_events": 20.0,
}


def _get_employee_anomalies(employee_id: str) -> List[Dict[str, Any]]:
    """Retrieves all persisted anomaly records for an employee from mongo_service."""
    return mongo_service.get_anomalies(employee_id=employee_id, limit=2000)


def score_behavioral_anomalies(employee_id: str) -> float:
    """
    Sub-score for Behavioral Anomalies (35% weight).
    Captures unusual login times (off-hours deviation) and ML Isolation Forest anomalies.
    Maxes out at 10 occurrences (multiplier: 10.0).
    """
    anomalies = _get_employee_anomalies(employee_id)
    count = 0
    for a in anomalies:
        anom_type = str(a.get("anomaly_type") or "").strip().upper()
        indicator = str(a.get("indicator") or "").strip().lower()
        source = str(a.get("source") or "").strip().lower()

        # Behavioral anomalies are login/timing deviations and ML Isolation Forest flags
        is_timing_anom = anom_type.startswith("UNUSUAL_") or indicator == "avg_login_hour"
        is_ml_anom = (
            anom_type == "ML_ISOLATION_FOREST"
            or indicator == "isolation_forest"
            or source == "ml_anomaly"
            or (bool(a.get("is_anomaly")) and "PRIVILEGE" not in anom_type and "DEVICE" not in anom_type and "APPLICATION" not in anom_type)
        )
        if is_timing_anom or is_ml_anom:
            count += 1
    return float(min(count * FACTOR_MULTIPLIERS["behavioral_anomalies"], 100.0))


def score_privilege_misuse(employee_id: str) -> float:
    """
    Sub-score for Privilege Misuse (25% weight).
    Captures unauthorized privilege changes, role escalations, and administrative tampering.
    Maxes out at 4 occurrences (multiplier: 25.0).
    """
    anomalies = _get_employee_anomalies(employee_id)
    count = 0
    for a in anomalies:
        anom_type = str(a.get("anomaly_type") or "").strip().upper()
        indicator = str(a.get("indicator") or "").strip().lower()
        if (
            "PRIVILEGE" in anom_type
            or "ESCALATION" in anom_type
            or indicator in {"privilege_change", "privilege_misuse", "admin_escalation"}
        ):
            count += 1
    return float(min(count * FACTOR_MULTIPLIERS["privilege_misuse"], 100.0))


def score_data_access_violations(employee_id: str) -> float:
    """
    Sub-score for Data Access Violations (20% weight).
    Captures abnormal transfer volumes, excessive access frequencies, and exfiltration risks.
    Maxes out at 3 occurrences (multiplier: 40.0, cap 100.0).
    """
    anomalies = _get_employee_anomalies(employee_id)
    count = 0
    for a in anomalies:
        anom_type = str(a.get("anomaly_type") or "").strip().upper()
        indicator = str(a.get("indicator") or "").strip().lower()
        if (
            anom_type in {"ABNORMAL_DATA_TRANSFER", "EXCESSIVE_TRANSFER_FREQUENCY", "DATA_EXFILTRATION_RISK"}
            or "EXFILTRATION" in anom_type
            or indicator in {"data_transfer_volume", "resource_access_frequency"}
        ):
            count += 1
    return float(min(count * FACTOR_MULTIPLIERS["data_access_violations"], 100.0))


def score_access_pattern_deviations(employee_id: str) -> float:
    """
    Sub-score for Access Pattern Deviations (10% weight).
    Captures unapproved hardware, unauthorized applications, and unknown network vectors.
    Maxes out at 7 occurrences (multiplier: 15.0).
    """
    anomalies = _get_employee_anomalies(employee_id)
    count = 0
    for a in anomalies:
        anom_type = str(a.get("anomaly_type") or "").strip().upper()
        indicator = str(a.get("indicator") or "").strip().lower()
        if (
            anom_type in {"SUSPICIOUS_DEVICE", "UNAUTHORIZED_APPLICATION_ACCESS", "UNKNOWN_DEVICE", "UNKNOWN_APPLICATION", "UNKNOWN_IP"}
            or anom_type.startswith("UNKNOWN_")
            or indicator in {"device_usage", "application_usage"}
        ):
            count += 1
    return float(min(count * FACTOR_MULTIPLIERS["access_pattern_deviations"], 100.0))


def score_historical_events(employee_id: str, db: Session) -> float:
    """
    Sub-score for Historical Security Events (10% weight).
    Queries past confirmed security incidents recorded in PostgreSQL / SQLite.
    Maxes out at 5 historical incidents (multiplier: 20.0).
    """
    employee = db.query(Employee).filter(
        or_(
            Employee.employee_id == employee_id,
            Employee.id == int(employee_id) if employee_id.isdigit() else False,
        )
    ).first()
    if not employee:
        return 0.0

    count = db.query(Incident).filter(Incident.employee_id == employee.id).count()
    return float(min(count * FACTOR_MULTIPLIERS["historical_events"], 100.0))


def calculate_risk_score(employee_id: str, db: Session) -> Dict[str, Any]:
    """
    Computes the composite weighted insider risk score for an employee.

    Returns:
        dict:
            - employee_id: str
            - sub_scores: Dict[str, float] (0.0 - 100.0 per factor)
            - final_score: float (0.0 - 100.0, rounded to 1 decimal place)
            - risk_level: str ('Low', 'Medium', 'High', 'Critical')
    """
    sub_scores = {
        "behavioral_anomalies": score_behavioral_anomalies(employee_id),
        "privilege_misuse": score_privilege_misuse(employee_id),
        "data_access_violations": score_data_access_violations(employee_id),
        "access_pattern_deviations": score_access_pattern_deviations(employee_id),
        "historical_events": score_historical_events(employee_id, db),
    }

    final_score = sum(sub_scores[k] * WEIGHTS[k] for k in WEIGHTS)
    final_score = max(0.0, min(100.0, final_score))

    # Thresholds: Low < 25 <= Medium < 50 <= High < 75 <= Critical
    if final_score >= 75.0:
        risk_level = "Critical"
    elif final_score >= 50.0:
        risk_level = "High"
    elif final_score >= 25.0:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "employee_id": employee_id,
        "sub_scores": sub_scores,
        "final_score": round(final_score, 1),
        "risk_level": risk_level,
    }

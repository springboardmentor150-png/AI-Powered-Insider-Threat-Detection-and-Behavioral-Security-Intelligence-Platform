import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models import Employee, RiskScoreHistory, Alert


def compute_risk_level(score: int) -> str:
    """Map numeric risk score (0-100) to operational security risk level tiers."""
    if score >= 80:
        return "CRITICAL"
    elif score >= 60:
        return "HIGH"
    elif score >= 30:
        return "MEDIUM"
    return "LOW"


def evaluate_five_factor_risk(
    db: Session,
    employee: Employee,
    detected_anomalies: List[Dict[str, Any]],
) -> Tuple[int, Dict[str, Any], List[str]]:
    """
    North Star Insider Threat Behavioral Intelligence Weighted Scoring Model:
    1. Behavioral Anomalies: 35% (Max 35 points)
    2. Privilege Misuse Indicators: 25% (Max 25 points)
    3. Data Access Violations: 20% (Max 20 points)
    4. Access Pattern Deviations: 10% (Max 10 points)
    5. Historical Security Events: 10% (Max 10 points)
    Total = 100%
    """
    factors_detail = {
        "behavioral_anomalies": 0,
        "privilege_misuse": 0,
        "data_access_violations": 0,
        "access_pattern_deviations": 0,
        "historical_security_events": 0,
    }
    contributing_reasons = []

    if not detected_anomalies:
        # Check historical alerts in DB for 10% baseline
        historical_alerts_count = db.query(Alert).filter(Alert.employee_id == employee.id).count() if employee.id else 0
        if historical_alerts_count > 0:
            factors_detail["historical_security_events"] = min(10, historical_alerts_count * 5)
            contributing_reasons.append(f"Historical alert profile ({historical_alerts_count} active/prior events)")
        else:
            factors_detail["historical_security_events"] = 0
            contributing_reasons.append("Normal baseline operational pattern")
        total_score = sum(factors_detail.values())
        return total_score, factors_detail, contributing_reasons

    for anom in detected_anomalies:
        desc = str(anom.get("description", "")).lower()
        anom_type = str(anom.get("anomaly_type", "")).lower()
        sev = str(anom.get("severity", "MEDIUM")).upper()
        weight = int(anom.get("risk_contribution", 20))

        # 1. Behavioral Anomalies (35% max)
        if any(k in desc or k in anom_type for k in ["off-hours", "volume", "spike", "burst", "foreign device", "abnormal"]):
            pts = 35 if sev == "CRITICAL" else 25 if sev == "HIGH" else 15
            factors_detail["behavioral_anomalies"] = min(35, factors_detail["behavioral_anomalies"] + pts)
            contributing_reasons.append(anom.get("description", "Behavioral Anomaly detected"))

        # 2. Privilege Misuse Indicators (25% max)
        if any(k in desc or k in anom_type for k in ["privilege", "root", "domain admin", "elevation", "unauthorized admin", "sudo"]):
            pts = 25 if sev == "CRITICAL" else 20 if sev == "HIGH" else 12
            factors_detail["privilege_misuse"] = min(25, factors_detail["privilege_misuse"] + pts)
            contributing_reasons.append(anom.get("description", "Privilege Misuse indicator detected"))

        # 3. Data Access Violations (20% max)
        if any(k in desc or k in anom_type for k in ["exfiltration", "confidential", "download", "ntds", "bulk transfer", "usb", "mass"]):
            pts = 20 if sev == "CRITICAL" else 15 if sev == "HIGH" else 10
            factors_detail["data_access_violations"] = min(20, factors_detail["data_access_violations"] + pts)
            contributing_reasons.append(anom.get("description", "Data Access violation detected"))

        # 4. Access Pattern Deviations (10% max)
        if any(k in desc or k in anom_type for k in ["ip", "subnet", "untrusted", "vpn", "location", "foreign"]):
            pts = 10 if sev in ["CRITICAL", "HIGH"] else 5
            factors_detail["access_pattern_deviations"] = min(10, factors_detail["access_pattern_deviations"] + pts)
            contributing_reasons.append(anom.get("description", "Access Pattern deviation"))

    # 5. Historical Security Events (10% max)
    historical_alerts_count = db.query(Alert).filter(Alert.employee_id == employee.id).count() if employee.id else 0
    if historical_alerts_count > 0:
        factors_detail["historical_security_events"] = min(10, historical_alerts_count * 5)
        contributing_reasons.append(f"Historical alert profile ({historical_alerts_count} active/prior events)")
    else:
        factors_detail["historical_security_events"] = 0

    # Strict mathematical sum of the 5 North Star weighted factors (Total = 100%)
    total_score = min(100, max(0, sum(factors_detail.values())))

    return total_score, factors_detail, contributing_reasons


def calculate_and_update_employee_risk(
    db: Session,
    employee: Employee,
    detected_anomalies: List[Dict[str, Any]],
) -> int:
    new_score, factors_detail, contributing_factors = evaluate_five_factor_risk(db, employee, detected_anomalies)
    risk_level = compute_risk_level(new_score)

    employee.risk_score = new_score
    employee.risk_level = risk_level
    if new_score >= 80 and employee.status == "ACTIVE":
        employee.status = "FLAGGED"
    elif new_score >= 60 and employee.status == "ACTIVE":
        employee.status = "UNDER_REVIEW"

    # Persist in RiskScoreHistory
    history_entry = RiskScoreHistory(
        employee_id=employee.id,
        score=new_score,
        risk_level=risk_level,
        contributing_factors=json.dumps(contributing_factors),
        calculated_at=datetime.now(timezone.utc),
    )
    db.add(history_entry)
    db.commit()
    db.refresh(employee)

    return new_score


def update_employee_risk_score(db: Session, employee_id: int):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        return 0, "LOW"
    # Query recent anomalies from MongoDB
    from app.mongodb import mongo_service
    logs = mongo_service.query_activity_logs(employee_id=emp.employee_id, limit=5)["items"]
    anomalies = []
    for log in logs:
        if log.get("is_suspicious") or log.get("risk_weight", 0) >= 30:
            reasons = log.get("anomaly_reasons", [])
            for r in reasons:
                anomalies.append({
                    "anomaly_type": log.get("event_type", "anomaly"),
                    "severity": "CRITICAL" if log.get("risk_weight", 0) >= 80 else "HIGH",
                    "description": r,
                    "risk_contribution": min(40, log.get("risk_weight", 20)),
                })

    score = calculate_and_update_employee_risk(db, emp, anomalies)
    return score, emp.risk_level



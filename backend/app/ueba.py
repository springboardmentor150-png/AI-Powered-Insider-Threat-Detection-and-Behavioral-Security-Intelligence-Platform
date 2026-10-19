"""
ITBIS UEBA Intelligence Workflows (Milestone 3: Days 23-24)
AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform.

Provides contextual User and Entity Behavior Analytics around individual risk scores:
1. Peer Group Comparison: Compares an employee's risk score against peers in the same
   department, establishing whether an elevated score represents an anomalous departmental
   outlier or normal operational overhead. Excludes the subject employee from their peer baseline.
2. Behavioral Trend Analysis: Evaluates chronological anomaly volume over time windows (e.g. 14 / 30 days)
   with zero date gaps, tracking acceleration vs de-escalation of suspicious behavior.
3. Simple Threat Prediction: Compares weekly halves (days 1-7 vs days 8-14) using a 1.3x/0.7x
   noise margin to classify behavioral direction as 'increasing', 'decreasing', or 'stable'.
"""

import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models import Employee
from app.mongodb import mongo_service
from app.risk_scoring import calculate_risk_score

logger = logging.getLogger("itbis.ueba")


def get_peer_group_comparison(employee_id: str, db: Session) -> Optional[Dict[str, Any]]:
    """
    Compares an employee's risk score against coworkers in the same department.

    Key design principles:
    - Excludes the subject employee from their own peer average (Employee.employee_id != employee_id).
    - Gracefully handles single-employee departments with a descriptive note rather than divide-by-zero.
    - Computes deviation_from_peers (+ positive is riskier than peers, - negative is safer).
    - Computes peer_percentile (% of departmental peers who score lower than this employee).
    """
    employee = db.query(Employee).filter(
        or_(
            Employee.employee_id == employee_id,
            Employee.id == int(employee_id) if employee_id.isdigit() else False,
        )
    ).first()

    if not employee:
        return None

    emp_code = employee.employee_id
    employee_score = calculate_risk_score(emp_code, db)["final_score"]

    # Query peers in the exact same department, excluding subject employee
    peers = db.query(Employee).filter(
        Employee.department == employee.department,
        Employee.employee_id != emp_code,
    ).all()

    if not peers:
        return {
            "employee_id": emp_code,
            "employee_score": employee_score,
            "peer_count": 0,
            "department": employee.department,
            "department_avg_score": None,
            "deviation_from_peers": None,
            "peer_percentile": None,
            "note": "No peers found in this department for comparison",
        }

    peer_scores = [calculate_risk_score(p.employee_id, db)["final_score"] for p in peers]
    peer_avg = sum(peer_scores) / len(peer_scores)

    # Percentage of peers whose risk score is strictly less than employee's score
    lower_peers_count = sum(1 for s in peer_scores if s < employee_score)
    peer_percentile = round((lower_peers_count / len(peer_scores)) * 100.0, 1)

    return {
        "employee_id": emp_code,
        "employee_score": employee_score,
        "peer_count": len(peers),
        "department": employee.department,
        "department_avg_score": round(peer_avg, 1),
        "deviation_from_peers": round(employee_score - peer_avg, 1),
        "peer_percentile": peer_percentile,
        "note": None,
    }


def get_risk_trend(employee_id: str, days: int = 30) -> List[Dict[str, Any]]:
    """
    Builds a day-by-day chronological anomaly time series for an employee.

    Guarantees:
    - Returns exactly 'days' contiguous daily entries with no date gaps.
    - Accurately reconciles both rule-based and ML anomaly storage timestamp formats.
    """
    now = datetime.now(timezone.utc)
    # Generate list of exact calendar dates in UTC: from (now - days + 1) to today
    start_date = (now - timedelta(days=days - 1)).date()
    end_date = now.date()

    # Query all stored anomaly records for this employee
    all_anomalies = mongo_service.get_anomalies(employee_id=employee_id, limit=3000)

    # Bucket anomaly counts by UTC date 'YYYY-MM-DD'
    daily_counts: Dict[str, int] = defaultdict(int)
    for a in all_anomalies:
        details = a.get("details") if isinstance(a.get("details"), dict) else {}
        date_str = details.get("date") or a.get("date")
        if not date_str:
            ts = str(a.get("detected_at") or a.get("detection_timestamp") or a.get("timestamp") or "").strip()
            if len(ts) >= 10:
                date_str = ts[:10]
        if date_str:
            daily_counts[str(date_str)[:10]] += 1

    # Walk from start_date to end_date with zero missing days
    trend: List[Dict[str, Any]] = []
    curr = start_date
    while curr <= end_date:
        d_iso = curr.isoformat()
        trend.append({
            "date": d_iso,
            "anomaly_count": daily_counts.get(d_iso, 0),
        })
        curr += timedelta(days=1)

    return trend[-days:] if len(trend) > days else trend


def get_trend_direction(employee_id: str) -> Dict[str, Any]:
    """
    Evaluates short-term behavioral acceleration by comparing anomaly volume
    across two consecutive 7-day windows (Days 1-7 vs Days 8-14 of the last 14 days).

    Direction criteria:
    - 'increasing': second_week_avg > first_week_avg * 1.3 (or first_week == 0 and second_week > 0)
    - 'decreasing': second_week_avg < first_week_avg * 0.7
    - 'stable': within normal expected operational variation
    """
    trend = get_risk_trend(employee_id, days=14)
    first_week = trend[:7]
    second_week = trend[7:]

    first_week_avg = sum(d["anomaly_count"] for d in first_week) / len(first_week) if first_week else 0.0
    second_week_avg = sum(d["anomaly_count"] for d in second_week) / len(second_week) if second_week else 0.0

    if first_week_avg == 0.0 and second_week_avg > 0.0:
        direction = "increasing"
    elif second_week_avg > (first_week_avg * 1.3):
        direction = "increasing"
    elif second_week_avg < (first_week_avg * 0.7):
        direction = "decreasing"
    else:
        direction = "stable"

    return {
        "employee_id": employee_id,
        "first_week_avg": round(first_week_avg, 2),
        "second_week_avg": round(second_week_avg, 2),
        "direction": direction,
    }


def get_ueba_profile(employee_id: str, db: Session) -> Optional[Dict[str, Any]]:
    """
    Assembles the full contextual UEBA intelligence profile:
    - 5-factor normalized composite risk score
    - Departmental peer group comparison & percentile
    - 14-day anomaly trend and threat direction
    """
    employee = db.query(Employee).filter(
        or_(
            Employee.employee_id == employee_id,
            Employee.id == int(employee_id) if employee_id.isdigit() else False,
        )
    ).first()

    if not employee:
        return None

    emp_code = employee.employee_id
    return {
        "employee_id": emp_code,
        "employee_name": employee.name,
        "department": employee.department,
        "risk_score": calculate_risk_score(emp_code, db),
        "peer_comparison": get_peer_group_comparison(emp_code, db),
        "trend": get_trend_direction(emp_code),
    }

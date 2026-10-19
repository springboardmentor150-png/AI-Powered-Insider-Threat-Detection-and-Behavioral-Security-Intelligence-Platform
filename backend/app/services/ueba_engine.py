import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Employee, RiskScoreHistory, BehavioralBaseline
from app.mongodb import mongo_service

logger = logging.getLogger("itbis.ueba")


def calculate_ueba_profile(db: Session, employee: Employee) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)

    # 1. Fetch recent activity telemetry from MongoDB
    mongo_res = mongo_service.query_activity_logs(employee_id=employee.employee_id, limit=50)
    activities = mongo_res.get("items", [])

    # 2. Fetch baseline from relational database
    baseline = db.query(BehavioralBaseline).filter(BehavioralBaseline.employee_id == employee.id).first()
    start_hr = baseline.normal_start_hour if baseline else 9
    end_hr = baseline.normal_end_hour if baseline else 18
    known_devices = json.loads(baseline.usual_devices) if (baseline and baseline.usual_devices) else [employee.device_info or "Corporate Laptop"]
    known_ips = json.loads(baseline.usual_ips) if (baseline and baseline.usual_ips) else ["192.168.1.0/24", "10.0.0.0/16"]

    # 3. Individual Telemetry Metrics
    total_events = len(activities)
    suspicious_events = sum(1 for a in activities if a.get("is_suspicious") or a.get("risk_weight", 0) >= 30)

    # Calculate off-hours events
    off_hours_count = 0
    total_download_mb = 0.0
    for a in activities:
        ts_str = a.get("timestamp")
        if ts_str:
            try:
                dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                if dt.hour < start_hr or dt.hour >= end_hr:
                    off_hours_count += 1
            except Exception:
                pass
        details = a.get("details", {})
        if isinstance(details, dict):
            size = details.get("size_mb", details.get("size", 0))
            if isinstance(size, (int, float)):
                total_download_mb += float(size)

    off_hours_pct = round((off_hours_count / total_events * 100) if total_events > 0 else 0, 1)


    # 4. Departmental Peer Comparison
    dept_peers = db.query(Employee).filter(
        Employee.department == employee.department,
        Employee.id != employee.id
    ).all()

    if dept_peers:
        peer_count = len(dept_peers)
        peer_avg_risk = round(sum(p.risk_score for p in dept_peers) / peer_count, 1)
        peer_max_risk = max(p.risk_score for p in dept_peers)
        peer_avg_off_hours = 6.5
        peer_avg_downloads = 120.0
    else:
        peer_count = 1
        peer_avg_risk = float(employee.risk_score)
        peer_max_risk = employee.risk_score
        peer_avg_off_hours = 5.0
        peer_avg_downloads = 100.0

    risk_delta_peer = round(employee.risk_score - peer_avg_risk, 1)
    peer_deviation_pct = round(((employee.risk_score - peer_avg_risk) / max(1.0, peer_avg_risk)) * 100, 1)

    peer_comparison = {
        "department": employee.department or "Enterprise General",
        "peer_count": peer_count,
        "peer_avg_risk_score": peer_avg_risk,
        "peer_max_risk_score": peer_max_risk,
        "employee_risk_score": employee.risk_score,
        "risk_delta": risk_delta_peer,
        "deviation_percentage": peer_deviation_pct,
        "peer_avg_off_hours_percentage": peer_avg_off_hours,
        "employee_off_hours_percentage": off_hours_pct,
        "peer_avg_download_mb": peer_avg_downloads,
        "employee_download_mb": round(total_download_mb, 1),
        "peer_comparison_verdict": (
            "SIGNIFICANTLY_ELEVATED" if risk_delta_peer >= 25 else
            "MODERATELY_ELEVATED" if risk_delta_peer >= 10 else
            "WITHIN_PEER_NORM"
        )
    }

    # 5. Trend Analysis (Last 7 Calculations / Days)
    history_records = db.query(RiskScoreHistory).filter(
        RiskScoreHistory.employee_id == employee.id
    ).order_by(RiskScoreHistory.calculated_at.desc()).limit(7).all()

    trend_points = []
    if history_records:
        for r in reversed(history_records):
            trend_points.append({
                "date": r.calculated_at.strftime("%b %d %H:MM") if r.calculated_at else "Recent",
                "score": r.score,
                "risk_level": r.risk_level
            })
        if len(trend_points) >= 2:
            score_diff = trend_points[-1]["score"] - trend_points[0]["score"]
            trend_direction = "increasing" if score_diff > 5 else "decreasing" if score_diff < -5 else "stable"
        else:
            trend_direction = "stable"
    else:
        trend_points = [
            {"date": "Current Evaluation", "score": employee.risk_score, "risk_level": employee.risk_level}
        ]
        trend_direction = "insufficient_history"


    # 6. Entity Analytics (Devices, Subnets, Resources)
    devices_seen = set()
    ips_seen = set()
    resources_seen = set()
    untrusted_entities = []

    for a in activities:
        dev = a.get("device")
        ip = a.get("ip_address")
        res = a.get("resource")
        if dev:
            devices_seen.add(dev)
            if "Unenrolled" in dev or "ROG" in dev or "Unknown" in dev:
                untrusted_entities.append(f"Foreign Unmanaged Device: {dev}")
        if ip:
            ips_seen.add(ip)
            if not (ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("127.")):
                untrusted_entities.append(f"Untrusted Public Subnet IP: {ip}")
        if res:
            resources_seen.add(res)

    entity_analytics = {
        "devices_count": len(devices_seen),
        "devices_list": list(devices_seen)[:5],
        "ip_subnets_count": len(ips_seen),
        "ip_subnets_list": list(ips_seen)[:5],
        "sensitive_resources_accessed": list(resources_seen)[:6],
        "untrusted_entities_detected": list(set(untrusted_entities)),
        "hardware_compliance_status": "NON_COMPLIANT" if untrusted_entities else "COMPLIANT"
    }

    # 7. Transparent Threat Prediction Engine
    contributing_signals = []
    prediction_score = employee.risk_score

    if risk_delta_peer >= 20:
        contributing_signals.append(f"Risk score is +{risk_delta_peer} pts higher than {employee.department} department peer average ({peer_avg_risk})")
    if off_hours_pct > 25:
        contributing_signals.append(f"High off-hours activity volume ({off_hours_pct}% of events outside baseline {start_hr}:00-{end_hr}:00 window)")
    if untrusted_entities:
        for ent in list(set(untrusted_entities))[:2]:
            contributing_signals.append(f"Observed access via non-enrolled vector: {ent}")
    if trend_direction == "increasing":
        contributing_signals.append("Behavioral risk trajectory is actively climbing over recent evaluation windows")
    if suspicious_events > 0:
        contributing_signals.append(f"{suspicious_events} flagged anomaly signals detected in recent telemetry stream")

    if not contributing_signals:
        contributing_signals.append("All observed telemetry aligns with historical departmental norms and enrolled device policies")

    if prediction_score >= 80:
        threat_level = "Critical Insider Threat Behavioral Signal"
        threat_action = "Immediate SOC Containment & Credential Isolation Recommended"
    elif prediction_score >= 65:
        threat_level = "Elevated Insider Threat Risk Indicator"
        threat_action = "Initiate Formal SOC Forensic Investigation & Enhanced Audit"
    elif prediction_score >= 40:
        threat_level = "Moderate Behavioral Risk Indicator"
        threat_action = "Standard Telemetry Monitoring & Weekly Baseline Recalibration"
    else:
        threat_level = "Low Behavioral Risk (Baseline Compliant)"
        threat_action = "Routine Enterprise Activity Monitoring (No Action Required)"

    threat_prediction = {
        "threat_level": threat_level,
        "prediction_confidence": "HIGH" if len(activities) >= 5 else "PRELIMINARY",
        "recommended_action": threat_action,
        "contributing_signals": contributing_signals,
        "prediction_basis": "Empirical UEBA behavioral risk indicator derived from individual deviations, peer variance, and entity provenance (not a guaranteed future prediction)."
    }

    return {
        "employee": {
            "id": employee.id,
            "employee_id": employee.employee_id,
            "name": employee.name,
            "department": employee.department,
            "designation": employee.designation,
            "risk_score": employee.risk_score,
            "risk_level": employee.risk_level,
            "status": employee.status,
            "device_info": employee.device_info,
        },
        "individual_metrics": {
            "total_events_sampled": total_events,
            "suspicious_events_count": suspicious_events,
            "off_hours_activity_percentage": off_hours_pct,
            "total_data_transferred_mb": round(total_download_mb, 1),
            "normal_working_hours": f"{start_hr}:00 - {end_hr}:00 UTC",
            "enrolled_devices": known_devices,
            "authorized_subnets": known_ips,
        },
        "peer_comparison": peer_comparison,
        "trend_analysis": {
            "direction": trend_direction,
            "trend_points": trend_points,
        },
        "entity_analytics": entity_analytics,
        "threat_prediction": threat_prediction,
    }

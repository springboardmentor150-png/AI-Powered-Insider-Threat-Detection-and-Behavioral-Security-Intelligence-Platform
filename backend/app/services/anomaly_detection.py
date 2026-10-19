import json
from datetime import datetime
from typing import List, Dict, Any
from app.models import Employee, BehavioralBaseline, ActivityLog

SENSITIVE_KEYWORDS = [
    "payroll", "secret", "credential", "master-key", "production-db",
    "executive-comp", "customer-pii", "source-vault", "private-key", "analytics-archive"
]


def evaluate_activity_anomalies(
    employee: Employee,
    baseline: BehavioralBaseline,
    activity: ActivityLog,
    metadata: Dict[str, Any] = None,
) -> List[Dict[str, Any]]:
    anomalies = []
    meta = metadata or {}
    if activity.metadata_json and not meta:
        try:
            meta = json.loads(activity.metadata_json)
        except Exception:
            meta = {}

    usual_devices = []
    usual_ips = []
    if baseline:
        if baseline.usual_devices:
            try:
                usual_devices = json.loads(baseline.usual_devices)
            except Exception:
                usual_devices = [baseline.usual_devices]
        if baseline.usual_ips:
            try:
                usual_ips = json.loads(baseline.usual_ips)
            except Exception:
                usual_ips = [baseline.usual_ips]

    # 1. Off-Hours Access Check
    act_time = activity.timestamp or datetime.utcnow()
    hour = act_time.hour
    start_hour = baseline.normal_start_hour if baseline else 8
    end_hour = baseline.normal_end_hour if baseline else 19

    # Check if hour is outside standard working window (before 8 AM or after 7 PM)
    if hour < start_hour or hour >= end_hour:
        anomalies.append({
            "anomaly_type": "OFF_HOURS_ACCESS",
            "category": "OFF_HOURS_ACCESS",
            "severity": "HIGH" if (hour >= 0 and hour <= 5) else "MEDIUM",
            "description": f"Activity recorded at {hour:02d}:{act_time.minute:02d} UTC outside baseline business shift ({start_hour:02d}:00–{end_hour:02d}:00).",
            "risk_contribution": 25,
            "observed_value": f"{hour:02d}:{act_time.minute:02d} UTC",
            "expected_baseline": f"{start_hour:02d}:00–{end_hour:02d}:00 UTC",
        })

    # 2. Unusual Device Check
    if activity.device_id:
        is_known_device = False
        if employee.device_info and activity.device_id.lower() in employee.device_info.lower():
            is_known_device = True
        for dev in usual_devices:
            if activity.device_id.lower() in str(dev).lower():
                is_known_device = True
                break

        if not is_known_device:
            anomalies.append({
                "anomaly_type": "UNUSUAL_DEVICE",
                "category": "UNUSUAL_LOGIN",
                "severity": "MEDIUM",
                "description": f"Unrecognized hardware node ({activity.device_id}) not registered in employee device profile.",
                "risk_contribution": 25,
                "observed_value": activity.device_id,
                "expected_baseline": employee.device_info or "Registered Corporate Node",
            })

    # 3. Unusual IP Network Check
    if activity.ip_address:
        is_private = (
            activity.ip_address.startswith("10.") or
            activity.ip_address.startswith("192.168.") or
            activity.ip_address.startswith("172.16.") or
            activity.ip_address.startswith("127.0.0.1") or
            activity.ip_address == "localhost"
        )
        is_known_ip = is_private or any(activity.ip_address in str(ip) for ip in usual_ips)

        if not is_known_ip:
            anomalies.append({
                "anomaly_type": "UNUSUAL_IP_NETWORK",
                "category": "ANOMALOUS_BEHAVIOR",
                "severity": "MEDIUM",
                "description": f"Telemetry ingress from untrusted public IP subnet ({activity.ip_address}).",
                "risk_contribution": 20,
                "observed_value": activity.ip_address,
                "expected_baseline": "Enterprise VPN / Corporate Intranet (10.0.0.0/16)",
            })

    # 4. Mass Download / Exfiltration Check
    download_mb = meta.get("download_size_mb") or meta.get("file_size_mb") or 0
    limit_mb = baseline.usual_download_limit_mb if baseline else 500
    if activity.activity_type in ["FILE_DOWNLOAD", "DATA_EXPORT", "DATABASE_DUMP"] or download_mb >= limit_mb:
        if download_mb >= limit_mb or "exfil" in activity.action.lower() or "mass" in activity.action.lower():
            anomalies.append({
                "anomaly_type": "MASS_DOWNLOAD_EXFILTRATION",
                "category": "DATA_EXFILTRATION",
                "severity": "CRITICAL",
                "description": f"High-volume data transfer ({download_mb} MB) exceeding baseline transfer limit ({limit_mb} MB).",
                "risk_contribution": 45,
                "observed_value": f"{download_mb} MB transferred",
                "expected_baseline": f"<= {limit_mb} MB safe quota",
            })

    # 5. Privilege Escalation Check
    is_priv_type = activity.activity_type in ["PRIVILEGE_CHANGE", "ROLE_ELEVATION", "IAM_MODIFICATION"]
    has_priv_kw = any(k in activity.action.lower() for k in ["cluster-admin", "sudo", "grant", "elevate", "iam:attach"])
    if is_priv_type or has_priv_kw:
        anomalies.append({
            "anomaly_type": "PRIVILEGE_ESCALATION",
            "category": "PRIVILEGE_ESCALATION",
            "severity": "CRITICAL",
            "description": f"Unauthorized attempt to modify authorization privileges or assume elevated administrative role.",
            "risk_contribution": 40,
            "observed_value": activity.action,
            "expected_baseline": employee.access_privileges or "STANDARD",
        })

    # 6. Sensitive Resource Access
    resource_lower = (activity.resource or "").lower()
    if any(kw in resource_lower for kw in SENSITIVE_KEYWORDS):
        anomalies.append({
            "anomaly_type": "SENSITIVE_RESOURCE_ACCESS",
            "category": "SENSITIVE_RESOURCE_ACCESS",
            "severity": "HIGH",
            "description": f"Access query targeting classified high-sensitivity enterprise asset ({activity.resource}).",
            "risk_contribution": 30,
            "observed_value": activity.resource,
            "expected_baseline": "Standard departmental project repository",
        })

    # 7. Failed Authentication
    if not activity.is_success and activity.activity_type == "LOGIN":
        anomalies.append({
            "anomaly_type": "FAILED_AUTH_BURST",
            "category": "UNUSUAL_LOGIN",
            "severity": "MEDIUM",
            "description": "Authentication failure registered on identity provider gateway.",
            "risk_contribution": 20,
            "observed_value": "FAILED",
            "expected_baseline": "SUCCESS",
        })

    return anomalies

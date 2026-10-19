import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import Employee, BehavioralBaseline, ActivityLog


def get_or_create_baseline(db: Session, employee: Employee) -> BehavioralBaseline:
    baseline = db.query(BehavioralBaseline).filter(BehavioralBaseline.employee_id == employee.id).first()
    if not baseline:
        baseline = BehavioralBaseline(
            employee_id=employee.id,
            normal_start_hour=9,
            normal_end_hour=18,
            usual_devices=json.dumps([employee.device_info] if employee.device_info else ["Corporate Workstation"]),
            usual_ips=json.dumps(["10.0.0.0/16", "192.168.1.0/24"]),
            usual_resources=json.dumps(["internal-jira", "gitlab", "confluence", "email-server"]),
            usual_download_limit_mb=500,
            total_activities_sampled=0,
            last_baseline_update=datetime.now(timezone.utc),
        )
        db.add(baseline)
        db.commit()
        db.refresh(baseline)
    return baseline


def update_baseline_from_activities(db: Session, employee_id: int) -> BehavioralBaseline:
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        return None

    baseline = get_or_create_baseline(db, employee)

    activities = db.query(ActivityLog).filter(
        ActivityLog.employee_id == employee_id,
        ActivityLog.is_success == True,
        ActivityLog.is_test_event == False,
    ).all()

    total_sampled = len(activities)
    baseline.total_activities_sampled = total_sampled
    baseline.last_baseline_update = datetime.now(timezone.utc)

    if total_sampled >= 5:
        # Collect observed devices and IPs
        devices = list(set([a.device_id for a in activities if a.device_id]))
        if employee.device_info and employee.device_info not in devices:
            devices.append(employee.device_info)

        ips = list(set([a.ip_address for a in activities if a.ip_address]))
        if "10.0.0.0/16" not in ips:
            ips.append("10.0.0.0/16")

        resources = list(set([a.resource for a in activities if a.resource]))

        baseline.usual_devices = json.dumps(devices[:10])
        baseline.usual_ips = json.dumps(ips[:10])
        baseline.usual_resources = json.dumps(resources[:20])

    db.commit()
    db.refresh(baseline)
    return baseline


def get_baseline_status_message(baseline: BehavioralBaseline) -> str:
    if not baseline or baseline.total_activities_sampled < 5:
        sampled = baseline.total_activities_sampled if baseline else 0
        return f"Insufficient behavioral history ({sampled}/5 baseline activities sampled). Anomaly detector operating on standard enterprise policy."
    return f"Active behavioral baseline established from {baseline.total_activities_sampled} observed operational events."

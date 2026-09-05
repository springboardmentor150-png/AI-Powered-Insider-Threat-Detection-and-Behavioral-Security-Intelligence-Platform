# backend/app/routes/simulation_routes.py
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db, doc_db
from app.models import Employee, Alert, User
from app.schemas import SimulationRequest
from app.auth import get_current_user
from app.routes.log_routes import evaluate_realtime_log_trigger

router = APIRouter(prefix="/simulation", tags=["Threat Simulation Lab"])

@router.post("/run")
def run_simulation(
    sim_req: SimulationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Simulates realistic telemetry scenarios and streams them directly into the document store.
    """
    scenario = sim_req.scenario.lower()
    
    # Select or fallback employee
    employee = None
    if sim_req.employee_id:
        employee = db.query(Employee).filter(Employee.employee_id == sim_req.employee_id).first()
    if not employee:
        employee = db.query(Employee).first()
        if not employee:
            raise HTTPException(status_code=400, detail="No employees found in system to simulate.")

    emp_id = employee.employee_id
    generated_logs: List[Dict[str, Any]] = []
    now = datetime.utcnow()

    if scenario == "mass_exfiltration":
        # Disgruntled employee exfiltration sequence
        off_hour_base = now.replace(hour=2, minute=15)
        events = [
            ("login", {"ip_address": "192.168.1.185", "device": "workstation-mac-01", "is_off_hours": True, "auth_method": "VPN"}, off_hour_base),
            ("file_download", {"file_name": "src_core_proprietary_algorithms.zip", "size_mb": 420.5, "is_confidential": True}, off_hour_base + timedelta(minutes=5)),
            ("usb_connect", {"vendor_id": "SanDisk_Ultra_128G", "serial": "SD-99410-X", "action": "MOUNTED_READ_WRITE"}, off_hour_base + timedelta(minutes=10)),
            ("file_download", {"file_name": "customer_pci_tokens_q4.csv", "size_mb": 180.0, "is_confidential": True}, off_hour_base + timedelta(minutes=18)),
            ("email_sent", {"recipient": "personal.dropbox.backup@gmail.com", "attachment": "archive_backup.enc", "size_mb": 590.0}, off_hour_base + timedelta(minutes=25))
        ]
        for etype, details, ts in events:
            log_doc = {
                "employee_id": emp_id,
                "event_type": etype,
                "details": details,
                "timestamp": ts
            }
            doc_db.activity_logs.insert_one(log_doc)
            evaluate_realtime_log_trigger(log_doc, db)
            generated_logs.append(log_doc)

    elif scenario == "compromised_admin":
        # Compromised admin account scenario
        off_hour_base = now.replace(hour=3, minute=45)
        events = [
            ("login", {"ip_address": "185.220.101.42", "geo_country": "Tor_Exit_Node_RU", "is_off_hours": True, "mfa_bypassed": True}, off_hour_base),
            ("privilege_escalation", {"command": "sudo su - root", "target_role": "SUPERADMIN", "sudo": True}, off_hour_base + timedelta(minutes=2)),
            ("system_config", {"action": "DISABLE_AUDITD_LOGGING", "affected_host": "prod-auth-cluster"}, off_hour_base + timedelta(minutes=6)),
            ("access_key_created", {"iam_user": "shadow_admin_backdoor", "permissions": "FullAdministratorAccess"}, off_hour_base + timedelta(minutes=12))
        ]
        for etype, details, ts in events:
            log_doc = {
                "employee_id": emp_id,
                "event_type": etype,
                "details": details,
                "timestamp": ts
            }
            doc_db.activity_logs.insert_one(log_doc)
            evaluate_realtime_log_trigger(log_doc, db)
            generated_logs.append(log_doc)

    elif scenario == "database_scraping":
        # Database mass scraping scenario
        events = [
            ("database_query", {"table_name": "users_credit_cards", "rows_accessed": 18500, "query_type": "SELECT *", "execution_time_sec": 42.1}, now - timedelta(minutes=15)),
            ("database_query", {"table_name": "patient_health_records", "rows_accessed": 7200, "query_type": "SELECT *", "execution_time_sec": 19.4}, now - timedelta(minutes=8)),
            ("file_download", {"file_name": "dump_sql_export.tar.gz", "size_mb": 310.0, "is_confidential": True}, now - timedelta(minutes=2))
        ]
        for etype, details, ts in events:
            log_doc = {
                "employee_id": emp_id,
                "event_type": etype,
                "details": details,
                "timestamp": ts
            }
            doc_db.activity_logs.insert_one(log_doc)
            evaluate_realtime_log_trigger(log_doc, db)
            generated_logs.append(log_doc)

    else:
        # Normal workday benign activity
        events = [
            ("login", {"ip_address": "10.0.4.52", "device": "office-dock-04", "auth_method": "SSO_OKTA"}, now - timedelta(hours=4)),
            ("git_commit", {"repository": "itbis-core-service", "commit_hash": "a9f41b2", "lines_changed": 45}, now - timedelta(hours=3)),
            ("file_download", {"file_name": "sprint_design_spec.pdf", "size_mb": 4.2}, now - timedelta(hours=2)),
            ("database_query", {"table_name": "tasks", "rows_accessed": 12, "query_type": "SELECT"}, now - timedelta(hours=1)),
            ("slack_message", {"channel": "#engineering", "messages_sent": 14}, now - timedelta(minutes=30))
        ]
        for etype, details, ts in events:
            log_doc = {
                "employee_id": emp_id,
                "event_type": etype,
                "details": details,
                "timestamp": ts
            }
            doc_db.activity_logs.insert_one(log_doc)
            generated_logs.append(log_doc)

    return {
        "status": "simulation_completed",
        "scenario": scenario,
        "target_employee": {
            "employee_id": employee.employee_id,
            "name": employee.name,
            "department": employee.department
        },
        "generated_events_count": len(generated_logs),
        "events": [
            {
                "event_type": l["event_type"],
                "timestamp": l["timestamp"].isoformat() if isinstance(l["timestamp"], datetime) else str(l["timestamp"]),
                "details": l["details"]
            }
            for l in generated_logs
        ]
    }

# backend/app/routes/log_routes.py
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db, doc_db
from app.models import Employee, Alert, Incident, User
from app.schemas import ActivityLogIngest, ActivityLogOut
from app.auth import get_current_user

router = APIRouter(prefix="/logs", tags=["Activity Log Ingestion & Telemetry"])

def evaluate_realtime_log_trigger(log_entry: Dict[str, Any], db: Session):
    """
    Immediate micro-rule engine to automatically generate instant Alerts if severe high-risk patterns occur.
    """
    employee_id = log_entry.get("employee_id")
    event_type = (log_entry.get("event_type") or "").lower()
    details = log_entry.get("details") or {}

    alert_title = None
    alert_severity = "MEDIUM"
    anomaly_type = None

    # Check 1: USB connect
    if "usb" in event_type:
        alert_title = f"Physical Media Alert: Unauthorized USB Storage Connected"
        alert_severity = "HIGH"
        anomaly_type = "USB_EXFILTRATION"

    # Check 2: Massive Download
    size_mb = float(details.get("size_mb", details.get("file_size_mb", 0)))
    if size_mb > 250:
        alert_title = f"Data Egress Spike: High-Volume File Transfer ({size_mb} MB)"
        alert_severity = "HIGH" if size_mb < 500 else "CRITICAL"
        anomaly_type = "MASS_DOWNLOAD"

    # Check 3: Database Dump
    rows = int(details.get("rows_accessed", details.get("row_count", 0)))
    if rows > 3000:
        alert_title = f"Database Anomaly: Bulk Table Extraction ({rows} records)"
        alert_severity = "CRITICAL"
        anomaly_type = "DATABASE_SCRAPING"

    # Check 4: Privilege Escalation
    if "privilege" in event_type or details.get("sudo"):
        alert_title = f"Security Policy Violation: Unauthorized Privilege Escalation"
        alert_severity = "HIGH"
        anomaly_type = "PRIVILEGE_ESCALATION"

    if alert_title:
        # Create alert in relational database if employee exists
        emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if emp:
            code = f"ALT-{uuid.uuid4().hex[:6].upper()}"
            new_alert = Alert(
                alert_code=code,
                employee_id=employee_id,
                severity=alert_severity,
                title=alert_title,
                message=f"Event '{event_type}' triggered security rule. Details: {str(details)[:200]}",
                anomaly_type=anomaly_type,
                risk_score=85.0 if alert_severity == "CRITICAL" else 65.0,
                is_acknowledged=False,
                is_escalated=False
            )
            db.add(new_alert)
            # Slightly raise baseline risk score of employee
            emp.baseline_risk_score = min(100.0, (emp.baseline_risk_score or 15.0) + 12.0)
            db.commit()

@router.post("/ingest", status_code=201)
def ingest_activity_log(
    log: ActivityLogIngest,
    db: Session = Depends(get_db)
):
    """
    Ingests an activity log into MongoDB document collection.
    Accessible by collectors and microservices.
    """
    log_dict = {
        "employee_id": log.employee_id,
        "event_type": log.event_type,
        "details": log.details,
        "timestamp": log.timestamp or datetime.utcnow()
    }
    result = doc_db.activity_logs.insert_one(log_dict)
    log_dict["_id"] = str(result.inserted_id)

    # Real-time trigger check
    evaluate_realtime_log_trigger(log_dict, db)

    return {
        "status": "success",
        "message": "Activity log ingested successfully",
        "log_id": log_dict["_id"],
        "employee_id": log.employee_id,
        "event_type": log.event_type
    }

@router.post("/ingest-batch", status_code=201)
def ingest_batch_logs(
    logs: List[ActivityLogIngest],
    db: Session = Depends(get_db)
):
    """Ingests multiple activity logs at once."""
    docs = []
    for l in logs:
        d = {
            "employee_id": l.employee_id,
            "event_type": l.event_type,
            "details": l.details,
            "timestamp": l.timestamp or datetime.utcnow()
        }
        docs.append(d)
    
    result = doc_db.activity_logs.insert_many(docs)
    for d in docs:
        evaluate_realtime_log_trigger(d, db)

    return {
        "status": "success",
        "inserted_count": len(docs),
        "message": f"Successfully ingested {len(docs)} activity events"
    }

@router.get("")
def list_logs(
    employee_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = Query(50, le=500),
    current_user: User = Depends(get_current_user)
):
    """Fetch recent activity logs from MongoDB document collection."""
    query = {}
    if employee_id:
        query["employee_id"] = employee_id
    if event_type:
        query["event_type"] = event_type

    raw_logs = doc_db.activity_logs.find(query=query, limit=limit)
    # Serialize datetime and ObjectId for JSON output
    clean_logs = []
    for log in raw_logs:
        item = dict(log)
        item["_id"] = str(item.get("_id", ""))
        if isinstance(item.get("timestamp"), datetime):
            item["timestamp"] = item["timestamp"].isoformat()
        clean_logs.append(item)
    return clean_logs

@router.get("/stats")
def get_log_stats(
    current_user: User = Depends(get_current_user)
):
    """Returns real-time analytics aggregation over ingested activity logs."""
    all_logs = doc_db.activity_logs.find(limit=1000)
    total_count = len(all_logs)
    
    event_counts = {}
    employee_counts = {}
    off_hours_count = 0

    for log in all_logs:
        etype = log.get("event_type", "unknown")
        event_counts[etype] = event_counts.get(etype, 0) + 1
        
        empid = log.get("employee_id", "unknown")
        employee_counts[empid] = employee_counts.get(empid, 0) + 1

        ts = log.get("timestamp")
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts)
            except Exception:
                ts = None
        if isinstance(ts, datetime):
            if ts.hour < 7 or ts.hour > 19 or ts.weekday() >= 5:
                off_hours_count += 1

    return {
        "total_logs": total_count,
        "event_type_distribution": event_counts,
        "top_active_employees": sorted(employee_counts.items(), key=lambda x: x[1], reverse=True)[:5],
        "off_hours_ratio": round(off_hours_count / max(total_count, 1), 3)
    }

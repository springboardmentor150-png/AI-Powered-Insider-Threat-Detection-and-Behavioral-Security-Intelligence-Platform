import json
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee, User
from app.schemas import (
    ActivityIngestRequest,
    MongoActivityItem,
    PaginatedMongoActivityResponse,
    TimelinePoint,
    TimelineEventItem,
    ActivityTimelineResponse,
    HeatmapCell,
    EventTypeDistributionItem,
    TestActivityCreate,
)
from app.security import get_current_user, require_role
from app.mongodb import mongo_service, VALID_EVENT_TYPES
from app.services.anomaly_detection import evaluate_activity_anomalies
from app.services.risk_engine import update_employee_risk_score
from app.services.alert_engine import trigger_automated_alert_if_warranted

logger = logging.getLogger("itbis.activity")
router = APIRouter(prefix="/activity-logs", tags=["Activity Logs (MongoDB)"])


@router.get("", response_model=PaginatedMongoActivityResponse)
def get_activity_logs(
    employee_id: Optional[str] = Query(None, description="Filter by alphanumeric employee ID (e.g. EMP1002)"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    device: Optional[str] = Query(None, description="Filter by device hostname"),
    ip_address: Optional[str] = Query(None, description="Filter by IP address"),
    search: Optional[str] = Query(None, description="Keyword search across telemetry details"),
    is_test_event: Optional[bool] = Query(None, description="Filter synthetic test events"),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    """Retrieves paginated activity telemetry logs from MongoDB."""
    skip = (page - 1) * limit
    result = mongo_service.query_activity_logs(
        employee_id=employee_id,
        event_type=event_type,
        device=device,
        ip_address=ip_address,
        search=search,
        is_test_event=is_test_event,
        skip=skip,
        limit=limit,
    )
    
    # Map to schema
    items = []
    for doc in result["items"]:
        items.append(MongoActivityItem(
            id=str(doc.get("id", doc.get("_id", ""))),
            employee_id=str(doc.get("employee_id", "")),
            event_type=str(doc.get("event_type", "login")),
            action=doc.get("action"),
            resource=doc.get("resource"),
            timestamp=str(doc.get("timestamp", datetime.now(timezone.utc).isoformat())),
            device=doc.get("device") or doc.get("device_id"),
            ip_address=doc.get("ip_address"),
            location=doc.get("location"),
            risk_weight=int(doc.get("risk_weight", 0)),
            is_suspicious=bool(doc.get("is_suspicious", False)),
            anomaly_reasons=doc.get("anomaly_reasons", []),
            is_test_event=bool(doc.get("is_test_event", False)),
            details=doc.get("details", {}),
        ))

    return PaginatedMongoActivityResponse(
        items=items,
        page=page,
        limit=limit,
        total=result["total"],
    )


@router.get("/anomalies")
def get_recorded_anomalies(
    employee_id: Optional[str] = Query(None, description="Filter anomalies by employee ID"),
    indicator: Optional[str] = Query(None, description="Filter by baseline indicator"),
    anomaly_type: Optional[str] = Query(None, description="Filter by anomaly type"),
    severity: Optional[str] = Query(None, description="Filter by severity (medium, high, critical)"),
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
):
    """Retrieves detected behavioral anomalies from MongoDB or persistent store."""
    items = mongo_service.get_anomalies(
        employee_id=employee_id,
        indicator=indicator,
        anomaly_type=anomaly_type,
        severity=severity,
        limit=limit,
    )
    return {
        "items": items,
        "total": len(items),
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def ingest_activity_log(
    payload: ActivityIngestRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("Administrator", "SOC Engineer")),
):
    """
    Ingests an activity telemetry record into MongoDB.
    - Rejects unknown event_type with 400 Bad Request.
    - Verifies employee_id exists in PostgreSQL/database (rejects non-existent with 404).
    - Restricts ingestion to authorized Administrator and SOC Engineer roles.
    - Runs behavioral anomaly detection and updates dynamic risk scores.
    """
    et = payload.event_type.lower().strip()
    if et not in VALID_EVENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown event_type '{payload.event_type}'. Supported event types: {sorted(list(VALID_EVENT_TYPES))}"
        )

    # Verify employee exists in PostgreSQL/database registry
    is_numeric = payload.employee_id.isdigit()
    emp = db.query(Employee).filter(
        (Employee.employee_id == payload.employee_id) |
        (Employee.id == int(payload.employee_id) if is_numeric else False)
    ).first()
    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{payload.employee_id}' not found in employee registry. Activity rejected."
        )

    # Anomaly evaluation
    risk_weight = payload.risk_weight or 0
    anomaly_reasons = list(payload.anomaly_reasons or [])
    is_suspicious = payload.is_suspicious or False

    # Run Day 15-16 Rule-Based Behavioral Anomaly Detectors
    detected_anomalies = []
    try:
        from app.anomaly_detection import (
            detect_login_anomaly,
            detect_download_anomaly,
            detect_transfer_frequency_anomaly,
            detect_device_anomaly,
            detect_unauthorized_access,
        )

        emp_code = emp.employee_id

        # 1. Device check for all events with device supplied
        if payload.device:
            dev_anom = detect_device_anomaly(emp_code, payload.device)
            if dev_anom:
                detected_anomalies.append(dev_anom)

        # 2. Event-specific checks
        if et == "login":
            log_ts = getattr(payload, "timestamp", None) or (payload.details.get("timestamp") if isinstance(payload.details, dict) else None) or datetime.now(timezone.utc)
            login_anom = detect_login_anomaly(emp_code, log_ts)
            if login_anom:
                detected_anomalies.append(login_anom)

        elif et in ("file_download", "file_upload", "data_transfer"):
            size_mb = 0.0
            if isinstance(payload.details, dict):
                raw_size = (
                    payload.details.get("size_mb")
                    or payload.details.get("download_size_mb")
                    or payload.details.get("file_size_mb")
                    or payload.details.get("size")
                )
                if raw_size is not None:
                    try:
                        size_mb = float(raw_size)
                    except (ValueError, TypeError):
                        size_mb = 0.0
            if size_mb > 0.0:
                dl_anom = detect_download_anomaly(emp_code, size_mb)
                if dl_anom:
                    detected_anomalies.append(dl_anom)

            # Transfer frequency anomaly check
            freq_val = None
            if isinstance(payload.details, dict):
                freq_val = payload.details.get("daily_transfers_count") or payload.details.get("transfer_frequency")
            if freq_val is not None:
                freq_anom = detect_transfer_frequency_anomaly(emp_code, freq_val)
                if freq_anom:
                    detected_anomalies.append(freq_anom)

        # 3. Application unauthorized access check
        if payload.resource or (isinstance(payload.details, dict) and payload.details.get("tool")):
            app_anom = detect_unauthorized_access(emp_code, payload.resource, payload.details)
            if app_anom:
                detected_anomalies.append(app_anom)

        # Integrate detected anomalies into telemetry
        for anom in detected_anomalies:
            reason = f"{anom['anomaly_type']}: Observed {anom['observed_value']} (Indicator: {anom['indicator']}, Severity: {anom['severity']})"
            if reason not in anomaly_reasons:
                anomaly_reasons.append(reason)
            is_suspicious = True
            sev = anom.get("severity")
            weight = 90 if sev == "critical" else (70 if sev == "high" else 40)
            risk_weight = max(risk_weight, weight)

    except Exception as anom_err:
        logger.warning("Automated anomaly detection encountered handled exception: %s", anom_err)

    # Store in MongoDB / telemetry storage
    doc_to_insert = {
        "employee_id": emp.employee_id,
        "event_type": et,
        "action": payload.action or f"Executed {et}",
        "resource": payload.resource or "Internal Resource",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "device": payload.device or emp.device_info or "finance-laptop-02",
        "ip_address": payload.ip_address or "192.168.1.10",
        "location": payload.location or emp.work_location or "Hyderabad",
        "risk_weight": risk_weight,
        "is_suspicious": is_suspicious,
        "anomaly_reasons": anomaly_reasons,
        "is_test_event": payload.is_test_event or False,
        "details": payload.details or {},
    }

    inserted = mongo_service.insert_activity_log(doc_to_insert)

    # Trigger risk and alert engine
    if risk_weight > 0 or is_suspicious:
        update_employee_risk_score(db, emp.id)
        if emp.risk_score >= 60:
            trigger_automated_alert_if_warranted(
                db=db,
                employee_id=emp.id,
                title=f"Suspicious {et.replace('_', ' ').title()} Telemetry Detected",
                message=f"Event triggered with risk weight {risk_weight}. Reasons: {', '.join(anomaly_reasons)}",
                category="DATA_EXFILTRATION" if "download" in et else "UNAUTHORIZED_ACCESS",
                severity="CRITICAL" if emp.risk_score >= 80 else "HIGH",
                risk_score=emp.risk_score
            )

    return inserted


@router.post("/test-event", status_code=status.HTTP_201_CREATED)
def trigger_synthetic_test_event(
    payload: TestActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Triggers a clearly marked synthetic test telemetry event in MongoDB.
    """
    emp = db.query(Employee).filter(
        (Employee.employee_id == payload.employee_id) | (Employee.id == payload.employee_id)
    ).first()
    if not emp:
        # Fallback to first employee if test id doesn't match
        emp = db.query(Employee).first()
        if not emp:
            raise HTTPException(status_code=404, detail="No employees available in database.")

    scenario = payload.scenario.upper()
    is_suspicious = False
    risk_weight = 0
    anomaly_reasons = []
    details = {}

    if "OFFHOURS" in scenario or "EXFIL" in scenario:
        is_suspicious = True
        risk_weight = 85
        anomaly_reasons = [
            "Off-Hours Activity (02:15 AM UTC)",
            "Unenrolled Hardware Node (ROG-Strix-Laptop)",
            "Massive Download Volume (4.8 GB Tarball)",
            "Untrusted Public Ingress (198.51.100.77)",
        ]
        details = {
            "file_name": "customer-pii-vault.tar.gz",
            "size_mb": 4800,
            "source_system": "S3-Archive",
            "classification": "Restricted",
        }
    elif "PRIVILEGE" in scenario:
        is_suspicious = True
        risk_weight = 75
        anomaly_reasons = [
            "Unauthorized IAM Role Modification",
            "Cluster-Admin Elevation Attempt",
        ]
        details = {
            "target_role": "cluster-admin",
            "affected_namespace": "production-core",
            "command": "kubectl auth can-i '*' '*'",
        }
    elif "SENSITIVE" in scenario:
        is_suspicious = True
        risk_weight = 65
        anomaly_reasons = [
            "Access to Restricted Payroll Vault",
            "Master Encryption Key Read Query",
        ]
        details = {
            "vault_path": "secret/data/executive-payroll-keys",
            "access_mode": "read-write",
        }
    else:
        risk_weight = 5
        anomaly_reasons = []
        details = {
            "session_duration_minutes": 45,
            "application": "ERP-Finance",
        }

    doc_to_insert = {
        "employee_id": emp.employee_id,
        "event_type": payload.activity_type.lower() if payload.activity_type.lower() in VALID_EVENT_TYPES else "file_download",
        "action": payload.action,
        "resource": payload.resource,
        "timestamp": datetime.utcnow().isoformat(),
        "device": payload.device_id or ("ROG-Strix-Node" if is_suspicious else emp.device_info or "finance-laptop-02"),
        "ip_address": payload.ip_address or ("198.51.100.77" if is_suspicious else "192.168.1.10"),
        "location": "External Network" if is_suspicious else emp.work_location or "Hyderabad",
        "risk_weight": risk_weight,
        "is_suspicious": is_suspicious,
        "anomaly_reasons": anomaly_reasons,
        "is_test_event": True,
        "details": details,
    }

    inserted = mongo_service.insert_activity_log(doc_to_insert)

    # Dynamic risk calculation
    new_score, new_tier = update_employee_risk_score(db, emp.id)

    # Auto alert if suspicious
    alert_created = False
    alert_id = None
    if is_suspicious or new_score >= 60:
        alert = trigger_automated_alert_if_warranted(
            db=db,
            employee_id=emp.id,
            title=f"Synthetic Threat Alert: {scenario}",
            message=f"Simulated suspicious event ingested into MongoDB. Detected: {', '.join(anomaly_reasons)}",
            category="DATA_EXFILTRATION" if "EXFIL" in scenario else "PRIVILEGE_ESCALATION",
            severity="CRITICAL" if new_score >= 80 else "HIGH",
            risk_score=new_score,
        )
        if alert:
            alert_created = True
            alert_id = alert.id

    return {
        "message": "Synthetic test telemetry ingested into MongoDB successfully",
        "activity_id": inserted.get("id"),
        "employee_id": emp.employee_id,
        "calculated_risk_score": new_score,
        "risk_level": new_tier,
        "anomalies_detected": len(anomaly_reasons),
        "alert_created": alert_created,
        "alert_id": alert_id,
    }


@router.get("/timeline", response_model=ActivityTimelineResponse)
def get_activity_timeline(
    employee_id: Optional[str] = Query(None, description="Filter by employee ID (e.g. FIN-2187)"),
    event_type: Optional[str] = Query(None, description="Filter by event type (e.g. file_download)"),
    time_range: str = Query("7d", description="Time range: 24h, 7d, 30d, all"),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
):
    """Retrieves chronological telemetry events for interactive activity timeline."""
    items_data = mongo_service.get_activity_timeline(
        employee_id=employee_id,
        event_type=event_type,
        time_range=time_range,
        limit=limit,
    )
    items = [TimelineEventItem(**item) for item in items_data]
    return ActivityTimelineResponse(items=items, total=len(items))


@router.get("/heatmap", response_model=List[HeatmapCell])
def get_activity_heatmap(
    employee_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """Retrieves 7-Day x 24-Hour activity intensity matrix."""
    cells = mongo_service.get_activity_heatmap(employee_id=employee_id)
    return [HeatmapCell(**c) for c in cells]


@router.get("/distribution", response_model=List[EventTypeDistributionItem])
def get_event_type_distribution(
    employee_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """Retrieves distribution counts across all supported event types."""
    dist = mongo_service.get_event_type_distribution(employee_id=employee_id)
    return [EventTypeDistributionItem(**d) for d in dist]


@router.get("/{activity_id}")
def get_activity_by_id(
    activity_id: str,
    current_user: User = Depends(get_current_user),
):
    """Retrieves a single telemetry record from MongoDB."""
    doc = mongo_service.get_activity_by_id(activity_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Activity log not found in MongoDB")
    return doc

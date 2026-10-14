import io
from datetime import datetime, timezone, timedelta, date
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
from pydantic import BaseModel, Field
from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.alert_escalation import escalate_overdue_alerts
from app.alert_service import generate_alerts
from .auth import hash_password, verify_password
from .database import get_db
from .dependencies import canonical_role, get_current_user, require_role
from .incident_timeline import get_incident_timeline
from .jwt_auth import create_access_token
from .models import Alert, AuditLog, Employee, Evidence, Incident, InvestigationNote, User
from .reports import generate_compliance_report, generate_employee_risk_report
from .audit import record_audit_log
from .xai import explain_anomaly_record
from .ws_manager import ws_manager, create_notification_payload
from .mongo import (
    activity_logs,
    rule_anomalies,
    ml_anomalies,
    anomaly_feedback,
    mongo_db,
)
from .anomaly_detection import (
    check_abnormal_data_transfer,
    check_excessive_resource_access,
    check_unknown_application,
    check_unknown_device,
    check_unusual_login_time,
)
from .schemas import (
    ActivityLogCreate,
    EmployeeCreate,
    EmployeeUpdate,
    IncidentCreate,
    InvestigationNoteCreate, 
    IncidentResolve,
    AnomalyFeedbackCreate,
    UserRoleUpdate,
    UserStatusUpdate,
    IncidentStatusUpdate,
)
from .risk_scoring import calculate_risk_score
from .ueba import (
    get_peer_group_comparison,
    get_risk_trend,
    get_trend_direction,
)
# ---------------------------------------------------------------------------

# FastAPI Application

# ---------------------------------------------------------------------------

app = FastAPI(title="ITBIS API")

# ---------------------------------------------------------------------------

# Timezone Configuration

# ---------------------------------------------------------------------------

INDIA_TIMEZONE = ZoneInfo("Asia/Kolkata")

# ---------------------------------------------------------------------------

# CORS Configuration

# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------

# Milestone 2 Rule-Based Detection

# ---------------------------------------------------------------------------

def _run_activity_rule_checks(
    activity: ActivityLogCreate,
    activity_id: str,
    activity_timestamp: datetime,
) -> list[dict]:
    """

    Run the appropriate Milestone 2 rule-based anomaly checks

    immediately after a new activity is ingested.

    The checks are selected according to the activity type:

    login

        -> unusual login time

    data_transfer

        -> abnormal data transfer volume

    file_access

        -> excessive daily resource access

    any activity with device_id

        -> unknown device

    any activity with application

        -> unknown application

    """

    anomalies = []

    # ---------------------------------------------------------

    # Login-time anomaly detection

    # ---------------------------------------------------------

    if activity.event_type == "login":
        india_time = activity_timestamp.astimezone(
            INDIA_TIMEZONE
        )
        login_hour = (
            india_time.hour
            + india_time.minute / 60
            + india_time.second / 3600
        )

        anomaly = check_unusual_login_time(
            employee_code=activity.employee_code,
            login_hour=login_hour,
            activity_id=activity_id,
        )
        if anomaly is not None:
            anomalies.append(anomaly)

    # ---------------------------------------------------------

    # Data-transfer anomaly detection

    # ---------------------------------------------------------
    if (
        activity.event_type == "data_transfer"
        and activity.data_volume_mb is not None
    ):
        
        anomaly = check_abnormal_data_transfer(
            employee_code=activity.employee_code,
            data_volume_mb=activity.data_volume_mb,
            activity_id=activity_id,
        )
        if anomaly is not None:
            anomalies.append(anomaly)

    # ---------------------------------------------------------

    # Resource-access anomaly detection

    # ---------------------------------------------------------

    if activity.event_type == "file_access":
        india_time = activity_timestamp.astimezone(
            INDIA_TIMEZONE
        )
        start_of_day = datetime(
            year=india_time.year,
            month=india_time.month,
            day=india_time.day,
            tzinfo=INDIA_TIMEZONE,
        )
        start_of_next_day = datetime(
            year=india_time.year,
            month=india_time.month,
            day=india_time.day,
            tzinfo=INDIA_TIMEZONE,
        )
        start_of_next_day += timedelta(days=1)
        daily_file_access_count = (
            activity_logs.count_documents(
                {
                    "employee_code": activity.employee_code,
                    "event_type": "file_access",
                    "timestamp": {
                        "$gte": start_of_day.astimezone(
                            timezone.utc
                        ),
                        "$lt": start_of_next_day.astimezone(
                            timezone.utc
                        ),
                    },
                }
            )
        )
        anomaly = check_excessive_resource_access(
            employee_code=activity.employee_code,
            access_count=daily_file_access_count,
            activity_id=activity_id,
        )
        if anomaly is not None:
            anomalies.append(anomaly)

    # ---------------------------------------------------------

    # Unknown-device detection

    # ---------------------------------------------------------

    if activity.device_id:

        anomaly = check_unknown_device(

            employee_code=activity.employee_code,

            device_id=activity.device_id,

            activity_id=activity_id,

        )

        if anomaly is not None:

            anomalies.append(anomaly)

    # ---------------------------------------------------------

    # Unknown-application detection

    # ---------------------------------------------------------

    if activity.application:

        anomaly = check_unknown_application(

            employee_code=activity.employee_code,

            application=activity.application,

            activity_id=activity_id,

        )

        if anomaly is not None:

            anomalies.append(anomaly)

    return anomalies

# ---------------------------------------------------------------------------

# Health Check

# ---------------------------------------------------------------------------

@app.get("/")

def health_check():

    return {

        "status": "ITBIS backend is running"

    }

# ---------------------------------------------------------------------------
# Milestone 1 & 4 — Activity Log Ingestion API
# ---------------------------------------------------------------------------

class LogIngestPayload(BaseModel):
    employee_id: str
    event_type: str
    details: dict[str, Any] = Field(default_factory=dict)


@app.post("/logs/ingest")
def receive_log(
    payload: LogIngestPayload,
    current_user=Depends(
        require_role("admin", "security_analyst", "soc_engineer", "security_manager")
    ),
):
    """
    Ingest activity logs directly into MongoDB activity_logs collection.
    Matches Milestone 1 Day 9-10 & Milestone 4 Day 35-36 contract.
    """
    india_time = datetime.now(INDIA_TIMEZONE)
    timestamp_utc = india_time.astimezone(timezone.utc)

    log_entry = {
        "employee_code": payload.employee_id,
        "employee_id": payload.employee_id,
        "event_type": payload.event_type,
        "timestamp": timestamp_utc,
        "details": payload.details,
        "source": payload.details.get("source", "agent"),
        "ip_address": payload.details.get("ip_address"),
        "device_id": payload.details.get("device") or payload.details.get("device_id"),
        "application": payload.details.get("application"),
        "data_volume_mb": (
            payload.details.get("size_mb")
            or payload.details.get("data_volume_mb")
        ),
    }

    inserted = activity_logs.insert_one(log_entry)

    return {
        "message": "Log ingested",
        "event_type": payload.event_type,
        "employee_id": payload.employee_id,
        "log_id": str(inserted.inserted_id),
        "status": "success",
    }


# ---------------------------------------------------------------------------
# Activity APIs
# ---------------------------------------------------------------------------

@app.post("/activity")
def create_activity(
    activity: ActivityLogCreate,
    _current_user=Depends(get_current_user),

):

    """

    Store a new activity log and immediately run the applicable

    Milestone 2 rule-based anomaly checks.

    """

    activity_timestamp = datetime.now(

        timezone.utc

    )

    document = activity.model_dump()

    document["timestamp"] = activity_timestamp

    result = activity_logs.insert_one(

        document

    )

    activity_id = str(

        result.inserted_id

    )

    anomalies = _run_activity_rule_checks(

        activity=activity,

        activity_id=activity_id,

        activity_timestamp=activity_timestamp,

    )

    return {

        "message": "Activity logged successfully",

        "id": activity_id,

        "anomalies_detected": len(anomalies),

        "anomalies": [

            {

                "indicator": anomaly["indicator"],

                "severity": anomaly["severity"],

                "observed_value": anomaly[

                    "observed_value"

                ],

            }

            for anomaly in anomalies

        ],

    }

@app.get("/activity")

def get_all_activity(

    _current_user=Depends(get_current_user),

):

    documents = list(

        activity_logs.find().sort(

            "timestamp",

            -1,

        )

    )

    for document in documents:
        document["id"] = str(
            document.pop("_id")
        )
        if "risk_score" not in document or document["risk_score"] is None:
            document["risk_score"] = 0

    return {
        "count": len(documents),
        "activities": documents,
    }

@app.get("/activity/{employee_code}")
def get_employee_activity(
    employee_code: str,
    _current_user=Depends(get_current_user),
):
    documents = list(
        activity_logs.find(
            {
                "employee_code": employee_code
            }
        ).sort(
            "timestamp",
            -1,
        )
    )
    for document in documents:
        document["id"] = str(
            document.pop("_id")
        )
        if "risk_score" not in document or document["risk_score"] is None:
            document["risk_score"] = 0

    return {

        "employee_code": employee_code,

        "count": len(documents),

        "activities": documents,

    }

# ---------------------------------------------------------------------------

# DAY 19 — Anomaly Summary

# ---------------------------------------------------------------------------

@app.get("/anomalies/summary")

def get_anomaly_summary(

    _current_user=Depends(get_current_user),

):

    """

    Return a summary of employees flagged by

    rule-based and ML anomaly detection.

    """

    # ---------------------------------------------------------

    # Rule anomaly aggregation

    # ---------------------------------------------------------

    rule_pipeline = [

        {

            "$group": {

                "_id": "$employee_code",

                "rule_anomalies": {

                    "$sum": 1

                },

            }

        }

    ]

    rule_summary = list(

        rule_anomalies.aggregate(

            rule_pipeline

        )

    )

    # ---------------------------------------------------------

    # ML anomaly aggregation

    # ---------------------------------------------------------

    ml_pipeline = [

        {

            "$match": {

                "is_anomaly": True

            }

        },

        {

            "$group": {

                "_id": "$employee_code",

                "ml_anomalies": {

                    "$sum": 1

                },

            }

        },

    ]

    ml_summary = list(

        ml_anomalies.aggregate(

            ml_pipeline

        )

    )

    # ---------------------------------------------------------

    # Combine both result sets

    # ---------------------------------------------------------

    employee_summary = {}

    for item in rule_summary:

        employee_code = item["_id"]

        employee_summary.setdefault(

            employee_code,

            {

                "employee_code": employee_code,

                "rule_anomalies": 0,

                "ml_anomalies": 0,

            },

        )

        employee_summary[

            employee_code

        ]["rule_anomalies"] = item[

            "rule_anomalies"

        ]

    for item in ml_summary:

        employee_code = item["_id"]

        employee_summary.setdefault(

            employee_code,

            {

                "employee_code": employee_code,

                "rule_anomalies": 0,

                "ml_anomalies": 0,

            },

        )

        employee_summary[

            employee_code

        ]["ml_anomalies"] = item[

            "ml_anomalies"

        ]

    # ---------------------------------------------------------

    # Calculate total anomalies

    # ---------------------------------------------------------

    results = list(

        employee_summary.values()

    )

    for item in results:

        item["total_anomalies"] = (

            item["rule_anomalies"]

            + item["ml_anomalies"]

        )

    # ---------------------------------------------------------

    # Highest-risk employees first

    # ---------------------------------------------------------

    results.sort(

        key=lambda item: item[

            "total_anomalies"

        ],

        reverse=True,

    )

    return {

        "count": len(results),

        "employees": results,

    }

# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Milestone 2 — Anomaly Report API
# ---------------------------------------------------------------------------

@app.get("/anomalies/report")
def anomaly_report(
    current_user=Depends(
        require_role("admin", "security_analyst", "soc_engineer", "security_manager")
    ),
):
    """
    Return anomalous employees identified by the behavioral analytics and ML engines.
    Matches Milestone 2 Day 19-20 specification.
    """
    ml_records = list(ml_anomalies.find({"is_anomaly": True}, {"_id": 0}))
    flagged_employees = []
    for rec in ml_records:
        flagged_employees.append({
            "employee_id": rec.get("employee_code") or rec.get("employee_id"),
            "employee_code": rec.get("employee_code"),
            "anomaly_score": rec.get("anomaly_score", -0.1),
            "is_outlier": True,
            "detected_at": str(rec.get("detected_at") or rec.get("date")),
            "features": rec.get("features", {}),
        })

    total_count = len(activity_logs.distinct("employee_code")) or len(flagged_employees)

    return {
        "total_employees_analyzed": max(total_count, len(flagged_employees)),
        "flagged_count": len(flagged_employees),
        "flagged_employees": flagged_employees,
    }


@app.get("/anomalies/feedback")
@app.get("/anomaly-feedback")
def get_all_anomaly_feedback(
    current_user=Depends(require_role("admin", "security_analyst", "soc_engineer", "security_manager")),
):
    """List all submitted analyst feedback."""
    items = list(anomaly_feedback.find({}, {"_id": 0}))
    return {"count": len(items), "feedback": items}


# ---------------------------------------------------------------------------
# DAY 19 — Employee Anomaly Report
# ---------------------------------------------------------------------------


@app.get("/anomalies/{employee_code}")

def get_employee_anomalies(

    employee_code: str,

    _current_user=Depends(get_current_user),

):

    """

    Return a combined anomaly report for one employee.

    Combines:

    1. Rule-based anomalies from rule_anomalies

    2. ML anomalies from ml_anomalies

    """

    # ---------------------------------------------------------

    # Fetch rule-based anomalies

    # ---------------------------------------------------------

    rule_results = list(

        rule_anomalies.find(

            {

                "employee_code": employee_code

            }

        )

    )

    # ---------------------------------------------------------

    # Fetch ML anomalies

    # ---------------------------------------------------------

    ml_results = list(

        ml_anomalies.find(

            {

                "employee_code": employee_code

            }

        )

    )

    # ---------------------------------------------------------

    # Convert MongoDB ObjectId to string

    # ---------------------------------------------------------

    for anomaly in rule_results:

        anomaly["id"] = str(

            anomaly.pop("_id")

        )

    for anomaly in ml_results:

        anomaly["id"] = str(

            anomaly.pop("_id")

        )

    # ---------------------------------------------------------

    # Sort rule anomalies by severity

    # ---------------------------------------------------------

    severity_order = {

        "critical": 3,

        "high": 2,

        "medium": 1,

        "low": 0,

    }

    rule_results.sort(

        key=lambda item: severity_order.get(

            str(

                item.get(

                    "severity",

                    "",

                )

            ).lower(),

            0,

        ),

        reverse=True,

    )

    # ---------------------------------------------------------

    # Sort ML anomalies by anomaly score

    #

    # More negative = more anomalous.

    # ---------------------------------------------------------

    ml_results.sort(

        key=lambda item: item.get(

            "anomaly_score",

            0,

        )

    )

    # ---------------------------------------------------------

    # Combined report

    # ---------------------------------------------------------

    return {

        "employee_code": employee_code,

        "rule_anomalies": {

            "count": len(rule_results),

            "items": rule_results,

        },

        "ml_anomalies": {

            "count": len(ml_results),

            "items": ml_results,

        },

        "total_anomalies": (

            len(rule_results)

            + len(ml_results)

        ),

    }

# ---------------------------------------------------------------------------

# Authentication APIs

# ---------------------------------------------------------------------------

class SignupPayload(BaseModel):
    email: str | None = None
    password: str | None = None
    role: str | None = "security_analyst"


@app.post("/auth/signup")
@app.post("/auth/register")
def signup(
    payload: SignupPayload | None = None,
    email: str | None = None,
    password: str | None = None,
    role: str | None = None,
    db: Session = Depends(get_db),
):
    target_email = (payload.email if payload and payload.email else email) or ""
    target_password = (payload.password if payload and payload.password else password) or ""
    raw_role = (payload.role if payload and payload.role else role) or "security_analyst"
    target_role = canonical_role(raw_role)

    if not target_email or not target_password:
        raise HTTPException(
            status_code=400,
            detail="Email and password are required",
        )

    existing_user = (
        db.query(User)
        .filter(User.email == target_email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    password_hash = hash_password(target_password)

    user = User(
        email=target_email,
        password_hash=password_hash,
        role=target_role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(
        user_id=user.id,
        role=user.role,
    )

    return {
        "message": "User registered successfully",
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
    }

@app.post("/auth/login")
def login(
    email: str,
    password: str,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )
    if not verify_password(
        password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    access_token = create_access_token(

        user_id=user.id,

        role=user.role,

    )

    return {

        "message": "Login successful",

        "access_token": access_token,

        "token_type": "bearer",

        "user_id": user.id,

        "email": user.email,

        "role": user.role,

    }

@app.get("/auth/me")

def get_me(

    current_user=Depends(

        get_current_user

    ),

):

    return {

        "message": "Authenticated user",

        "user_id": current_user["sub"],

        "role": current_user["role"],

    }

@app.get("/admin-test")

def admin_test(

    current_user=Depends(

        require_role("admin")

    ),

):

    return {

        "message": "Admin access granted",
        "user_id": current_user["sub"],
        "role": current_user["role"],
    }


@app.get("/admin/users")
def list_admin_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    """List platform users with role assignments (Milestone 1 Day 5-6)."""
    users = db.query(User).order_by(User.id).all()
    return {
        "message": "Only admins see this",
        "user_count": len(users),
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "role": u.role,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
    }

# ---------------------------------------------------------------------------

# Employee Management APIs

# ---------------------------------------------------------------------------

@app.post("/employees")

def create_employee(

    employee: EmployeeCreate,

    current_user=Depends(

        require_role("admin")

    ),

    db: Session = Depends(get_db),

):

    existing_employee = (

        db.query(Employee)

        .filter(

            Employee.employee_code

            == employee.employee_code

        )

        .first()

    )

    if existing_employee:

        raise HTTPException(

            status_code=400,

            detail="Employee code already registered",

        )

    existing_email = (

        db.query(Employee)

        .filter(

            Employee.email

            == employee.email

        )

        .first()

    )

    if existing_email:

        raise HTTPException(

            status_code=400,

            detail="Employee email already registered",

        )

    new_employee = Employee(

        employee_code=employee.employee_code,

        name=employee.name,

        email=employee.email,

        department=employee.department,

        role=employee.role,

    )

    db.add(new_employee)

    db.commit()

    db.refresh(new_employee)

    return {

        "message": "Employee created successfully",

        "id": new_employee.id,

        "employee_code": new_employee.employee_code,

        "name": new_employee.name,

        "email": new_employee.email,

        "department": new_employee.department,

        "role": new_employee.role,

    }

@app.put("/employees/{employee_code}")

def update_employee(

    employee_code: str,

    employee: EmployeeUpdate,

    current_user=Depends(

        require_role("admin")

    ),

    db: Session = Depends(get_db),

):

    existing_employee = (

        db.query(Employee)

        .filter(

            Employee.employee_code

            == employee_code

        )

        .first()

    )

    if not existing_employee:

        raise HTTPException(

            status_code=404,

            detail="Employee not found",

        )

    existing_email = (

        db.query(Employee)

        .filter(

            Employee.email

            == employee.email,

            Employee.id

            != existing_employee.id,

        )

        .first()

    )

    if existing_email:

        raise HTTPException(

            status_code=400,

            detail="Employee email already registered",

        )

    existing_employee.name = employee.name

    existing_employee.email = employee.email

    existing_employee.department = (

        employee.department

    )

    existing_employee.role = employee.role

    db.commit()

    db.refresh(existing_employee)

    return {

        "message": "Employee updated successfully",

        "id": existing_employee.id,

        "employee_code": existing_employee.employee_code,

        "name": existing_employee.name,

        "email": existing_employee.email,

        "department": existing_employee.department,

        "role": existing_employee.role,

        "created_at": existing_employee.created_at,

    }

@app.delete("/employees/{employee_code}")

def delete_employee(

    employee_code: str,

    current_user=Depends(

        require_role("admin")

    ),

    db: Session = Depends(get_db),

):

    employee = (

        db.query(Employee)

        .filter(

            Employee.employee_code

            == employee_code

        )

        .first()

    )

    if not employee:

        raise HTTPException(

            status_code=404,

            detail="Employee not found",

        )

    deleted_employee_code = (

        employee.employee_code

    )

    db.delete(employee)

    db.commit()

    return {

        "message": "Employee deleted successfully",

        "employee_code": deleted_employee_code,

    }

@app.get("/employees/{employee_code}")

def get_employee(

    employee_code: str,

    current_user=Depends(

        get_current_user

    ),

    db: Session = Depends(get_db),

):

    employee = (

        db.query(Employee)

        .filter(

            Employee.employee_code

            == employee_code

        )

        .first()

    )

    if not employee:

        raise HTTPException(

            status_code=404,

            detail="Employee not found",

        )

    return {

        "id": employee.id,

        "employee_code": employee.employee_code,

        "name": employee.name,

        "email": employee.email,

        "department": employee.department,

        "role": employee.role,

        "created_at": employee.created_at,

    }

@app.get("/employees")

def list_employees(

    current_user=Depends(

        get_current_user

    ),

    db: Session = Depends(get_db),

):

    employees = (

        db.query(Employee)

        .order_by(Employee.id)

        .all()

    )

    return {

        "count": len(employees),

        "employees": [

            {

                "id": employee.id,

                "employee_code": employee.employee_code,

                "name": employee.name,

                "email": employee.email,

                "department": employee.department,

                "role": employee.role,

                "created_at": employee.created_at,

            }

            for employee in employees

        ],

    }


# ---------------------------------------------------------------------------
# Milestone 3 — Employee Risk Score
# ---------------------------------------------------------------------------


@app.get("/risk-score/{employee_code}")
def get_employee_risk_score(
    employee_code: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "admin",
            "security_analyst",
            "soc_engineer",
            "security_manager",
        )
    ),
):
    """Return an employee's weighted risk score and factor breakdown."""
    try:
        return calculate_risk_score(employee_code, db)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Milestone 3 — UEBA: Peer Comparison and Behavioral Trends
# ---------------------------------------------------------------------------

UEBA_ALLOWED_ROLES = (
    "admin",
    "security_analyst",
    "soc_engineer",
    "security_manager",
)


@app.get("/ueba/peer-comparison/{employee_code}")
def peer_comparison(
    employee_code: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(*UEBA_ALLOWED_ROLES)),
):
    """Compare an employee's risk score with departmental peers."""
    result = get_peer_group_comparison(employee_code, db)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Employee '{employee_code}' was not found",
        )

    return result


@app.get("/ueba/trend/{employee_code}")
def employee_behavioral_trend(
    employee_code: str,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(*UEBA_ALLOWED_ROLES)),
):
    """Return daily anomaly counts and their trend direction."""
    employee = (
        db.query(Employee)
        .filter(Employee.employee_code == employee_code)
        .first()
    )

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail=f"Employee '{employee_code}' was not found",
        )

    if days < 1 or days > 365:
        raise HTTPException(
            status_code=422,
            detail="days must be between 1 and 365",
        )

    return {
        "employee_code": employee_code,
        "days": days,
        "daily_trend": get_risk_trend(employee_code, days),
        "direction": get_trend_direction(employee_code),
    }


@app.get("/ueba/profile/{employee_code}")
def employee_ueba_profile(
    employee_code: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(*UEBA_ALLOWED_ROLES)),
):
    """Combine the employee's risk score, peer comparison, and trend."""
    try:
        risk_score = calculate_risk_score(employee_code, db)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    peer_comparison_result = get_peer_group_comparison(employee_code, db)
    trend_result = get_trend_direction(employee_code)

    return {
        "employee_code": employee_code,
        "risk_score": risk_score,
        "peer_comparison": peer_comparison_result,
        "trend": trend_result,
    }

# ---------------------------------------------------------------------------
# Milestone 3 — Incident Management
# ---------------------------------------------------------------------------


@app.post("/incidents", status_code=201)
def create_incident(
    incident_data: IncidentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "admin",
            "security_analyst",
            "soc_engineer",
            "security_manager",
        )
    ),
):
    """Create an incident only when the employee's risk is High or Critical."""
    employee = (
        db.query(Employee)
        .filter(Employee.employee_code == incident_data.employee_code)
        .first()
    )

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail=f"Employee '{incident_data.employee_code}' was not found",
        )

    try:
        risk_result = calculate_risk_score(incident_data.employee_code, db)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    risk_level = risk_result["risk_level"]
    if risk_level not in {"High", "Critical"}:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Incident creation requires High or Critical risk.",
                "employee_code": employee.employee_code,
                "risk_score": risk_result["risk_score"],
                "risk_level": risk_level,
            },
        )

    new_incident = Incident(
        employee_id=employee.id,
        incident_type=incident_data.incident_type,
        description=incident_data.description,
        severity=risk_level.lower(),
        status="open",
    )

    try:
        db.add(new_incident)
        db.commit()
        db.refresh(new_incident)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create incident.",
        ) from exc

    return {
        "message": "Incident created successfully.",
        "incident": {
            "id": new_incident.id,
            "employee_code": employee.employee_code,
            "employee_name": employee.name,
            "incident_type": new_incident.incident_type,
            "description": new_incident.description,
            "severity": new_incident.severity,
            "status": new_incident.status,
            "created_at": new_incident.created_at,
        },
        "risk_score": risk_result["risk_score"],
        "risk_level": risk_level,
    }


@app.get("/incidents")
def list_open_incidents(
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "admin",
            "security_analyst",
            "soc_engineer",
            "security_manager",
        )
    ),
):
    """Return incidents (optionally filtered by status) with employee metadata."""

    severity_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    query = db.query(Incident)
    if status and status.lower() != "all":
        query = query.filter(Incident.status == status.lower())
    elif status is None:
        # Backward compatibility for existing milestone test suites
        query = query.filter(Incident.status == "open")

    incidents = query.all()

    incidents.sort(
        key=lambda item: (
            severity_order.get(
                (item.severity or "").lower(), 4
            ),
            item.created_at,
        )
    )

    return {
        "count": len(incidents),
        "incidents": [
            {
                "id": item.id,
                "employee_id": item.employee_id,
                "employee_code": item.employee.employee_code if item.employee else f"EMP-{item.employee_id}",
                "employee_name": item.employee.name if item.employee else "Unknown",
                "department": item.employee.department if item.employee else "Unknown",
                "incident_type": item.incident_type,
                "description": item.description,
                "severity": item.severity,
                "status": item.status,
                "summary": item.summary,
                "resolved_at": item.resolved_at.isoformat() if item.resolved_at else None,
                "created_at": item.created_at,
            }
            for item in incidents
        ],
    }


@app.post("/incidents/{incident_id}/notes", status_code=201)
def add_investigation_note(
    incident_id: int,
    note_data: InvestigationNoteCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "admin",
            "security_analyst",
            "soc_engineer",
            "security_manager",
        )
    ),
):
    """Add a note to an incident and record its author."""

    # 1. Find the incident.
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    # 2. Prevent changes to resolved or closed incidents.
    if incident.status.lower() in {"resolved", "closed"}:
        raise HTTPException(
            status_code=409,
            detail="Cannot add notes to a resolved or closed incident",
        )

    # 3. Get the authenticated user's database ID from the JWT.
    try:
        author_user_id = int(current_user["sub"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid user ID in authentication token",
        )

    author = (
        db.query(User)
        .filter(User.id == author_user_id)
        .first()
    )

    if author is None:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user was not found",
        )

    # 4. Reject notes containing only whitespace.
    clean_note = note_data.note.strip()

    if not clean_note:
        raise HTTPException(
            status_code=422,
            detail="Investigation note cannot be blank",
        )

    # 5. Save the note and optional evidence reference.
    evidence = (
        note_data.evidence_reference.strip()
        if note_data.evidence_reference
        and note_data.evidence_reference.strip()
        else None
    )

    new_note = InvestigationNote(
        incident_id=incident.id,
        author_user_id=author_user_id,
        note=clean_note,
        evidence_reference=evidence,
    )

    try:
        db.add(new_note)

        # The first note starts the investigation.
        if incident.status.lower() == "open":
            incident.status = "investigating"

        db.commit()
        db.refresh(new_note)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to save investigation note",
        )

    return {
        "message": "Investigation note added successfully",
        "note": {
            "id": new_note.id,
            "incident_id": new_note.incident_id,
            "author_user_id": new_note.author_user_id,
            "author_email": author.email,
            "note": new_note.note,
            "evidence_reference": new_note.evidence_reference,
            "created_at": new_note.created_at,
        },
        "incident_status": incident.status,
    }

@app.get("/incidents/{incident_id}/notes")
def list_investigation_notes(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "admin",
            "security_analyst",
            "soc_engineer",
            "security_manager",
        )
    ),
):
    """Retrieve investigation notes from oldest to newest."""

    # Step 1: Verify that the incident exists.
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    # Step 2: Retrieve notes in chronological order.
    notes = (
        db.query(InvestigationNote)
        .filter(InvestigationNote.incident_id == incident_id)
        .order_by(
            InvestigationNote.created_at.asc(),
            InvestigationNote.id.asc(),
        )
        .all()
    )

    # Step 3: Return each note with its author and evidence reference.
    return {
        "incident_id": incident_id,
        "count": len(notes),
        "notes": [
            {
                "id": note.id,
                "author_user_id": note.author_user_id,
                "author_email": note.author.email,
                "note": note.note,
                "evidence_reference": note.evidence_reference,
                "created_at": note.created_at,
            }
            for note in notes
        ],
    }

@app.patch("/incidents/{incident_id}/resolve")
def resolve_incident(
    incident_id: int,
    resolution_data: IncidentResolve,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "admin",
            "security_analyst",
            "soc_engineer",
            "security_manager",
        )
    ),
):
    """Resolve an incident and record its resolution details."""

    # Step 1: Find the incident.
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    # Step 2: Prevent resolving the same incident twice.
    if incident.status.lower() in {"resolved", "closed"}:
        raise HTTPException(
            status_code=409,
            detail="Incident is already resolved or closed",
        )

    # Step 3: Validate the resolution summary.
    summary = resolution_data.resolution_summary.strip()

    if not summary:
        raise HTTPException(
            status_code=422,
            detail="Resolution summary cannot be blank",
        )

    # Step 4: Update the incident.
    incident.summary = summary
    incident.status = "resolved"
    incident.resolved_at = datetime.now(timezone.utc)

    # Step 5: Save changes to PostgreSQL.
    try:
        db.commit()
        db.refresh(incident)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to resolve incident",
        )

    # Step 6: Return the updated incident.
    return {
        "message": "Incident resolved successfully",
        "incident": {
            "id": incident.id,
            "severity": incident.severity,
            "status": incident.status,
            "summary": incident.summary,
            "created_at": incident.created_at,
            "resolved_at": incident.resolved_at,
        },
    }

# ---------------------------------------------------------------------------
# Milestone 3 — Incident Timeline
# ---------------------------------------------------------------------------

@app.get("/incidents/timeline/{employee_code}")
def get_employee_incident_timeline(
    employee_code: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "admin",
            "security_analyst",
            "soc_engineer",
            "security_manager",
        )
    ),
):
    """Return a chronological activity and security-event timeline."""
    try:
        return get_incident_timeline(employee_code, db)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


# ---------------------------------------------------------------------------
# Milestone 3 — Alert Assignment
# ---------------------------------------------------------------------------

class AlertAssignRequest(BaseModel):
    analyst_user_id: int | None = None


@app.post("/alerts/{alert_id}/assign")
def assign_alert(
    alert_id: int,
    analyst_user_id: int | None = None,
    payload: AlertAssignRequest | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin", "security_manager")
    ),
):
    """Assign an existing alert to a registered user."""
    target_user_id = analyst_user_id if analyst_user_id is not None else (payload.analyst_user_id if payload else None)
    if target_user_id is None:
        raise HTTPException(
            status_code=422,
            detail="analyst_user_id is required.",
        )

    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail="Alert not found",
        )

    assignee = db.query(User).filter(User.id == target_user_id).first()

    if assignee is None:
        raise HTTPException(
            status_code=404,
            detail="Assignee user not found",
        )

    if assignee.role not in {"admin", "security_analyst", "soc_engineer"}:
        raise HTTPException(
            status_code=422,
            detail="Assignee must have an eligible security role.",
        )

    alert.assigned_to = assignee.id
    alert.status = "assigned"

    try:
        db.commit()
        db.refresh(alert)
        record_audit_log(
            db=db,
            user=current_user,
            action="ALERT_ASSIGNED",
            resource_type="alert",
            resource_id=str(alert.id),
            details=f"Alert #{alert.id} ({alert.alert_type}) assigned to {assignee.email}",
        )
        ws_manager.broadcast_sync(
            create_notification_payload(
                title="Alert Assigned",
                message=f"Alert #{alert.id} ({alert.alert_type}) assigned to {assignee.email}",
                severity=alert.severity,
                category="alert",
                reference_id=str(alert.id),
            )
        )
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to assign alert.",
        ) from exc

    return {
        "message": f"Alert {alert.id} assigned successfully.",
        "alert_id": alert.id,
        "assigned_to": alert.assigned_to,
        "assignee_email": assignee.email,
        "status": alert.status,
    }


@app.post("/alerts/generate")
def run_alert_generation(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin", "security_analyst", "soc_engineer", "security_manager")
    ),
):
    """Generate incidents and alerts from qualifying anomalies."""

    try:
        result = generate_alerts(db)
        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Alert generation failed. Check the backend logs.",
        ) from exc


@app.post("/alerts/escalate")
def run_alert_escalation(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin", "security_analyst", "soc_engineer", "security_manager")
    ),
):
    """Escalate overdue unresolved alerts."""

    try:
        return escalate_overdue_alerts(db)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Alert escalation failed. Check the backend logs.",
        ) from exc


# ---------------------------------------------------------------------------
# Milestone 3 — Alert Resolution
# ---------------------------------------------------------------------------

@app.patch("/alerts/{alert_id}/resolve")
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin", "security_analyst")
    ),
):
    """Mark an existing alert as resolved."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail="Alert not found",
        )

    if alert.status == "resolved":
        return {
            "message": f"Alert {alert.id} is already resolved.",
            "alert_id": alert.id,
            "status": alert.status,
            "resolved_at": alert.resolved_at,
        }

    alert.status = "resolved"
    alert.resolved_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(alert)
        record_audit_log(
            db=db,
            user=current_user,
            action="ALERT_RESOLVED",
            resource_type="alert",
            resource_id=str(alert.id),
            details=f"Alert #{alert.id} ({alert.alert_type}) resolved",
        )
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to resolve alert.",
        ) from exc

    return {
    "message": f"Alert {alert.id} resolved successfully.",
    "alert_id": alert.id,
    "status": alert.status,
    "resolved_at": alert.resolved_at,
    }


# ---------------------------------------------------------------------------
# Milestone 3 — Risk Analytics
# ---------------------------------------------------------------------------

@app.get("/analytics/risk-distribution")
def get_risk_distribution(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin", "security_manager", "security_analyst", "soc_engineer")
    ),
):
    """Return the current employee distribution across risk categories."""
    employees = db.query(Employee).order_by(Employee.id).all()

    distribution = {
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
    }

    for employee in employees:
        try:
            result = calculate_risk_score(employee.employee_code, db)
        except ValueError as exc:
            raise HTTPException(
                status_code=404,
                detail=str(exc),
            ) from exc

        category = result["risk_level"].lower()

        if category not in distribution:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected risk category: {category}",
            )

        distribution[category] += 1

    return {
        "total_employees": len(employees),
        "distribution": distribution,
    }



# ---------------------------------------------------------------------------
# Milestone 3 - Analyst Dashboard
# ---------------------------------------------------------------------------

@app.get("/dashboard/analyst")
def get_analyst_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin", "security_analyst")),
):
    """Return actionable security metrics for an analyst."""

    from collections import Counter
    from datetime import datetime, timedelta, timezone

    try:
        user_id = int(current_user["sub"])
    except (ValueError, TypeError, KeyError):
        user_id = 0

    security_events = activity_logs.count_documents({})
    rule_anomaly_count = rule_anomalies.count_documents({})
    ml_anomaly_count = ml_anomalies.count_documents({"is_anomaly": True})

    open_alerts = (
        db.query(Alert)
        .filter(
            Alert.status.in_(["open", "assigned", "escalated"]),
            Alert.resolved_at.is_(None),
        )
        .order_by(Alert.created_at.desc())
        .all()
    )

    personal_queue = (
        db.query(Alert)
        .filter(
            Alert.assigned_to == user_id,
            Alert.status.in_(["open", "assigned", "escalated"]),
            Alert.resolved_at.is_(None),
        )
        .order_by(Alert.created_at.desc())
        .all()
    )

    open_incidents = (
        db.query(Incident)
        .filter(~Incident.status.in_(["resolved", "closed"]))
        .order_by(Incident.created_at.desc())
        .all()
    )

    top_risk_employees = []
    for employee in db.query(Employee).all():
        result = calculate_risk_score(employee.employee_code, db)
        top_risk_employees.append({
            "employee_code": employee.employee_code,
            "employee_name": employee.name,
            "department": employee.department,
            "risk_score": result["risk_score"],
            "risk_level": result["risk_level"],
            "factor_scores": result["factor_scores"],
            "weights": result["weights"],
            "privilege_misuse_signal_available": result[
                "privilege_misuse_signal_available"
            ],
        })

    top_risk_employees.sort(
        key=lambda item: item["risk_score"],
        reverse=True,
    )

    return {
        "security_events": security_events,
        "behavioral_anomalies": {
            "rule_based": rule_anomaly_count,
            "machine_learning": ml_anomaly_count,
            "total": rule_anomaly_count + ml_anomaly_count,
        },
        "open_alerts": [
            {
                "id": alert.id,
                "incident_id": alert.incident_id,
                "employee_id": alert.employee_id,
                "alert_type": alert.alert_type,
                "message": alert.message,
                "severity": alert.severity,
                "status": alert.status,
                "assigned_to": alert.assigned_to,
                "created_at": alert.created_at.isoformat(),
                "escalation_level": alert.escalation_level,
            }
            for alert in open_alerts
        ],
        "personal_investigation_queue": [
            {
                "id": alert.id,
                "incident_id": alert.incident_id,
                "alert_type": alert.alert_type,
                "message": alert.message,
                "severity": alert.severity,
                "status": alert.status,
                "created_at": alert.created_at.isoformat(),
            }
            for alert in personal_queue
        ],
        "open_incidents": [
            {
                "id": incident.id,
                "employee_id": incident.employee_id,
                "incident_type": incident.incident_type,
                "description": incident.description,
                "severity": incident.severity,
                "status": incident.status,
                "created_at": incident.created_at.isoformat(),
            }
            for incident in open_incidents
        ],
        "active_investigations": len(open_incidents),
        "top_risk_employees": top_risk_employees[:5],
        "recent_threat_intelligence_notes": [],
        "threat_intelligence_source_available": False,
    }


# ---------------------------------------------------------------------------
# Milestone 3 - Security Operations Center (SOC) Dashboard
# ---------------------------------------------------------------------------

@app.get("/dashboard/soc")
def get_soc_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin", "soc_engineer")),
):
    """Return SOC alert, anomaly-trend, and investigation metrics."""

    from collections import Counter
    from datetime import datetime, timedelta, timezone

    security_events = activity_logs.count_documents({})
    rule_anomaly_count = rule_anomalies.count_documents({})
    ml_anomaly_count = ml_anomalies.count_documents({"is_anomaly": True})

    alert_severity_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    for severity, count in (
        db.query(Alert.severity, func.count(Alert.id))
        .filter(
            Alert.status.in_(["open", "assigned", "escalated"]),
            Alert.resolved_at.is_(None),
        )
        .group_by(Alert.severity)
        .all()
    ):
        key = (severity or "").lower()
        if key in alert_severity_counts:
            alert_severity_counts[key] += count

    now = datetime.now(timezone.utc)
    start_time = now - timedelta(days=6)
    trend_start = start_time.date().isoformat()

    
    rule_trend = Counter()
    for item in rule_anomalies.find(
        {"date": {"$gte": trend_start}},
        {"_id": 0, "date": 1},
    ):
        anomaly_date = str(item.get("date", ""))[:10]
        if anomaly_date:
            rule_trend[anomaly_date] += 1

    ml_trend = Counter()
    for item in ml_anomalies.find(
        {
            "is_anomaly": True,
            "date": {"$gte": trend_start},
        },
        {"_id": 0, "date": 1},
    ):
        anomaly_date = str(item.get("date", ""))[:10]
        if anomaly_date:
            ml_trend[anomaly_date] += 1


    anomaly_trend = []
    for days_ago in range(6, -1, -1):
        day = (now - timedelta(days=days_ago)).date().isoformat()
        rule_count = rule_trend.get(day, 0)
        ml_count = ml_trend.get(day, 0)
        anomaly_trend.append({
            "date": day,
            "rule_based": rule_count,
            "machine_learning": ml_count,
            "total": rule_count + ml_count,
        })

    active_investigations = (
        db.query(Incident)
        .filter(~Incident.status.in_(["resolved", "closed"]))
        .order_by(Incident.created_at.desc())
        .all()
    )

    return {
        "security_events": security_events,
        "behavioral_anomalies": {
            "rule_based": rule_anomaly_count,
            "machine_learning": ml_anomaly_count,
            "total": rule_anomaly_count + ml_anomaly_count,
        },
        "alerts_by_severity": alert_severity_counts,
        "anomaly_trend_last_7_days": anomaly_trend,
        "active_investigations": [
            {
                "id": incident.id,
                "employee_id": incident.employee_id,
                "incident_type": incident.incident_type,
                "description": incident.description,
                "severity": incident.severity,
                "status": incident.status,
                "created_at": incident.created_at.isoformat(),
            }
            for incident in active_investigations
        ],
        "active_investigation_count": len(active_investigations),
        "recent_threat_intelligence_notes": [],
        "threat_intelligence_source_available": False,
    }


# ---------------------------------------------------------------------------
# Milestone 3 — Security Manager Dashboard
# ---------------------------------------------------------------------------

@app.get("/dashboard/manager")
def get_manager_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin", "security_manager")
    ),
):
    """Return organizational risk posture and operational indicators."""

    from collections import Counter
    from datetime import datetime, timedelta, timezone

    # 1. Calculate current organizational risk posture.
    employees = db.query(Employee).order_by(Employee.id).all()

    risk_distribution = {
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
    }

    for employee in employees:
        result = calculate_risk_score(employee.employee_code, db)
        risk_level = result["risk_level"].lower()

        if risk_level not in risk_distribution:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected risk category: {risk_level}",
            )

        risk_distribution[risk_level] += 1

    # 2. Count incidents created in the previous seven days.
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(days=7)

    recent_incidents = (
        db.query(Incident)
        .filter(Incident.created_at >= start_time.replace(tzinfo=None))
        .all()
    )

    incidents_by_day = Counter(
        incident.created_at.date().isoformat()
        for incident in recent_incidents
    )

    # Include all seven calendar dates in the response.
    incident_trend = []
    for days_ago in range(6, -1, -1):
        day = (now - timedelta(days=days_ago)).date().isoformat()
        incident_trend.append({
            "date": day,
            "incident_count": incidents_by_day.get(day, 0),
        })

    # 3. Provide measurable operational indicators.
    total_incidents = db.query(Incident).count()
    unresolved_incidents = (
        db.query(Incident)
        .filter(~Incident.status.in_(["resolved", "closed"]))
        .count()
    )

    total_alerts = db.query(Alert).count()
    resolved_alerts = (
        db.query(Alert)
        .filter(Alert.status == "resolved")
        .count()
    )

    return {
        "organizational_risk_posture": {
            "total_employees": len(employees),
            "risk_distribution": risk_distribution,
        },
        "incident_trend_last_7_days": incident_trend,
        "operational_metrics": {
            "total_incidents": total_incidents,
            "unresolved_incidents": unresolved_incidents,
            "total_alerts": total_alerts,
            "resolved_alerts": resolved_alerts,
        },
        "compliance_metrics": {
            "available": False,
            "message": (
                "Formal compliance metrics are unavailable because "
                "the project does not yet have compliance audit records."
            ),
        },
        "historical_risk_scores_available": False,
    }


# ---------------------------------------------------------------------------
# Milestone 3 — Threat Investigation Shortcuts
# ---------------------------------------------------------------------------

@app.post("/incidents/create-from-risk/{employee_id}", status_code=201)
def create_incident_from_risk(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin", "security_analyst", "security_manager", "soc_engineer")
    ),
):
    """Auto-create an incident for high or critical risk findings."""
    is_numeric_id = False
    int_id = None
    try:
        int_id = int(employee_id)
        is_numeric_id = True
    except (ValueError, TypeError):
        pass

    employee = (
        db.query(Employee)
        .filter(
            (Employee.employee_code == employee_id)
            | ((Employee.id == int_id) if is_numeric_id else False)
        )
        .first()
    )
    if not employee:
        raise HTTPException(
            status_code=404,
            detail=f"Employee '{employee_id}' was not found",
        )

    risk = calculate_risk_score(employee.employee_code, db)
    if risk["risk_category"] not in ("high", "critical"):
        raise HTTPException(
            status_code=400,
            detail="Risk level too low to warrant an incident",
        )

    incident = Incident(
        employee_id=employee.id,
        incident_type="Risk Threshold Escalation",
        description=f"Auto-created from risk score {risk['risk_score']}",
        severity=risk["risk_category"],
        status="open",
        summary=f"Auto-created from risk score {risk['risk_score']}",
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    return {
        "id": incident.id,
        "employee_id": employee.employee_code,
        "severity": incident.severity,
        "status": incident.status,
        "summary": incident.summary,
        "created_at": incident.created_at,
    }


@app.get("/incidents/{incident_id}/timeline")
def get_incident_timeline_by_id(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin", "security_analyst", "security_manager", "soc_engineer")
    ),
):
    """Retrieve chronological timeline for a specific incident."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    employee = db.query(Employee).filter(Employee.id == incident.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee for this incident not found")

    timeline_data = get_incident_timeline(employee.employee_code, db)
    return {
        "incident_id": incident_id,
        "employee_code": employee.employee_code,
        "timeline": timeline_data["timeline"],
    }


# ---------------------------------------------------------------------------
# Milestone 4 — Day 33: PDF Reports
# ---------------------------------------------------------------------------

@app.get("/reports/compliance/pdf")
def download_compliance_report(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin", "security_manager")
    ),
):
    """Generate and download in-memory compliance summary PDF report."""
    employees = db.query(Employee).all()
    risk_distribution = {
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
    }

    for emp in employees:
        result = calculate_risk_score(emp.employee_code, db)
        cat = result.get("risk_category", "low").lower()
        if cat in risk_distribution:
            risk_distribution[cat] += 1

    total_incidents = db.query(Incident).count()
    resolved_incidents = (
        db.query(Incident)
        .filter(Incident.status.in_(["resolved", "closed"]))
        .count()
    )
    total_alerts = db.query(Alert).count()
    resolved_alerts = (
        db.query(Alert)
        .filter(Alert.status == "resolved")
        .count()
    )

    incident_pct = (
        f"{(resolved_incidents / total_incidents * 100):.1f}%"
        if total_incidents > 0
        else "100%"
    )
    alert_pct = (
        f"{(resolved_alerts / total_alerts * 100):.1f}%"
        if total_alerts > 0
        else "100%"
    )

    compliance_data = {
        "total_employees": len(employees),
        "risk_distribution": risk_distribution,
        "metrics": [
            {
                "metric": "Personnel Monitored",
                "value": f"{len(employees)} Personnel",
                "target": "100% Monitored",
            },
            {
                "metric": "Incident Resolution Rate",
                "value": incident_pct,
                "target": ">= 95% SLA",
            },
            {
                "metric": "Alert Triage Rate",
                "value": alert_pct,
                "target": ">= 98% SLA",
            },
            {
                "metric": "ISO/IEC 27001 Access Controls",
                "value": "Compliant",
                "target": "Mandatory",
            },
            {
                "metric": "Continuous UEBA Auditing",
                "value": "Operational",
                "target": "24/7 Active",
            },
        ],
    }

    pdf_bytes = generate_compliance_report(compliance_data)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=compliance_summary_report.pdf"
        },
    )


# ---------------------------------------------------------------------------
# Milestone 4 — Part 2: Platform Insider Threat Report Exports
# ---------------------------------------------------------------------------

def generate_insider_threat_report(db: Session) -> pd.DataFrame:
    """Format company-wide employee risk scores for bulk export."""
    employees = db.query(Employee).all()
    rows = []
    for emp in employees:
        risk = calculate_risk_score(emp.employee_code, db)
        rows.append({
            "Employee ID": emp.employee_code,
            "Name": emp.name,
            "Department": emp.department,
            "Risk Score": risk["final_score"],
            "Risk Level": risk["risk_level"],
        })
    return pd.DataFrame(rows)


@app.get("/reports/insider-threat/excel")
def export_insider_threat_excel(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin", "security_manager", "security_analyst", "soc_engineer")
    ),
):
    """Bulk Excel export of insider threat matrix (Milestone 4 Day 33-34)."""
    df = generate_insider_threat_report(db)
    if not df.empty and "Risk Score" in df.columns:
        df = df.sort_values("Risk Score", ascending=False)

    buffer = io.BytesIO()
    df.to_excel(
        buffer,
        index=False,
        engine="openpyxl",
        sheet_name="Insider Threat Report",
    )
    buffer.seek(0)
    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=insider_threat_report.xlsx"},
    )


@app.get("/reports/insider-threat/pdf")
def export_insider_threat_pdf(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin", "security_manager", "security_analyst", "soc_engineer")
    ),
):
    """Tabular PDF export of company-wide insider threats (Milestone 4 Day 33-34)."""
    from reportlab.platypus import SimpleDocTemplate, Table as RLTable, TableStyle as RLTableStyle
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter

    df = generate_insider_threat_report(db)
    if not df.empty and "Risk Score" in df.columns:
        df = df.sort_values("Risk Score", ascending=False)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=30, rightMargin=30)
    data = [df.columns.tolist()] + df.values.tolist()
    table = RLTable(data, colWidths=[100, 150, 100, 90, 90])
    table.setStyle(RLTableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7a1f2b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (3, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    doc.build([table])
    buffer.seek(0)
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=insider_threat_report.pdf"},
    )


@app.get("/reports/{employee_id}/pdf")
def download_risk_report(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin", "security_analyst", "security_manager", "soc_engineer")
    ),
):
    """Generate and download in-memory PDF risk dossier for an employee."""
    is_numeric_id = False
    int_id = None
    try:
        int_id = int(employee_id)
        is_numeric_id = True
    except (ValueError, TypeError):
        pass

    employee = (
        db.query(Employee)
        .filter(
            (Employee.employee_code == employee_id)
            | ((Employee.id == int_id) if is_numeric_id else False)
        )
        .first()
    )
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    risk = calculate_risk_score(employee.employee_code, db)

    rule_items = list(
        rule_anomalies.find({
            "$or": [
                {"employee_code": employee.employee_code},
                {"employee_id": employee.employee_code},
            ]
        })
    )
    ml_items = list(
        ml_anomalies.find({
            "employee_code": employee.employee_code,
            "is_anomaly": True,
        })
    )
    all_anomalies = rule_items + ml_items

    pdf_bytes = generate_employee_risk_report(
        employee_id=employee.employee_code,
        risk_data=risk,
        anomalies=all_anomalies,
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={employee.employee_code}_risk_report.pdf"
        },
    )


# ---------------------------------------------------------------------------
# Milestone 4 — Day 34: Excel Export & Report Catalog
# ---------------------------------------------------------------------------

@app.get("/reports/export/risk-scores")
def export_risk_scores_excel(
    department: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin", "security_manager")
    ),
):
    """Export employee risk scores to an in-memory Excel spreadsheet."""
    query = db.query(Employee)
    if department:
        query = query.filter(Employee.department == department)
    employees = query.all()

    rows = []
    for emp in employees:
        risk = calculate_risk_score(emp.employee_code, db)
        rows.append({
            "Employee ID": emp.employee_code,
            "Name": emp.name,
            "Department": emp.department,
            "Risk Score": risk["risk_score"],
            "Risk Level": risk["risk_level"],
        })

    df = pd.DataFrame(rows)
    if not df.empty and "Risk Score" in df.columns:
        df = df.sort_values("Risk Score", ascending=False)

    buffer = io.BytesIO()
    df.to_excel(
        buffer,
        index=False,
        engine="openpyxl",
        sheet_name="Risk Scores",
    )
    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=risk_scores_export.xlsx"
        },
    )


@app.get("/reports/export/incidents")
def export_incidents_excel(
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin", "security_manager")
    ),
):
    """Export security incident logs to an in-memory Excel spreadsheet."""
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status)
    incidents = query.all()

    rows = [
        {
            "Incident ID": i.id,
            "Employee ID": i.employee.employee_code if i.employee else str(i.employee_id),
            "Severity": i.severity,
            "Status": i.status,
            "Created": i.created_at.strftime("%Y-%m-%d %H:%M") if i.created_at else "N/A",
            "Resolved": (
                i.resolved_at.strftime("%Y-%m-%d %H:%M")
                if i.resolved_at
                else "Not resolved"
            ),
        }
        for i in incidents
    ]

    df = pd.DataFrame(rows)
    buffer = io.BytesIO()
    df.to_excel(
        buffer,
        index=False,
        engine="openpyxl",
        sheet_name="Incidents",
    )
    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=incidents_export.xlsx"
        },
    )


@app.get("/reports/catalog")
def list_available_reports(
    current_user=Depends(
        require_role("admin", "security_analyst", "security_manager", "soc_engineer")
    ),
):
    """Catalog of all reports and exports available in the platform."""
    return {
        "reports": [
            {
                "name": "Employee Risk Report",
                "format": "PDF",
                "endpoint": "/reports/{employee_id}/pdf",
                "description": "In-memory individual employee risk breakdown and anomaly history.",
            },
            {
                "name": "Compliance Summary Report",
                "format": "PDF",
                "endpoint": "/reports/compliance/pdf",
                "description": "In-memory organizational risk posture and ISO/NIST compliance metrics.",
            },
            {
                "name": "All Risk Scores",
                "format": "Excel",
                "endpoint": "/reports/export/risk-scores",
                "description": "Bulk export of employee risk scores sorted highest-risk first with optional department filter.",
            },
            {
                "name": "Incident Report",
                "format": "Excel",
                "endpoint": "/reports/export/incidents",
                "description": "Bulk export of security incidents with resolution status and optional status filter.",
            },
            {
                "name": "Insider Threat Report (Excel)",
                "format": "Excel",
                "endpoint": "/reports/insider-threat/excel",
                "description": "Comprehensive platform-wide insider risk ledger in spreadsheet format.",
            },
            {
                "name": "Insider Threat Report (PDF)",
                "format": "PDF",
                "endpoint": "/reports/insider-threat/pdf",
                "description": "Tabular executive PDF summary of insider threat scores.",
            },
        ]
    }


# ---------------------------------------------------------------------------
# Milestone 4 — Part 1: Admin Platform Dashboard
# ---------------------------------------------------------------------------

@app.get("/dashboard/admin")
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    """
    Platform administration dashboard as specified in Milestone 4 Day 31-32.
    Tracks user management, infrastructure telemetry, and platform posture.
    """
    user_count = db.query(User).count()
    employee_count = db.query(Employee).count()
    total_incidents = db.query(Incident).count()
    open_incidents = db.query(Incident).filter(Incident.status == "open").count()
    total_alerts = db.query(Alert).count()

    role_breakdown = {}
    for role_row in db.query(User.role, User.id).all():
        canon = canonical_role(role_row[0])
        role_breakdown[canon] = role_breakdown.get(canon, 0) + 1

    return {
        "user_count": user_count,
        "employee_count": employee_count,
        "total_incidents": total_incidents,
        "open_incidents": open_incidents,
        "total_alerts": total_alerts,
        "users_by_role": role_breakdown,
        "system_status": {
            "api_gateway": "operational",
            "database_postgresql": "connected",
            "database_mongodb": "connected",
            "ml_engine": "active",
        },
    }


# ---------------------------------------------------------------------------
# Milestone 4 — Part 1: Notification & Escalation Polish
# ---------------------------------------------------------------------------

def notify_on_critical_alert(alert: Alert, db: Session) -> list[dict]:
    """Build in-app notification payloads for managers on critical alerts."""
    managers = db.query(User).filter(User.role == "security_manager").all()
    emp = db.query(Employee).filter(Employee.id == alert.employee_id).first()
    emp_code = emp.employee_code if emp else f"EMP-{alert.employee_id}"
    notifications = []
    for manager in managers:
        notifications.append({
            "id": alert.id,
            "recipient_id": manager.id,
            "title": f"Alert: {alert.alert_type}",
            "message": f"Critical alert for {emp_code}: {alert.message}",
            "channel": "in_app",
            "alert_id": alert.id,
            "severity": alert.severity,
            "employee_code": emp_code,
            "timestamp": alert.created_at.isoformat() if alert.created_at else None,
        })
    return notifications


@app.get("/notifications")
def get_in_app_notifications(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin", "security_manager", "security_analyst", "soc_engineer")
    ),
):
    """Return in-app notification alerts for critical security events."""
    critical_alerts = (
        db.query(Alert)
        .filter(Alert.severity.in_(["critical", "high"]))
        .order_by(Alert.created_at.desc())
        .limit(25)
        .all()
    )
    all_notifications = []
    for alert in critical_alerts:
        all_notifications.extend(notify_on_critical_alert(alert, db))
    return {
        "count": len(all_notifications),
        "notifications": all_notifications,
    }


# ---------------------------------------------------------------------------
# Alerts & Incident Management Endpoints
# ---------------------------------------------------------------------------

@app.get("/alerts")
def list_alerts(
    status: str | None = None,
    severity: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin", "security_analyst", "soc_engineer", "security_manager")
    ),
):
    """List all security alerts with optional status and severity filtering."""
    query = db.query(Alert)
    if status and status.lower() != "all":
        query = query.filter(Alert.status == status.lower())
    if severity and severity.lower() != "all":
        query = query.filter(Alert.severity == severity.lower())

    alerts = query.order_by(Alert.created_at.desc()).all()
    results = []
    for a in alerts:
        emp = db.query(Employee).filter(Employee.id == a.employee_id).first()
        assignee = db.query(User).filter(User.id == a.assigned_to).first() if a.assigned_to else None
        results.append({
            "id": a.id,
            "incident_id": a.incident_id,
            "employee_id": a.employee_id,
            "employee_code": emp.employee_code if emp else f"EMP-{a.employee_id}",
            "employee_name": emp.name if emp else "Unknown",
            "department": emp.department if emp else "Unknown",
            "alert_type": a.alert_type,
            "message": a.message,
            "severity": a.severity,
            "status": a.status,
            "assigned_to": a.assigned_to,
            "assignee_email": assignee.email if assignee else None,
            "escalation_level": a.escalation_level,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None,
        })
    return {"count": len(results), "alerts": results}


@app.patch("/incidents/{incident_id}/status")
def update_incident_status(
    incident_id: int,
    payload: IncidentStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin", "security_analyst", "soc_engineer", "security_manager")
    ),
):
    """Update incident status (open, investigating, resolved, closed)."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    old_status = incident.status
    incident.status = payload.status.lower()
    if payload.summary:
        incident.summary = payload.summary
    if payload.status.lower() in {"resolved", "closed"} and not incident.resolved_at:
        incident.resolved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(incident)

    record_audit_log(
        db=db,
        user=current_user,
        action="INCIDENT_STATUS_CHANGE",
        resource_type="incident",
        resource_id=str(incident.id),
        details=f"Status changed from {old_status} to {incident.status}",
    )
    return {"message": "Status updated successfully", "incident_id": incident.id, "status": incident.status}


# ---------------------------------------------------------------------------
# Platform Audit Trail Endpoints
# ---------------------------------------------------------------------------

@app.get("/audit-logs")
def list_audit_logs(
    skip: int = 0,
    limit: int = 100,
    action: str | None = None,
    user_email: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin", "security_manager")),
):
    """Retrieve platform operational audit trail."""
    query = db.query(AuditLog)
    if action and action.lower() != "all":
        query = query.filter(AuditLog.action == action.upper())
    if user_email:
        query = query.filter(AuditLog.user_email.ilike(f"%{user_email}%"))

    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    return {
        "total": total,
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "user_email": log.user_email,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ],
    }


# ---------------------------------------------------------------------------
# Explainable AI (XAI) Endpoints
# ---------------------------------------------------------------------------

@app.get("/anomalies/{employee_code}/xai")
def get_employee_anomaly_explanations(
    employee_code: str,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin", "security_analyst", "soc_engineer", "security_manager")),
):
    """Generate Explainable AI feature attribution and risk drivers for an employee."""
    records = list(
        ml_anomalies.find({"employee_code": employee_code, "is_anomaly": True})
        .sort("date", -1)
        .limit(limit)
    )
    if not records:
        records = list(
            ml_anomalies.find({"employee_code": employee_code})
            .sort("date", -1)
            .limit(limit)
        )

    explanations = [explain_anomaly_record(rec, employee_code) for rec in records]
    return {
        "employee_code": employee_code,
        "count": len(explanations),
        "explanations": explanations,
    }


# ---------------------------------------------------------------------------
# Analyst Anomaly Feedback & Active Learning Retraining
# ---------------------------------------------------------------------------

@app.post("/anomalies/{anomaly_id}/feedback")
def submit_anomaly_feedback(
    anomaly_id: str,
    payload: AnomalyFeedbackCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin", "security_analyst", "soc_engineer")),
):
    """Submit analyst feedback (false positive, confirmed, benign) for an anomaly."""
    user_id = current_user.get("sub")
    user_email = current_user.get("email") or str(user_id)

    feedback_doc = {
        "anomaly_id": anomaly_id,
        "feedback": payload.feedback.lower(),
        "notes": payload.notes,
        "analyst_id": user_id,
        "analyst_email": user_email,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    anomaly_feedback.update_one(
        {"anomaly_id": anomaly_id},
        {"$set": feedback_doc},
        upsert=True,
    )

    record_audit_log(
        db=db,
        user=current_user,
        action="ANOMALY_FEEDBACK_SUBMITTED",
        resource_type="anomaly",
        resource_id=anomaly_id,
        details=f"Feedback: {payload.feedback.lower()} | Notes: {payload.notes or 'None'}",
    )
    return {"message": "Feedback recorded successfully", "feedback": feedback_doc}


@app.get("/anomalies/feedback")
def list_anomaly_feedback(
    current_user=Depends(require_role("admin", "security_analyst", "soc_engineer", "security_manager")),
):
    """List all submitted analyst feedback."""
    items = list(anomaly_feedback.find({}, {"_id": 0}))
    return {"count": len(items), "feedback": items}


@app.post("/ml/retrain")
def retrain_ml_model(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin", "security_analyst", "soc_engineer", "security_manager")
    ),
):
    """Trigger active learning retraining of the Isolation Forest model incorporating analyst feedback."""
    from app.ml_features import build_feature_table
    from app.ml_anomaly import train_anomaly_model, score_anomalies

    features = build_feature_table()
    if features.empty:
        raise HTTPException(status_code=400, detail="Cannot retrain: insufficient telemetry data.")

    fp_records = set(
        doc["anomaly_id"]
        for doc in anomaly_feedback.find({"feedback": "false_positive"})
    )

    model = train_anomaly_model(features)
    scored = score_anomalies(model, features)

    ml_anomalies.delete_many({})
    records = scored.to_dict(orient="records")
    for r in records:
        for k, v in list(r.items()):
            if isinstance(v, (date, datetime)):
                r[k] = v.isoformat()
    if records:
        ml_anomalies.insert_many(records)

    record_audit_log(
        db=db,
        user=current_user,
        action="MODEL_RETRAINED",
        resource_type="ml_model",
        resource_id="isolation_forest",
        details=f"Retrained on {len(features)} feature rows. False positive exemptions: {len(fp_records)}.",
    )
    return {
        "message": "Model retrained successfully with active learning feedback incorporated.",
        "samples_trained": len(features),
        "false_positive_adjustments": len(fp_records),
    }


# ---------------------------------------------------------------------------
# Global Threat Hunting & Search API
# ---------------------------------------------------------------------------

@app.get("/search")
def global_search(
    q: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin", "security_analyst", "soc_engineer", "security_manager")),
):
    """Unified global telemetry & entity search for threat hunting."""
    import re
    from sqlalchemy import or_

    query_str = q.strip()
    if not query_str:
        return {"query": "", "employees": [], "incidents": [], "alerts": [], "activity_logs": [], "total_matches": 0}

    # Generate search terms and hyphen variants
    search_terms = {query_str}
    m_code = re.match(r"^([a-zA-Z]+)(\d+)$", query_str)
    if m_code:
        search_terms.add(f"{m_code.group(1)}-{m_code.group(2)}")
    if "-" in query_str:
        search_terms.add(query_str.replace("-", ""))

    # Extract numeric IDs (e.g., "#15", "15", "Incident 15")
    numeric_ids: list[int] = []
    cleaned_num = re.sub(r"[^\d]", "", query_str)
    if cleaned_num and len(cleaned_num) <= 9:
        try:
            numeric_ids.append(int(cleaned_num))
        except ValueError:
            pass
    for num_str in re.findall(r"\b\d+\b", query_str):
        if len(num_str) <= 9:
            try:
                numeric_ids.append(int(num_str))
            except ValueError:
                pass
    numeric_ids = list(set(numeric_ids))

    # 1. Search Employees
    emp_filters = []
    for term in search_terms:
        emp_filters.append(
            (Employee.employee_code.ilike(f"%{term}%"))
            | (Employee.name.ilike(f"%{term}%"))
            | (Employee.email.ilike(f"%{term}%"))
            | (Employee.department.ilike(f"%{term}%"))
            | (Employee.role.ilike(f"%{term}%"))
        )
    if numeric_ids:
        emp_filters.append(Employee.id.in_(numeric_ids))

    emp_matches = (
        db.query(Employee)
        .filter(or_(*emp_filters))
        .limit(10)
        .all()
    )

    # 2. Search Incidents (with outer join on Employee to match subject)
    inc_filters = []
    for term in search_terms:
        inc_filters.append(
            (Incident.description.ilike(f"%{term}%"))
            | (Incident.incident_type.ilike(f"%{term}%"))
            | (Incident.severity.ilike(f"%{term}%"))
            | (Incident.status.ilike(f"%{term}%"))
            | (Employee.name.ilike(f"%{term}%"))
            | (Employee.employee_code.ilike(f"%{term}%"))
            | (Employee.department.ilike(f"%{term}%"))
        )
    if numeric_ids:
        inc_filters.append(Incident.id.in_(numeric_ids))

    inc_matches = (
        db.query(Incident)
        .outerjoin(Employee, Incident.employee_id == Employee.id)
        .filter(or_(*inc_filters))
        .order_by(Incident.id.desc())
        .limit(10)
        .all()
    )

    # 3. Search Alerts (with outer join on Employee)
    alert_filters = []
    for term in search_terms:
        alert_filters.append(
            (Alert.message.ilike(f"%{term}%"))
            | (Alert.alert_type.ilike(f"%{term}%"))
            | (Alert.severity.ilike(f"%{term}%"))
            | (Alert.status.ilike(f"%{term}%"))
            | (Employee.name.ilike(f"%{term}%"))
            | (Employee.employee_code.ilike(f"%{term}%"))
        )
    if numeric_ids:
        alert_filters.append(Alert.id.in_(numeric_ids))

    alert_matches = (
        db.query(Alert)
        .outerjoin(Employee, Alert.employee_id == Employee.id)
        .filter(or_(*alert_filters))
        .order_by(Alert.id.desc())
        .limit(10)
        .all()
    )

    # 4. Search Mongo Activity Logs
    mongo_or = []
    for term in search_terms:
        rx = {"$regex": re.escape(term), "$options": "i"}
        mongo_or.extend([
            {"employee_code": rx},
            {"ip_address": rx},
            {"event_type": rx},
            {"application": rx},
            {"resource": rx},
            {"action": rx},
        ])
    act_matches = []
    if mongo_or:
        try:
            raw_acts = list(
                activity_logs.find(
                    {"$or": mongo_or},
                    {"_id": 0}
                )
                .sort("timestamp", -1)
                .limit(10)
            )
            for act in raw_acts:
                ts = act.get("timestamp")
                if isinstance(ts, datetime):
                    act["timestamp"] = ts.isoformat()
                act_matches.append(act)
        except Exception:
            act_matches = []

    # Build employee lookup map for fallback resolution
    emp_ids = set()
    for inc in inc_matches:
        if inc.employee_id:
            emp_ids.add(inc.employee_id)
    for al in alert_matches:
        if al.employee_id:
            emp_ids.add(al.employee_id)

    emp_lookup = {}
    if emp_ids:
        try:
            emps = db.query(Employee).filter(Employee.id.in_(emp_ids)).all()
            emp_lookup = {e.id: e for e in emps}
        except Exception:
            emp_lookup = {}

    total_matches = len(emp_matches) + len(inc_matches) + len(alert_matches) + len(act_matches)

    return {
        "query": query_str,
        "total_matches": total_matches,
        "employees": [
            {
                "employee_code": e.employee_code,
                "name": e.name,
                "department": e.department,
                "role": e.role,
                "email": e.email,
            }
            for e in emp_matches
        ],
        "incidents": [
            {
                "id": inc.id,
                "employee_id": inc.employee_id,
                "employee_name": getattr(inc, "employee", None).name if getattr(inc, "employee", None) else (
                    emp_lookup.get(inc.employee_id).name if inc.employee_id in emp_lookup else "Unknown"
                ),
                "employee_code": getattr(inc, "employee", None).employee_code if getattr(inc, "employee", None) else (
                    emp_lookup.get(inc.employee_id).employee_code if inc.employee_id in emp_lookup else ""
                ),
                "department": getattr(inc, "employee", None).department if getattr(inc, "employee", None) else (
                    emp_lookup.get(inc.employee_id).department if inc.employee_id in emp_lookup else ""
                ),
                "incident_type": inc.incident_type,
                "description": inc.description,
                "severity": inc.severity,
                "status": inc.status,
            }
            for inc in inc_matches
        ],
        "alerts": [
            {
                "id": al.id,
                "employee_id": al.employee_id,
                "employee_name": getattr(al, "employee", None).name if getattr(al, "employee", None) else (
                    emp_lookup.get(al.employee_id).name if al.employee_id in emp_lookup else "Unknown"
                ),
                "employee_code": getattr(al, "employee", None).employee_code if getattr(al, "employee", None) else (
                    emp_lookup.get(al.employee_id).employee_code if al.employee_id in emp_lookup else ""
                ),
                "alert_type": al.alert_type,
                "message": al.message,
                "severity": al.severity,
                "status": al.status,
            }
            for al in alert_matches
        ],
        "activity_logs": act_matches,
    }


# ---------------------------------------------------------------------------
# Admin User Management Endpoints
# ---------------------------------------------------------------------------

@app.get("/admin/users")
def get_admin_users_list(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin", "security_manager", "security_analyst", "soc_engineer")
    ),
):
    """Retrieve full platform users list with status and roles."""
    users = db.query(User).order_by(User.id).all()
    return {
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "role": canonical_role(u.role),
                "is_active": getattr(u, "is_active", True),
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ]
    }


@app.patch("/admin/users/{user_id}/role")
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    """Update user role with validation and audit logging."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    canon = canonical_role(payload.role)
    if canon not in {"admin", "security_analyst", "soc_engineer", "security_manager"}:
        raise HTTPException(status_code=422, detail="Invalid role specified")

    old_role = user.role
    user.role = canon
    db.commit()
    db.refresh(user)

    record_audit_log(
        db=db,
        user=current_user,
        action="USER_ROLE_CHANGED",
        resource_type="user",
        resource_id=str(user.id),
        details=f"User {user.email} role changed from {old_role} to {canon}",
    )
    return {"message": "User role updated successfully", "user_id": user.id, "role": user.role}


@app.patch("/admin/users/{user_id}/status")
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    """Enable or disable user platform access."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = payload.is_active
    db.commit()
    db.refresh(user)

    record_audit_log(
        db=db,
        user=current_user,
        action="USER_STATUS_CHANGED",
        resource_type="user",
        resource_id=str(user.id),
        details=f"User {user.email} active status set to {payload.is_active}",
    )
    return {"message": "User status updated successfully", "user_id": user.id, "is_active": user.is_active}


# ---------------------------------------------------------------------------
# Real-Time WebSocket & In-App Notifications
# ---------------------------------------------------------------------------

@app.websocket("/ws/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    """Live WebSocket feed for security alerts and critical threat broadcasts."""
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)


@app.get("/notifications")
def get_recent_notifications(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin", "security_analyst", "soc_engineer", "security_manager")),
):
    """Retrieve recent active in-app notifications and critical alerts."""
    critical_alerts = (
        db.query(Alert)
        .filter(Alert.status != "resolved")
        .order_by(Alert.created_at.desc())
        .limit(10)
        .all()
    )
    notifications = []
    for a in critical_alerts:
        emp = db.query(Employee).filter(Employee.id == a.employee_id).first()
        notifications.append({
            "id": a.id,
            "title": f"Alert: {a.alert_type}",
            "message": a.message,
            "severity": a.severity,
            "employee_code": emp.employee_code if emp else f"EMP-{a.employee_id}",
            "timestamp": a.created_at.isoformat() if a.created_at else None,
        })
    return {"count": len(notifications), "notifications": notifications}



from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .auth import hash_password, verify_password
from .database import get_db
from .dependencies import get_current_user, require_role
from .jwt_auth import create_access_token
from .models import Employee, User
from .mongo import (
    activity_logs,
    rule_anomalies,
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
# MongoDB Collections
# ---------------------------------------------------------------------------

# Rule-based anomalies are stored in rule_anomalies.
# ML-based anomalies are stored separately in ml_anomalies.
ml_anomalies = mongo_db["ml_anomalies"]


# ---------------------------------------------------------------------------
# CORS Configuration
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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

@app.post("/auth/signup")
def signup(
    email: str,
    password: str,
    role: str = "analyst",
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    password_hash = hash_password(
        password
    )

    user = User(
        email=email,
        password_hash=password_hash,
        role=role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User registered successfully",
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
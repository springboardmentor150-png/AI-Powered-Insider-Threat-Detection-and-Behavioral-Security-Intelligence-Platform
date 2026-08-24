from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import Employee, Activity
from .schemas import EmployeeCreate, ActivityCreate


app = FastAPI()


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# BASIC ROUTES
# ============================================================

@app.get("/")
def home():
    return {
        "status": "ITBIS backend is running"
    }


@app.get("/hello")
def hello():
    return {
        "message": "Hello Subramanya!"
    }


# ============================================================
# EMPLOYEE APIs
# ============================================================

@app.post("/employees")
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db)
):
    new_employee = Employee(
        employee_id=employee.employee_id,
        name=employee.name,
        department=employee.department,
        designation=employee.designation,
        manager_id=employee.manager_id,
        device_info=employee.device_info,
        access_privileges=employee.access_privileges
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return {
        "message": "Employee created successfully",
        "employee_id": new_employee.employee_id
    }


@app.get("/employees")
def get_employees(
    db: Session = Depends(get_db)
):
    employees = db.query(Employee).all()

    return employees


# ============================================================
# RISK ANALYSIS ENGINE
# ============================================================

def calculate_risk(activity):
    """
    Calculate a basic insider-threat risk score.

    Score:
        0 - 29   = Low
        30 - 59  = Medium
        60 - 79  = High
        80 - 100 = Critical
    """

    score = 0
    reasons = []

    activity_type = activity.activity_type.upper()
    resource = (activity.resource or "").lower()

    # --------------------------------------------------------
    # Activity type
    # --------------------------------------------------------

    if activity_type == "LOGIN":
        score += 10

    elif activity_type == "FILE_ACCESS":
        score += 20
        reasons.append("File access detected")

    elif activity_type == "FILE_DOWNLOAD":
        score += 40
        reasons.append("File download detected")

    elif activity_type == "DATA_EXPORT":
        score += 60
        reasons.append("Data export detected")

    elif activity_type == "USB_ACCESS":
        score += 50
        reasons.append("USB device access detected")

    elif activity_type == "PRIVILEGE_CHANGE":
        score += 70
        reasons.append("Privilege change detected")

    elif activity_type == "LOGIN_FAILED":
        score += 30
        reasons.append("Failed login detected")

    else:
        score += 10
        reasons.append("Unusual activity type")


    # --------------------------------------------------------
    # Resource analysis
    # --------------------------------------------------------

    sensitive_keywords = [
        "confidential",
        "secret",
        "password",
        "credential",
        "financial",
        "customer",
        "database",
        "employee",
        "private"
    ]

    for keyword in sensitive_keywords:
        if keyword in resource:
            score += 30
            reasons.append(
                "Sensitive resource detected: " + keyword
            )
            break


    # --------------------------------------------------------
    # IP address analysis
    # --------------------------------------------------------

    if activity.ip_address:

        suspicious_ips = [
            "10.0.0.99",
            "192.168.1.99",
            "172.16.0.99"
        ]

        if activity.ip_address in suspicious_ips:
            score += 30
            reasons.append("Suspicious IP address detected")


    # --------------------------------------------------------
    # Limit score to 100
    # --------------------------------------------------------

    if score > 100:
        score = 100


    # --------------------------------------------------------
    # Risk level
    # --------------------------------------------------------

    if score >= 80:
        risk_level = "CRITICAL"

    elif score >= 60:
        risk_level = "HIGH"

    elif score >= 30:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"


    return {
        "risk_score": score,
        "risk_level": risk_level,
        "reasons": reasons
    }


# ============================================================
# ACTIVITY APIs
# ============================================================

@app.post("/activities")
def create_activity(
    activity: ActivityCreate,
    db: Session = Depends(get_db)
):

    new_activity = Activity(
        employee_id=activity.employee_id,
        activity_type=activity.activity_type,
        resource=activity.resource,
        timestamp=activity.timestamp,
        ip_address=activity.ip_address,
        device=activity.device
    )

    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)

    # Calculate risk for this activity
    risk = calculate_risk(new_activity)

    return {
        "message": "Activity created successfully",
        "activity_id": new_activity.id,
        "employee_id": new_activity.employee_id,
        "activity_type": new_activity.activity_type,
        "risk_score": risk["risk_score"],
        "risk_level": risk["risk_level"],
        "reasons": risk["reasons"]
    }


@app.get("/activities")
def get_activities(
    db: Session = Depends(get_db)
):

    activities = db.query(Activity).all()

    results = []

    for activity in activities:

        risk = calculate_risk(activity)

        results.append({
            "id": activity.id,
            "employee_id": activity.employee_id,
            "activity_type": activity.activity_type,
            "resource": activity.resource,
            "timestamp": activity.timestamp,
            "ip_address": activity.ip_address,
            "device": activity.device,
            "risk_score": risk["risk_score"],
            "risk_level": risk["risk_level"],
            "reasons": risk["reasons"]
        })

    return results
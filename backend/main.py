from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from . import models
from .database import engine, Base, get_db, mongo_db
from .schemas import (
    SignupRequest, LoginRequest, EmployeeCreate, LogIngestRequest,
    AlertCreate, EvidenceCreate
)
from .auth import create_token, verify_password, hash_password, decode_token
from .log_ingestion import ingest_log
from .behavioral_profiling import calculate_all_baselines
from .anomaly_detection import (
    check_login_time_anomaly, check_resource_access_anomaly,
    check_data_transfer_anomaly, check_privilege_abuse,
    check_suspicious_device
)
from .ml_anomaly_model import train_anomaly_model
from .risk_scoring import calculate_risk_score
from .ueba import compare_to_peers, get_risk_trend

app = FastAPI(
    title="ITBIS Backend API",
    description="Insider Threat Behavioral Intelligence System",
    version="3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
security = HTTPBearer()

ROLES = {"admin", "security_manager", "security_analyst", "soc_engineer"}

def current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        return decode_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def require_roles(*roles):
    def checker(payload=Depends(current_user)):
        if payload.get("role") not in roles:
            raise HTTPException(status_code=403, detail="Not authorized for this action")
        return payload
    return checker

@app.get("/")
def health_check():
    return {"message": "ITBIS Backend is running successfully"}

@app.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    if data.role not in ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")
    if db.query(models.User).filter(models.User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role
    )
    db.add(user); db.commit(); db.refresh(user)
    return {"message": "User created successfully", "user_id": user.id, "email": user.email, "role": user.role}

@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_token(user.id, user.role)
    return {"message": "Login successful", "access_token": token, "token_type": "bearer", "user_id": user.id, "role": user.role}

@app.get("/protected")
def protected(payload=Depends(current_user)):
    return {"message": "Protected endpoint accessed successfully", "user_id": payload.get("sub"), "role": payload.get("role")}

@app.get("/admin")
def admin_only(payload=Depends(require_roles("admin"))):
    return {"message": "Admin endpoint accessed successfully", "user_id": payload.get("sub"), "role": payload.get("role")}

@app.post("/employees")
def create_employee(data: EmployeeCreate, payload=Depends(require_roles("admin", "security_manager")), db: Session = Depends(get_db)):
    if db.query(models.Employee).filter(models.Employee.employee_id == data.employee_id).first():
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    employee = models.Employee(**data.model_dump())
    db.add(employee); db.commit(); db.refresh(employee)
    return {"message": "Employee onboarded successfully", "employee_id": employee.employee_id}

@app.get("/employees")
def list_employees(payload=Depends(require_roles("admin", "security_analyst", "soc_engineer")), db: Session = Depends(get_db)):
    return db.query(models.Employee).all()

@app.get("/employees/{employee_id}")
def get_employee(employee_id: str, payload=Depends(require_roles("admin", "security_analyst", "soc_engineer")), db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@app.post("/logs/ingest")
def receive_log(data: LogIngestRequest, payload=Depends(require_roles(*ROLES))):
    try:
        entry = ingest_log(data.employee_id, data.event_type, data.details)
        return {"message": "Log ingested", "employee_id": entry["employee_id"], "event_type": entry["event_type"]}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"MongoDB unavailable: {exc}")

# ---------------- MILESTONE 2 ----------------

@app.post("/baselines/{employee_id}")
def build_baselines(employee_id: str, payload=Depends(require_roles("admin", "security_analyst", "soc_engineer"))):
    try:
        result = calculate_all_baselines(employee_id)
        return {"employee_id": employee_id, "baselines_created": len(result), "baselines": result}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"MongoDB unavailable: {exc}")

@app.get("/baselines/{employee_id}")
def get_baselines(employee_id: str, payload=Depends(require_roles("admin", "security_analyst", "soc_engineer"))):
    return list(mongo_db["behavioral_baselines"].find({"employee_id": employee_id}, {"_id": 0}))

@app.get("/anomalies/login-time/{employee_id}")
def login_time_anomaly(employee_id: str, login_hour: float, payload=Depends(require_roles("admin", "security_analyst", "soc_engineer"))):
    return check_login_time_anomaly(employee_id, login_hour)

@app.get("/anomalies/resource-access/{employee_id}")
def resource_access_anomaly(employee_id: str, actual_count: float, payload=Depends(require_roles("admin", "security_analyst", "soc_engineer"))):
    return check_resource_access_anomaly(employee_id, actual_count)

@app.get("/anomalies/data-transfer/{employee_id}")
def data_transfer_anomaly(employee_id: str, actual_mb: float, payload=Depends(require_roles("admin", "security_analyst", "soc_engineer"))):
    return check_data_transfer_anomaly(employee_id, actual_mb)

@app.post("/anomalies/privilege/{employee_id}")
def privilege_anomaly(employee_id: str, requested_privilege: str, allowed_privileges: str, payload=Depends(require_roles("admin", "security_analyst", "soc_engineer"))):
    allowed = [x.strip() for x in allowed_privileges.split(",") if x.strip()]
    return check_privilege_abuse(employee_id, requested_privilege, allowed)

@app.post("/anomalies/device/{employee_id}")
def device_anomaly(employee_id: str, device: str, known_devices: str, payload=Depends(require_roles("admin", "security_analyst", "soc_engineer"))):
    known = [x.strip() for x in known_devices.split(",") if x.strip()]
    return check_suspicious_device(employee_id, device, known)

@app.get("/anomalies/report")
def anomaly_report(payload=Depends(require_roles("admin", "security_analyst", "soc_engineer"))):
    try:
        ml_results = train_anomaly_model()
        flagged = ml_results[ml_results["is_outlier"] == True]
        records = flagged.to_dict(orient="records")
        return {
            "total_employees_analyzed": len(ml_results),
            "flagged_count": len(flagged),
            "flagged_employees": records
        }
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Analytics unavailable: {exc}")

# ---------------- MILESTONE 3 ----------------

@app.get("/risk/{employee_id}")
def employee_risk(employee_id: str, payload=Depends(require_roles("admin", "security_analyst", "soc_engineer", "security_manager"))):
    return calculate_risk_score(employee_id)

@app.get("/ueba/peers/{employee_id}")
def peer_comparison(employee_id: str, payload=Depends(require_roles("admin", "security_analyst", "soc_engineer", "security_manager")), db: Session = Depends(get_db)):
    return compare_to_peers(db, employee_id)

@app.get("/ueba/trend/{employee_id}")
def risk_trend(employee_id: str, days: int = 30, payload=Depends(require_roles("admin", "security_analyst", "soc_engineer", "security_manager"))):
    return {"employee_id": employee_id, "days": days, "trend": get_risk_trend(employee_id, days)}

@app.post("/incidents/create-from-risk/{employee_id}")
def create_incident_from_risk(employee_id: str, payload=Depends(require_roles("admin", "security_analyst")), db: Session = Depends(get_db)):
    risk = calculate_risk_score(employee_id)
    if risk["risk_category"] not in ("high", "critical"):
        raise HTTPException(status_code=400, detail="Risk level too low to warrant an incident")
    incident = models.Incident(
        employee_id=employee_id,
        severity=risk["risk_category"],
        summary=f"Auto-created from risk score {risk['risk_score']}"
    )
    db.add(incident); db.commit(); db.refresh(incident)
    return incident

@app.get("/incidents/{incident_id}/timeline")
def get_incident_timeline(incident_id: int, payload=Depends(require_roles("admin", "security_analyst")), db: Session = Depends(get_db)):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    logs = list(mongo_db["activity_logs"].find({"employee_id": incident.employee_id}).sort("timestamp", -1).limit(50))
    anomalies = list(mongo_db["rule_anomalies"].find({"employee_id": incident.employee_id}))
    timeline = (
        [{"type": "activity", "timestamp": l["timestamp"], "detail": l.get("event_type")} for l in logs] +
        [{"type": "anomaly", "timestamp": a["detected_at"], "detail": a.get("anomaly_type")} for a in anomalies]
    )
    timeline.sort(key=lambda x: x["timestamp"], reverse=True)
    for item in timeline:
        if hasattr(item["timestamp"], "isoformat"):
            item["timestamp"] = item["timestamp"].isoformat()
    return {"incident_id": incident_id, "timeline": timeline}

@app.post("/incidents/{incident_id}/evidence")
def add_evidence(incident_id: int, data: EvidenceCreate, payload=Depends(require_roles("admin", "security_analyst")), db: Session = Depends(get_db)):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    evidence = models.Evidence(incident_id=incident_id, note=data.note, added_by=int(payload["sub"]))
    db.add(evidence); db.commit(); db.refresh(evidence)
    return evidence

@app.get("/incidents")
def list_incidents(payload=Depends(require_roles("admin", "security_analyst", "security_manager", "soc_engineer")), db: Session = Depends(get_db)):
    return db.query(models.Incident).order_by(models.Incident.created_at.desc()).all()

@app.post("/alerts")
def create_alert(data: AlertCreate, payload=Depends(require_roles("admin", "security_manager", "security_analyst")), db: Session = Depends(get_db)):
    alert = models.Alert(**data.model_dump())
    db.add(alert); db.commit(); db.refresh(alert)
    return alert

@app.post("/alerts/{alert_id}/assign")
def assign_alert(alert_id: int, analyst_user_id: int, payload=Depends(require_roles("admin", "security_manager")), db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.assigned_to = analyst_user_id
    alert.status = "assigned"
    db.commit()
    return {"message": f"Alert {alert_id} assigned", "status": alert.status}

@app.patch("/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: int, payload=Depends(require_roles("admin", "security_analyst")), db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = "resolved"
    db.commit()
    return {"message": f"Alert {alert_id} resolved"}

@app.get("/analytics/risk-distribution")
def get_risk_distribution(payload=Depends(require_roles("admin", "security_manager")), db: Session = Depends(get_db)):
    employees = db.query(models.Employee).all()
    distribution = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for emp in employees:
        risk = calculate_risk_score(emp.employee_id)
        distribution[risk["risk_category"]] += 1
    return {"total_employees": len(employees), "distribution": distribution}

@app.get("/dashboard/analyst")
def analyst_dashboard(payload=Depends(require_roles("admin", "security_analyst")), db: Session = Depends(get_db)):
    open_alerts = db.query(models.Alert).filter(models.Alert.status == "open").count()
    active_investigations = db.query(models.Incident).filter(models.Incident.status == "investigating").count()
    high_risk_employees = [
        emp.employee_id for emp in db.query(models.Employee).all()
        if calculate_risk_score(emp.employee_id)["risk_category"] in ("high", "critical")
    ]
    return {
        "open_alerts": open_alerts,
        "active_investigations": active_investigations,
        "high_risk_employees": high_risk_employees[:10]
    }

@app.get("/dashboard/soc")
def soc_dashboard(payload=Depends(require_roles("admin", "soc_engineer")), db: Session = Depends(get_db)):
    return {
        "security_events_count": mongo_db["activity_logs"].count_documents({}),
        "behavioral_anomalies_count": mongo_db["rule_anomalies"].count_documents({}),
        "active_investigations": db.query(models.Incident).filter(models.Incident.status == "investigating").count(),
        "recent_threat_intelligence_notes": []
    }

@app.get("/dashboard/security-manager")
def security_manager_dashboard(payload=Depends(require_roles("admin", "security_manager")), db: Session = Depends(get_db)):
    employees = db.query(models.Employee).all()
    distribution = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for emp in employees:
        category = calculate_risk_score(emp.employee_id)["risk_category"]
        distribution[category] += 1
    return {
        "risk_distribution": distribution,
        "total_employees": len(employees),
        "risk_trends": []
    }

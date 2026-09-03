from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import engine, Base, SessionLocal
from .models import User, Employee, verify_password
from .routes.auth import router as auth_router
from .auth import get_current_user, create_token

from app.employees import router as employee_router
from app.mongo_database import test_mongodb
from app.activity_logs import ActivityLog, create_activity_log
from app.anomaly_detection import detect_anomaly
from app.behavioral_baselines import create_behavioral_baseline

from fastapi.middleware.cors import CORSMiddleware
# ============================================================
# CREATE DATABASE TABLES
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(title="ITBIS API")


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REGISTER ROUTERS
# ============================================================

app.include_router(auth_router)
app.include_router(employee_router)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def health_check():
    return {
        "status": "ITBIS backend is running"
    }


# ============================================================
# DATABASE TEST
# ============================================================

@app.get("/db-test")
def database_test(
    current_user=Depends(get_current_user)
):
    try:
        with engine.connect() as connection:
            return {
                "database": "connected",
                "user_id": current_user["user_id"],
                "role": current_user["role"]
            }

    except Exception as e:
        return {
            "database": "error",
            "message": str(e)
        }


# ============================================================
# MONGODB TEST
# ============================================================

@app.get("/db-test/mongodb")
def mongodb_test():

    if test_mongodb():
        return {
            "status": "MongoDB connected successfully"
        }

    return {
        "status": "MongoDB connection failed"
    }


# ============================================================
# LOGIN
# ============================================================

class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/auth/login")
def login(data: LoginRequest):

    db: Session = SessionLocal()

    try:

        # Find user by email
        user = (
            db.query(User)
            .filter(User.email == data.email)
            .first()
        )

        # User does not exist
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        # Check password
        if not verify_password(
            data.password,
            user.password_hash
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        # Create JWT token
        token = create_token(
            user_id=user.id,
            role=user.role
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.id,
            "email": user.email,
            "role": user.role
        }

    finally:
        db.close()


# ============================================================
# ACTIVITY LOGS
# ============================================================

@app.post("/activity-logs")
def add_activity_log(log: ActivityLog):
    return create_activity_log(log)


# ============================================================
# BEHAVIORAL BASELINE
# ============================================================

@app.post("/behavioral-baselines")
def add_behavioral_baseline(
    employee_id: int,
    average_daily_activities: float,
    common_action: str,
    common_resource: str | None = None
):
    return create_behavioral_baseline(
        employee_id=employee_id,
        average_daily_activities=average_daily_activities,
        common_action=common_action,
        common_resource=common_resource
    )


# ============================================================
# ANOMALY DETECTION
# ============================================================

@app.post("/detect-anomaly")
def check_anomaly(
    employee_id: int,
    action: str,
    resource: str | None = None
):
    return detect_anomaly(
        employee_id=employee_id,
        action=action,
        resource=resource
    )

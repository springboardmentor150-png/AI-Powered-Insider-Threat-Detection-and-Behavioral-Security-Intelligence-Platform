from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import SystemSetting
from app.schemas import SystemSettingsUpdate
from app.security import get_current_user, require_role

router = APIRouter(prefix="/settings", tags=["Settings"])

DEFAULT_SETTINGS = {
    "anomaly_threshold": "60",
    "critical_threshold": "80",
    "max_download_mb": "500",
    "business_start_hour": "8",
    "business_end_hour": "19",
    "alert_dedup_window_mins": "15",
    "sensor_sensitivity": "HIGH",
    "auto_flag_critical": "true",
}


@router.get("")
def get_settings(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    settings = dict(DEFAULT_SETTINGS)
    db_settings = db.query(SystemSetting).all()
    for s in db_settings:
        settings[s.key] = s.value
    return settings


@router.get("/db-diagnostics")
def get_database_diagnostics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Reports exact active SQL database engine, driver, host, database name without exposing credentials."""
    from app.database import engine, DATABASE_URL, DEFAULT_DB_FILE
    from app.models import User, Employee

    dialect_name = engine.dialect.name
    driver_name = engine.driver

    if dialect_name.startswith("sqlite"):
        db_engine_type = "SQLite"
        db_host = "Local Workstation (Embedded Storage)"
        db_name = DEFAULT_DB_FILE.name
    elif "postgres" in dialect_name:
        db_engine_type = "PostgreSQL"
        db_host = engine.url.host or "localhost"
        db_name = engine.url.database or "itbis"
    else:
        db_engine_type = dialect_name.capitalize()
        db_host = engine.url.host or "localhost"
        db_name = engine.url.database or "itbis"

    try:
        user_count = db.query(User).count()
        employee_count = db.query(Employee).count()
        connection_status = "CONNECTED (OPERATIONAL)"
    except Exception as e:
        user_count = 0
        employee_count = 0
        connection_status = f"ERROR: {str(e)}"

    return {
        "database_engine": db_engine_type,
        "database_driver": driver_name,
        "database_host": db_host,
        "database_name": db_name,
        "connection_status": connection_status,
        "total_users_registered": user_count,
        "total_employees_stored": employee_count,
        "is_production_ready": db_engine_type in ["PostgreSQL", "SQLite"],
        "schema_version": "1.0.0",
    }


@router.get("/telemetry-diagnostics")
def get_telemetry_diagnostics(
    current_user: dict = Depends(get_current_user),
):
    """Reports telemetry storage backend, connection status, and exact record counts without exposing credentials."""
    from app.mongodb import mongo_service

    is_mongo = mongo_service.is_connected
    backend_type = "MongoDB (Distributed Telemetry Store)" if is_mongo else "JSON Fallback Store (Local Dev Persistence)"
    conn_status = "CONNECTED" if is_mongo else "FALLBACK_ACTIVE"

    all_logs = mongo_service.query_activity_logs(limit=500)["items"]
    record_count = len(all_logs)

    event_counts = {}
    for a in all_logs:
        et = a.get("event_type", "unknown")
        event_counts[et] = event_counts.get(et, 0) + 1

    return {
        "telemetry_backend": backend_type,
        "connection_status": conn_status,
        "total_records": record_count,
        "event_types_breakdown": event_counts,
        "collection_name": "activity_logs",
    }


@router.post("")
def update_settings(
    data: SystemSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "security_manager", "soc_engineer", "security_analyst")),
):
    for key, value in data.settings.items():
        db_s = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if db_s:
            db_s.value = str(value)
        else:
            db_s = SystemSetting(key=key, value=str(value))
            db.add(db_s)
    db.commit()
    return {"message": "Settings updated successfully", "settings": data.settings}

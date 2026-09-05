# backend/app/models.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default="security_analyst") # "admin", "security_manager", "security_analyst", "soc_engineer"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    audit_logs = relationship("AuditLog", back_populates="user")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    department = Column(String(100), nullable=False)
    designation = Column(String(100), nullable=False)
    manager_id = Column(Integer, nullable=True)
    device_info = Column(String(255), nullable=True) # e.g. "MacBook Pro M2 - Serial #MBP-8921"
    access_privileges = Column(String(255), nullable=True) # e.g. "PROD_DB, AWS_ADMIN, FINANCE_PORTAL"
    status = Column(String(50), default="ACTIVE") # "ACTIVE", "SUSPENDED", "UNDER_REVIEW"
    baseline_risk_score = Column(Float, default=15.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    incidents = relationship("Incident", back_populates="employee")
    alerts = relationship("Alert", back_populates="employee")


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_code = Column(String(50), unique=True, index=True, nullable=False) # e.g. "INC-2026-0042"
    employee_id = Column(String(50), ForeignKey("employees.employee_id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(50), default="HIGH") # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    status = Column(String(50), default="OPEN") # "OPEN", "INVESTIGATING", "CONTAINED", "RESOLVED", "FALSE_POSITIVE"
    assigned_to = Column(String(255), nullable=True) # Analyst email / name
    mitre_attack_technique = Column(String(100), nullable=True) # e.g. "T1052.001 - Exfiltration over USB"
    ai_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = relationship("Employee", back_populates="incidents")
    alerts = relationship("Alert", back_populates="incident")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_code = Column(String(50), unique=True, index=True, nullable=False) # e.g. "ALT-9081"
    employee_id = Column(String(50), ForeignKey("employees.employee_id"), nullable=False)
    severity = Column(String(50), nullable=False, default="MEDIUM") # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    anomaly_type = Column(String(100), nullable=True) # "MASS_DOWNLOAD", "UNUSUAL_HOURS", "USB_EXFILTRATION", etc.
    risk_score = Column(Float, default=50.0)
    is_acknowledged = Column(Boolean, default=False)
    is_escalated = Column(Boolean, default=False)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="alerts")
    incident = relationship("Incident", back_populates="alerts")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_email = Column(String(255), nullable=True)
    action = Column(String(100), nullable=False) # "LOGIN", "VIEW_EMPLOYEE", "ESCALATE_ALERT", "CHANGE_STATUS"
    target_resource = Column(String(255), nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")

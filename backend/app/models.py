from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Float
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="security_analyst")

    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    email = Column(String, nullable=True)
    department = Column(String, nullable=True, index=True)
    designation = Column(String, nullable=True)
    manager_name = Column(String, nullable=True)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    employment_type = Column(String, default="Full-time")
    work_location = Column(String, default="Hyderabad")
    joining_date = Column(String, default="2022-01-15")
    years_of_experience = Column(Integer, default=5)
    education = Column(String, default="B.Tech Computer Science")
    previous_role = Column(String, nullable=True)
    skills = Column(String, nullable=True)
    professional_summary = Column(Text, nullable=True)
    device_info = Column(String, nullable=True)
    access_privileges = Column(String, nullable=True)
    risk_score = Column(Integer, default=0, index=True)
    risk_level = Column(String, default="LOW", index=True)
    status = Column(String, default="ACTIVE", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    alerts = relationship("Alert", back_populates="employee", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="employee", cascade="all, delete-orphan")
    baseline = relationship("BehavioralBaseline", back_populates="employee", uselist=False, cascade="all, delete-orphan")
    risk_history = relationship("RiskScoreHistory", back_populates="employee", cascade="all, delete-orphan")
    investigation_notes = relationship("InvestigationNote", back_populates="employee", cascade="all, delete-orphan")
    manager = relationship("Employee", remote_side=[id], backref="direct_reports")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    activity_type = Column(String, nullable=False, index=True)  # LOGIN, FILE_DOWNLOAD, DATABASE_ACCESS, etc.
    action = Column(String, nullable=False)
    resource = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    device_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    location_network = Column(String, nullable=True)
    is_success = Column(Boolean, default=True)
    metadata_json = Column(Text, nullable=True)
    risk_weight = Column(Integer, default=0)
    is_test_event = Column(Boolean, default=False, index=True)


class BehavioralBaseline(Base):
    __tablename__ = "behavioral_baselines"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), unique=True, nullable=False, index=True)
    normal_start_hour = Column(Integer, default=9)
    normal_end_hour = Column(Integer, default=18)
    usual_devices = Column(Text, nullable=True)  # JSON or comma-separated list
    usual_ips = Column(Text, nullable=True)       # JSON or comma-separated list
    usual_resources = Column(Text, nullable=True)
    usual_download_limit_mb = Column(Integer, default=500)
    total_activities_sampled = Column(Integer, default=0)
    last_baseline_update = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="baseline")


class RiskScoreHistory(Base):
    __tablename__ = "risk_score_history"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    risk_level = Column(String, nullable=False)
    contributing_factors = Column(Text, nullable=True)  # JSON list of detected anomaly factors
    calculated_at = Column(DateTime, default=datetime.utcnow, index=True)

    employee = relationship("Employee", back_populates="risk_history")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String, default="DATA_EXFILTRATION", index=True)
    severity = Column(String, nullable=False, default="MEDIUM", index=True)
    status = Column(String, default="OPEN", index=True)  # OPEN, ACKNOWLEDGED, RESOLVED, in_progress, escalated
    risk_score = Column(Integer, default=0)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    escalated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    employee = relationship("Employee", back_populates="alerts")
    incident = relationship("Incident", back_populates="alert", uselist=False, foreign_keys="Incident.alert_id")
    notifications = relationship("Notification", back_populates="alert", cascade="all, delete-orphan")


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    summary = Column(String, nullable=True)
    status = Column(String, default="OPEN", index=True)  # OPEN, INVESTIGATING, CONTAINED, RESOLVED, CLOSED, open, investigating, resolved
    severity = Column(String, nullable=False, default="HIGH", index=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    investigation_started_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    employee = relationship("Employee", back_populates="incidents")
    alert = relationship("Alert", back_populates="incident", foreign_keys=[alert_id])
    notes = relationship("InvestigationNote", back_populates="incident", cascade="all, delete-orphan")


class InvestigationNote(Base):
    __tablename__ = "investigation_notes"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True, index=True)
    author_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    author_email = Column(String, nullable=True)
    note = Column(Text, nullable=True)
    note_text = Column(Text, nullable=True)
    evidence_reference = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    employee = relationship("Employee", back_populates="investigation_notes")
    incident = relationship("Incident", back_populates="notes")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    user_email = Column(String, nullable=True, index=True)
    action = Column(String, nullable=False, index=True)  # e.g. "VIEW_INVESTIGATION", "ADD_NOTE", "UPDATE_INCIDENT"
    target_type = Column(String, nullable=True)        # "EMPLOYEE", "ALERT", "INCIDENT"
    target_id = Column(String, nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=True)
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="notifications")
    alert = relationship("Alert", back_populates="notifications")


class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    description = Column(String, nullable=True)


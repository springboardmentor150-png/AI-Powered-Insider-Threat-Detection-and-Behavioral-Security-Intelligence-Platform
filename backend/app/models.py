"""
SQLAlchemy ORM models for PostgreSQL.

Tables
------
users        — platform console accounts (login, roles)
employees    — monitored workforce identities
incidents    — security incidents linked to alerts
alerts       — threat detection records
"""
import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ── Enumerations ───────────────────────────────────────────────────────────────

class RoleEnum(str, enum.Enum):
    administrator = "Administrator"
    security_manager = "Security Manager"
    security_analyst = "Security Analyst"
    soc_engineer = "SOC Engineer"


class RiskLevelEnum(str, enum.Enum):
    low = "Low"
    medium = "Medium"
    high = "High"
    critical = "Critical"


class SeverityEnum(str, enum.Enum):
    informational = "Informational"
    low = "Low"
    medium = "Medium"
    high = "High"
    critical = "Critical"


class AlertStatusEnum(str, enum.Enum):
    open = "Open"
    investigating = "Investigating"
    resolved = "Resolved"


class UserStatusEnum(str, enum.Enum):
    active = "Active"
    invited = "Invited"
    suspended = "Suspended"


class IncidentStatusEnum(str, enum.Enum):
    triage = "Triage"
    in_progress = "In progress"
    awaiting_review = "Awaiting review"
    closed = "Closed"


# Shared SQLAlchemy Enum type objects — reused across tables so PostgreSQL
# creates each ENUM type only once and both columns reference the same type.
_role_type = SAEnum(RoleEnum, name="role_enum", create_constraint=True)
_risk_type = SAEnum(RiskLevelEnum, name="risk_level_enum", create_constraint=True)
_severity_type = SAEnum(SeverityEnum, name="severity_enum", create_constraint=True)
_alert_status_type = SAEnum(AlertStatusEnum, name="alert_status_enum", create_constraint=True)
_user_status_type = SAEnum(UserStatusEnum, name="user_status_enum", create_constraint=True)
_incident_status_type = SAEnum(IncidentStatusEnum, name="incident_status_enum", create_constraint=True)


# ── Users (platform console accounts) ─────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(
        _role_type, nullable=False, default=RoleEnum.security_analyst
    )
    status: Mapped[UserStatusEnum] = mapped_column(
        _user_status_type, nullable=False, default=UserStatusEnum.active
    )
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    alerts: Mapped[list["Alert"]] = relationship(
        "Alert", back_populates="assigned_user", lazy="select"
    )


# ── Employees (monitored workforce) ───────────────────────────────────────────

class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    designation: Mapped[str] = mapped_column(String(150), nullable=False)
    manager: Mapped[str] = mapped_column(String(255), nullable=False)
    risk_level: Mapped[RiskLevelEnum] = mapped_column(
        _risk_type, nullable=False, default=RiskLevelEnum.low
    )
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    location: Mapped[str] = mapped_column(String(150), nullable=False, default="")
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    alerts: Mapped[list["Alert"]] = relationship(
        "Alert", back_populates="employee", lazy="select"
    )
    incidents: Mapped[list["Incident"]] = relationship(
        "Incident", back_populates="employee", lazy="select"
    )


# ── Alerts (threat detections) ─────────────────────────────────────────────────

class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alert_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    employee_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("employees.employee_id"), nullable=False, index=True
    )
    severity: Mapped[SeverityEnum] = mapped_column(_severity_type, nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[AlertStatusEnum] = mapped_column(
        _alert_status_type, nullable=False, default=AlertStatusEnum.open
    )
    rule: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    narrative: Mapped[str] = mapped_column(Text, nullable=False, default="")
    # Role queue this alert is assigned to (not a per-user FK)
    assigned_to: Mapped[RoleEnum] = mapped_column(
        _role_type, nullable=False, default=RoleEnum.security_analyst
    )
    assigned_user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    employee: Mapped["Employee"] = relationship("Employee", back_populates="alerts")
    assigned_user: Mapped["User | None"] = relationship("User", back_populates="alerts")
    incident: Mapped["Incident | None"] = relationship(
        "Incident", back_populates="alert", uselist=False
    )


# ── Incidents ──────────────────────────────────────────────────────────────────

class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    incident_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    employee_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("employees.employee_id"), nullable=False, index=True
    )
    alert_id: Mapped[str | None] = mapped_column(
        String(20), ForeignKey("alerts.alert_id"), nullable=True
    )
    status: Mapped[IncidentStatusEnum] = mapped_column(
        _incident_status_type, nullable=False, default=IncidentStatusEnum.triage
    )
    severity: Mapped[SeverityEnum] = mapped_column(_severity_type, nullable=False)
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")

    employee: Mapped["Employee"] = relationship("Employee", back_populates="incidents")
    alert: Mapped["Alert | None"] = relationship("Alert", back_populates="incident")

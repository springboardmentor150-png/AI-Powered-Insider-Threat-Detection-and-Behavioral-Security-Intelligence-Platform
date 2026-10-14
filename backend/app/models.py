"""
SQLAlchemy models for ITBIS.

Core tables:
- users
- employees
- incidents
- alerts
- investigation_notes
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from app.database import Base


# =========================================================
# Users
# =========================================================

class User(Base):
    """
    Platform users:
    security analysts, SOC engineers, security managers, admins.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    email = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String,
        nullable=False
    )

    role = Column(
        String,
        nullable=False
    )

    # Alerts assigned to this platform user
    assigned_alerts = relationship(
        "Alert",
        back_populates="assigned_user"
    )

    # Investigation notes written by this user
    investigation_notes = relationship(
        "InvestigationNote",
        back_populates="author"
    )


# =========================================================
# Employees
# =========================================================

class Employee(Base):
    """
    Organization employees being monitored by ITBIS.
    """

    __tablename__ = "employees"

    id = Column(
        Integer,
        primary_key=True
    )

    employee_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    department = Column(
        String
    )

    designation = Column(
        String
    )

    manager_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=True
    )

    device_info = Column(
        String,
        nullable=True
    )

    access_privileges = Column(
        String,
        nullable=True
    )

    # Manager / direct reports
    manager = relationship(
        "Employee",
        remote_side=[id],
        backref="direct_reports"
    )

    # Incidents associated with this employee
    incidents = relationship(
        "Incident",
        back_populates="employee"
    )

    # Alerts associated with this employee
    alerts = relationship(
        "Alert",
        back_populates="employee"
    )


# =========================================================
# Incidents
# =========================================================

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(
        Integer,
        primary_key=True
    )

    employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=False
    )

    status = Column(
        String,
        default="open",
        nullable=False
    )
    # open | investigating | resolved

    severity = Column(
        String,
        nullable=False
    )
    # informational | low | medium | high | critical

    summary = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    resolved_at = Column(
        DateTime,
        nullable=True
    )

    # Employee involved in the incident
    employee = relationship(
        "Employee",
        back_populates="incidents"
    )

    # Investigation notes
    investigation_notes = relationship(
        "InvestigationNote",
        back_populates="incident",
        cascade="all, delete-orphan"
    )

    # Alerts generated for this incident
    alerts = relationship(
        "Alert",
        back_populates="incident"
    )


# =========================================================
# Investigation Notes
# =========================================================

class InvestigationNote(Base):
    __tablename__ = "investigation_notes"

    id = Column(
        Integer,
        primary_key=True
    )

    incident_id = Column(
        Integer,
        ForeignKey("incidents.id"),
        nullable=False
    )

    author_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    note = Column(
        Text,
        nullable=False
    )

    evidence_reference = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Incident containing this note
    incident = relationship(
        "Incident",
        back_populates="investigation_notes"
    )

    # User who wrote the note
    author = relationship(
        "User",
        back_populates="investigation_notes"
    )


# =========================================================
# Alerts
# =========================================================

class Alert(Base):
    """
    Security alerts generated from:
    - Rule-based anomalies
    - ML anomalies
    """

    __tablename__ = "alerts"

    id = Column(
        Integer,
        primary_key=True
    )

    employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=False
    )

    incident_id = Column(
        Integer,
        ForeignKey("incidents.id"),
        nullable=True
    )

    severity = Column(
        String,
        nullable=False
    )

    message = Column(
        String,
        nullable=False
    )

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    status = Column(
        String,
        default="open",
        nullable=False
    )
    # open | acknowledged | resolved

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    resolved_at = Column(
        DateTime,
        nullable=True
    )

    escalated_at = Column(
        DateTime,
        nullable=True
    )

    # Employee who generated the alert
    employee = relationship(
        "Employee",
        back_populates="alerts"
    )

    # Incident associated with this alert
    incident = relationship(
        "Incident",
        back_populates="alerts"
    )

    # Platform user assigned to the alert
    assigned_user = relationship(
        "User",
        back_populates="assigned_alerts"
    )
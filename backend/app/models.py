"""
SQLAlchemy models for the 4 core PostgreSQL tables defined on Day 2:
users, employees, incidents, alerts.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """Platform users: the people who LOG IN (analysts, SOC engineers, managers, admins)."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # security_analyst | soc_engineer | security_manager | admin

    assigned_alerts = relationship("Alert", back_populates="assigned_user")


class Employee(Base):
    """Org staff being monitored. Employees never log into the platform."""

    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    employee_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    department = Column(String)
    designation = Column(String)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    device_info = Column(String, nullable=True)
    access_privileges = Column(String, nullable=True)

    # Self-referencing relationship: an employee's manager is also an employee.
    manager = relationship("Employee", remote_side=[id], backref="direct_reports")

    incidents = relationship("Incident", back_populates="employee")
    alerts = relationship("Alert", back_populates="employee")


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    status = Column(String, default="open", nullable=False)  # open | investigating | resolved
    severity = Column(String, nullable=False)  # informational | low | medium | high | critical
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    employee = relationship("Employee", back_populates="incidents")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    severity = Column(String, nullable=False)
    message = Column(String, nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    employee = relationship("Employee", back_populates="alerts")
    assigned_user = relationship("User", back_populates="assigned_alerts")

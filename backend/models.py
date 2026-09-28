from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="analyst")

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    designation = Column(String, nullable=False)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    device_info = Column(String, nullable=True)
    access_privileges = Column(String, nullable=True)

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True)
    employee_id = Column(String, nullable=False)
    status = Column(String, default="open")
    severity = Column(String, nullable=False)
    summary = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    note = Column(String)
    added_by = Column(Integer, ForeignKey("users.id"))
    added_at = Column(DateTime, default=datetime.utcnow)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True)
    employee_id = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    message = Column(String, nullable=False)
    status = Column(String, default="open")
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

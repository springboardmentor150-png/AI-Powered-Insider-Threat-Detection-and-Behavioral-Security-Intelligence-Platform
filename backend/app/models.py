from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from app.database import Base

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    employee_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    email = Column(String)

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
    note = Column(Text, nullable=False)
    added_by = Column(Integer, nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True)
    employee_id = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    message = Column(String, nullable=False)
    status = Column(String, default="open")
    assigned_to = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

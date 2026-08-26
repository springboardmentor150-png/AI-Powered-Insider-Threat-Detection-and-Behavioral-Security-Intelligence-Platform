from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    designation = Column(String(100), nullable=False)
    manager_id = Column(Integer, nullable=True)
    device_info = Column(String(255), nullable=True)
    access_privileges = Column(String(255), nullable=True)


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), nullable=False)
    status = Column(String(50))
    severity = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), nullable=False)
    severity = Column(String(50))
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
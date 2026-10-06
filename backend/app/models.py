from sqlalchemy import Column, Integer, String
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    department = Column(String)
    designation = Column(String)
    manager_id = Column(Integer)


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer)
    status = Column(String)
    severity = Column(String)
    created_at = Column(String)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer)
    severity = Column(String)
    message = Column(String)
    created_at = Column(String)
class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, nullable=False)
    event_type = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)
    details = Column(String)

class BehavioralBaseline(Base):
    __tablename__ = "behavioral_baselines"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, nullable=False)
    indicator = Column(String, nullable=False)
    typical_value = Column(String, nullable=False)
    std_deviation = Column(String, nullable=False)
    sample_size = Column(Integer, nullable=False)
    last_updated = Column(String, nullable=False)

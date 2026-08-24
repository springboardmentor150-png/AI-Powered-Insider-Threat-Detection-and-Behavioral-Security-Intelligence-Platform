from sqlalchemy import Column, Integer, String
from .database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    employee_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    department = Column(String)
    designation = Column(String)
    manager_id = Column(String)
    device_info = Column(String)
    access_privileges = Column(String)


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True)
    employee_id = Column(String, nullable=False)
    activity_type = Column(String, nullable=False)
    resource = Column(String)
    timestamp = Column(String)
    ip_address = Column(String)
    device = Column(String)
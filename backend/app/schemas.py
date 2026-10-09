from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserBase(BaseModel):
    email: str
    role: str
    employee_id: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class EmployeeBase(BaseModel):
    employee_id: str
    name: str
    department: str
    designation: str
    manager_id: Optional[int] = None
    device_info: Optional[str] = None
    access_privileges: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    id: int

    class Config:
        from_attributes = True

class ActivityLogCreate(BaseModel):
    employee_id: str
    event_type: str
    details: dict

class AlertBase(BaseModel):
    employee_id: str
    severity: str
    message: str
    anomaly_type: str
    status: str = "open"

class Alert(AlertBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class IncidentBase(BaseModel):
    alert_id: int
    assigned_to: Optional[int] = None
    status: str = "open"
    notes: Optional[str] = None

class Incident(IncidentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

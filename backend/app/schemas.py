"""
Pydantic schemas: the exact shape of data clients can SEND and RECEIVE.
These are deliberately separate from the SQLAlchemy models in models.py.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    role: str  # "security_analyst" | "soc_engineer" | "security_manager" | "admin"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


# ---------- Employees ----------

class EmployeeCreate(BaseModel):
    employee_id: str
    name: str
    department: str
    designation: str
    manager_id: Optional[int] = None
    device_info: Optional[str] = None
    access_privileges: Optional[str] = None


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    manager_id: Optional[int] = None
    device_info: Optional[str] = None
    access_privileges: Optional[str] = None

class EmployeeResponse(BaseModel):
    id: int
    employee_id: str
    name: str
    department: Optional[str]
    designation: Optional[str]
    manager_id: Optional[int]
    device_info: Optional[str] = None
    access_privileges: Optional[str] = None

    class Config:
        from_attributes = True


class DirectReportsResponse(BaseModel):
    manager: str
    direct_reports: list[str]


# ---------- Incidents & Alerts ----------
# These tables are defined in the Day 2 schema; the guides don't provide their
# CRUD endpoints yet (that lands in later milestones), but a minimal create/read
# shape is included here so /alerts/my and /reports/risk-posture are testable.

class IncidentCreate(BaseModel):
    employee_id: int
    status: str = "open"
    severity: str  # informational | low | medium | high | critical


class IncidentResponse(BaseModel):
    id: int
    employee_id: int
    status: str
    severity: str
    created_at: datetime

    class Config:
        from_attributes = True


class AlertCreate(BaseModel):
    employee_id: int
    severity: str
    message: str
    assigned_to: Optional[int] = None


class AlertResponse(BaseModel):
    id: int
    employee_id: int
    severity: str
    message: str
    assigned_to: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class RiskPostureResponse(BaseModel):
    total_employees: int
    open_incidents: int
    incidents_by_severity: dict
    alerts_by_severity: dict

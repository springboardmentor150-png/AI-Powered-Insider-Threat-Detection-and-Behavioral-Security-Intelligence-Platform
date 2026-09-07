"""
Pydantic v2 schemas — request bodies and response models.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Shared enums (string literals keep things simple) ─────────────────────────

Role = Literal["Administrator", "Security Manager", "Security Analyst", "SOC Engineer"]
RiskLevel = Literal["Low", "Medium", "High", "Critical"]
Severity = Literal["Informational", "Low", "Medium", "High", "Critical"]
AlertStatus = Literal["Open", "Investigating", "Resolved"]
UserStatus = Literal["Active", "Invited", "Suspended"]
IncidentStatus = Literal["Triage", "In progress", "Awaiting review", "Closed"]
EventType = Literal[
    "login", "logout", "file_download", "file_upload",
    "usb_connect", "email_external", "vpn_access", "privilege_change",
]


# ── Auth ──────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Role
    email: str


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, description="Minimum 8 characters")
    role: Role = "Security Analyst"

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return v


# ── Users ─────────────────────────────────────────────────────────────────────

class UserOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    email: str
    role: Role
    status: UserStatus
    last_login: datetime | None = None
    created_at: datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    role: Role = "Security Analyst"


class UserUpdate(BaseModel):
    role: Role | None = None
    status: UserStatus | None = None


# ── Employees ─────────────────────────────────────────────────────────────────

class EmployeeOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    employee_id: str
    name: str
    email: str
    department: str
    designation: str
    manager: str
    risk_level: RiskLevel
    risk_score: int = Field(ge=0, le=100)
    location: str
    joined_at: datetime
    is_active: bool


class EmployeeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    department: str = Field(min_length=1, max_length=100)
    designation: str = Field(min_length=1, max_length=150)
    manager: str = Field(min_length=1, max_length=255)
    risk_level: RiskLevel = "Low"
    risk_score: int = Field(default=0, ge=0, le=100)
    location: str = Field(default="", max_length=150)


class EmployeeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    department: str | None = Field(default=None, min_length=1, max_length=100)
    designation: str | None = Field(default=None, min_length=1, max_length=150)
    manager: str | None = Field(default=None, min_length=1, max_length=255)
    risk_level: RiskLevel | None = None
    risk_score: int | None = Field(default=None, ge=0, le=100)
    location: str | None = None
    is_active: bool | None = None


# ── Alerts ────────────────────────────────────────────────────────────────────

class AlertOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    alert_id: str
    employee_id: str
    severity: Severity
    message: str
    status: AlertStatus
    rule: str
    narrative: str
    assigned_to: Role
    created_at: datetime

    # Populated via join — not in the ORM column, added manually in router
    employee_name: str = ""


class AlertCreate(BaseModel):
    employee_id: str
    severity: Severity
    message: str = Field(min_length=1, max_length=500)
    rule: str = Field(default="", max_length=200)
    narrative: str = ""
    assigned_to: Role = "Security Analyst"


class AlertUpdate(BaseModel):
    status: AlertStatus | None = None
    severity: Severity | None = None
    message: str | None = Field(default=None, min_length=1, max_length=500)
    narrative: str | None = None
    assigned_to: Role | None = None


# ── Activity Logs (MongoDB) ───────────────────────────────────────────────────

class ActivityLogOut(BaseModel):
    """Mirrors the MongoDB document shape."""
    log_id: str = ""
    employee_id: str
    event_type: EventType
    timestamp: str   # ISO-8601 string
    details: str = ""
    host: str = ""
    ip: str = ""


class ActivityLogCreate(BaseModel):
    employee_id: str
    event_type: EventType
    timestamp: str | None = None   # defaults to now if omitted
    details: str = ""
    host: str = ""
    ip: str = ""


# ── Incidents ─────────────────────────────────────────────────────────────────

class IncidentOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    incident_id: str
    title: str
    employee_id: str
    alert_id: str | None
    status: IncidentStatus
    severity: Severity
    opened_at: datetime
    closed_at: datetime | None
    notes: str


class IncidentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    employee_id: str
    alert_id: str | None = None
    severity: Severity
    notes: str = ""

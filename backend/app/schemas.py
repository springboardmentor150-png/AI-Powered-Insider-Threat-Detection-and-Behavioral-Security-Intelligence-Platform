from datetime import datetime

from pydantic import BaseModel, Field


class ActivityLogCreate(BaseModel):
    employee_code: str = Field(min_length=1, max_length=50)
    event_type: str = Field(min_length=1, max_length=100)
    source: str = Field(min_length=1, max_length=100)

    ip_address: str | None = None
    device_id: str | None = None
    application: str | None = None
    resource: str | None = None
    data_volume_mb: float | None = Field(default=None, ge=0)
    communication_type: str | None = None

    risk_score: int = Field(default=0, ge=0, le=100)


class ActivityLogResponse(ActivityLogCreate):
    id: str
    timestamp: datetime


class EmployeeCreate(BaseModel):
    employee_code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=150)
    email: str = Field(min_length=1, max_length=255)
    department: str = Field(min_length=1, max_length=100)
    role: str = Field(min_length=1, max_length=100)


class EmployeeUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    email: str = Field(min_length=1, max_length=255)
    department: str = Field(min_length=1, max_length=100)
    role: str = Field(min_length=1, max_length=100)


class EmployeeResponse(EmployeeCreate):
    id: int
    created_at: datetime


class IncidentCreate(BaseModel):
    employee_code: str = Field(min_length=1, max_length=50)
    incident_type: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=5000)


class InvestigationNoteCreate(BaseModel):
    note: str = Field(min_length=1, max_length=10000)
    evidence_reference: str | None = Field(
        default=None,
        max_length=500,
    )


class IncidentResolve(BaseModel):
    resolution_summary: str = Field(
        min_length=1,
        max_length=5000,
    )


class AnomalyFeedbackCreate(BaseModel):
    feedback: str = Field(min_length=1, max_length=50)  # "false_positive", "confirmed", "benign"
    notes: str | None = Field(default=None, max_length=5000)


class UserRoleUpdate(BaseModel):
    role: str = Field(min_length=1, max_length=50)


class UserStatusUpdate(BaseModel):
    is_active: bool


class IncidentStatusUpdate(BaseModel):
    status: str = Field(min_length=1, max_length=50)
    summary: str | None = Field(default=None, max_length=5000)


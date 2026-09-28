from typing import Any
from pydantic import BaseModel, EmailStr, Field

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    role: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class EmployeeCreate(BaseModel):
    employee_id: str
    name: str
    department: str
    designation: str
    manager_id: int | None = None
    device_info: str | None = None
    access_privileges: str | None = None

class LogIngestRequest(BaseModel):
    employee_id: str
    event_type: str
    details: dict[str, Any] = Field(default_factory=dict)

class AlertCreate(BaseModel):
    employee_id: str
    severity: str
    message: str

class EvidenceCreate(BaseModel):
    note: str

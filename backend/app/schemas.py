from pydantic import BaseModel, EmailStr
from typing import Any


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
    details: dict[str, Any] = {}
# backend/app/schemas.py
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

# --- User & Auth Schemas ---
class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None
    role: str = "security_analyst"

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class TokenPayload(BaseModel):
    sub: str
    role: str
    exp: int

# --- Employee Schemas ---
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

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    manager_id: Optional[int] = None
    device_info: Optional[str] = None
    access_privileges: Optional[str] = None
    status: Optional[str] = None
    baseline_risk_score: Optional[float] = None

class EmployeeOut(EmployeeBase):
    id: int
    status: str
    baseline_risk_score: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Activity Log Schemas ---
class ActivityLogIngest(BaseModel):
    employee_id: str
    event_type: str
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: Optional[datetime] = None

class ActivityLogOut(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    employee_id: str
    event_type: str
    timestamp: datetime
    details: Dict[str, Any]

# --- Alert Schemas ---
class AlertOut(BaseModel):
    id: int
    alert_code: str
    employee_id: str
    severity: str
    title: str
    message: str
    anomaly_type: Optional[str] = None
    risk_score: float
    is_acknowledged: bool
    is_escalated: bool
    incident_id: Optional[int] = None
    created_at: datetime
    employee: Optional[EmployeeOut] = None
    model_config = ConfigDict(from_attributes=True)

class AlertAcknowledge(BaseModel):
    is_acknowledged: bool = True

# --- Incident Schemas ---
class IncidentCreate(BaseModel):
    employee_id: str
    title: str
    description: Optional[str] = None
    severity: str = "HIGH"
    assigned_to: Optional[str] = None
    mitre_attack_technique: Optional[str] = None

class IncidentStatusUpdate(BaseModel):
    status: str
    assigned_to: Optional[str] = None
    ai_summary: Optional[str] = None

class IncidentOut(BaseModel):
    id: int
    incident_code: str
    employee_id: str
    title: str
    description: Optional[str] = None
    severity: str
    status: str
    assigned_to: Optional[str] = None
    mitre_attack_technique: Optional[str] = None
    ai_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    employee: Optional[EmployeeOut] = None
    model_config = ConfigDict(from_attributes=True)

# --- AI & Threat Intelligence Schemas ---
class AIAnalysisResult(BaseModel):
    employee_id: str
    overall_risk_score: float
    threat_level: str
    anomaly_detected: bool
    anomaly_score: float
    top_risk_factors: List[str]
    mitre_mapping: List[Dict[str, str]]
    recommended_actions: List[str]
    ai_narrative: str
    analyzed_event_count: int

class SimulationRequest(BaseModel):
    scenario: str
    employee_id: Optional[str] = None
    event_count: int = 10

from datetime import datetime

from pydantic import BaseModel, Field


class ActivityLogCreate(BaseModel):
    employee_code: str = Field(min_length=1, max_length=50)
    event_type: str = Field(min_length=1, max_length=100)
    source: str = Field(min_length=1, max_length=100)
    ip_address: str | None = None
    risk_score: int = Field(default=0, ge=0, le=100)


class ActivityLogResponse(ActivityLogCreate):
    id: str
    timestamp: datetime
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import Optional

from .mongo_database import activity_logs_collection


class ActivityLog(BaseModel):
    employee_id: int
    action: str
    resource: Optional[str] = None
    ip_address: Optional[str] = None


def create_activity_log(log: ActivityLog):
    document = {
        "employee_id": log.employee_id,
        "action": log.action,
        "resource": log.resource,
        "ip_address": log.ip_address,
        "timestamp": datetime.now(timezone.utc)
    }

    result = activity_logs_collection.insert_one(document)

    return {
        "message": "Activity log created successfully",
        "log_id": str(result.inserted_id)
    }
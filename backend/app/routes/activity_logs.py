from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient


router = APIRouter(tags=["Activity Logs"])

client = MongoClient("mongodb://localhost:27017/")
mongo_db = client["itbis"]
activity_logs = mongo_db["activity_logs"]


class ActivityLog(BaseModel):
    employee_id: str
    event_type: str
    timestamp: datetime
    details: dict


@router.post("/activity-logs")
def create_activity_log(data: ActivityLog):
    employee = data.model_dump()

    result = activity_logs.insert_one(employee)

    return {
        "message": "Activity log stored successfully",
        "log_id": str(result.inserted_id)
    }


@router.get("/activity-logs/{employee_id}")
def get_activity_logs(employee_id: str):
    logs = list(
        activity_logs.find(
            {"employee_id": employee_id},
            {"_id": 0}
        )
    )

    return {
        "employee_id": employee_id,
        "logs": logs
    }
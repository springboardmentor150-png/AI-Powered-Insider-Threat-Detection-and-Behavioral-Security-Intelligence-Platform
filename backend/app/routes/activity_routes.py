"""
Milestone 2 - Day 10
Activity log ingestion and retrieval.
"""

from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from pymongo import DESCENDING

from app.database import activity_logs_collection
from app.schemas import ActivityLogCreate, ActivityLogResponse
from app.security import require_role


router = APIRouter(tags=["activity logs"])


VALID_EVENT_TYPES = {
    "login",
    "file_download",
    "file_upload",
    "application_usage",
    "data_transfer",
}


@router.post(
    "/activity-logs",
    response_model=ActivityLogResponse,
    status_code=201,
)
def ingest_activity_log(
    data: ActivityLogCreate,
    user=Depends(
        require_role(
            "admin",
            "security_analyst",
            "soc_engineer",
            "security_manager",
        )
    ),
):
    """
    Store one employee activity event in MongoDB.
    """

    if data.event_type not in VALID_EVENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"event_type must be one of "
                f"{sorted(VALID_EVENT_TYPES)}"
            ),
        )

    document = {
        "employee_id": data.employee_id,
        "event_type": data.event_type,
        "timestamp": data.timestamp,
        "details": data.details,
    }

    result = activity_logs_collection.insert_one(document)

    return ActivityLogResponse(
        id=str(result.inserted_id),
        employee_id=data.employee_id,
        event_type=data.event_type,
        timestamp=data.timestamp,
        details=data.details,
    )


@router.get(
    "/activity-logs/{employee_id}",
    response_model=list[ActivityLogResponse],
)
def get_employee_activity_logs(
    employee_id: str,
    user=Depends(
        require_role(
            "admin",
            "security_analyst",
            "soc_engineer",
            "security_manager",
        )
    ),
):
    """
    Return activity logs for one employee.
    """

    documents = list(
        activity_logs_collection
        .find({"employee_id": employee_id})
        .sort("timestamp", DESCENDING)
    )

    response = []

    for document in documents:
        response.append(
            ActivityLogResponse(
                id=str(document["_id"]),
                employee_id=document["employee_id"],
                event_type=document["event_type"],
                timestamp=document["timestamp"],
                details=document.get("details", {}),
            )
        )

    return response
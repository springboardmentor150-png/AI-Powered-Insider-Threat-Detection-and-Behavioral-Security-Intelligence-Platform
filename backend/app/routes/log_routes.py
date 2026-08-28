from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any
from ..security import get_current_user
from ..log_ingestion import ingest_log

router = APIRouter(prefix="/logs", tags=["Activity Logs"])


class LogRequest(BaseModel):
    employee_id: str
    event_type: str
    details: Dict[str, Any]


@router.post("/ingest")
def ingest_activity_log(
    request: LogRequest,
    current_user=Depends(get_current_user),
):
    log_id = ingest_log(
        employee_id=request.employee_id,
        event_type=request.event_type,
        details=request.details,
    )
    return {"message": "Log ingested", "log_id": log_id}

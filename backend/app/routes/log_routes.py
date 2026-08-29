from fastapi import APIRouter, status, Depends
from typing import List
from app.schemas import ActivityLogCreate
from app.log_ingestion import ingest_activity_log, get_activity_logs
from app.auth import require_role

router = APIRouter(prefix="/logs", tags=["logs"])

@router.post("/ingest", status_code=status.HTTP_201_CREATED)
def ingest_log(log: ActivityLogCreate):
    inserted_id = ingest_activity_log(
        employee_id=log.employee_id,
        event_type=log.event_type,
        details=log.details
    )
    return {"message": "Activity log ingested successfully", "id": inserted_id}

@router.get("/")
def list_logs(_: dict = Depends(require_role("admin", "security_analyst", "soc_engineer", "security_manager"))):
    return get_activity_logs()

from datetime import datetime, timezone
from app.mongo_database import activity_logs_collection

def ingest_activity_log(employee_id: str, event_type: str, details: dict) -> str:
    """
    Ingest a single activity log into MongoDB.
    Generates the UTC timestamp on the backend.
    """
    log_entry = {
        "employee_id": employee_id,
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc),
        "details": details
    }
    
    result = activity_logs_collection.insert_one(log_entry)
    return str(result.inserted_id)

def get_activity_logs(limit: int = 100, employee_id: str = None):
    query = {}
    if employee_id:
        query["employee_id"] = employee_id
    logs = list(activity_logs_collection.find(query).sort("timestamp", -1).limit(limit))
    for log in logs:
        log["_id"] = str(log["_id"])
    return logs

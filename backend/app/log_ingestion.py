from datetime import datetime
from app.mongo_database import activity_logs_collection

def ingest_activity_log(employee_id: str, event_type: str, details: dict) -> str:
    """
    Ingest a single activity log into MongoDB.
    Generates the UTC timestamp on the backend.
    """
    log_entry = {
        "employee_id": employee_id,
        "event_type": event_type,
        "timestamp": datetime.utcnow(),
        "details": details
    }
    
    result = activity_logs_collection.insert_one(log_entry)
    return str(result.inserted_id)

def get_activity_logs(limit: int = 100):
    logs = list(activity_logs_collection.find().sort("timestamp", -1).limit(limit))
    for log in logs:
        log["_id"] = str(log["_id"])
    return logs

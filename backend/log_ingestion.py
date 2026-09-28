from datetime import datetime, timezone
from .database import mongo_db

activity_logs = mongo_db["activity_logs"]

def ingest_log(employee_id: str, event_type: str, details: dict):
    entry = {
        "employee_id": employee_id,
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc),
        "details": details,
    }
    result = activity_logs.insert_one(entry)
    entry["_id"] = str(result.inserted_id)
    return entry

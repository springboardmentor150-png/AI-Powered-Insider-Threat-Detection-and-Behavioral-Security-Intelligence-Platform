from datetime import datetime, timezone
from .database import activity_logs_collection


def ingest_log(employee_id: str, event_type: str, details: dict) -> str:
    document = {
        "employee_id": employee_id,
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": details,
    }
    result = activity_logs_collection.insert_one(document)
    return str(result.inserted_id)

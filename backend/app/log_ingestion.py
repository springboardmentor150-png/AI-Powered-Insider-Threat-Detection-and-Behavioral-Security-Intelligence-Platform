import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

MONGO_URL = os.getenv(
    "MONGO_URL",
    "mongodb://localhost:27017"
)

MONGO_DB = os.getenv(
    "MONGO_DB",
    "itbis"
)


client = MongoClient(
    MONGO_URL,
    serverSelectionTimeoutMS=3000
)

db = client[MONGO_DB]

activity_logs = db["activity_logs"]


def ingest_log(
    employee_id: str,
    event_type: str,
    details: dict
):
    log_entry = {
        "employee_id": employee_id,
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc),
        "details": details
    }

    result = activity_logs.insert_one(log_entry)

    log_entry["_id"] = str(result.inserted_id)

    return log_entry
    
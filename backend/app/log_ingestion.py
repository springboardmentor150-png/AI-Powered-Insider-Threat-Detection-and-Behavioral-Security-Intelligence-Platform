from pymongo import MongoClient
from datetime import datetime

MONGO_URL = "mongodb+srv://shriesat06_db_user:VflLQHGEYsr21Y8l@itbis.fdclztu.mongodb.net/?appName=ITBIS"

client = MongoClient(MONGO_URL)
db = client["itbis"]
activity_logs = db["activity_logs"]

def ingest_log(employee_id: str, event_type: str, details: dict):
    log_entry = {
        "employee_id": employee_id,
        "event_type": event_type,
        "timestamp": datetime.utcnow(),
        "details": details
    }
    activity_logs.insert_one(log_entry)
    return log_entry
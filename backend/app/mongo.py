"""
MongoDB helpers for ActivityLog storage and retrieval.

Collection schema (no hard schema enforcement — MongoDB is flexible):
{
    "_id":          ObjectId (auto),
    "log_id":       str   e.g. "LOG-9001"
    "employee_id":  str   e.g. "EMP-1042"
    "event_type":   str   one of ALLOWED_EVENT_TYPES
    "timestamp":    datetime (UTC)
    "details":      str
    "host":         str
    "ip":           str
}
"""
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_mongo_db

COLLECTION = "activity_logs"

ALLOWED_EVENT_TYPES = {
    "login",
    "logout",
    "file_download",
    "file_upload",
    "usb_connect",
    "email_external",
    "vpn_access",
    "privilege_change",
}


def _serialize(doc: dict) -> dict:
    """Convert MongoDB doc to JSON-serialisable dict."""
    doc = dict(doc)
    doc["_id"] = str(doc["_id"])
    if isinstance(doc.get("timestamp"), datetime):
        doc["timestamp"] = doc["timestamp"].replace(tzinfo=timezone.utc).isoformat()
    return doc


# ── Read ──────────────────────────────────────────────────────────────────────

async def get_logs(
    *,
    employee_id: str | None = None,
    event_type: str | None = None,
    date_from: str | None = None,   # "YYYY-MM-DD"
    date_to: str | None = None,     # "YYYY-MM-DD"
    skip: int = 0,
    limit: int = 200,
    db: AsyncIOMotorDatabase | None = None,
) -> list[dict]:
    if db is None:
        db = get_mongo_db()

    query: dict[str, Any] = {}

    if employee_id:
        query["employee_id"] = {"$regex": employee_id, "$options": "i"}
    if event_type and event_type in ALLOWED_EVENT_TYPES:
        query["event_type"] = event_type

    # Date range on timestamp field
    ts_filter: dict[str, datetime] = {}
    if date_from:
        try:
            ts_filter["$gte"] = datetime.fromisoformat(date_from)
        except ValueError:
            pass
    if date_to:
        try:
            # Include the entire "to" day
            ts_filter["$lte"] = datetime.fromisoformat(date_to).replace(
                hour=23, minute=59, second=59
            )
        except ValueError:
            pass
    if ts_filter:
        query["timestamp"] = ts_filter

    cursor = db[COLLECTION].find(query).sort("timestamp", -1).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    return [_serialize(d) for d in docs]


async def get_logs_for_employee(employee_id: str, limit: int = 50) -> list[dict]:
    db = get_mongo_db()
    cursor = db[COLLECTION].find({"employee_id": employee_id}).sort("timestamp", -1).limit(limit)
    docs = await cursor.to_list(length=limit)
    return [_serialize(d) for d in docs]


# ── Write ─────────────────────────────────────────────────────────────────────

async def insert_log(payload: dict) -> dict:
    """Insert a single activity log document. Returns the inserted doc."""
    db = get_mongo_db()

    if payload.get("event_type") not in ALLOWED_EVENT_TYPES:
        raise ValueError(
            f"Invalid event_type '{payload.get('event_type')}'. "
            f"Allowed: {sorted(ALLOWED_EVENT_TYPES)}"
        )

    doc: dict[str, Any] = {
        "log_id": payload.get("log_id", ""),
        "employee_id": payload["employee_id"],
        "event_type": payload["event_type"],
        "details": payload.get("details", ""),
        "host": payload.get("host", "UNKNOWN"),
        "ip": payload.get("ip", "0.0.0.0"),
        "timestamp": _parse_timestamp(payload.get("timestamp")),
    }

    result = await db[COLLECTION].insert_one(doc)
    inserted = await db[COLLECTION].find_one({"_id": result.inserted_id})
    return _serialize(inserted)


async def insert_many_logs(payloads: list[dict]) -> int:
    """Bulk-insert activity logs. Returns count inserted."""
    db = get_mongo_db()
    docs = []
    for p in payloads:
        if p.get("event_type") not in ALLOWED_EVENT_TYPES:
            continue  # skip invalid; don't abort entire batch
        docs.append(
            {
                "log_id": p.get("log_id", ""),
                "employee_id": p["employee_id"],
                "event_type": p["event_type"],
                "details": p.get("details", ""),
                "host": p.get("host", "UNKNOWN"),
                "ip": p.get("ip", "0.0.0.0"),
                "timestamp": _parse_timestamp(p.get("timestamp")),
            }
        )
    if not docs:
        return 0
    result = await db[COLLECTION].insert_many(docs)
    return len(result.inserted_ids)


def _parse_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return dt.replace(tzinfo=None)  # store naive UTC in Mongo
        except ValueError:
            pass
    return datetime.utcnow()

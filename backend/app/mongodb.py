import os
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from bson import ObjectId

logger = logging.getLogger("itbis.mongodb")

MONGODB_DATABASE = os.environ.get("MONGODB_DATABASE", "itbis").strip() or "itbis"

def _normalize_mongodb_url(raw_url: str, db_name: str) -> str:
    if not raw_url or not isinstance(raw_url, str):
        return ""
    cleaned = raw_url.strip()
    if cleaned.lower() in {"", "none", "false", "disabled", "null", "undefined", "itbis", "itbis_production", db_name.lower()}:
        return ""
    if not (cleaned.startswith("mongodb://") or cleaned.startswith("mongodb+srv://")):
        return ""
    return cleaned

MONGODB_URL = _normalize_mongodb_url(os.environ.get("MONGODB_URL", ""), MONGODB_DATABASE)
MONGODB_COLLECTION = "activity_logs"

VALID_EVENT_TYPES = {
    "login",
    "file_download",
    "file_upload",
    "data_transfer",
    "email_activity",
    "privilege_change",
    "remote_access",
    "usb_connect",
}

# Persistent development file store path
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
_DEV_FILE_PATH = os.path.join(_DATA_DIR, "activity_logs.json")

MONGODB_BASELINES_COLLECTION = "behavioral_baselines"
_BASELINES_DEV_FILE_PATH = os.path.join(_DATA_DIR, "behavioral_baselines.json")

MONGODB_ANOMALIES_COLLECTION = "anomalies"
_ANOMALIES_DEV_FILE_PATH = os.path.join(_DATA_DIR, "anomalies.json")


class MongoDBService:
    def __init__(self):
        self._client = None
        self._db = None
        self._collection = None
        self._baselines_collection = None
        self._anomalies_collection = None
        self._connected = False
        self._dev_storage: List[Dict[str, Any]] = []
        self._dev_baselines: List[Dict[str, Any]] = []
        self._dev_anomalies: List[Dict[str, Any]] = []
        self._ensure_data_dir()
        self._load_dev_storage()
        self._load_dev_baselines()
        self._load_dev_anomalies()
        self._init_connection()

    def _ensure_data_dir(self):
        try:
            if not os.path.exists(_DATA_DIR):
                os.makedirs(_DATA_DIR, exist_ok=True)
        except Exception as e:
            logger.warning("Could not create data directory: %s", e)

    def _load_dev_storage(self):
        try:
            if os.path.exists(_DEV_FILE_PATH):
                with open(_DEV_FILE_PATH, "r", encoding="utf-8") as f:
                    self._dev_storage = json.load(f)
                logger.info("Loaded %d activity records from persistent dev store (%s)", len(self._dev_storage), _DEV_FILE_PATH)
            else:
                self._dev_storage = []
        except Exception as e:
            logger.warning("Failed to load persistent dev store: %s", e)
            self._dev_storage = []

    def _save_dev_storage(self):
        try:
            self._ensure_data_dir()
            with open(_DEV_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(self._dev_storage, f, indent=2)
        except Exception as e:
            logger.warning("Failed to save persistent dev store: %s", e)

    def _load_dev_baselines(self):
        try:
            if os.path.exists(_BASELINES_DEV_FILE_PATH):
                with open(_BASELINES_DEV_FILE_PATH, "r", encoding="utf-8") as f:
                    self._dev_baselines = json.load(f)
                logger.info("Loaded %d baseline records from persistent dev store (%s)", len(self._dev_baselines), _BASELINES_DEV_FILE_PATH)
            else:
                self._dev_baselines = []
        except Exception as e:
            logger.warning("Failed to load persistent dev baselines: %s", e)
            self._dev_baselines = []

    def _save_dev_baselines(self):
        try:
            self._ensure_data_dir()
            with open(_BASELINES_DEV_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(self._dev_baselines, f, indent=2)
        except Exception as e:
            logger.warning("Failed to save persistent dev baselines: %s", e)

    def _load_dev_anomalies(self):
        try:
            if os.path.exists(_ANOMALIES_DEV_FILE_PATH):
                with open(_ANOMALIES_DEV_FILE_PATH, "r", encoding="utf-8") as f:
                    self._dev_anomalies = json.load(f)
                logger.info("Loaded %d anomaly records from persistent dev store (%s)", len(self._dev_anomalies), _ANOMALIES_DEV_FILE_PATH)
            else:
                self._dev_anomalies = []
        except Exception as e:
            logger.warning("Failed to load persistent dev anomalies: %s", e)
            self._dev_anomalies = []

    def _save_dev_anomalies(self):
        try:
            self._ensure_data_dir()
            with open(_ANOMALIES_DEV_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(self._dev_anomalies, f, indent=2)
        except Exception as e:
            logger.warning("Failed to save persistent dev anomalies: %s", e)

    def _init_connection(self):
        if not MONGODB_URL:
            self._connected = False
            self._client = None
            raw_val = os.environ.get("MONGODB_URL", "").strip()
            if raw_val:
                logger.warning(
                    "MONGODB_URL is configured as '%s' (not a valid MongoDB connection string starting with 'mongodb://' or 'mongodb+srv://'). "
                    "Skipping MongoDB network connection and using persistent JSON telemetry storage (%s).",
                    raw_val,
                    _DEV_FILE_PATH,
                )
            else:
                logger.info(
                    "MONGODB_URL not configured. Operating in persistent JSON telemetry mode (%s).",
                    _DEV_FILE_PATH,
                )
            return

        try:
            from pymongo import MongoClient
            self._client = MongoClient(
                MONGODB_URL,
                serverSelectionTimeoutMS=2000,
                connectTimeoutMS=2000,
                socketTimeoutMS=2000,
            )
            self._client.admin.command('ping')
            self._db = self._client[MONGODB_DATABASE]
            self._collection = self._db[MONGODB_COLLECTION]
            self._baselines_collection = self._db[MONGODB_BASELINES_COLLECTION]
            self._anomalies_collection = self._db[MONGODB_ANOMALIES_COLLECTION]
            self._connected = True
            logger.info("Successfully connected to MongoDB (%s/%s.%s)", MONGODB_URL, MONGODB_DATABASE, MONGODB_COLLECTION)
            
            # Sync persistent storage to MongoDB if MongoDB collection is empty
            if self._collection is not None and self._dev_storage:
                try:
                    if self._collection.count_documents({}) == 0:
                        docs_to_insert = []
                        for d in self._dev_storage:
                            doc = dict(d)
                            doc.pop("_id", None)
                            docs_to_insert.append(doc)
                        if docs_to_insert:
                            self._collection.insert_many(docs_to_insert)
                            logger.info("Synchronized %d records from persistent buffer into MongoDB collection", len(docs_to_insert))
                except Exception as sync_err:
                    logger.warning("Sync to MongoDB collection skipped: %s", sync_err)

            # Sync persistent baselines to MongoDB if MongoDB baselines collection is empty
            if self._baselines_collection is not None and self._dev_baselines:
                try:
                    if self._baselines_collection.count_documents({}) == 0:
                        baselines_to_insert = []
                        for b in self._dev_baselines:
                            b_doc = dict(b)
                            b_doc.pop("_id", None)
                            baselines_to_insert.append(b_doc)
                        if baselines_to_insert:
                            self._baselines_collection.insert_many(baselines_to_insert)
                            logger.info("Synchronized %d baselines from persistent buffer into MongoDB collection", len(baselines_to_insert))
                except Exception as sync_err:
                    logger.warning("Sync to MongoDB baselines collection skipped: %s", sync_err)

            # Sync persistent anomalies to MongoDB if MongoDB anomalies collection is empty
            if self._anomalies_collection is not None and self._dev_anomalies:
                try:
                    if self._anomalies_collection.count_documents({}) == 0:
                        anomalies_to_insert = []
                        for a in self._dev_anomalies:
                            a_doc = dict(a)
                            a_doc.pop("_id", None)
                            anomalies_to_insert.append(a_doc)
                        if anomalies_to_insert:
                            self._anomalies_collection.insert_many(anomalies_to_insert)
                            logger.info("Synchronized %d anomalies from persistent buffer into MongoDB collection", len(anomalies_to_insert))
                except Exception as sync_err:
                    logger.warning("Sync to MongoDB anomalies collection skipped: %s", sync_err)
        except Exception as e:
            self._connected = False
            if self._client is not None:
                try:
                    self._client.close()
                except Exception:
                    pass
                self._client = None
            logger.warning("MongoDB not reachable at %s. Persistent development mode active (%s). Error: %s", MONGODB_URL, _DEV_FILE_PATH, e)

    @property
    def is_connected(self) -> bool:
        return self._connected

    def count_activities(self, query: Optional[Dict[str, Any]] = None) -> int:
        """Returns total activity document count from MongoDB or persistent dev store."""
        if self._connected and self._collection is not None:
            try:
                return self._collection.count_documents(query or {})
            except Exception as e:
                logger.error("MongoDB count error: %s", e)
        
        if not self._connected:
            self._load_dev_storage()
        if query:
            filtered = self._filter_dev_storage(query)
            return len(filtered)
        return len(self._dev_storage)

    def insert_activity_log(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Inserts an activity log with flexible details dictionary into MongoDB and persistent store."""
        event_type = str(data.get("event_type", "")).lower().strip()
        if event_type not in VALID_EVENT_TYPES:
            raise ValueError(f"Unknown event_type '{event_type}'. Must be one of: {sorted(list(VALID_EVENT_TYPES))}")

        # Ensure ISO timestamp format
        if "timestamp" not in data or not data["timestamp"]:
            data["timestamp"] = datetime.now(timezone.utc).isoformat()
        elif isinstance(data["timestamp"], datetime):
            data["timestamp"] = data["timestamp"].isoformat()

        doc = dict(data)
        doc["event_type"] = event_type
        if "details" not in doc or not isinstance(doc["details"], dict):
            doc["details"] = {}

        # Insert into MongoDB if connected
        if self._connected and self._collection is not None:
            try:
                res = self._collection.insert_one(doc)
                doc["id"] = str(res.inserted_id)
                doc.pop("_id", None)
                # Keep local store in sync
                self._dev_storage.insert(0, dict(doc))
                self._save_dev_storage()
                return doc
            except Exception as e:
                logger.error("MongoDB insertion error: %s. Using persistent storage.", e)

        # Persistent development storage
        doc_id = str(ObjectId())
        doc["id"] = doc_id
        doc.pop("_id", None)
        self._dev_storage.insert(0, dict(doc))
        self._save_dev_storage()
        return doc

    def _filter_dev_storage(
        self,
        query: Optional[Dict[str, Any]] = None,
        employee_id: Optional[str] = None,
        event_type: Optional[str] = None,
        device: Optional[str] = None,
        ip_address: Optional[str] = None,
        search: Optional[str] = None,
        is_test_event: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        if not self._connected:
            self._load_dev_storage()
        filtered = list(self._dev_storage)
        if query:
            if "employee_id" in query:
                filtered = [x for x in filtered if x.get("employee_id") == query["employee_id"]]
            if "event_type" in query:
                filtered = [x for x in filtered if x.get("event_type") == query["event_type"]]
            if "is_test_event" in query:
                filtered = [x for x in filtered if x.get("is_test_event") == query["is_test_event"]]

        if employee_id:
            filtered = [x for x in filtered if x.get("employee_id") == employee_id]
        if event_type and event_type.lower() != "all":
            filtered = [x for x in filtered if str(x.get("event_type", "")).lower() == event_type.lower()]
        if is_test_event is not None:
            filtered = [x for x in filtered if bool(x.get("is_test_event", False)) == is_test_event]
        if device:
            filtered = [x for x in filtered if device.lower() in str(x.get("device", "")).lower()]
        if ip_address:
            filtered = [x for x in filtered if ip_address.lower() in str(x.get("ip_address", "")).lower()]
        if search:
            s = search.lower()
            filtered = [
                x for x in filtered
                if s in str(x.get("employee_id", "")).lower()
                or s in str(x.get("event_type", "")).lower()
                or s in str(x.get("action", "")).lower()
                or s in str(x.get("resource", "")).lower()
                or s in str(x.get("details", "")).lower()
            ]
        return filtered

    def query_activity_logs(
        self,
        employee_id: Optional[str] = None,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        device: Optional[str] = None,
        ip_address: Optional[str] = None,
        search: Optional[str] = None,
        is_test_event: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """Queries activity logs from MongoDB with filtering and pagination."""
        query: Dict[str, Any] = {}
        if employee_id:
            query["employee_id"] = employee_id
        if event_type and event_type.lower() != "all":
            query["event_type"] = event_type.lower()
        if is_test_event is not None:
            query["is_test_event"] = is_test_event
        if device:
            query["device"] = {"$regex": device, "$options": "i"}
        if ip_address:
            query["ip_address"] = {"$regex": ip_address, "$options": "i"}

        if self._connected and self._collection is not None:
            try:
                cursor = self._collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
                items = []
                for doc in cursor:
                    doc["id"] = str(doc.get("_id", doc.get("id", "")))
                    doc.pop("_id", None)
                    items.append(doc)
                total = self._collection.count_documents(query)
                return {"items": items, "total": total}
            except Exception as e:
                logger.error("MongoDB query error: %s", e)

        # Query persistent dev store
        filtered = self._filter_dev_storage(
            employee_id=employee_id,
            event_type=event_type,
            device=device,
            ip_address=ip_address,
            search=search,
            is_test_event=is_test_event,
        )
        # Guarantee newest-first sorting by timestamp descending
        filtered.sort(key=lambda x: str(x.get("timestamp", "")), reverse=True)
        total = len(filtered)
        items = filtered[skip : skip + limit]
        return {"items": items, "total": total}

    def get_activity_by_id(self, activity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves single activity record from MongoDB."""
        if self._connected and self._collection is not None:
            try:
                try:
                    obj_id = ObjectId(activity_id)
                    doc = self._collection.find_one({"_id": obj_id})
                except Exception:
                    doc = self._collection.find_one({"id": activity_id})

                if doc:
                    doc["id"] = str(doc.get("_id", doc.get("id", "")))
                    doc.pop("_id", None)
                    return doc
            except Exception as e:
                logger.error("MongoDB find error: %s", e)

        for x in self._dev_storage:
            if str(x.get("id")) == str(activity_id):
                return x
        return None

    def get_activity_timeline(
        self,
        employee_id: Optional[str] = None,
        event_type: Optional[str] = None,
        time_range: str = "7d",
        limit: int = 150,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves chronological employee activity data from MongoDB telemetry.
        Filters by time_range ('24h', '7d', '30d', 'all'), employee_id, and event_type.
        Returns list of structured timeline events sorted newest first.
        """
        now = datetime.now(timezone.utc)
        cutoff: Optional[datetime] = None
        range_lower = time_range.lower()
        if range_lower == "24h":
            cutoff = now - timedelta(hours=24)
        elif range_lower == "7d":
            cutoff = now - timedelta(days=7)
        elif range_lower == "30d":
            cutoff = now - timedelta(days=30)

        query: Dict[str, Any] = {}
        if employee_id and employee_id.upper() != "ALL":
            query["employee_id"] = employee_id
        if event_type and event_type.lower() != "all":
            query["event_type"] = event_type.lower()
        if cutoff:
            query["timestamp"] = {"$gte": cutoff.isoformat()}

        raw_logs = []
        if self._connected and self._collection is not None:
            try:
                cursor = self._collection.find(query).sort("timestamp", -1).limit(limit)
                for doc in cursor:
                    doc["id"] = str(doc.get("_id", doc.get("id", "")))
                    doc.pop("_id", None)
                    raw_logs.append(doc)
            except Exception as e:
                logger.error("MongoDB timeline query error: %s", e)

        if not raw_logs:
            filtered = list(self._dev_storage)
            if employee_id and employee_id.upper() != "ALL":
                filtered = [x for x in filtered if x.get("employee_id") == employee_id]
            if event_type and event_type.lower() != "all":
                filtered = [x for x in filtered if str(x.get("event_type", "")).lower() == event_type.lower()]
            if cutoff:
                cutoff_iso = cutoff.isoformat()
                filtered = [x for x in filtered if str(x.get("timestamp", "")) >= cutoff_iso]

            try:
                filtered.sort(key=lambda x: str(x.get("timestamp", "")), reverse=True)
            except Exception:
                pass
            raw_logs = filtered[:limit]

        timeline_items = []
        for log in raw_logs:
            risk = int(log.get("risk_weight", 0))
            is_susp = bool(log.get("is_suspicious", False) or risk >= 35)
            anomaly_reasons = list(log.get("anomaly_reasons", []))
            
            if risk >= 80:
                severity = "CRITICAL"
            elif risk >= 50:
                severity = "HIGH"
            elif risk >= 20:
                severity = "MEDIUM"
            else:
                severity = "LOW"

            reason_str = "; ".join(anomaly_reasons) if anomaly_reasons else ("Suspicious anomaly detected" if is_susp else "Normal behavioral telemetry")

            timeline_items.append({
                "id": str(log.get("id", "")),
                "employee_id": str(log.get("employee_id", "")),
                "event_type": str(log.get("event_type", "login")).lower(),
                "action": log.get("action", f"Executed {log.get('event_type')}"),
                "resource": log.get("resource", "Internal System"),
                "timestamp": str(log.get("timestamp", "")),
                "device": log.get("device") or "N/A",
                "ip_address": log.get("ip_address") or "N/A",
                "location": log.get("location") or "Hyderabad",
                "risk_weight": risk,
                "severity": severity,
                "is_suspicious": is_susp,
                "is_anomalous": is_susp,
                "is_anomaly": is_susp,
                "anomaly_reasons": anomaly_reasons,
                "reason": reason_str,
                "why_suspicious": reason_str,
                "is_test_event": bool(log.get("is_test_event", False)),
                "details": log.get("details", {}) if isinstance(log.get("details"), dict) else {},
            })

        return timeline_items


    def get_activity_heatmap(self, employee_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Calculates 7-Day x 24-Hour activity intensity and off-hours flags."""
        logs = self.query_activity_logs(employee_id=employee_id, limit=2000)["items"]
        
        grid: Dict[str, Dict[str, Any]] = {}
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        
        for d_idx, day_name in enumerate(day_names):
            for hour in range(24):
                key = f"{day_name}_{hour:02d}"
                grid[key] = {
                    "day": day_name,
                    "day_index": d_idx,
                    "hour": hour,
                    "hour_label": f"{hour:02d}:00",
                    "event_count": 0,
                    "suspicious_count": 0,
                    "is_off_hours": hour < 8 or hour >= 19 or d_idx >= 5,
                    "primary_event": None,
                }

        for log in logs:
            ts_str = log.get("timestamp", "")
            try:
                dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                d_idx = dt.weekday()
                day_name = day_names[d_idx]
                hour = dt.hour
                key = f"{day_name}_{hour:02d}"
                if key in grid:
                    grid[key]["event_count"] += 1
                    if log.get("is_suspicious") or log.get("risk_weight", 0) >= 30:
                        grid[key]["suspicious_count"] += 1
                    grid[key]["primary_event"] = log.get("event_type")
            except Exception:
                continue

        return list(grid.values())

    def get_event_type_distribution(self, employee_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Returns distribution of events across all supported types grouped by event_type.
        Uses native MongoDB aggregation when connected, and persistent buffer when offline.
        """
        counts: Dict[str, int] = {k: 0 for k in sorted(VALID_EVENT_TYPES)}

        if self._connected and self._collection is not None:
            try:
                pipeline = []
                if employee_id:
                    pipeline.append({"$match": {"employee_id": employee_id}})
                pipeline.append({"$group": {"_id": "$event_type", "count": {"$sum": 1}}})
                
                results = list(self._collection.aggregate(pipeline))
                for r in results:
                    et = str(r.get("_id", "")).lower()
                    if et in counts:
                        counts[et] = int(r.get("count", 0))
            except Exception as e:
                logger.error("MongoDB aggregation pipeline error: %s", e)
                # Fallback to dev storage
                logs = self.query_activity_logs(employee_id=employee_id, limit=5000)["items"]
                for log in logs:
                    et = str(log.get("event_type", "")).lower()
                    if et in counts:
                        counts[et] += 1
        else:
            logs = self.query_activity_logs(employee_id=employee_id, limit=5000)["items"]
            for log in logs:
                et = str(log.get("event_type", "")).lower()
                if et in counts:
                    counts[et] += 1

        total = sum(counts.values()) or 1
        distribution = []
        for et, count in counts.items():
            distribution.append({
                "event_type": et,
                "label": et.replace("_", " ").title(),
                "count": count,
                "percentage": round((count / total) * 100, 1),
            })
        distribution.sort(key=lambda x: x["count"], reverse=True)
        return distribution

    def get_employee_activity_profile(self, employee_id: str) -> Dict[str, Any]:
        """Computes statistical activity profile for a specific employee."""
        logs = self.query_activity_logs(employee_id=employee_id, limit=1000)["items"]
        if not logs:
            return {
                "employee_id": employee_id,
                "typical_login_time": "09:00 AM",
                "typical_logout_time": "06:00 PM",
                "known_devices": ["finance-laptop-02"],
                "known_ips": ["192.168.1.10"],
                "average_daily_events": 12,
                "most_common_event_type": "login",
                "total_downloads_mb": 45.2,
                "off_hours_percentage": 5.0,
                "total_events": 0,
                "suspicious_events": 0,
            }

        devices = set()
        ips = set()
        event_types: Dict[str, int] = {}
        total_downloads = 0.0
        off_hours_count = 0
        suspicious_count = 0

        for log in logs:
            if log.get("device"):
                devices.add(str(log["device"]))
            if log.get("ip_address"):
                ips.add(str(log["ip_address"]))
            et = log.get("event_type", "event")
            event_types[et] = event_types.get(et, 0) + 1

            if log.get("is_suspicious") or log.get("risk_weight", 0) >= 30:
                suspicious_count += 1

            details = log.get("details", {})
            if isinstance(details, dict):
                size = details.get("size_mb", details.get("download_size_mb", 0))
                try:
                    total_downloads += float(size)
                except Exception:
                    pass

            ts_str = log.get("timestamp", "")
            try:
                dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                if dt.hour < 8 or dt.hour >= 19 or dt.weekday() >= 5:
                    off_hours_count += 1
            except Exception:
                pass

        most_common = max(event_types.items(), key=lambda x: x[1])[0] if event_types else "login"
        total = len(logs)
        off_hours_pct = round((off_hours_count / total) * 100, 1) if total > 0 else 0.0

        return {
            "employee_id": employee_id,
            "typical_login_time": "09:00 AM",
            "typical_logout_time": "06:00 PM",
            "known_devices": list(devices) if devices else ["finance-laptop-02"],
            "known_ips": list(ips) if ips else ["192.168.1.10"],
            "average_daily_events": max(1, total // 7),
            "most_common_event_type": most_common.replace("_", " ").title(),
            "total_downloads_mb": round(total_downloads, 1),
            "off_hours_percentage": off_hours_pct,
            "total_events": total,
            "suspicious_events": suspicious_count,
        }

    def upsert_baseline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upserts a behavioral baseline record into MongoDB collection 'behavioral_baselines'
        or the persistent development store.
        Recalculation updates existing records by (employee_id, indicator) instead of creating duplicates.
        """
        if "employee_id" not in data or "indicator" not in data:
            raise ValueError("Baseline record must contain 'employee_id' and 'indicator'.")

        doc = dict(data)
        if "last_updated" not in doc or not doc["last_updated"]:
            doc["last_updated"] = datetime.now(timezone.utc).isoformat()
        elif isinstance(doc["last_updated"], datetime):
            doc["last_updated"] = doc["last_updated"].isoformat()

        # MongoDB storage
        if self._connected and self._baselines_collection is not None:
            try:
                self._baselines_collection.update_one(
                    {"employee_id": doc["employee_id"], "indicator": doc["indicator"]},
                    {"$set": doc},
                    upsert=True
                )
                logger.info("Upserted baseline in MongoDB for employee %s (%s)", doc["employee_id"], doc["indicator"])
            except Exception as e:
                logger.error("MongoDB baseline upsert error: %s. Using persistent dev storage.", e)

        # Persistent dev storage upsert
        found = False
        for idx, item in enumerate(self._dev_baselines):
            if item.get("employee_id") == doc["employee_id"] and item.get("indicator") == doc["indicator"]:
                self._dev_baselines[idx] = dict(doc)
                found = True
                break
        if not found:
            self._dev_baselines.append(dict(doc))
        self._save_dev_baselines()

        return doc

    def get_baselines(
        self,
        employee_id: Optional[str] = None,
        indicator: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieves behavioral baseline records from MongoDB or persistent store."""
        query: Dict[str, Any] = {}
        if employee_id:
            query["employee_id"] = employee_id
        if indicator:
            query["indicator"] = indicator

        if self._connected and self._baselines_collection is not None:
            try:
                cursor = self._baselines_collection.find(query)
                results = []
                for b in cursor:
                    b_doc = dict(b)
                    b_doc.pop("_id", None)
                    results.append(b_doc)
                return results
            except Exception as e:
                logger.error("MongoDB get_baselines error: %s. Using persistent storage.", e)

        # Dev storage query
        if not self._connected:
            self._load_dev_baselines()
        filtered = list(self._dev_baselines)
        if employee_id:
            filtered = [x for x in filtered if x.get("employee_id") == employee_id]
        if indicator:
            filtered = [x for x in filtered if x.get("indicator") == indicator]
        return [dict(x) for x in filtered]

    def get_baseline(self, employee_id: str, indicator: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single baseline record by employee_id and indicator."""
        results = self.get_baselines(employee_id=employee_id, indicator=indicator)
        return results[0] if results else None

    def delete_baseline(self, employee_id: str, indicator: str) -> bool:
        """Deletes a baseline record from MongoDB or persistent store."""
        deleted = False
        if self._connected and self._baselines_collection is not None:
            try:
                res = self._baselines_collection.delete_one({"employee_id": employee_id, "indicator": indicator})
                deleted = (res.deleted_count > 0)
            except Exception as e:
                logger.error("MongoDB delete_baseline error: %s", e)

        before_len = len(self._dev_baselines)
        self._dev_baselines = [
            x for x in self._dev_baselines
            if not (x.get("employee_id") == employee_id and x.get("indicator") == indicator)
        ]
        if len(self._dev_baselines) < before_len:
            deleted = True
            self._save_dev_baselines()
        return deleted

    def count_baselines(self, query: Optional[Dict[str, Any]] = None) -> int:
        """Counts total behavioral baselines."""
        if self._connected and self._baselines_collection is not None:
            try:
                return self._baselines_collection.count_documents(query or {})
            except Exception as e:
                logger.error("MongoDB count_baselines error: %s", e)
        if not self._connected:
            self._load_dev_baselines()
        if query:
            filtered = list(self._dev_baselines)
            if "employee_id" in query:
                filtered = [x for x in filtered if x.get("employee_id") == query["employee_id"]]
            if "indicator" in query:
                filtered = [x for x in filtered if x.get("indicator") == query["indicator"]]
            return len(filtered)
        return len(self._dev_baselines)

    def record_anomaly(self, anomaly_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Records a detected behavioral anomaly in MongoDB collection 'anomalies'
        or the persistent development store.
        """
        doc = dict(anomaly_data)
        if "id" not in doc:
            doc["id"] = str(ObjectId())
        if "detection_timestamp" not in doc or not doc["detection_timestamp"]:
            doc["detection_timestamp"] = datetime.now(timezone.utc).isoformat()
        elif isinstance(doc["detection_timestamp"], datetime):
            doc["detection_timestamp"] = doc["detection_timestamp"].isoformat()

        if self._connected and self._anomalies_collection is not None:
            try:
                mongo_doc = dict(doc)
                if ObjectId.is_valid(doc["id"]):
                    mongo_doc["_id"] = ObjectId(doc["id"])
                else:
                    mongo_doc["_id"] = doc["id"]
                self._anomalies_collection.insert_one(mongo_doc)
                logger.info("Recorded anomaly in MongoDB for %s (%s)", doc.get("employee_id"), doc.get("anomaly_type"))
            except Exception as e:
                logger.error("MongoDB anomaly record error: %s. Using persistent dev storage.", e)

        self._dev_anomalies.append(dict(doc))
        self._save_dev_anomalies()
        return doc

    save_anomaly = record_anomaly

    def get_anomalies(
        self,
        employee_id: Optional[str] = None,
        indicator: Optional[str] = None,
        anomaly_type: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Retrieves recorded anomaly events from MongoDB or persistent store."""
        query: Dict[str, Any] = {}
        if employee_id:
            query["employee_id"] = employee_id
        if indicator:
            query["indicator"] = indicator
        if anomaly_type:
            query["anomaly_type"] = anomaly_type
        if severity:
            query["severity"] = severity

        if self._connected and self._anomalies_collection is not None:
            try:
                cursor = self._anomalies_collection.find(query).sort("detection_timestamp", -1).limit(limit)
                results = []
                for a in cursor:
                    a_doc = dict(a)
                    a_doc["id"] = str(a_doc.pop("_id", a_doc.get("id", "")))
                    results.append(a_doc)
                return results
            except Exception as e:
                logger.error("MongoDB get_anomalies error: %s. Using persistent dev storage.", e)

        if not self._connected:
            self._load_dev_anomalies()
        filtered = list(self._dev_anomalies)
        if employee_id:
            filtered = [x for x in filtered if x.get("employee_id") == employee_id]
        if indicator:
            filtered = [x for x in filtered if x.get("indicator") == indicator]
        if anomaly_type:
            filtered = [x for x in filtered if x.get("anomaly_type") == anomaly_type]
        if severity:
            filtered = [x for x in filtered if x.get("severity") == severity]

        filtered.sort(key=lambda x: str(x.get("detection_timestamp", "")), reverse=True)
        return [dict(x) for x in filtered[:limit]]

    def count_anomalies(self, query: Optional[Dict[str, Any]] = None) -> int:
        """Counts recorded anomalies."""
        if self._connected and self._anomalies_collection is not None:
            try:
                return self._anomalies_collection.count_documents(query or {})
            except Exception as e:
                logger.error("MongoDB count_anomalies error: %s", e)
        if not self._connected:
            self._load_dev_anomalies()
        if query:
            filtered = list(self._dev_anomalies)
            for k, v in query.items():
                filtered = [x for x in filtered if x.get(k) == v]
            return len(filtered)
        return len(self._dev_anomalies)

    def clear_anomalies(self, employee_id: Optional[str] = None) -> int:
        """Clears recorded anomalies (for testing or cleanup)."""
        deleted_count = 0
        if self._connected and self._anomalies_collection is not None:
            try:
                q = {"employee_id": employee_id} if employee_id else {}
                res = self._anomalies_collection.delete_many(q)
                deleted_count = res.deleted_count
            except Exception as e:
                logger.error("MongoDB clear_anomalies error: %s", e)
        if employee_id:
            before = len(self._dev_anomalies)
            self._dev_anomalies = [x for x in self._dev_anomalies if x.get("employee_id") != employee_id]
            deleted_count = max(deleted_count, before - len(self._dev_anomalies))
        else:
            deleted_count = max(deleted_count, len(self._dev_anomalies))
            self._dev_anomalies = []
        self._save_dev_anomalies()
        return deleted_count

    def mark_anomaly_alerted(self, anomaly_id: Optional[str] = None, anomaly_doc: Optional[Dict[str, Any]] = None) -> bool:
        """Marks an anomaly record as having generated an alert in MongoDB or dev store."""
        if not anomaly_id and not anomaly_doc:
            return False
        
        target_id = str(anomaly_id) if anomaly_id else ""
        if not target_id and anomaly_doc:
            target_id = str(anomaly_doc.get("id") or anomaly_doc.get("_id") or "")

        if self._connected and self._anomalies_collection is not None:
            try:
                from bson import ObjectId
                query: Dict[str, Any] = {}
                if target_id and len(target_id) == 24 and ObjectId.is_valid(target_id):
                    query = {"$or": [{"_id": ObjectId(target_id)}, {"id": target_id}]}
                elif target_id:
                    query = {"$or": [{"id": target_id}, {"_id": target_id}]}
                elif anomaly_doc:
                    query = {
                        "employee_id": anomaly_doc.get("employee_id"),
                        "detection_timestamp": anomaly_doc.get("detection_timestamp"),
                        "anomaly_type": anomaly_doc.get("anomaly_type"),
                    }
                if query:
                    self._anomalies_collection.update_one(query, {"$set": {"alert_generated": True}})
            except Exception as e:
                logger.warning("MongoDB mark_anomaly_alerted error: %s", e)

        # Persistent dev store
        if not self._connected:
            self._load_dev_anomalies()
        updated = False
        for a in self._dev_anomalies:
            a_id = str(a.get("id") or a.get("_id") or "")
            if target_id and a_id == target_id:
                a["alert_generated"] = True
                updated = True
                break
            elif anomaly_doc and (
                a.get("employee_id") == anomaly_doc.get("employee_id")
                and a.get("detection_timestamp") == anomaly_doc.get("detection_timestamp")
                and a.get("anomaly_type") == anomaly_doc.get("anomaly_type")
            ):
                a["alert_generated"] = True
                updated = True
                break
        if updated:
            self._save_dev_anomalies()
        return updated


# Global singleton
mongo_service = MongoDBService()

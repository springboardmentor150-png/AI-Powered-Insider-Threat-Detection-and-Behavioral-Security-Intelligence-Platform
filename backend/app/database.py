# backend/app/database.py
import json
import os
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# -------------------------------------------------------------
# 1. Relational Database (SQLAlchemy - SQLite / PostgreSQL)
# -------------------------------------------------------------
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------------------------------------------
# 2. Document Store (MongoDB with Automatic Fallback & Aggregate Support)
# -------------------------------------------------------------
class InMemoryCollection:
    """Thread-safe document collection with MongoDB-compatible syntax and aggregation pipeline support."""
    def __init__(self, name: str, backing_file: Optional[str] = None):
        self.name = name
        self.backing_file = backing_file
        self.lock = threading.Lock()
        self.docs: List[Dict[str, Any]] = []
        self._load_from_file()

    def _load_from_file(self):
        if self.backing_file and os.path.exists(self.backing_file):
            try:
                with open(self.backing_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        for ts_key in ["timestamp", "detected_at", "last_updated"]:
                            if ts_key in item and isinstance(item[ts_key], str):
                                try:
                                    item[ts_key] = datetime.fromisoformat(item[ts_key])
                                except Exception:
                                    pass
                    self.docs = data
            except Exception:
                self.docs = []

    def _persist_to_file(self):
        if self.backing_file:
            try:
                serializable = []
                for d in self.docs:
                    copied = dict(d)
                    for ts_key in ["timestamp", "detected_at", "last_updated"]:
                        if ts_key in copied and isinstance(copied[ts_key], datetime):
                            copied[ts_key] = copied[ts_key].isoformat()
                    if "_id" in copied:
                        copied["_id"] = str(copied["_id"])
                    serializable.append(copied)
                with open(self.backing_file, "w", encoding="utf-8") as f:
                    json.dump(serializable, f, indent=2)
            except Exception:
                pass

    def insert_one(self, document: Dict[str, Any]):
        with self.lock:
            doc = dict(document)
            if "_id" not in doc:
                import uuid
                doc["_id"] = str(uuid.uuid4())
            if "timestamp" not in doc and "detected_at" not in doc:
                doc["timestamp"] = datetime.utcnow()
            self.docs.insert(0, doc)
            self._persist_to_file()
            return type("InsertResult", (), {"inserted_id": doc["_id"]})()

    def insert_many(self, documents: List[Dict[str, Any]]):
        with self.lock:
            inserted_ids = []
            for d in documents:
                doc = dict(d)
                if "_id" not in doc:
                    import uuid
                    doc["_id"] = str(uuid.uuid4())
                if "timestamp" not in doc and "detected_at" not in doc:
                    doc["timestamp"] = datetime.utcnow()
                self.docs.insert(0, doc)
                inserted_ids.append(doc["_id"])
            self._persist_to_file()
            return type("InsertManyResult", (), {"inserted_ids": inserted_ids})()

    def find(self, query: Optional[Dict[str, Any]] = None, sort: Optional[List] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        with self.lock:
            query = query or {}
            results = []
            for doc in self.docs:
                matches = True
                for k, v in query.items():
                    if k == "$gte" or isinstance(v, dict):
                        if isinstance(v, dict) and "$gte" in v:
                            doc_val = doc.get(k)
                            if doc_val is None or doc_val < v["$gte"]:
                                matches = False
                                break
                    elif doc.get(k) != v:
                        matches = False
                        break
                if matches:
                    results.append(dict(doc))
                if len(results) >= limit:
                    break
            return results

    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        results = self.find(query=query, limit=1)
        return results[0] if results else None

    def count_documents(self, query: Optional[Dict[str, Any]] = None) -> int:
        return len(self.find(query=query, limit=100000))

    def delete_many(self, query: Dict[str, Any]):
        with self.lock:
            if not query:
                deleted_count = len(self.docs)
                self.docs = []
                self._persist_to_file()
                return type("DeleteResult", (), {"deleted_count": deleted_count})()
            initial_count = len(self.docs)
            self.docs = [d for d in self.docs if not all(d.get(k) == v for k, v in query.items())]
            self._persist_to_file()
            return type("DeleteResult", (), {"deleted_count": initial_count - len(self.docs)})()

    def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Executes MongoDB aggregation pipeline ($match, $group, $sort, $limit).
        """
        with self.lock:
            results = [dict(d) for d in self.docs]

            for stage in pipeline:
                if "$match" in stage:
                    match_query = stage["$match"]
                    filtered = []
                    for doc in results:
                        matched = True
                        for k, v in match_query.items():
                            if isinstance(v, dict) and "$gte" in v:
                                doc_val = doc.get(k)
                                if doc_val is None or doc_val < v["$gte"]:
                                    matched = False
                                    break
                            elif doc.get(k) != v:
                                matched = False
                                break
                        if matched:
                            filtered.append(doc)
                    results = filtered

                elif "$group" in stage:
                    group_def = stage["$group"]
                    id_expr = group_def.get("_id")
                    grouped = {}

                    for doc in results:
                        # Extract group key
                        if isinstance(id_expr, str) and id_expr.startswith("$"):
                            key = doc.get(id_expr[1:])
                        elif isinstance(id_expr, dict) and "$dateToString" in id_expr:
                            date_field = id_expr["$dateToString"]["date"].replace("$", "")
                            dt = doc.get(date_field)
                            if isinstance(dt, datetime):
                                key = dt.strftime("%Y-%m-%d")
                            elif isinstance(dt, str):
                                key = dt[:10]
                            else:
                                key = str(datetime.utcnow().date())
                        else:
                            key = str(doc.get(id_expr, "unknown"))

                        if key not in grouped:
                            grouped[key] = {"_id": key, "items": []}
                        grouped[key]["items"].append(doc)

                    # Compute accumulators
                    agg_results = []
                    for k, grp in grouped.items():
                        out = {"_id": k}
                        for field, acc in group_def.items():
                            if field == "_id":
                                continue
                            if isinstance(acc, dict) and "$sum" in acc:
                                sum_val = acc["$sum"]
                                if sum_val == 1:
                                    out[field] = len(grp["items"])
                                    out["count"] = len(grp["items"])
                                    out["flag_count"] = len(grp["items"])
                                else:
                                    out[field] = sum(doc.get(sum_val.replace("$", ""), 0) for doc in grp["items"])
                        agg_results.append(out)
                    results = agg_results

                elif "$sort" in stage:
                    sort_def = stage["$sort"]
                    for field, direction in sort_def.items():
                        results.sort(key=lambda x: x.get(field, 0), reverse=(direction == -1))

                elif "$limit" in stage:
                    limit_val = stage["$limit"]
                    results = results[:limit_val]

            return results


class DocumentDatabase:
    """Provides access to activity_logs, rule_anomalies, ml_anomalies, and behavioral_baselines collections."""
    def __init__(self):
        self.is_connected_to_mongo = False
        self.mongo_client = None
        self.mongo_db = None
        
        try:
            from pymongo import MongoClient
            client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=1000)
            client.admin.command('ping')
            self.mongo_client = client
            self.mongo_db = client[settings.MONGODB_DB_NAME]
            self.is_connected_to_mongo = True
            print("[INFO] Connected successfully to live MongoDB server.")
        except Exception:
            data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
            os.makedirs(data_dir, exist_ok=True)
            self._activity_logs = InMemoryCollection("activity_logs", os.path.join(data_dir, "activity_logs.json"))
            self._rule_anomalies = InMemoryCollection("rule_anomalies", os.path.join(data_dir, "rule_anomalies.json"))
            self._ml_anomalies = InMemoryCollection("ml_anomalies", os.path.join(data_dir, "ml_anomalies.json"))
            self._behavioral_baselines = InMemoryCollection("behavioral_baselines", os.path.join(data_dir, "behavioral_baselines.json"))

    def __getitem__(self, name: str):
        if self.is_connected_to_mongo and self.mongo_db is not None:
            return self.mongo_db[name]
        if name == "activity_logs":
            return self._activity_logs
        elif name == "rule_anomalies":
            return self._rule_anomalies
        elif name == "ml_anomalies":
            return self._ml_anomalies
        elif name == "behavioral_baselines":
            return self._behavioral_baselines
        return InMemoryCollection(name)

    @property
    def activity_logs(self):
        return self["activity_logs"]

    @property
    def rule_anomalies(self):
        return self["rule_anomalies"]

    @property
    def ml_anomalies(self):
        return self["ml_anomalies"]

    @property
    def behavioral_baselines(self):
        return self["behavioral_baselines"]

doc_db = DocumentDatabase()
mongo_db = doc_db
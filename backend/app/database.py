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
# 2. Document Store (MongoDB with Automatic Fallback)
# -------------------------------------------------------------
class InMemoryCollection:
    """Thread-safe document collection with MongoDB-compatible syntax."""
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
                        # Filter operator check, e.g. {"detected_at": {"$gte": cutoff}}
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

    def sort(self, field: str, direction: int = -1):
        class SortedQuery:
            def __init__(self, docs, field, direction):
                self._docs = sorted(docs, key=lambda x: x.get(field, datetime.min), reverse=(direction == -1))
            def limit(self, count: int):
                return self._docs[:count]
            def __iter__(self):
                return iter(self._docs)
        return SortedQuery(self.docs, field, direction)

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
mongo_db = doc_db  # Alias matching Milestone 3 specification
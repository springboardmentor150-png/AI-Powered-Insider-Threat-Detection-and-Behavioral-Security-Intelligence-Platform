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
# 2. Document Store (MongoDB with Automatic Local Fallback)
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
                        if "timestamp" in item and isinstance(item["timestamp"], str):
                            try:
                                item["timestamp"] = datetime.fromisoformat(item["timestamp"])
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
                    if "timestamp" in copied and isinstance(copied["timestamp"], datetime):
                        copied["timestamp"] = copied["timestamp"].isoformat()
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
            if "timestamp" not in doc:
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
                if "timestamp" not in doc:
                    doc["timestamp"] = datetime.utcnow()
                self.docs.insert(0, doc)
                inserted_ids.append(doc["_id"])
            self._persist_to_file()
            return type("InsertManyResult", (), {"inserted_ids": inserted_ids})()

    def find(self, query: Optional[Dict[str, Any]] = None, sort: Optional[List] = None, limit: int = 100) -> List[Dict[str, Any]]:
        with self.lock:
            query = query or {}
            results = []
            for doc in self.docs:
                matches = True
                for k, v in query.items():
                    if k == "employee_id" and doc.get("employee_id") != v:
                        matches = False
                        break
                    elif k == "event_type" and doc.get("event_type") != v:
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


class DocumentDatabase:
    """Provides access to activity_logs and behavioral_baselines collections."""
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
        except Exception as e:
            print(f"[INFO] MongoDB server not reachable at {settings.MONGODB_URI}. Using embedded document store. (Fallback Mode Active)")
            
            data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
            os.makedirs(data_dir, exist_ok=True)
            self._activity_logs = InMemoryCollection("activity_logs", os.path.join(data_dir, "activity_logs.json"))
            self._behavioral_baselines = InMemoryCollection("behavioral_baselines", os.path.join(data_dir, "behavioral_baselines.json"))

    @property
    def activity_logs(self):
        if self.is_connected_to_mongo and self.mongo_db is not None:
            return self.mongo_db["activity_logs"]
        return self._activity_logs

    @property
    def behavioral_baselines(self):
        if self.is_connected_to_mongo and self.mongo_db is not None:
            return self.mongo_db["behavioral_baselines"]
        return self._behavioral_baselines

doc_db = DocumentDatabase()

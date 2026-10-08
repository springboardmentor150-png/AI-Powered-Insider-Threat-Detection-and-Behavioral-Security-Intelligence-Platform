from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pymongo import MongoClient

SQLITE_URL = "sqlite:///./itbis_m3.db"
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

MONGO_URL = "mongodb://localhost:27017"
try:
    mongo_client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=1000)
    mongo_client.server_info()
    mongo_db = mongo_client["itbis_m3"]
except Exception:
    mongo_client = None
    mongo_db = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from pymongo import MongoClient

# =========================
# SQLite Database
# =========================

DATABASE_URL = "sqlite:///./itbis.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# MongoDB Database
# =========================

MONGO_URL = "mongodb://localhost:27017"

mongo_client = MongoClient(MONGO_URL)

mongo_db = mongo_client["itbis"]


def get_mongo_db():
    return mongo_db
"""
Database connections for ITBIS.

PostgreSQL holds fixed-structure relational data (users, employees, incidents, alerts).
MongoDB holds flexible-structure data (activity_logs, behavioral_baselines).

Both connections are configured through environment variables (see .env.example).
If you don't have PostgreSQL/MongoDB installed yet, you can temporarily point
DATABASE_URL at a local SQLite file (e.g. "sqlite:///./itbis.db") to keep moving,
then switch back once your real databases are ready.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pymongo import MongoClient

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:yourpassword@localhost:5432/itbis"
)
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "itbis")

# --- PostgreSQL setup ---
# `connect_args` is only needed for SQLite; it's harmless to leave out for Postgres,
# but we detect SQLite here so the same file works with either backend during dev.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- MongoDB setup ---
mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client[MONGO_DB_NAME]

# Convenience handles for the two collections described in the Day 2 schema.
activity_logs_collection = mongo_db["activity_logs"]
behavioral_baselines_collection = mongo_db["behavioral_baselines"]

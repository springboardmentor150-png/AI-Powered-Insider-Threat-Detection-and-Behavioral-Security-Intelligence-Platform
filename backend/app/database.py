import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pymongo import MongoClient

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
MONGODB_URL = os.getenv("MONGODB_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

mongo_client = MongoClient(MONGODB_URL)
mongo_db = mongo_client["itbis_db"]
activity_logs_collection = mongo_db["activity_logs"]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

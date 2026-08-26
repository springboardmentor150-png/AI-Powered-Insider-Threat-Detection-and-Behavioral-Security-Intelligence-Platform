import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "itbis")

client = MongoClient(MONGO_URL)

mongo_db = client[MONGO_DB_NAME]
activity_logs = mongo_db["activity_logs"]
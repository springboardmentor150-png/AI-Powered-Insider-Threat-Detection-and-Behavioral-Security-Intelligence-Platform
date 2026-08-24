from pymongo import MongoClient


# MongoDB connection
MONGO_URL = "mongodb://127.0.0.1:27017"

client = MongoClient(MONGO_URL)

# ITBIS database
mongo_db = client["itbis"]

# Activity logs collection
activity_logs = mongo_db["activity_logs"]


# Test the connection
try:
    client.admin.command("ping")
    print("MongoDB connected successfully!")
except Exception as e:
    print("MongoDB connection failed:", e)
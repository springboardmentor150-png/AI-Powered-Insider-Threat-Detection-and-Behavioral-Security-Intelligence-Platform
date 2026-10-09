from pymongo import MongoClient

# MongoDB Connection settings
MONGO_URI = "mongodb://localhost:27017"

client = MongoClient(MONGO_URI)
db = client["itbis"]
activity_logs_collection = db["activity_logs"]

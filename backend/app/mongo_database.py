from pymongo import MongoClient
MONGO_URL = "mongodb://localhost:27017"

client = MongoClient(MONGO_URL)

mongo_db = client["itbis_db"]

activity_logs_collection = mongo_db["activity_logs"]
behavioral_baselines_collection = mongo_db["behavioral_baselines"]


def test_mongodb():
    try:
        client.admin.command("ping")
        return True
    except Exception:
        return False

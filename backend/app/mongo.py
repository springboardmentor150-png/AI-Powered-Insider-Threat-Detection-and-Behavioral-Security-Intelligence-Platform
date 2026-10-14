
import os

from pymongo import MongoClient


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["itbis"]

# Activity and behavioral analytics collections
activity_logs = mongo_db["activity_logs"]
behavioral_baselines = mongo_db["behavioral_baselines"]

# Anomaly detection collections
rule_anomalies = mongo_db["rule_anomalies"]
ml_anomalies = mongo_db["ml_anomalies"]
anomaly_feedback = mongo_db["anomaly_feedback"]

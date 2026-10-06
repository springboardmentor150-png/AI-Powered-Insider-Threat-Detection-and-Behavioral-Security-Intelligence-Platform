"""
ITBIS MongoDB Configuration

This module creates the MongoDB connection and exposes the
collections used by the application.
"""

import os

from pymongo import MongoClient


# ---------------------------------------------------------------------------
# MongoDB Connection
# ---------------------------------------------------------------------------

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://localhost:27017",
)

mongo_client = MongoClient(MONGO_URI)

mongo_db = mongo_client["itbis"]


# ---------------------------------------------------------------------------
# MongoDB Collections
# ---------------------------------------------------------------------------

# Milestone 1 + Milestone 2 activity data
activity_logs = mongo_db["activity_logs"]


# Milestone 2 behavioral profiling baselines
behavioral_baselines = mongo_db["behavioral_baselines"]

# Milestone 2 rule-based anomaly detection results
rule_anomalies = mongo_db["rule_anomalies"]
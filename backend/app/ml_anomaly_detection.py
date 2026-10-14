"""
ML-Based Anomaly Detection for ITBIS.

Milestone 2 - Day 17–18

Uses Isolation Forest to detect unusual employee behavior
from daily activity features.

Daily features:
- avg_login_hour
- download_count
- total_download_mb
- unique_devices
- total_events

Model:
- IsolationForest
- n_estimators = 100
- contamination = 0.05
- random_state = 42

Model file:
models/anomaly_model.pkl

ML anomalies are stored in:
MongoDB -> ml_anomalies
"""

from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

from app.database import (
    activity_logs_collection,
    ml_anomalies_collection,
)


# =========================================================
# Constants
# =========================================================

MODEL_DIR = Path("models")
MODEL_PATH = MODEL_DIR / "anomaly_model.pkl"

N_ESTIMATORS = 100
CONTAMINATION = 0.05
RANDOM_STATE = 42

FEATURE_NAMES = [
    "avg_login_hour",
    "download_count",
    "total_download_mb",
    "unique_devices",
    "total_events",
]


# =========================================================
# Get recent activity logs
# =========================================================

def get_recent_activity_logs(days_back: int = 90):
    """
    Get activity logs from the last `days_back` days.
    """

    cutoff = datetime.utcnow() - timedelta(
        days=days_back
    )

    logs = activity_logs_collection.find(
        {
            "timestamp": {
                "$gte": cutoff
            }
        }
    )

    return list(logs)


# =========================================================
# Build daily features
# =========================================================

def build_daily_features(days_back: int = 90):
    """
    Convert raw activity logs into one feature row
    per employee per day.
    """

    logs = get_recent_activity_logs(
        days_back
    )

    daily_data = defaultdict(
        lambda: {
            "login_hours": [],
            "download_count": 0,
            "total_download_mb": 0.0,
            "devices": set(),
            "total_events": 0,
        }
    )

    for log in logs:

        employee_id = log.get(
            "employee_id"
        )

        timestamp = log.get(
            "timestamp"
        )

        if not employee_id or not timestamp:
            continue

        day = timestamp.date()

        key = (
            employee_id,
            day
        )

        data = daily_data[key]

        # ---------------------------------------------
        # Count every event
        # ---------------------------------------------

        data["total_events"] += 1

        # ---------------------------------------------
        # Login time
        # ---------------------------------------------

        if log.get("event_type") == "login":

            login_hour = (
                timestamp.hour
                + (
                    timestamp.minute / 60
                )
            )

            data["login_hours"].append(
                login_hour
            )

        # ---------------------------------------------
        # File downloads
        # ---------------------------------------------

        if log.get("event_type") == "file_download":

            data["download_count"] += 1

            details = (
                log.get("details")
                or {}
            )

            size_mb = details.get(
                "size_mb",
                0
            )

            try:

                data["total_download_mb"] += float(
                    size_mb
                )

            except (TypeError, ValueError):

                pass

        # ---------------------------------------------
        # Device usage
        # ---------------------------------------------

        details = (
            log.get("details")
            or {}
        )

        device = details.get(
            "device"
        )

        if device:

            data["devices"].add(
                str(device)
            )

    # =====================================================
    # Convert aggregated data into feature rows
    # =====================================================

    feature_rows = []

    for (employee_id, day), data in daily_data.items():

        login_hours = data["login_hours"]

        if login_hours:

            avg_login_hour = (
                sum(login_hours)
                / len(login_hours)
            )

        else:

            # No login recorded that day.
            # Use 0 so the model receives a numeric value.
            avg_login_hour = 0.0

        row = {
            "employee_id": employee_id,
            "date": day,
            "avg_login_hour": round(
                avg_login_hour,
                4
            ),
            "download_count": data[
                "download_count"
            ],
            "total_download_mb": round(
                data["total_download_mb"],
                4
            ),
            "unique_devices": len(
                data["devices"]
            ),
            "total_events": data[
                "total_events"
            ],
        }

        feature_rows.append(row)

    return feature_rows


# =========================================================
# Convert rows into ML matrix
# =========================================================

def create_feature_matrix(feature_rows):
    """
    Convert daily feature dictionaries into a NumPy matrix.
    """

    matrix = []

    for row in feature_rows:

        matrix.append(
            [
                row["avg_login_hour"],
                row["download_count"],
                row["total_download_mb"],
                row["unique_devices"],
                row["total_events"],
            ]
        )

    if not matrix:

        return np.empty(
            (0, len(FEATURE_NAMES))
        )

    return np.array(
        matrix,
        dtype=float
    )


# =========================================================
# Train Isolation Forest
# =========================================================

def train_isolation_forest(
    feature_rows,
    contamination: float = CONTAMINATION,
):
    """
    Train an Isolation Forest model using daily
    employee behavioral features.
    """

    if len(feature_rows) < 10:

        raise ValueError(
            "At least 10 daily feature rows are required "
            "to train the Isolation Forest model."
        )

    X = create_feature_matrix(
        feature_rows
    )

    model = IsolationForest(
        n_estimators=N_ESTIMATORS,
        contamination=contamination,
        random_state=RANDOM_STATE,
    )

    model.fit(X)

    return model


# =========================================================
# Save model
# =========================================================

def save_model(model):
    """
    Save the trained Isolation Forest model.
    """

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_PATH
    )

    return str(
        MODEL_PATH
    )


# =========================================================
# Load model
# =========================================================

def load_model():
    """
    Load the previously trained Isolation Forest model.
    """

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}"
        )

    return joblib.load(
        MODEL_PATH
    )


# =========================================================
# Detect anomalies
# =========================================================

def detect_ml_anomalies(
    model,
    feature_rows,
):
    """
    Calculate Isolation Forest scores and predictions.

    predict():
        1  -> normal
       -1  -> anomaly

    decision_function():
        Higher -> more normal
        Lower  -> more anomalous
    """

    if not feature_rows:

        return []

    X = create_feature_matrix(
        feature_rows
    )

    predictions = model.predict(
        X
    )

    scores = model.decision_function(
        X
    )

    results = []

    for row, prediction, score in zip(
        feature_rows,
        predictions,
        scores
    ):

        result = {
            **row,
            "prediction": int(
                prediction
            ),
            "ml_score": float(
                score
            ),
            "is_anomaly": (
                prediction == -1
            ),
        }

        results.append(
            result
        )

    return results


# =========================================================
# Save ML anomalies
# =========================================================

def save_ml_anomalies(results):
    """
    Save detected ML anomalies to MongoDB.

    Existing ML anomaly records generated by this
    training run are cleared first to avoid duplicates.
    """

    ml_anomalies_collection.delete_many(
        {
            "generated_by": "isolation_forest_v1"
        }
    )

    documents = []

    for result in results:

        if not result["is_anomaly"]:
            continue

        # MongoDB/PyMongo does not directly encode
        # Python datetime.date objects.
        # Convert the date to a BSON-compatible datetime.
        anomaly_date = result["date"]

        if hasattr(anomaly_date, "year"):
            anomaly_date = datetime(
                anomaly_date.year,
                anomaly_date.month,
                anomaly_date.day,
            )

        document = {
            "employee_id": result["employee_id"],
            "date": anomaly_date,
            "features": {
                "avg_login_hour": float(
                    result["avg_login_hour"]
                ),
                "download_count": int(
                    result["download_count"]
                ),
                "total_download_mb": float(
                    result["total_download_mb"]
                ),
                "unique_devices": int(
                    result["unique_devices"]
                ),
                "total_events": int(
                    result["total_events"]
                ),
            },
            "ml_score": float(
                result["ml_score"]
            ),
            "prediction": int(
                result["prediction"]
            ),
            "detected_at": datetime.utcnow(),
            "generated_by": "isolation_forest_v1",
        }

        documents.append(document)

    if documents:

        ml_anomalies_collection.insert_many(
            documents
        )

    return documents


# =========================================================
# Complete ML pipeline
# =========================================================

def run_ml_anomaly_pipeline(
    days_back: int = 90,
    contamination: float = CONTAMINATION,
):
    """
    Complete Day 17–18 ML anomaly detection pipeline.

    Steps:
    1. Extract recent activity logs.
    2. Build daily behavioral features.
    3. Train Isolation Forest.
    4. Save model.
    5. Calculate anomaly scores.
    6. Save anomalies to MongoDB.
    """

    print("\n========== ML ANOMALY PIPELINE ==========")

    # -----------------------------------------------------
    # Step 1: Build daily features
    # -----------------------------------------------------

    feature_rows = build_daily_features(
        days_back
    )

    print(
        "Daily feature rows:",
        len(feature_rows)
    )

    if not feature_rows:

        raise ValueError(
            "No activity data available "
            "for ML training."
        )

    # -----------------------------------------------------
    # Step 2: Train model
    # -----------------------------------------------------

    model = train_isolation_forest(
        feature_rows,
        contamination=contamination,
    )

    print(
        "Isolation Forest trained."
    )

    # -----------------------------------------------------
    # Step 3: Save model
    # -----------------------------------------------------

    model_path = save_model(
        model
    )

    print(
        "Model saved:",
        model_path
    )

    # -----------------------------------------------------
    # Step 4: Detect anomalies
    # -----------------------------------------------------

    results = detect_ml_anomalies(
        model,
        feature_rows,
    )

    anomaly_results = [
        result
        for result in results
        if result["is_anomaly"]
    ]

    print(
        "ML anomalies detected:",
        len(anomaly_results)
    )

    # -----------------------------------------------------
    # Step 5: Save anomalies
    # -----------------------------------------------------

    saved_anomalies = save_ml_anomalies(
        results
    )

    print(
        "ML anomalies saved:",
        len(saved_anomalies)
    )

    return {
        "feature_rows": feature_rows,
        "results": results,
        "anomalies": saved_anomalies,
        "model_path": model_path,
    }
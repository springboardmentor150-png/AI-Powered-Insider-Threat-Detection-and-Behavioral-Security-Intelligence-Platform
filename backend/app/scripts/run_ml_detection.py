from __future__ import annotations

from datetime import datetime, timezone

from app.ml_features import build_feature_table
from app.ml_anomaly import train_anomaly_model, score_anomalies
from app.mongo import mongo_db


# ---------------------------------------------------------------------------
# MongoDB Collection
# ---------------------------------------------------------------------------

# ML-based anomaly results are intentionally stored separately
# from rule-based anomalies.
ml_anomalies = mongo_db["ml_anomalies"]


# ---------------------------------------------------------------------------
# ML Configuration
# ---------------------------------------------------------------------------

# Selected after comparing:
# 0.02 -> 4 anomalies
# 0.05 -> 8 anomalies
# 0.10 -> 16 anomalies
CONTAMINATION = 0.05


# ---------------------------------------------------------------------------
# Save ML Anomalies
# ---------------------------------------------------------------------------

def save_ml_anomalies(scored_features):
    """
    Save Isolation Forest anomalies into the ml_anomalies collection.

    One document represents one employee-day.
    """

    anomaly_rows = scored_features[
        scored_features["is_anomaly"]
    ]

    saved_count = 0

    for _, row in anomaly_rows.iterrows():

        employee_code = str(
            row["employee_code"]
        )

        anomaly_date = str(
            row["date"]
        )

        document = {
            "employee_code": employee_code,
            "date": anomaly_date,
            "anomaly_score": float(
                row["anomaly_score"]
            ),
            "is_anomaly": bool(
                row["is_anomaly"]
            ),
            "features": {
                "avg_login_hour": float(
                    row["avg_login_hour"]
                ),
                "download_count": float(
                    row["download_count"]
                ),
                "total_download_mb": float(
                    row["total_download_mb"]
                ),
                "unique_devices": float(
                    row["unique_devices"]
                ),
                "total_events": float(
                    row["total_events"]
                ),
            },
            "detected_at": datetime.now(
                timezone.utc
            ),
        }

        ml_anomalies.update_one(
            {
                "employee_code": employee_code,
                "date": anomaly_date,
            },
            {
                "$set": document
            },
            upsert=True,
        )

        saved_count += 1

    return saved_count


# ---------------------------------------------------------------------------
# Main ML Detection Workflow
# ---------------------------------------------------------------------------

def main():

    print("BUILDING ML FEATURE TABLE")
    print("-------------------------")

    features = build_feature_table()

    print(
        "Feature rows:",
        len(features)
    )

    print()
    print("TRAINING ISOLATION FOREST")
    print("-------------------------")

    print(
        "Contamination:",
        CONTAMINATION
    )

    model = train_anomaly_model(
        features,
        contamination=CONTAMINATION,
    )

    print(
        "Model training complete."
    )

    print()
    print("SCORING EMPLOYEE-DAYS")
    print("---------------------")

    scored = score_anomalies(
        model,
        features,
    )

    anomaly_count = int(
        scored["is_anomaly"].sum()
    )

    print(
        "Total employee-days:",
        len(scored)
    )

    print(
        "ML anomalies detected:",
        anomaly_count
    )

    print()
    print("SAVING ML ANOMALIES")
    print("-------------------")

    saved_count = save_ml_anomalies(
        scored
    )

    print(
        "ML anomalies saved:",
        saved_count
    )

    print()
    print("TOP ML ANOMALIES")
    print("----------------")

    print(
        scored[
            scored["is_anomaly"]
        ][
            [
                "employee_code",
                "date",
                "anomaly_score",
                "avg_login_hour",
                "download_count",
                "total_download_mb",
                "unique_devices",
                "total_events",
            ]
        ].to_string(index=False)
    )


# ---------------------------------------------------------------------------
# Script Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()
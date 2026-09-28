from datetime import datetime
import pandas as pd
from sklearn.ensemble import IsolationForest
from .database import mongo_db

def build_feature_table():
    baselines = list(mongo_db["behavioral_baselines"].find())
    rows = {}
    for b in baselines:
        emp = b["employee_id"]
        rows.setdefault(emp, {"employee_id": emp})
        value = b.get("typical_value", 0)
        rows[emp][b["indicator"]] = value if isinstance(value, (int, float)) else 0
    return pd.DataFrame(rows.values()).fillna(0)

def train_anomaly_model():
    df = build_feature_table()
    if len(df) < 2:
        return df.assign(anomaly_score=0.0, is_outlier=False, is_anomaly=False)
    features = df.drop(columns=["employee_id"])
    model = IsolationForest(contamination=min(0.1, max(1 / len(df), 0.01)), random_state=42)
    model.fit(features)
    df["anomaly_score"] = model.decision_function(features)
    df["is_outlier"] = model.predict(features) == -1
    df["is_anomaly"] = df["is_outlier"]
    mongo = mongo_db["ml_anomalies"]
    for row in df.to_dict(orient="records"):
        mongo.update_one(
            {"employee_id": row["employee_id"]},
            {"$set": {
                "employee_id": row["employee_id"],
                "anomaly_score": float(row["anomaly_score"]),
                "is_outlier": bool(row["is_outlier"]),
                "is_anomaly": bool(row["is_anomaly"]),
                "detected_at": datetime.utcnow(),
            }},
            upsert=True,
        )
    return df[["employee_id", "anomaly_score", "is_outlier", "is_anomaly"]]

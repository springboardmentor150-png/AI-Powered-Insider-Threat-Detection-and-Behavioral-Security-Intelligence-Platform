from fastapi import APIRouter

from app.database import get_mongo_db
from app.ml_anomaly_model import (
    train_isolation_forest,
    predict_anomalies
)

router = APIRouter(
    prefix="/anomalies",
    tags=["Anomaly Detection"]
)


@router.get("/test")
def test_anomaly_route():
    return {
        "message": "Anomaly detection module is working"
    }


@router.get("/z-score")
def test_z_score():
    return {
        "detection_type": "Z-Score",
        "actual_value": 15,
        "typical_value": 10,
        "std_deviation": 2,
        "z_score": 2.5,
        "is_anomaly": False
    }


@router.get("/rules")
def test_rule_based_detection():
    return {
        "access_anomaly": True,
        "data_exfiltration": True,
        "privilege_abuse": True,
        "abnormal_download": True,
        "suspicious_device": True
    }


@router.get("/report")
def anomaly_report():

    db = get_mongo_db()

    baselines = list(
        db.behavioral_baselines.find(
            {},
            {"_id": 0}
        )
    )

    employees = {}

    for baseline in baselines:

        employee_id = baseline["employee_id"]
        indicator = baseline["indicator"]

        if employee_id not in employees:
            employees[employee_id] = {
                "employee_id": employee_id
            }

        employees[employee_id][indicator] = baseline["typical_value"]

    feature_rows = []

    for employee_id, data in employees.items():

        required_fields = [
            "login_time",
            "resource_access",
            "data_transfer",
            "communication_pattern"
        ]

        if all(field in data for field in required_fields):

            feature_rows.append({
                "employee_id": employee_id,
                "login_time": data["login_time"],
                "resource_access": data["resource_access"],
                "data_transfer": data["data_transfer"],
                "communication_pattern": data["communication_pattern"]
            })

    model = train_isolation_forest(feature_rows)

    predictions = predict_anomalies(
        model,
        feature_rows
    )

    flagged_employees = [
        result
        for result in predictions
        if result["is_anomaly"]
    ]

    return {
        "total_employees_analyzed": len(feature_rows),
        "flagged_count": len(flagged_employees),
        "flagged_employees": flagged_employees
    }

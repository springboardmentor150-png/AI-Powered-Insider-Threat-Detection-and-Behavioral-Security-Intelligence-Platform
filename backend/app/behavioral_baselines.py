from datetime import datetime, timezone
from .mongo_database import behavioral_baselines_collection


def create_behavioral_baseline(
    employee_id: int,
    average_daily_activities: float,
    common_action: str,
    common_resource: str | None = None
):
    baseline = {
        "employee_id": employee_id,
        "average_daily_activities": average_daily_activities,
        "common_action": common_action,
        "common_resource": common_resource,
        "created_at": datetime.now(timezone.utc)
    }

    # Check whether a baseline already exists
    existing = behavioral_baselines_collection.find_one(
        {"employee_id": employee_id}
    )

    if existing:
        behavioral_baselines_collection.update_one(
            {"employee_id": employee_id},
            {"$set": baseline}
        )

        return {
            "message": "Behavioral baseline updated successfully",
            "employee_id": employee_id
        }

    result = behavioral_baselines_collection.insert_one(baseline)

    return {
        "message": "Behavioral baseline created successfully",
        "baseline_id": str(result.inserted_id),
        "employee_id": employee_id
    }
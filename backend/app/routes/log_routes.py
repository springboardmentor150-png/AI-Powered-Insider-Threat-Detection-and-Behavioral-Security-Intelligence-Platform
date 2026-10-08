from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_current_user
from app.database import get_mongo_db

router = APIRouter(
    prefix="/logs",
    tags=["Activity Logs"]
)


@router.post("/ingest")
def ingest_log(
    log_data: dict,
    current_user=Depends(get_current_user)
):
    try:
        db = get_mongo_db()
        result = db.activity_logs.insert_one(log_data)

        return {
            "message": "Activity log ingested successfully",
            "log_id": str(result.inserted_id)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to store activity log: {str(e)}"
        )


@router.get("/")
def get_logs(
    current_user=Depends(get_current_user)
):
    try:
        db = get_mongo_db()

        logs = list(
            db.activity_logs.find(
                {},
                {"_id": 0}
            )
        )

        return logs

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to fetch activity logs: {str(e)}"
        )

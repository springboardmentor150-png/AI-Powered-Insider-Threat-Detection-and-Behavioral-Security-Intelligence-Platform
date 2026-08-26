from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .mongo import activity_logs
from .schemas import ActivityLogCreate


app = FastAPI(title="ITBIS API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "ITBIS backend is running"}


@app.post("/activity")
def create_activity(activity: ActivityLogCreate):
    document = activity.model_dump()
    document["timestamp"] = datetime.now(timezone.utc)

    result = activity_logs.insert_one(document)

    return {
        "message": "Activity logged successfully",
        "id": str(result.inserted_id),
    }
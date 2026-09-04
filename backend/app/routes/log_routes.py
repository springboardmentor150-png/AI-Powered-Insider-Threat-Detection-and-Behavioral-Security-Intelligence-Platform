from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user

router = APIRouter(
    prefix="/logs",
    tags=["Activity Logs"]
)


@router.get("/")
def get_logs(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return {
        "message": "Activity Log API is protected",
        "logged_in_user": current_user.email,
        "role": current_user.role
    }
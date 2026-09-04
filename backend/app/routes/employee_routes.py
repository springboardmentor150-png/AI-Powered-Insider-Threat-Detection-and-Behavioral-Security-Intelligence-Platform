from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user

router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)


@router.get("/")
def get_employees(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return {
        "message": "Employee API is protected",
        "logged_in_user": current_user.email,
        "role": current_user.role
    }
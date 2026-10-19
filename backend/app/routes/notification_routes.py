from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Notification, User
from app.schemas import NotificationResponse
from app.security import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=List[NotificationResponse])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Fetch user notifications or all recent SOC alerts
    user = db.query(User).filter(User.email == current_user.get("sub")).first()
    if user:
        notifs = db.query(Notification).filter(
            Notification.user_id == user.id
        ).order_by(Notification.created_at.desc()).limit(20).all()
    else:
        notifs = db.query(Notification).order_by(Notification.created_at.desc()).limit(20).all()

    return notifs


@router.patch("/{notif_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notif_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification {notif_id} not found"
        )
    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return notif


@router.patch("/mark-all-read")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = db.query(User).filter(User.email == current_user.get("sub")).first()
    if user:
        db.query(Notification).filter(Notification.user_id == user.id, Notification.is_read == False).update({"is_read": True})
        db.commit()
    return {"message": "All notifications marked as read."}

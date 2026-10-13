from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Alert

router = APIRouter(prefix="/alerts", tags=["Alert Management"])

@router.get("")
def list_alerts(db: Session = Depends(get_db)):
    return db.query(Alert).order_by(Alert.id.desc()).all()

@router.post("/{alert_id}/assign")
def assign_alert(alert_id: int, analyst_user_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.assigned_to = analyst_user_id
    alert.status = "assigned"
    db.commit()
    return {"message": f"Alert {alert_id} assigned", "status": alert.status}

@router.patch("/{alert_id}/resolve")
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = "resolved"
    db.commit()
    return {"message": f"Alert {alert_id} resolved", "status": alert.status}

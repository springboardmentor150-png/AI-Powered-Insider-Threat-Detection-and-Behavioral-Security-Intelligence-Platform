from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import Notification, User, Alert

def notify_on_critical_alert(alert: Alert, db: Session) -> int:
    """
    Creates in-app Notification records for active analysts/managers/admins
    whenever an alert with 'critical' severity is created or escalated.
    Returns the count of notifications created.
    """
    if not alert or str(getattr(alert, "severity", "")).lower() != "critical":
        return 0

    users = db.query(User).filter(
        User.role.in_(["admin", "security_manager", "security_analyst", "soc_engineer"])
    ).all()

    title = f"CRITICAL ALERT: {alert.title or 'Insider Threat Detected'}"
    msg = alert.message or f"Critical security alert on employee ID {alert.employee_id}. Immediate review required."
    created_count = 0

    if not users:
        notif = Notification(
            user_id=None,
            alert_id=alert.id,
            title=title,
            message=msg,
            is_read=False,
            created_at=datetime.now(timezone.utc),
        )
        db.add(notif)
        created_count += 1
    else:
        for u in users:
            notif = Notification(
                user_id=u.id,
                alert_id=alert.id,
                title=title,
                message=msg,
                is_read=False,
                created_at=datetime.now(timezone.utc),
            )
            db.add(notif)
            created_count += 1

    try:
        db.commit()
    except Exception:
        db.rollback()
        return 0

    return created_count

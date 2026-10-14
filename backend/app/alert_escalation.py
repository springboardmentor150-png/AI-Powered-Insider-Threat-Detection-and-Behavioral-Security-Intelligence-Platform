
"""Escalate unresolved ITBIS alerts after severity-based thresholds."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import Alert


IST = timezone(timedelta(hours=5, minutes=30))

ESCALATION_THRESHOLDS_MINUTES = {
    "critical": 15,
    "high": 30,
    "medium": 60,
}


def _as_utc(value: datetime) -> datetime:
    """Convert a database timestamp to UTC.

    PostgreSQL's current session timezone is Asia/Calcutta.
    Naive timestamps are therefore interpreted as IST.
    """
    if value.tzinfo is None:
        value = value.replace(tzinfo=IST)

    return value.astimezone(timezone.utc)


def escalate_overdue_alerts(db: Session) -> dict:
    """Escalate only unresolved alerts past their severity threshold."""

    now = datetime.now(timezone.utc)

    eligible_alerts = (
        db.query(Alert)
        .filter(
            Alert.status.in_(["open", "assigned", "escalated"]),
            Alert.resolved_at.is_(None),
        )
        .all()
    )

    escalated_count = 0
    skipped_not_overdue = 0
    skipped_low_severity = 0

    try:
        for alert in eligible_alerts:
            severity = (alert.severity or "").lower()
            threshold = ESCALATION_THRESHOLDS_MINUTES.get(severity)

            if threshold is None:
                skipped_low_severity += 1
                continue

            created_at = _as_utc(alert.created_at)
            overdue_at = created_at + timedelta(minutes=threshold)

            # Never escalate an alert before its deadline.
            if now < overdue_at:
                skipped_not_overdue += 1
                continue

            # Escalate only once; repeated calls must not reset the timestamp.
            if alert.escalation_level == 0:
                alert.escalation_level = 1
                alert.escalated_at = now
                alert.status = "escalated"
                escalated_count += 1

        db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "checked_alerts": len(eligible_alerts),
        "escalated_alerts": escalated_count,
        "skipped_not_overdue": skipped_not_overdue,
        "skipped_low_severity": skipped_low_severity,
        "thresholds_minutes": ESCALATION_THRESHOLDS_MINUTES,
    }

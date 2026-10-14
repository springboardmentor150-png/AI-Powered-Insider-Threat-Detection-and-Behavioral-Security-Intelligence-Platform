"""
ITBIS Alert Escalation Engine.

Day 28:
- Escalate stale alerts based on severity
- Use different thresholds for different severities
- Mark escalated_at timestamp
- Upgrade escalated alerts to critical
"""

from datetime import datetime, timedelta

from app.models import Alert


# =========================================================
# Escalation Thresholds
# =========================================================

ESCALATION_THRESHOLDS_HOURS = {
    "critical": 2,
    "high": 8,
    "medium": 24,
}


# =========================================================
# Escalate Stale Alerts
# =========================================================

def escalate_stale_alerts(db):
    """
    Find open alerts that have exceeded their severity-specific
    escalation threshold.

    Escalated alerts:
    - status -> escalated
    - severity -> critical
    - escalated_at -> current UTC time

    Returns:
        List of escalated alert IDs.
    """

    escalated = []

    now = datetime.utcnow()

    for severity, hours in ESCALATION_THRESHOLDS_HOURS.items():

        cutoff = now - timedelta(hours=hours)

        stale_alerts = (
            db.query(Alert)
            .filter(
                Alert.status == "open",
                Alert.severity == severity,
                Alert.created_at < cutoff,
            )
            .all()
        )

        for alert in stale_alerts:

            alert.status = "escalated"

            # Every escalated alert becomes critical.
            alert.severity = "critical"

            # Record exactly when escalation happened.
            alert.escalated_at = now

            escalated.append(alert.id)

    db.commit()

    return escalated
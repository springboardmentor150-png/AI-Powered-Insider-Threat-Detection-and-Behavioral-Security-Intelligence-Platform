"""
ITBIS Enterprise Audit Logging Service (Milestone 4: Day 31-32)
Records immutable forensic audit records for compliance, governance, and traceability.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models import AuditLog, User

logger = logging.getLogger("itbis.audit")


def log_action(
    db: Session,
    user_id: Optional[int],
    action: str,
    details: str,
    user_email: Optional[str] = None,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
) -> AuditLog:
    """
    Persists an audit log entry for critical and sensitive operations:
    - Alert assignment
    - Incident creation and resolution
    - Operator account creation / role modifications
    - Evidence additions
    """
    resolved_email = user_email
    if not resolved_email and user_id:
        try:
            u = db.query(User).filter(User.id == user_id).first()
            if u and u.email:
                resolved_email = u.email
        except Exception:
            pass
    if not resolved_email:
        resolved_email = f"user_{user_id or 0}@itbis.cyber"

    audit_entry = AuditLog(
        user_id=user_id,
        user_email=resolved_email,
        action=action,
        details=details,
        target_type=target_type or "OPERATIONAL",
        target_id=str(target_id) if target_id else None,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(audit_entry)
    try:
        db.commit()
        db.refresh(audit_entry)
    except Exception as e:
        logger.error("Failed to commit audit log entry: %s", e)
        db.rollback()
    return audit_entry

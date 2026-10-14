"""
ITBIS Platform Audit Trail Logger
Logs platform actions, user operations, and investigation activities for compliance & SOC 2 audit readiness.
"""

from typing import Any
from sqlalchemy.orm import Session
from .models import AuditLog


def record_audit_log(
    db: Session,
    user: dict[str, Any] | None,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    details: str | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    """
    Persist an audit log record in PostgreSQL.
    """
    user_id = None
    user_email = "system"

    if user:
        if isinstance(user, dict):
            sub = user.get("sub")
            if sub and str(sub).isdigit():
                user_id = int(sub)
            user_email = user.get("email") or str(sub)
        elif hasattr(user, "id"):
            user_id = user.id
            user_email = getattr(user, "email", str(user.id))

    audit_entry = AuditLog(
        user_id=user_id,
        user_email=user_email,
        action=action.upper(),
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id is not None else None,
        details=details,
        ip_address=ip_address,
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    return audit_entry

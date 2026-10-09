from sqlalchemy.orm import Session
from app.models import AuditLog

def log_audit(db: Session, actor_id: int, action: str, target: str, metadata_info: str = ""):
    audit_entry = AuditLog(
        actor_id=actor_id,
        action=action,
        target=target,
        metadata_info=metadata_info
    )
    db.add(audit_entry)
    db.commit()

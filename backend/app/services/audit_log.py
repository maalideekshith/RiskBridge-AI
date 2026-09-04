from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    merchant_id: int,
    user_id: int | None,
    action: str,
    description: str,
    entity_type: str | None = None,
    entity_id: int | None = None,
) -> AuditLog:
    if not action.strip():
        raise ValueError("action cannot be empty")

    if not description.strip():
        raise ValueError("description cannot be empty")

    audit_log = AuditLog(
        merchant_id=merchant_id,
        user_id=user_id,
        action=action.strip().upper(),
        entity_type=entity_type,
        entity_id=entity_id,
        description=description.strip(),
        created_at=datetime.now(timezone.utc),
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log
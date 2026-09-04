from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse
from app.services.audit_log import create_audit_log

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)
@router.post("/onboarding-completed", response_model=AuditLogResponse)
def record_onboarding_completed(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    merchant = current_user.merchant

    if merchant is None:
        raise HTTPException(
            status_code=400,
            detail="No merchant profile found for this user",
        )

    return create_audit_log(
        db=db,
        merchant_id=merchant.id,
        user_id=current_user.id,
        action="ONBOARDING_COMPLETED",
        entity_type="merchant",
        entity_id=merchant.id,
        description="Merchant onboarding completed successfully",
    )

@router.get(
    "/{merchant_id}",
    response_model=list[AuditLogResponse],
)
def get_audit_logs(
    merchant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    merchant = current_user.merchant

    if merchant is None:
        raise HTTPException(
            status_code=400,
            detail="No merchant profile found for this user",
        )

    if merchant.id != merchant_id:
        raise HTTPException(
            status_code=403,
            detail="You can only access your own audit logs",
        )

    return (
        db.query(AuditLog)
        .filter(
            AuditLog.merchant_id == merchant_id,
        )
        .order_by(
            AuditLog.created_at.desc(),
        )
        .all()
    )
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models.merchant import Merchant
from app.models.payment import Payment
from app.models.refund import Refund
from app.models.user import User
from app.schemas.refund import (
    RefundCreate,
    RefundResponse,
)
from app.services.kafka import kafka_producer


router = APIRouter(
    prefix="/payments",
    tags=["Refunds"],
)


@router.post(
    "/{payment_id}/refunds",
    response_model=RefundResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_refund(
    payment_id: int,
    data: RefundCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Find the payment first
    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    # 2. Verify that the payment belongs to a merchant
    # owned by the authenticated user
    merchant = (
        db.query(Merchant)
        .filter(
            Merchant.id == payment.merchant_id,
            Merchant.user_id == current_user.id,
        )
        .first()
    )

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this payment",
        )

    # 3. Prevent duplicate refund references
    existing = (
        db.query(Refund)
        .filter(
            Refund.refund_reference == data.refund_reference
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refund reference already exists",
        )

    # 4. Prevent refunding more than the payment amount
    if data.amount > payment.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refund amount cannot exceed payment amount",
        )

    # 5. Create refund
    refund = Refund(
        payment_id=payment_id,
        **data.model_dump(),
    )

    db.add(refund)
    db.commit()
    db.refresh(refund)

    # 6. Publish refund event to Kafka
    refund_event = {
        "event_type": "refund.created",
        "refund_id": refund.id,
        "payment_id": refund.payment_id,
        "refund_reference": refund.refund_reference,
        "amount": str(refund.amount),
        "status": refund.status,
        "reason": refund.reason,
        "created_at": refund.created_at.isoformat(),
    }

    kafka_producer.publish(
        topic="refund-events",
        event=refund_event,
    )

    return refund


@router.get(
    "/{payment_id}/refunds",
    response_model=list[RefundResponse],
)
def list_refunds(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Find the payment first
    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    # 2. Verify ownership through the merchant
    merchant = (
        db.query(Merchant)
        .filter(
            Merchant.id == payment.merchant_id,
            Merchant.user_id == current_user.id,
        )
        .first()
    )

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this payment",
        )

    # 3. Return refunds for the payment
    return (
        db.query(Refund)
        .filter(Refund.payment_id == payment_id)
        .order_by(Refund.created_at.desc())
        .all()
    )
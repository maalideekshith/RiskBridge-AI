from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models.dispute import Dispute
from app.models.merchant import Merchant
from app.models.payment import Payment
from app.models.user import User
from app.schemas.dispute import (
    DisputeCreate,
    DisputeResponse,
)
from app.services.kafka import kafka_producer


router = APIRouter(
    prefix="/payments",
    tags=["Disputes"],
)


@router.post(
    "/{payment_id}/disputes",
    response_model=DisputeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_dispute(
    payment_id: int,
    data: DisputeCreate,
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

    # 2. Find the merchant associated with the payment
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

    # 3. Prevent duplicate dispute references
    existing = (
        db.query(Dispute)
        .filter(
            Dispute.dispute_reference
            == data.dispute_reference
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dispute reference already exists",
        )

    # 4. Prevent dispute amount from exceeding payment amount
    if data.amount > payment.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dispute amount cannot exceed payment amount",
        )

    # 5. Create dispute
    dispute = Dispute(
        payment_id=payment_id,
        **data.model_dump(),
    )

    db.add(dispute)
    db.commit()
    db.refresh(dispute)

    # 6. Publish dispute event to Kafka
    dispute_event = {
        "event_type": "dispute.created",
        "dispute_id": dispute.id,
        "payment_id": dispute.payment_id,
        "dispute_reference": dispute.dispute_reference,
        "amount": str(dispute.amount),
        "status": dispute.status,
        "reason": dispute.reason,
        "created_at": dispute.created_at.isoformat(),
    }

    kafka_producer.publish(
        topic="dispute-events",
        event=dispute_event,
    )

    return dispute


@router.get(
    "/{payment_id}/disputes",
    response_model=list[DisputeResponse],
)
def list_disputes(
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

    # 2. Verify merchant ownership
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

    # 3. Return disputes for this payment
    return (
        db.query(Dispute)
        .filter(
            Dispute.payment_id == payment_id
        )
        .order_by(Dispute.created_at.desc())
        .all()
    )
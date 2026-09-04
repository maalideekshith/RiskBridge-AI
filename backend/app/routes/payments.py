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
from app.models.user import User
from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
)
from app.services.kafka import kafka_producer


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


def get_merchant(
    db: Session,
    merchant_id: int,
) -> Merchant:
    merchant = (
        db.query(Merchant)
        .filter(Merchant.id == merchant_id)
        .first()
    )

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found",
        )

    return merchant


def verify_merchant_access(
    merchant: Merchant,
    current_user: User,
) -> None:
    if merchant.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this merchant",
        )


# ============================================================
# Get Payment
# ============================================================

@router.get(
    "/{merchant_id}/{payment_id}",
    response_model=PaymentResponse,
)
def get_payment(
    merchant_id: int,
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Find merchant
    merchant = get_merchant(db, merchant_id)

    # 2. Verify merchant ownership
    verify_merchant_access(merchant, current_user)

    # 3. Find payment belonging to this merchant
    payment = (
        db.query(Payment)
        .filter(
            Payment.id == payment_id,
            Payment.merchant_id == merchant_id,
        )
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return payment


# ============================================================
# Create Payment
# ============================================================

@router.post(
    "/{merchant_id}",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_payment(
    merchant_id: int,
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Find merchant
    merchant = get_merchant(db, merchant_id)

    # 2. Verify merchant ownership
    verify_merchant_access(merchant, current_user)

    # 3. Prevent duplicate payment references
    existing = (
        db.query(Payment)
        .filter(
            Payment.payment_reference == data.payment_reference
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment reference already exists",
        )

    # 4. Create payment
    payment = Payment(
        merchant_id=merchant_id,
        **data.model_dump(),
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    # 5. Publish payment event to Kafka
    payment_event = {
        "event_type": "payment.created",
        "payment_id": payment.id,
        "merchant_id": payment.merchant_id,
        "payment_reference": payment.payment_reference,
        "customer_reference": payment.customer_reference,
        "amount": str(payment.amount),
        "currency": payment.currency,
        "status": payment.status,
        "payment_method": payment.payment_method,
        "ip_address": payment.ip_address,
        "device_reference": payment.device_reference,
        "country": payment.country,
        "failure_reason": payment.failure_reason,
        "created_at": payment.created_at.isoformat(),
    }

    kafka_producer.publish(
        topic="payment-events",
        event=payment_event,
    )

    return payment
# ============================================================
# List Payments
# ============================================================

@router.get(
    "/{merchant_id}",
    response_model=list[PaymentResponse],
)
def list_payments(
    merchant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Find merchant
    merchant = get_merchant(db, merchant_id)

    # 2. Verify merchant ownership
    verify_merchant_access(merchant, current_user)

    # 3. Return payments belonging to merchant
    return (
        db.query(Payment)
        .filter(
            Payment.merchant_id == merchant_id
        )
        .order_by(Payment.created_at.desc())
        .all()
    )
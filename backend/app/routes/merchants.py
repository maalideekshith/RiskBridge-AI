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
from app.models.user import User
from app.schemas.merchant import (
    MerchantCreate,
    MerchantResponse,
)
from app.services.kafka import kafka_producer


router = APIRouter(
    prefix="/merchants",
    tags=["Merchants"],
)


@router.post(
    "/{user_id}",
    response_model=MerchantResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_merchant(
    user_id: int,
    data: MerchantCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only manage your own merchant profile",
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    existing = (
        db.query(Merchant)
        .filter(Merchant.user_id == user_id)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Merchant profile already exists",
        )

    merchant = Merchant(
        user_id=user_id,
        **data.model_dump(),
    )

    db.add(merchant)
    db.commit()
    db.refresh(merchant)

    # Publish merchant event to Kafka
    merchant_event = {
        "event_type": "merchant.created",
        "merchant_id": merchant.id,
        "user_id": merchant.user_id,
        "created_at": merchant.created_at.isoformat(),
    }

    kafka_producer.publish(
        topic="merchant-events",
        event=merchant_event,
    )

    return merchant


@router.get(
    "/{user_id}",
    response_model=MerchantResponse,
)
def get_merchant(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only access your own merchant profile",
        )

    merchant = (
        db.query(Merchant)
        .filter(Merchant.user_id == user_id)
        .first()
    )

    if not merchant:
        raise HTTPException(
            status_code=404,
            detail="Merchant profile not found",
        )

    return merchant
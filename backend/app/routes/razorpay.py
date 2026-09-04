from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User
from app.services.razorpay.connection import connect_razorpay
from app.services.razorpay.sync import sync_razorpay_data
from app.models.razorpay_connection import RazorpayConnection
from datetime import datetime, timezone
from app.services.audit_log import create_audit_log
router = APIRouter(
    prefix="/integrations/razorpay",
    tags=["Razorpay Integration"],
)


@router.post("/connect")
def connect_razorpay_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    merchant = current_user.merchant

    if merchant is None:
        raise HTTPException(
            status_code=400,
            detail="No merchant profile found for this user",
        )

    connection = connect_razorpay(
        db=db,
        merchant_id=merchant.id,
    )
    create_audit_log(
    db=db,
    merchant_id=merchant.id,
    user_id=current_user.id,
    action="RAZORPAY_CONNECTED",
    entity_type="razorpay_connection",
    entity_id=connection.id,
    description="Razorpay account connected successfully",
)

    return {
        "message": "Razorpay connected successfully",
        "merchant_id": merchant.id,
        "provider": connection.provider,
        "status": connection.status,
        "last_synced_at": connection.last_synced_at,
    }
@router.get("/status")
def get_razorpay_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    merchant = current_user.merchant

    if merchant is None:
        raise HTTPException(
            status_code=400,
            detail="No merchant profile found for this user",
        )

    connection = (
        db.query(RazorpayConnection)
        .filter(
            RazorpayConnection.merchant_id == merchant.id
        )
        .first()
    )

    if connection is None:
        return {
            "merchant_id": merchant.id,
            "provider": "razorpay",
            "status": "not_connected",
            "last_synced_at": None,
        }

    return {
        "merchant_id": merchant.id,
        "provider": connection.provider,
        "status": connection.status,
        "last_synced_at": connection.last_synced_at,
    }

@router.post("/sync")
def sync_razorpay(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    merchant = current_user.merchant

    if merchant is None:
        raise HTTPException(
            status_code=400,
            detail="No merchant profile found for this user",
        )

    result = sync_razorpay_data(
        db=db,
        merchant_id=merchant.id,
    )

    connection = (
        db.query(RazorpayConnection)
        .filter(
            RazorpayConnection.merchant_id == merchant.id
        )
        .first()
    )

    if connection is None:
        connection = RazorpayConnection(
            merchant_id=merchant.id,
            provider="razorpay",
            status="connected",
        )
        db.add(connection)

    connection.status = "connected"
    connection.last_synced_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(connection)

    create_audit_log(
    db=db,
    merchant_id=merchant.id,
    user_id=current_user.id,
    action="RAZORPAY_SYNCED",
    entity_type="razorpay_connection",
    entity_id=connection.id,
    description="Razorpay data synchronized successfully",
)

    return {
        "message": "Razorpay data synchronized successfully",
        "merchant_id": merchant.id,
        "last_synced_at": connection.last_synced_at,
        **result,
    }
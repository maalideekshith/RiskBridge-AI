import hashlib
import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db, settings
from app.models.user import User
from app.services.razorpay.webhook import (
    parse_webhook_event,
    process_webhook_event,
)


router = APIRouter(
    prefix="/integrations/razorpay",
    tags=["Razorpay Webhooks"],
)


@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str | None = Header(default=None),
    x_razorpay_event_id: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    if not x_razorpay_signature:
        raise HTTPException(
            status_code=400,
            detail="Missing Razorpay webhook signature",
        )
    if not x_razorpay_event_id:
     raise HTTPException(
        status_code=400,
        detail="Missing Razorpay webhook event ID",
    )

    raw_body = await request.body()

    expected_signature = hmac.new(
        settings.razorpay_key_secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(
        expected_signature,
        x_razorpay_signature,
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid Razorpay webhook signature",
        )

    try:
        payload = parse_webhook_event(raw_body)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    merchant_id = 3

    try:
        result = process_webhook_event(
    db=db,
    merchant_id=merchant_id,
    payload=payload,
    event_id=x_razorpay_event_id,
)
    except Exception:
        db.rollback()
        raise

    return {
        "message": "Razorpay webhook processed successfully",
        **result,
    }
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.razorpay_connection import RazorpayConnection


def connect_razorpay(
    db: Session,
    merchant_id: int,
) -> RazorpayConnection:
    connection = (
        db.query(RazorpayConnection)
        .filter(
            RazorpayConnection.merchant_id == merchant_id
        )
        .first()
    )

    if connection is None:
        connection = RazorpayConnection(
            merchant_id=merchant_id,
            provider="razorpay",
            status="connected",
            last_synced_at=None,
        )

        db.add(connection)
    else:
        connection.provider = "razorpay"
        connection.status = "connected"
        connection.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(connection)

    return connection
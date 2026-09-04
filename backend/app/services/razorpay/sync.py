from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models import Dispute, Payment, Refund
from app.services.razorpay.ingestion import (
    fetch_disputes,
    fetch_payments,
    fetch_refunds,
)
from app.services.razorpay.mapping import (
    map_dispute,
    map_payment,
    map_refund,
)


def sync_razorpay_data(db: Session, merchant_id: int) -> dict[str, int]:
    payments_created = 0
    payments_updated = 0
    refunds_created = 0
    refunds_updated = 0
    disputes_created = 0
    disputes_updated = 0

    # -------------------------
    # Payments
    # -------------------------
    skip = 0

    while True:
        response = fetch_payments(count=100, skip=skip)
        items = response.get("items", [])

        for item in items:
            data = map_payment(item)

            payment = (
                db.query(Payment)
                .filter(
                    Payment.payment_reference == data["payment_reference"]
                )
                .first()
            )

            if payment is None:
                payment = Payment(
                    merchant_id=merchant_id,
                    payment_reference=data["payment_reference"],
                    customer_reference=data["customer_reference"],
                    amount=data["amount"],
                    currency=data["currency"],
                    status=data["status"],
                    payment_method=data["payment_method"],
                    failure_reason=data["failure_reason"],
                    created_at=data["created_at"] or datetime.utcnow(),
                )
                db.add(payment)
                payments_created += 1
            else:
                payment.merchant_id = merchant_id
                payment.customer_reference = data["customer_reference"]
                payment.amount = data["amount"]
                payment.currency = data["currency"]
                payment.status = data["status"]
                payment.payment_method = data["payment_method"]
                payment.failure_reason = data["failure_reason"]

                if data["created_at"] is not None:
                    payment.created_at = data["created_at"]

                payments_updated += 1

        if len(items) < 100:
            break

        skip += 100

    db.commit()

    # -------------------------
    # Refunds
    # -------------------------
    skip = 0

    while True:
        response = fetch_refunds(count=100, skip=skip)
        items = response.get("items", [])

        for item in items:
            data = map_refund(item)

            payment = (
                db.query(Payment)
                .filter(
                    Payment.payment_reference == data["payment_reference"]
                )
                .first()
            )

            if payment is None or payment.merchant_id != merchant_id:
                continue

            refund = (
                db.query(Refund)
                .filter(
                    Refund.refund_reference == data["refund_reference"]
                )
                .first()
            )

            if refund is None:
                refund = Refund(
                    payment_id=payment.id,
                    refund_reference=data["refund_reference"],
                    amount=data["amount"],
                    status=data["status"],
                    reason=data["reason"],
                    created_at=data["created_at"] or datetime.utcnow(),
                )
                db.add(refund)
                refunds_created += 1
            else:
                refund.payment_id = payment.id
                refund.amount = data["amount"]
                refund.status = data["status"]
                refund.reason = data["reason"]

                if data["created_at"] is not None:
                    refund.created_at = data["created_at"]

                refunds_updated += 1

        if len(items) < 100:
            break

        skip += 100

    db.commit()

    # -------------------------
    # Disputes
    # -------------------------
    skip = 0

    while True:
        response = fetch_disputes(count=100, skip=skip)
        items = response.get("items", [])

        for item in items:
            data = map_dispute(item)

            payment = (
                db.query(Payment)
                .filter(
                    Payment.payment_reference == data["payment_reference"]
                )
                .first()
            )

            if payment is None or payment.merchant_id != merchant_id:
                continue

            dispute = (
                db.query(Dispute)
                .filter(
                    Dispute.dispute_reference == data["dispute_reference"]
                )
                .first()
            )

            if dispute is None:
                dispute = Dispute(
                    payment_id=payment.id,
                    dispute_reference=data["dispute_reference"],
                    amount=data["amount"],
                    status=data["status"],
                    reason=data["reason"],
                    evidence_status=data["evidence_status"],
                    created_at=data["created_at"] or datetime.utcnow(),
                )
                db.add(dispute)
                disputes_created += 1
            else:
                dispute.payment_id = payment.id
                dispute.amount = data["amount"]
                dispute.status = data["status"]
                dispute.reason = data["reason"]
                dispute.evidence_status = data["evidence_status"]

                if data["created_at"] is not None:
                    dispute.created_at = data["created_at"]

                disputes_updated += 1

        if len(items) < 100:
            break

        skip += 100

    db.commit()

    return {
        "payments_created": payments_created,
        "payments_updated": payments_updated,
        "refunds_created": refunds_created,
        "refunds_updated": refunds_updated,
        "disputes_created": disputes_created,
        "disputes_updated": disputes_updated,
    }
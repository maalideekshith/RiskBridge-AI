from datetime import datetime, timezone
from decimal import Decimal
from typing import Any


def razorpay_amount_to_decimal(amount: int | float | str | None) -> Decimal:
    if amount is None:
        return Decimal("0.00")

    return Decimal(str(amount)) / Decimal("100")


def razorpay_timestamp_to_datetime(timestamp: int | float | None) -> datetime | None:
    if timestamp is None:
        return None

    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def map_payment(payment: dict[str, Any]) -> dict[str, Any]:
    customer_reference = (
        payment.get("email")
        or payment.get("contact")
        or payment.get("customer_id")
        or "unknown"
    )

    return {
        "payment_reference": payment["id"],
        "customer_reference": str(customer_reference),
        "amount": razorpay_amount_to_decimal(payment.get("amount")),
        "currency": payment.get("currency", "INR"),
        "status": payment.get("status", "created"),
        "payment_method": payment.get("method", "unknown"),
        "failure_reason": (
            payment.get("error_description")
            or payment.get("error_reason")
            or payment.get("error_code")
        ),
        "created_at": razorpay_timestamp_to_datetime(
            payment.get("created_at")
        ),
    }


def map_refund(refund: dict[str, Any]) -> dict[str, Any]:
    return {
        "refund_reference": refund["id"],
        "payment_reference": refund["payment_id"],
        "amount": razorpay_amount_to_decimal(refund.get("amount")),
        "status": refund.get("status", "requested"),
        "reason": refund.get("notes"),
        "created_at": razorpay_timestamp_to_datetime(
            refund.get("created_at")
        ),
    }


def map_dispute(dispute: dict[str, Any]) -> dict[str, Any]:
    return {
        "dispute_reference": dispute["id"],
        "payment_reference": dispute["payment_id"],
        "amount": razorpay_amount_to_decimal(dispute.get("amount")),
        "status": dispute.get("status", "open"),
        "reason": dispute.get("reason", "Unknown"),
        "evidence_status": "missing",
        "created_at": razorpay_timestamp_to_datetime(
            dispute.get("created_at")
        ),
    }
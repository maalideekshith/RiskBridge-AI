from typing import Any

from app.services.razorpay.client import get_razorpay_client


def fetch_payments(count: int = 100, skip: int = 0) -> dict[str, Any]:
    client = get_razorpay_client()
    return client.payment.all(
        {
            "count": count,
            "skip": skip,
        }
    )


def fetch_refunds(count: int = 100, skip: int = 0) -> dict[str, Any]:
    client = get_razorpay_client()
    return client.refund.all(
        {
            "count": count,
            "skip": skip,
        }
    )


def fetch_disputes(count: int = 100, skip: int = 0) -> dict[str, Any]:
    client = get_razorpay_client()
    return client.dispute.all(
        {
            "count": count,
            "skip": skip,
        }
    )
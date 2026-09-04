from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.payment import Payment


AMOUNT_ANOMALY_MULTIPLIER = Decimal("3.0")


def detect_amount_anomaly(
    db: Session,
    payment: Payment,
) -> dict:
    """
    Detect whether a payment amount is unusually high
    compared with the merchant's historical payments.

    The current payment is excluded from the historical
    average to prevent it from influencing its own score.
    """

    historical_payments = (
        db.query(Payment)
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Payment.id != payment.id,
        )
        .all()
    )

    if not historical_payments:
        return {
            "signal": "amount_anomaly",
            "detected": False,
            "current_amount": payment.amount,
            "historical_average": None,
            "ratio": None,
            "reason": "Insufficient historical payment data",
        }

    historical_average = (
        sum(
            (p.amount for p in historical_payments),
            Decimal("0"),
        )
        / Decimal(len(historical_payments))
    )

    if historical_average <= 0:
        return {
            "signal": "amount_anomaly",
            "detected": False,
            "current_amount": payment.amount,
            "historical_average": historical_average,
            "ratio": None,
            "reason": "Historical average is not valid",
        }

    ratio = payment.amount / historical_average

    detected = ratio >= AMOUNT_ANOMALY_MULTIPLIER

    if detected:
        reason = (
            f"Payment amount is {ratio:.2f}x the "
            "merchant's historical average"
        )
    else:
        reason = (
            "Payment amount is within the expected "
            "historical range"
        )

    return {
        "signal": "amount_anomaly",
        "detected": detected,
        "current_amount": payment.amount,
        "historical_average": historical_average,
        "ratio": ratio,
        "reason": reason,
    }
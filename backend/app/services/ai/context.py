
from sqlalchemy.orm import Session

from app.models.merchant import Merchant
from app.models.payment import Payment
from app.models.refund import Refund
from app.models.dispute import Dispute
from app.models.risk_assessment import RiskAssessment


def gather_merchant_profile(
    db: Session,
    merchant_id: int,
) -> dict:
    """
    Gather merchant profile information for the AI context engine.
    """

    merchant = (
        db.query(Merchant)
        .filter(Merchant.id == merchant_id)
        .first()
    )

    if not merchant:
        raise ValueError(
            f"Merchant not found: {merchant_id}"
        )

    return {
        "merchant_id": merchant.id,
        "user_id": merchant.user_id,
        "business_name": merchant.business_name,
        "business_type": merchant.business_type,
        "website": merchant.website,
        "country": merchant.country,
        "currency": merchant.currency,
    }


def gather_transaction_history(
    db: Session,
    merchant_id: int,
) -> list[dict]:
    """
    Gather transaction history for the merchant.
    """

    payments = (
        db.query(Payment)
        .filter(Payment.merchant_id == merchant_id)
        .order_by(Payment.created_at.desc())
        .all()
    )

    return [
        {
            "payment_id": payment.id,
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
            "created_at": payment.created_at,
        }
        for payment in payments
    ]


def gather_refund_history(
    db: Session,
    merchant_id: int,
) -> list[dict]:
    """
    Gather refund history for the merchant.
    """

    refunds = (
        db.query(Refund)
        .join(Payment, Refund.payment_id == Payment.id)
        .filter(Payment.merchant_id == merchant_id)
        .order_by(Refund.created_at.desc())
        .all()
    )

    return [
        {
            "refund_id": refund.id,
            "payment_id": refund.payment_id,
            "refund_reference": refund.refund_reference,
            "amount": str(refund.amount),
            "status": refund.status,
            "reason": refund.reason,
            "created_at": refund.created_at,
        }
        for refund in refunds
    ]


def gather_dispute_history(
    db: Session,
    merchant_id: int,
) -> list[dict]:
    """
    Gather dispute history for the merchant.
    """

    disputes = (
        db.query(Dispute)
        .join(Payment, Dispute.payment_id == Payment.id)
        .filter(Payment.merchant_id == merchant_id)
        .order_by(Dispute.created_at.desc())
        .all()
    )

    return [
        {
            "dispute_id": dispute.id,
            "payment_id": dispute.payment_id,
            "dispute_reference": dispute.dispute_reference,
            "amount": str(dispute.amount),
            "status": dispute.status,
            "reason": dispute.reason,
            "evidence_status": dispute.evidence_status,
            "created_at": dispute.created_at,
        }
        for dispute in disputes
    ]


def gather_risk_signals(
    db: Session,
    merchant_id: int,
) -> list[dict]:
    """
    Gather previously generated risk assessments and signals
    for the merchant.
    """

    assessments = (
        db.query(RiskAssessment)
        .join(Payment, RiskAssessment.payment_id == Payment.id)
        .filter(Payment.merchant_id == merchant_id)
        .order_by(
            RiskAssessment.payment_id,
            RiskAssessment.created_at.desc(),
        )
        .all()
    )

    latest_by_payment = {}

    for assessment in assessments:
        if assessment.payment_id not in latest_by_payment:
            latest_by_payment[assessment.payment_id] = assessment

    assessments = list(latest_by_payment.values())

    return [
        {
            "assessment_id": assessment.id,
            "payment_id": assessment.payment_id,
            "risk_score": assessment.risk_score,
            "risk_category": assessment.risk_category,
            "signals": assessment.signals,
            "created_at": assessment.created_at,
        }
        for assessment in assessments
    ]

from sqlalchemy.orm import Session

from app.core.risk_scoring import calculate_risk_score
from app.models.payment import Payment
from app.models.refund import Refund
from app.models.dispute import Dispute
from app.models.risk_assessment import RiskAssessment


def _calculate_projected_score(
    baseline_signals: dict,
    refund_rate: float,
    dispute_rate: float,
    transaction_volume: int,
    high_value_transactions: int,
    failed_payments: int,
) -> float:
    """
    Calculate projected risk using the same scoring engine as the
    real Risk Engine.

    Scenario inputs modify merchant-level signals while all other
    signals remain at their latest real-assessment state.
    """

    signals = dict(baseline_signals)

    # Merchant-level scenario signals
    signals["refund_rate"] = refund_rate >= 20.0
    signals["dispute_rate"] = dispute_rate >= 10.0
    signals["transaction_volume"] = transaction_volume >= 100
    signals["high_value_transaction"] = (
        high_value_transactions >= 1
    )

    failed_payment_rate = (
        failed_payments / transaction_volume
        if transaction_volume > 0
        else 0
    )

    signals["failed_payment"] = (
        failed_payments >= 3
        or failed_payment_rate >= 0.5
    )

    result = calculate_risk_score(signals)

    return float(result["score"])


def simulate_risk(
    db: Session,
    merchant_id: int,
    refund_rate: float | None = None,
    dispute_rate: float | None = None,
    transaction_volume_change: float | None = None,
    high_value_transactions: int | None = None,
    failed_payments: int | None = None,
) -> dict:
    if merchant_id <= 0:
        raise ValueError("merchant_id must be greater than 0")

    # ---------------------------------------------------------
    # 1. Get merchant's real transaction data
    # ---------------------------------------------------------
    transactions = (
        db.query(Payment)
        .filter(Payment.merchant_id == merchant_id)
        .all()
    )

    refunds = (
        db.query(Refund)
        .join(Payment, Refund.payment_id == Payment.id)
        .filter(Payment.merchant_id == merchant_id)
        .all()
    )

    disputes = (
        db.query(Dispute)
        .join(Payment, Dispute.payment_id == Payment.id)
        .filter(Payment.merchant_id == merchant_id)
        .all()
    )

    current_transaction_volume = len(transactions)

    if current_transaction_volume > 0:
        current_refund_rate = (
            len(refunds) / current_transaction_volume
        ) * 100

        current_dispute_rate = (
            len(disputes) / current_transaction_volume
        ) * 100
    else:
        current_refund_rate = 0.0
        current_dispute_rate = 0.0

    # ---------------------------------------------------------
    # 2. Determine projected merchant values
    # ---------------------------------------------------------
    projected_refund_rate = (
        current_refund_rate
        if refund_rate is None
        else refund_rate
    )

    projected_dispute_rate = (
        current_dispute_rate
        if dispute_rate is None
        else dispute_rate
    )

    if transaction_volume_change is None:
        projected_transaction_volume = current_transaction_volume
    else:
        projected_transaction_volume = round(
            current_transaction_volume
            * (1 + transaction_volume_change / 100)
        )

    projected_transaction_volume = max(
        0,
        projected_transaction_volume,
    )
    projected_high_value_transactions = (
        0
        if high_value_transactions is None
        else high_value_transactions
    )

    projected_failed_payments = (
        0
        if failed_payments is None
        else failed_payments
    )

    # ---------------------------------------------------------
    # 3. Get latest real risk assessment
    # ---------------------------------------------------------
    latest_assessment = (
        db.query(RiskAssessment)
        .join(Payment, RiskAssessment.payment_id == Payment.id)
        .filter(Payment.merchant_id == merchant_id)
        .order_by(RiskAssessment.created_at.desc())
        .first()
    )

    # ---------------------------------------------------------
    # 4. Use latest real signals as simulator baseline
    # ---------------------------------------------------------
    if latest_assessment and isinstance(
        latest_assessment.signals,
        dict,
    ):
        baseline_signals = dict(latest_assessment.signals)
    else:
        baseline_signals = {
            "amount_anomaly": False,
            "transaction_velocity": False,
            "failed_payment": False,
            "transaction_frequency": False,
            "high_value_transaction": False,
            "refund_rate": current_refund_rate >= 20.0,
            "dispute_rate": current_dispute_rate >= 10.0,
            "refund_trend": False,
            "dispute_trend": False,
            "transaction_volume": current_transaction_volume >= 100,
            "device_ip_anomaly": False,
            "geographic_anomaly": False,
            "behavior_change": False,
        }

    # ---------------------------------------------------------
    # 5. Calculate CURRENT score using the real Risk Engine
    # ---------------------------------------------------------
    current_signals = dict(baseline_signals)

    current_signals["refund_rate"] = (
        current_refund_rate >= 20.0
    )

    current_signals["dispute_rate"] = (
        current_dispute_rate >= 10.0
    )

    current_signals["transaction_volume"] = (
        current_transaction_volume >= 100
    )

    current_result = calculate_risk_score(current_signals)
    current_risk_score = float(current_result["score"])

    # ---------------------------------------------------------
    # 6. Calculate PROJECTED score
    # ---------------------------------------------------------
    projected_risk_score = _calculate_projected_score(
    baseline_signals=baseline_signals,
    refund_rate=projected_refund_rate,
    dispute_rate=projected_dispute_rate,
    transaction_volume=projected_transaction_volume,
    high_value_transactions=projected_high_value_transactions,
    failed_payments=projected_failed_payments,
)

    # ---------------------------------------------------------
    # 7. Calculate change + status
    # ---------------------------------------------------------
    risk_change = round(
        projected_risk_score - current_risk_score,
        2,
    )

    if risk_change > 0:
        status = "increased"
    elif risk_change < 0:
        status = "decreased"
    else:
        status = "unchanged"

    return {
        "merchant_id": merchant_id,
        "current_risk_score": current_risk_score,
        "projected_risk_score": projected_risk_score,
        "risk_change": risk_change,
        "current_refund_rate": round(current_refund_rate, 2),
        "projected_refund_rate": round(projected_refund_rate, 2),
        "current_dispute_rate": round(current_dispute_rate, 2),
        "projected_dispute_rate": round(projected_dispute_rate, 2),
        "current_transaction_volume": current_transaction_volume,
        "projected_transaction_volume": projected_transaction_volume,
        "projected_high_value_transactions": ( projected_high_value_transactions),
        "projected_failed_payments": (projected_failed_payments),
        "status": status,
    }
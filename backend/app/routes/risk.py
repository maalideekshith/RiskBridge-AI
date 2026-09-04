from datetime import datetime, timedelta, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.core.security import get_current_user
from app.database import get_db
from app.models.merchant import Merchant
from app.models.payment import Payment
from app.models.user import User
from app.models.refund import Refund
from app.models.dispute import Dispute
from app.core.risk_scoring import calculate_risk_score
from app.core.risk_categories import categorize_risk
from app.models.risk_assessment import RiskAssessment
from app.services.risk_alerts import create_risk_alert
router = APIRouter(
    prefix="/payments",
    tags=["Risk Engine"],
)


def get_payment_with_access(
    payment_id: int,
    db: Session,
    current_user: User,
) -> Payment:
    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    merchant = (
        db.query(Merchant)
        .filter(
            Merchant.id == payment.merchant_id,
            Merchant.user_id == current_user.id,
        )
        .first()
    )

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this payment",
        )

    return payment


@router.get("/{payment_id}/risk/amount-anomaly")
def analyze_amount_anomaly(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = get_payment_with_access(
        payment_id,
        db,
        current_user,
    )

    historical_payments = (
        db.query(Payment)
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Payment.id != payment.id,
            Payment.created_at < payment.created_at,
        )
        .all()
    )

    if not historical_payments:
        return {
            "payment_id": payment.id,
            "signal": "amount_anomaly",
            "detected": False,
            "current_amount": payment.amount,
            "historical_average": None,
            "ratio": None,
            "reason": "Insufficient historical payment data",
        }

    historical_average = sum(
        p.amount for p in historical_payments
    ) / len(historical_payments)

    if historical_average == 0:
        return {
            "payment_id": payment.id,
            "signal": "amount_anomaly",
            "detected": False,
            "current_amount": payment.amount,
            "historical_average": historical_average,
            "ratio": None,
            "reason": "Historical average is zero",
        }

    ratio = float(
        payment.amount / historical_average
    )

    detected = ratio >= 3.0

    if detected:
        reason = (
            "Payment amount is significantly higher "
            "than the historical merchant average"
        )
    else:
        reason = (
            "Payment amount is within the normal "
            "historical range"
        )

    return {
        "payment_id": payment.id,
        "signal": "amount_anomaly",
        "detected": detected,
        "current_amount": payment.amount,
        "historical_average": historical_average,
        "ratio": ratio,
        "reason": reason,
    }


@router.get("/{payment_id}/risk/transaction-velocity")
def analyze_transaction_velocity(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = get_payment_with_access(
        payment_id,
        db,
        current_user,
    )

    # Velocity window: previous 10 minutes
    window_start = payment.created_at - timedelta(
        minutes=10
    )

    recent_payments = (
        db.query(Payment)
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Payment.customer_reference
            == payment.customer_reference,
            Payment.created_at >= window_start,
            Payment.created_at <= payment.created_at,
        )
        .all()
    )

    transaction_count = len(recent_payments)

    velocity_threshold = 5

    detected = transaction_count >= velocity_threshold

    if detected:
        reason = (
            f"High transaction velocity detected: "
            f"{transaction_count} transactions within "
            f"10 minutes"
        )
    else:
        reason = (
            f"Normal transaction velocity: "
            f"{transaction_count} transaction(s) within "
            f"10 minutes"
        )

    return {
        "payment_id": payment.id,
        "signal": "transaction_velocity",
        "detected": detected,
        "transaction_count": transaction_count,
        "window_minutes": 10,
        "threshold": velocity_threshold,
        "customer_reference": payment.customer_reference,
        "reason": reason,
    }
@router.get("/{payment_id}/risk/failed-payment")
def analyze_failed_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = get_payment_with_access(
        payment_id,
        db,
        current_user,
    )

    failed_statuses = {
        "failed",
        "declined",
        "cancelled",
        "canceled",
    }

    failed_payments = (
        db.query(Payment)
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Payment.customer_reference
            == payment.customer_reference,
            Payment.status.in_(failed_statuses),
        )
        .all()
    )

    failed_count = len(failed_payments)

    total_payments = (
        db.query(Payment)
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Payment.customer_reference
            == payment.customer_reference,
        )
        .count()
    )

    failure_rate = (
        failed_count / total_payments
        if total_payments > 0
        else 0
    )

    detected = failed_count >= 3 or failure_rate >= 0.5

    if detected:
        reason = (
            f"High failed-payment activity detected: "
            f"{failed_count} failed payment(s) out of "
            f"{total_payments} total payment(s)"
        )
    else:
        reason = (
            f"Normal failed-payment activity: "
            f"{failed_count} failed payment(s) out of "
            f"{total_payments} total payment(s)"
        )

    return {
        "payment_id": payment.id,
        "signal": "failed_payment",
        "detected": detected,
        "failed_payment_count": failed_count,
        "total_payment_count": total_payments,
        "failure_rate": round(failure_rate, 4),
        "reason": reason,
    }
@router.get("/{payment_id}/risk/transaction-frequency")
def analyze_transaction_frequency(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = get_payment_with_access(
        payment_id,
        db,
        current_user,
    )

    # Current 24-hour window
    current_window_start = (
        payment.created_at - timedelta(hours=24)
    )

    current_count = (
        db.query(Payment)
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Payment.customer_reference
            == payment.customer_reference,
            Payment.created_at >= current_window_start,
            Payment.created_at <= payment.created_at,
        )
        .count()
    )

    # Previous 24-hour window
    previous_window_end = current_window_start
    previous_window_start = (
        previous_window_end - timedelta(hours=24)
    )

    previous_count = (
        db.query(Payment)
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Payment.customer_reference
            == payment.customer_reference,
            Payment.created_at >= previous_window_start,
            Payment.created_at < previous_window_end,
        )
        .count()
    )

    if previous_count == 0:
        detected = current_count >= 10

        ratio = None

        if detected:
            reason = (
                f"Unusually high transaction frequency: "
                f"{current_count} transactions in the last 24 hours"
            )
        else:
            reason = (
                "Insufficient previous transaction history "
                "for frequency comparison"
            )

    else:
        ratio = current_count / previous_count

        detected = (
            current_count >= 10
            or ratio >= 3.0
        )

        if detected:
            reason = (
                f"Transaction frequency increased significantly: "
                f"{current_count} transactions in the current "
                f"24-hour window versus {previous_count} previously"
            )
        else:
            reason = (
                f"Transaction frequency is within the normal range: "
                f"{current_count} current versus "
                f"{previous_count} previous"
            )

    return {
        "payment_id": payment.id,
        "signal": "transaction_frequency",
        "detected": detected,
        "current_24h_count": current_count,
        "previous_24h_count": previous_count,
        "ratio": ratio,
        "window_hours": 24,
        "reason": reason,
    }
@router.get("/{payment_id}/risk/high-value")
def analyze_high_value_transaction(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = get_payment_with_access(
        payment_id,
        db,
        current_user,
    )

    historical_payments = (
        db.query(Payment)
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Payment.id != payment.id,
            Payment.created_at < payment.created_at,
        )
        .all()
    )

    if not historical_payments:
        return {
            "payment_id": payment.id,
            "signal": "high_value_transaction",
            "detected": False,
            "current_amount": payment.amount,
            "historical_average": None,
            "historical_maximum": None,
            "reason": "Insufficient historical payment data",
        }

    historical_average = (
        sum(p.amount for p in historical_payments)
        / len(historical_payments)
    )

    historical_maximum = max(
        p.amount for p in historical_payments
    )

    # High-value rule:
    # 3x historical average OR greater than historical maximum
    detected = (
        payment.amount >= historical_average * 3
        or payment.amount > historical_maximum
    )

    if detected:
        reason = (
            "Payment is significantly higher than "
            "the merchant's historical transaction values"
        )
    else:
        reason = (
            "Payment amount is within the historical "
            "transaction range"
        )

    return {
        "payment_id": payment.id,
        "signal": "high_value_transaction",
        "detected": detected,
        "current_amount": payment.amount,
        "historical_average": historical_average,
        "historical_maximum": historical_maximum,
        "reason": reason,
    }
# ============================================================
# PHASE 2 — MERCHANT SIGNALS
# ============================================================


# ------------------------------------------------------------
# Step 1 — Refund Rate Calculation
# ------------------------------------------------------------

@router.get("/{payment_id}/risk/refund-rate")
def analyze_refund_rate(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = get_payment_with_access(
        payment_id,
        db,
        current_user,
    )

    total_payments = (
        db.query(Payment)
        .filter(
            Payment.merchant_id == payment.merchant_id
        )
        .count()
    )

    total_refunds = (
        db.query(Refund)
        .join(
            Payment,
            Refund.payment_id == Payment.id,
        )
        .filter(
            Payment.merchant_id == payment.merchant_id
        )
        .count()
    )

    refunded_amount = (
        db.query(
            func.coalesce(
                func.sum(Refund.amount),
                0,
            )
        )
        .join(
            Payment,
            Refund.payment_id == Payment.id,
        )
        .filter(
            Payment.merchant_id == payment.merchant_id
        )
        .scalar()
    )

    total_payment_amount = (
        db.query(
            func.coalesce(
                func.sum(Payment.amount),
                0,
            )
        )
        .filter(
            Payment.merchant_id == payment.merchant_id
        )
        .scalar()
    )

    refund_rate = (
        total_refunds / total_payments
        if total_payments > 0
        else 0
    )

    refund_amount_rate = (
        float(refunded_amount / total_payment_amount)
        if total_payment_amount > 0
        else 0
    )

    detected = refund_rate >= 0.20

    if detected:
        reason = (
            f"High merchant refund rate: "
            f"{refund_rate:.2%} of payments have refunds"
        )
    else:
        reason = (
            f"Merchant refund rate is within the normal range: "
            f"{refund_rate:.2%}"
        )

    return {
        "payment_id": payment.id,
        "merchant_id": payment.merchant_id,
        "signal": "refund_rate",
        "detected": detected,
        "total_payments": total_payments,
        "total_refunds": total_refunds,
        "refund_rate": round(refund_rate, 4),
        "total_payment_amount": total_payment_amount,
        "refunded_amount": refunded_amount,
        "refund_amount_rate": round(refund_amount_rate, 4),
        "reason": reason,
    }


# ------------------------------------------------------------
# Step 2 — Dispute Rate Calculation
# ------------------------------------------------------------

@router.get("/{payment_id}/risk/dispute-rate")
def analyze_dispute_rate(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = get_payment_with_access(
        payment_id,
        db,
        current_user,
    )

    total_payments = (
        db.query(Payment)
        .filter(
            Payment.merchant_id == payment.merchant_id
        )
        .count()
    )

    total_disputes = (
        db.query(Dispute)
        .join(
            Payment,
            Dispute.payment_id == Payment.id,
        )
        .filter(
            Payment.merchant_id == payment.merchant_id
        )
        .count()
    )

    disputed_amount = (
        db.query(
            func.coalesce(
                func.sum(Dispute.amount),
                0,
            )
        )
        .join(
            Payment,
            Dispute.payment_id == Payment.id,
        )
        .filter(
            Payment.merchant_id == payment.merchant_id
        )
        .scalar()
    )

    total_payment_amount = (
        db.query(
            func.coalesce(
                func.sum(Payment.amount),
                0,
            )
        )
        .filter(
            Payment.merchant_id == payment.merchant_id
        )
        .scalar()
    )

    dispute_rate = (
        total_disputes / total_payments
        if total_payments > 0
        else 0
    )

    dispute_amount_rate = (
        float(disputed_amount / total_payment_amount)
        if total_payment_amount > 0
        else 0
    )

    detected = dispute_rate >= 0.10

    if detected:
        reason = (
            f"High merchant dispute rate: "
            f"{dispute_rate:.2%} of payments have disputes"
        )
    else:
        reason = (
            f"Merchant dispute rate is within the normal range: "
            f"{dispute_rate:.2%}"
        )

    return {
        "payment_id": payment.id,
        "merchant_id": payment.merchant_id,
        "signal": "dispute_rate",
        "detected": detected,
        "total_payments": total_payments,
        "total_disputes": total_disputes,
        "dispute_rate": round(dispute_rate, 4),
        "total_payment_amount": total_payment_amount,
        "disputed_amount": disputed_amount,
        "dispute_amount_rate": round(
            dispute_amount_rate,
            4,
        ),
        "reason": reason,
    }


# ------------------------------------------------------------
# Step 3 — Refund Trend Analysis
# ------------------------------------------------------------

@router.get("/{payment_id}/risk/refund-trend")
def analyze_refund_trend(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = get_payment_with_access(
        payment_id,
        db,
        current_user,
    )

    current_start = (
        payment.created_at - timedelta(days=30)
    )

    previous_start = (
        current_start - timedelta(days=30)
    )

    current_refunds = (
        db.query(Refund)
        .join(
            Payment,
            Refund.payment_id == Payment.id,
        )
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Refund.created_at >= current_start,
            Refund.created_at <= payment.created_at,
        )
        .count()
    )

    previous_refunds = (
        db.query(Refund)
        .join(
            Payment,
            Refund.payment_id == Payment.id,
        )
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Refund.created_at >= previous_start,
            Refund.created_at < current_start,
        )
        .count()
    )

    if previous_refunds == 0:
        detected = current_refunds >= 3
        change_ratio = None

        if detected:
            reason = (
                f"Refund activity increased: "
                f"{current_refunds} refunds in the current "
                f"30-day period"
            )
        else:
            reason = (
                "Insufficient previous refund history "
                "for trend comparison"
            )

    else:
        change_ratio = (
            current_refunds / previous_refunds
        )

        detected = change_ratio >= 2.0

        if detected:
            reason = (
                f"Refund activity has increased significantly: "
                f"{current_refunds} current refunds versus "
                f"{previous_refunds} previous refunds"
            )
        else:
            reason = (
                f"Refund activity is stable: "
                f"{current_refunds} current refunds versus "
                f"{previous_refunds} previous refunds"
            )

    return {
        "payment_id": payment.id,
        "merchant_id": payment.merchant_id,
        "signal": "refund_trend",
        "detected": detected,
        "current_30d_refunds": current_refunds,
        "previous_30d_refunds": previous_refunds,
        "change_ratio": change_ratio,
        "window_days": 30,
        "reason": reason,
    }


# ------------------------------------------------------------
# Step 4 — Dispute Trend Analysis
# ------------------------------------------------------------

@router.get("/{payment_id}/risk/dispute-trend")
def analyze_dispute_trend(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = get_payment_with_access(
        payment_id,
        db,
        current_user,
    )

    current_start = (
        payment.created_at - timedelta(days=30)
    )

    previous_start = (
        current_start - timedelta(days=30)
    )

    current_disputes = (
        db.query(Dispute)
        .join(
            Payment,
            Dispute.payment_id == Payment.id,
        )
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Dispute.created_at >= current_start,
            Dispute.created_at <= payment.created_at,
        )
        .count()
    )

    previous_disputes = (
        db.query(Dispute)
        .join(
            Payment,
            Dispute.payment_id == Payment.id,
        )
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Dispute.created_at >= previous_start,
            Dispute.created_at < current_start,
        )
        .count()
    )

    if previous_disputes == 0:
        detected = current_disputes >= 2
        change_ratio = None

        if detected:
            reason = (
                f"Dispute activity increased: "
                f"{current_disputes} disputes in the current "
                f"30-day period"
            )
        else:
            reason = (
                "Insufficient previous dispute history "
                "for trend comparison"
            )

    else:
        change_ratio = (
            current_disputes / previous_disputes
        )

        detected = change_ratio >= 2.0

        if detected:
            reason = (
                f"Dispute activity has increased significantly: "
                f"{current_disputes} current disputes versus "
                f"{previous_disputes} previous disputes"
            )
        else:
            reason = (
                f"Dispute activity is stable: "
                f"{current_disputes} current disputes versus "
                f"{previous_disputes} previous disputes"
            )

    return {
        "payment_id": payment.id,
        "merchant_id": payment.merchant_id,
        "signal": "dispute_trend",
        "detected": detected,
        "current_30d_disputes": current_disputes,
        "previous_30d_disputes": previous_disputes,
        "change_ratio": change_ratio,
        "window_days": 30,
        "reason": reason,
    }


# ------------------------------------------------------------
# Step 5 — Transaction Volume Anomaly
# ------------------------------------------------------------

@router.get("/{payment_id}/risk/transaction-volume")
def analyze_transaction_volume(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = get_payment_with_access(
        payment_id,
        db,
        current_user,
    )

    current_start = (
        payment.created_at - timedelta(days=7)
    )

    previous_start = (
        current_start - timedelta(days=7)
    )

    current_volume = (
        db.query(Payment)
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Payment.created_at >= current_start,
            Payment.created_at <= payment.created_at,
        )
        .count()
    )

    previous_volume = (
        db.query(Payment)
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Payment.created_at >= previous_start,
            Payment.created_at < current_start,
        )
        .count()
    )

    if previous_volume == 0:
        detected = current_volume >= 20
        change_ratio = None

        if detected:
            reason = (
                f"Unusually high transaction volume: "
                f"{current_volume} transactions in the "
                f"current 7-day period"
            )
        else:
            reason = (
                "Insufficient previous transaction volume "
                "for comparison"
            )

    else:
        change_ratio = (
            current_volume / previous_volume
        )

        detected = (
            change_ratio >= 3.0
            or current_volume >= 20
        )

        if detected:
            reason = (
                f"Transaction volume anomaly detected: "
                f"{current_volume} current transactions versus "
                f"{previous_volume} previous transactions"
            )
        else:
            reason = (
                f"Transaction volume is within the normal range: "
                f"{current_volume} current versus "
                f"{previous_volume} previous"
            )

    return {
        "payment_id": payment.id,
        "merchant_id": payment.merchant_id,
        "signal": "transaction_volume",
        "detected": detected,
        "current_7d_volume": current_volume,
        "previous_7d_volume": previous_volume,
        "change_ratio": change_ratio,
        "window_days": 7,
        "reason": reason,
    }
# ============================================================
# PHASE 3 — BEHAVIORAL SIGNALS
# STEP 1 — Customer Transaction History
# ============================================================

@router.get(
    "/{payment_id}/risk/customer-history",
)
def analyze_customer_transaction_history(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    merchant = (
        db.query(Merchant)
        .filter(
            Merchant.id == payment.merchant_id,
            Merchant.user_id == current_user.id,
        )
        .first()
    )

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this payment",
        )

    previous_payments = (
        db.query(Payment)
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Payment.customer_reference == payment.customer_reference,
            Payment.id != payment.id,
        )
        .order_by(Payment.created_at.desc())
        .limit(20)
        .all()
    )

    return {
        "payment_id": payment.id,
        "customer_reference": payment.customer_reference,
        "transaction_count": len(previous_payments),
        "transactions": [
            {
                "payment_id": item.id,
                "amount": str(item.amount),
                "currency": item.currency,
                "status": item.status,
                "payment_method": item.payment_method,
                "country": item.country,
                "created_at": item.created_at,
            }
            for item in previous_payments
        ],
    }
# ============================================================
# STEP 2 — Average Transaction Calculation
# ============================================================

@router.get(
    "/{payment_id}/risk/customer-average",
)
def analyze_customer_average_transaction(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    merchant = (
        db.query(Merchant)
        .filter(
            Merchant.id == payment.merchant_id,
            Merchant.user_id == current_user.id,
        )
        .first()
    )

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this payment",
        )

    previous_payments = (
        db.query(Payment)
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Payment.customer_reference == payment.customer_reference,
            Payment.id != payment.id,
        )
        .all()
    )

    if not previous_payments:
        return {
            "payment_id": payment.id,
            "customer_reference": payment.customer_reference,
            "current_amount": str(payment.amount),
            "historical_average": None,
            "transaction_count": 0,
            "reason": "Insufficient historical customer data",
        }

    total_amount = sum(
        item.amount for item in previous_payments
    )

    average_amount = (
        total_amount / len(previous_payments)
    )

    return {
        "payment_id": payment.id,
        "customer_reference": payment.customer_reference,
        "current_amount": str(payment.amount),
        "historical_average": str(
            round(average_amount, 2)
        ),
        "transaction_count": len(previous_payments),
        "reason": "Historical customer average calculated",
    }
# ============================================================
# STEP 3 — Device/IP Anomaly Simulation
# ============================================================

@router.get(
    "/{payment_id}/risk/device-ip-anomaly",
)
def analyze_device_ip_anomaly(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    merchant = (
        db.query(Merchant)
        .filter(
            Merchant.id == payment.merchant_id,
            Merchant.user_id == current_user.id,
        )
        .first()
    )

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this payment",
        )

    previous_payments = (
        db.query(Payment)
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Payment.customer_reference == payment.customer_reference,
            Payment.id != payment.id,
        )
        .all()
    )

    if not previous_payments:
        return {
            "payment_id": payment.id,
            "customer_reference": payment.customer_reference,
            "device_anomaly": False,
            "ip_anomaly": False,
            "detected": False,
            "reason": "Insufficient historical customer data",
        }

    historical_devices = {
        item.device_reference
        for item in previous_payments
        if item.device_reference
    }

    historical_ips = {
        item.ip_address
        for item in previous_payments
        if item.ip_address
    }

    device_anomaly = (
        payment.device_reference is not None
        and payment.device_reference not in historical_devices
    )

    ip_anomaly = (
        payment.ip_address is not None
        and payment.ip_address not in historical_ips
    )

    detected = device_anomaly or ip_anomaly

    return {
        "payment_id": payment.id,
        "customer_reference": payment.customer_reference,
        "current_device": payment.device_reference,
        "current_ip": payment.ip_address,
        "device_anomaly": device_anomaly,
        "ip_anomaly": ip_anomaly,
        "detected": detected,
        "reason": (
            "New device or IP detected"
            if detected
            else "Device and IP match historical behavior"
        ),
    }
# ============================================================
# STEP 4 — Geographic Anomaly Simulation
# ============================================================

@router.get(
    "/{payment_id}/risk/geographic-anomaly",
)
def analyze_geographic_anomaly(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    merchant = (
        db.query(Merchant)
        .filter(
            Merchant.id == payment.merchant_id,
            Merchant.user_id == current_user.id,
        )
        .first()
    )

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this payment",
        )

    previous_payments = (
        db.query(Payment)
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Payment.customer_reference == payment.customer_reference,
            Payment.id != payment.id,
        )
        .all()
    )

    if not previous_payments:
        return {
            "payment_id": payment.id,
            "customer_reference": payment.customer_reference,
            "current_country": payment.country,
            "geographic_anomaly": False,
            "detected": False,
            "reason": "Insufficient historical customer data",
        }

    historical_countries = {
        item.country
        for item in previous_payments
        if item.country
    }

    geographic_anomaly = (
        payment.country is not None
        and payment.country not in historical_countries
    )

    return {
        "payment_id": payment.id,
        "customer_reference": payment.customer_reference,
        "current_country": payment.country,
        "historical_countries": list(
            historical_countries
        ),
        "geographic_anomaly": geographic_anomaly,
        "detected": geographic_anomaly,
        "reason": (
            "New country detected"
            if geographic_anomaly
            else "Country matches historical behavior"
        ),
    }
# ============================================================
# STEP 5 — Customer Behavior Change Detection
# ============================================================

@router.get(
    "/{payment_id}/risk/behavior-change",
)
def analyze_customer_behavior_change(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    merchant = (
        db.query(Merchant)
        .filter(
            Merchant.id == payment.merchant_id,
            Merchant.user_id == current_user.id,
        )
        .first()
    )

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this payment",
        )

    previous_payments = (
        db.query(Payment)
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Payment.customer_reference == payment.customer_reference,
            Payment.id != payment.id,
        )
        .order_by(Payment.created_at.desc())
        .limit(20)
        .all()
    )

    if not previous_payments:
        return {
            "payment_id": payment.id,
            "customer_reference": payment.customer_reference,
            "behavior_changed": False,
            "signals": [],
            "reason": "Insufficient historical customer data",
        }

    signals = []

    # --------------------------------------------------------
    # Amount behavior
    # --------------------------------------------------------

    total_amount = sum(
        item.amount for item in previous_payments
    )

    average_amount = (
        total_amount / len(previous_payments)
    )

    if average_amount > 0:
        amount_ratio = (
            payment.amount / average_amount
        )

        if amount_ratio >= 2:
            signals.append("amount_significantly_above_average")

    # --------------------------------------------------------
    # Device behavior
    # --------------------------------------------------------

    historical_devices = {
        item.device_reference
        for item in previous_payments
        if item.device_reference
    }

    if (
        payment.device_reference
        and payment.device_reference not in historical_devices
    ):
        signals.append("new_device")

    # --------------------------------------------------------
    # IP behavior
    # --------------------------------------------------------

    historical_ips = {
        item.ip_address
        for item in previous_payments
        if item.ip_address
    }

    if (
        payment.ip_address
        and payment.ip_address not in historical_ips
    ):
        signals.append("new_ip")

    # --------------------------------------------------------
    # Geographic behavior
    # --------------------------------------------------------

    historical_countries = {
        item.country
        for item in previous_payments
        if item.country
    }

    if (
        payment.country
        and payment.country not in historical_countries
    ):
        signals.append("new_country")

    behavior_changed = len(signals) > 0

    return {
        "payment_id": payment.id,
        "customer_reference": payment.customer_reference,
        "behavior_changed": behavior_changed,
        "signal_count": len(signals),
        "signals": signals,
        "historical_transaction_count": len(
            previous_payments
        ),
        "historical_average": str(
            round(average_amount, 2)
        ),
        "current_amount": str(payment.amount),
        "reason": (
            "Customer behavior differs from historical pattern"
            if behavior_changed
            else "Customer behavior is consistent with historical pattern"
        ),
    }
# ============================================================
# PHASE 4 — RISK SCORE
# STEP 3 — Generate 0–100 Risk Score
# ============================================================

@router.get(
    "/{payment_id}/risk/score",
)
def generate_risk_score(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # --------------------------------------------------------
    # 1. Find payment
    # --------------------------------------------------------

    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    # --------------------------------------------------------
    # 2. Verify merchant ownership
    # --------------------------------------------------------

    merchant = (
        db.query(Merchant)
        .filter(
            Merchant.id == payment.merchant_id,
            Merchant.user_id == current_user.id,
        )
        .first()
    )

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this payment",
        )

    # --------------------------------------------------------
    # 3. Historical customer payments
    # --------------------------------------------------------

    previous_payments = (
        db.query(Payment)
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Payment.customer_reference
            == payment.customer_reference,
            Payment.id != payment.id,
        )
        .all()
    )

    # --------------------------------------------------------
    # 4. Amount anomaly
    # --------------------------------------------------------

    amount_anomaly = False

    if previous_payments:
        total_amount = sum(
            item.amount
            for item in previous_payments
        )

        average_amount = (
            total_amount / len(previous_payments)
        )

        if average_amount > 0:
            amount_ratio = (
                payment.amount / average_amount
            )

            amount_anomaly = amount_ratio >= 2

    # --------------------------------------------------------
    # 5. Transaction velocity
    # --------------------------------------------------------

    velocity_payments = (
        db.query(Payment)
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Payment.customer_reference
            == payment.customer_reference,
            Payment.id != payment.id,
            Payment.created_at >= (
                payment.created_at
                - timedelta(minutes=10)
            ),
        )
        .count()
    )

    transaction_velocity = (
        velocity_payments >= 5
    )

    # --------------------------------------------------------
    # 6. Failed payment
    # --------------------------------------------------------

    failed_payment = (
        payment.status.lower()
        in {
            "failed",
            "failure",
            "declined",
        }
    )

    # --------------------------------------------------------
    # 7. Transaction frequency
    # --------------------------------------------------------

    frequency_count = (
        db.query(Payment)
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Payment.customer_reference
            == payment.customer_reference,
            Payment.id != payment.id,
            Payment.created_at >= (
                payment.created_at
                - timedelta(hours=1)
            ),
        )
        .count()
    )

    transaction_frequency = (
        frequency_count >= 10
    )

    # --------------------------------------------------------
    # 8. High-value transaction
    # --------------------------------------------------------

    high_value_transaction = False

    if previous_payments:
        amounts = [
            item.amount
            for item in previous_payments
        ]

        average = (
            sum(amounts) / len(amounts)
        )

        high_value_transaction = (
            payment.amount >= average * 3
        )
    else:
        high_value_transaction = (
            payment.amount >= 100000
        )

    # --------------------------------------------------------
    # 9. Refund rate
    # --------------------------------------------------------

    total_payments = (
        db.query(Payment)
        .filter(
            Payment.merchant_id == payment.merchant_id
        )
        .count()
    )

    total_refunds = (
        db.query(Refund)
        .join(
            Payment,
            Refund.payment_id == Payment.id,
        )
        .filter(
            Payment.merchant_id == payment.merchant_id
        )
        .count()
    )

    refund_rate = (
        total_refunds / total_payments
        if total_payments > 0
        else 0
    )

    refund_rate_signal = (
        refund_rate >= 0.20
    )

    # --------------------------------------------------------
    # 10. Dispute rate
    # --------------------------------------------------------

    total_disputes = (
        db.query(Dispute)
        .join(
            Payment,
            Dispute.payment_id == Payment.id,
        )
        .filter(
            Payment.merchant_id == payment.merchant_id
        )
        .count()
    )

    dispute_rate = (
        total_disputes / total_payments
        if total_payments > 0
        else 0
    )

    dispute_rate_signal = (
        dispute_rate >= 0.10
    )

    # --------------------------------------------------------
    # 11. Refund trend
    # --------------------------------------------------------

    recent_refunds = (
        db.query(Refund)
        .join(
            Payment,
            Refund.payment_id == Payment.id,
        )
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Refund.created_at >= (
                payment.created_at
                - timedelta(days=7)
            ),
        )
        .count()
    )

    refund_trend = (
        recent_refunds >= 5
    )

    # --------------------------------------------------------
    # 12. Dispute trend
    # --------------------------------------------------------

    recent_disputes = (
        db.query(Dispute)
        .join(
            Payment,
            Dispute.payment_id == Payment.id,
        )
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Dispute.created_at >= (
                payment.created_at
                - timedelta(days=7)
            ),
        )
        .count()
    )

    dispute_trend = (
        recent_disputes >= 3
    )

    # --------------------------------------------------------
    # 13. Transaction volume anomaly
    # --------------------------------------------------------

    recent_volume = (
        db.query(Payment)
        .filter(
            Payment.merchant_id == payment.merchant_id,
            Payment.created_at >= (
                payment.created_at
                - timedelta(days=1)
            ),
        )
        .count()
    )

    transaction_volume = (
        recent_volume >= 100
    )

    # --------------------------------------------------------
    # 14. Device/IP anomaly
    # --------------------------------------------------------

    historical_devices = {
        item.device_reference
        for item in previous_payments
        if item.device_reference
    }

    historical_ips = {
        item.ip_address
        for item in previous_payments
        if item.ip_address
    }

    device_anomaly = (
        payment.device_reference is not None
        and payment.device_reference
        not in historical_devices
    )

    ip_anomaly = (
        payment.ip_address is not None
        and payment.ip_address
        not in historical_ips
    )

    device_ip_anomaly = (
        device_anomaly or ip_anomaly
    )

    # --------------------------------------------------------
    # 15. Geographic anomaly
    # --------------------------------------------------------

    historical_countries = {
        item.country
        for item in previous_payments
        if item.country
    }

    geographic_anomaly = (
        payment.country is not None
        and payment.country
        not in historical_countries
        and len(previous_payments) > 0
    )

    # --------------------------------------------------------
    # 16. Customer behavior change
    # --------------------------------------------------------

    behavior_change_signals = []

    if amount_anomaly:
        behavior_change_signals.append(
            "amount"
        )

    if device_ip_anomaly:
        behavior_change_signals.append(
            "device_or_ip"
        )

    if geographic_anomaly:
        behavior_change_signals.append(
            "geography"
        )

    behavior_change = (
        len(behavior_change_signals) > 0
    )

    # --------------------------------------------------------
    # 17. Collect all signals
    # --------------------------------------------------------

    signals = {
        "amount_anomaly": amount_anomaly,
        "transaction_velocity": transaction_velocity,
        "failed_payment": failed_payment,
        "transaction_frequency": transaction_frequency,
        "high_value_transaction": high_value_transaction,

        "refund_rate": refund_rate_signal,
        "dispute_rate": dispute_rate_signal,
        "refund_trend": refund_trend,
        "dispute_trend": dispute_trend,
        "transaction_volume": transaction_volume,

        "device_ip_anomaly": device_ip_anomaly,
        "geographic_anomaly": geographic_anomaly,
        "behavior_change": behavior_change,
    }

    # --------------------------------------------------------
    # 18. Calculate score
    # --------------------------------------------------------

    result = calculate_risk_score(
        signals
    )
    risk_score = result["score"]

    risk_category = categorize_risk(
    risk_score)
    assessment = RiskAssessment(
    payment_id=payment.id,
    risk_score=risk_score,
    risk_category=risk_category,
    signals=result["signals"],
)

    db.add(assessment)
    db.commit()
    db.refresh(assessment)

# --------------------------------------------------------
# Create risk alert for elevated assessments
# --------------------------------------------------------

    create_risk_alert(
    db=db,
    assessment=assessment,
    payment=payment,
)

    return {
        "assessment_id": assessment.id,
        "payment_id": payment.id,
        "risk_score": risk_score,
        "risk_category": risk_category,
        "raw_score": result["raw_score"],
        "max_score": result["max_score"],
        "signals": signals,
        "signal_details": result["signals"],
        "created_at": assessment.created_at,
    }
@router.get(
    "/{payment_id}/risk/assessments",
)
def list_risk_assessments(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    merchant = (
        db.query(Merchant)
        .filter(
            Merchant.id == payment.merchant_id,
            Merchant.user_id == current_user.id,
        )
        .first()
    )

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this payment",
        )

    assessments = (
        db.query(RiskAssessment)
        .filter(
            RiskAssessment.payment_id == payment_id
        )
        .order_by(
            RiskAssessment.created_at.desc()
        )
        .all()
    )

    return [
        {
            "id": assessment.id,
            "payment_id": assessment.payment_id,
            "risk_score": assessment.risk_score,
            "risk_category": assessment.risk_category,
            "signals": assessment.signals,
            "created_at": assessment.created_at,
        }
        for assessment in assessments
    ]
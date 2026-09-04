from fastapi import APIRouter

from app.services.evidence import (
    collect_relevant_transactions,
    collect_refund_information,
    collect_dispute_information,
    collect_merchant_policies,
    collect_risk_signals,
)


router = APIRouter(
    prefix="/risk-review",
    tags=["Evidence"],
)


@router.post("/evidence/transactions")
def collect_transactions(
    merchant_id: int,
    transactions: list[dict],
):
    """
    Collect relevant transactions for a merchant.
    """

    return collect_relevant_transactions(
        merchant_id,
        transactions,
    )


@router.post("/evidence/refunds")
def collect_refunds(
    merchant_id: int,
    refunds: list[dict],
):
    """
    Collect refund information for a merchant.
    """

    return collect_refund_information(
        merchant_id,
        refunds,
    )


@router.post("/evidence/disputes")
def collect_disputes(
    merchant_id: int,
    disputes: list[dict],
):
    """
    Collect dispute information for a merchant.
    """

    return collect_dispute_information(
        merchant_id,
        disputes,
    )


@router.post("/evidence/policies")
def collect_policies(
    merchant_id: int,
    policies: list[dict],
):
    """
    Collect applicable merchant policies.
    """

    return collect_merchant_policies(
        merchant_id,
        policies,
    )


@router.post("/evidence/risk-signals")
def collect_risk_signals_api(
    merchant_id: int,
    risk_signals: list[dict],
):
    """
    Collect risk signals for a merchant.
    """

    return collect_risk_signals(
        merchant_id,
        risk_signals,
    )